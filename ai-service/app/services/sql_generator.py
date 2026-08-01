# ChatMistralAI is LangChain's interface to Mistral's chat (LLM) models.
# A "chat" model takes a list of messages (system + human) and returns a response.
from langchain_mistralai import ChatMistralAI

# ChatPromptTemplate lets us define a reusable prompt with variable placeholders
# (like template literals in JavaScript: `Hello ${name}`).
from langchain_core.prompts import ChatPromptTemplate

# StrOutputParser takes the raw LLM response object and extracts the plain text string from it.
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings


# Initialize the Mistral LLM client once at module load time.
# temperature controls how "creative" vs "deterministic" the model is:
#   temperature=0.0 → Fully deterministic. The model always picks the most likely next token.
#                     This is what we want for code/SQL generation — no surprises.
#   temperature=1.0 → Maximum creativity/randomness (good for writing, bad for code).
llm = ChatMistralAI(
    model=settings.MISTRAL_LLM_MODEL,        # "mistral-small-latest" (free tier)
    mistral_api_key=settings.MISTRAL_API_KEY,
    temperature=0.0
)


from app.core.prompts import SQL_SYSTEM_PROMPT


# ChatPromptTemplate.from_messages() defines the structure of the conversation we send to the LLM.
# It is a list of (role, content) tuples:
#   "system" → Sets the LLM's role and rules (sent before every request)
#   "human"  → The actual user input with our variable placeholders {schema} and {question}
# The {schema} and {question} parts are filled in when we call .invoke() later.
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SQL_SYSTEM_PROMPT),
    ("human", "SCHEMA:\n{schema}\n\nQUESTION: {question}")
])


# This is a LangChain CHAIN — a pipeline of steps connected with the | (pipe) operator.
# It works exactly like a Unix pipe: the output of each step becomes the input of the next.
#
#   prompt_template  →  Fills in {schema} and {question}, produces a list of messages
#         |
#         llm         →  Sends those messages to Mistral API, returns an AI response object
#         |
#   StrOutputParser  →  Extracts just the plain text string from the response object
#
# The final result of .invoke() on this chain is a plain Python string (the SQL query).
sql_generation_chain = prompt_template | llm | StrOutputParser()


def generate_sql(question: str, schema_context: str) -> str:
    """
    Generates a safe, read-only SQL query from a natural language question and schema.

    This is the core AI function of the entire service. It takes:
      - question: The user's plain English question. e.g., "Who has the most late marks?"
      - schema_context: The relevant table descriptions retrieved by RAG. e.g.,
                        "Table: employees. Columns: id, name, late_marks."

    The LLM is responsible for understanding the question and mapping it to the
    correct columns. Our validator.py is responsible for ensuring the output is safe.

    Returns:
        A raw SQL string. e.g., "SELECT name, late_marks FROM employees ORDER BY late_marks DESC LIMIT 5;"
    """
    # .invoke() runs the chain with our actual values, replacing the {placeholders}.
    response = sql_generation_chain.invoke({
        "schema": schema_context,
        "question": question
    })

    # --- Defensive Cleanup ---
    # Despite being told not to, some LLMs occasionally wrap their SQL in markdown
    # code blocks like: ```sql\nSELECT ...\n```
    # We strip these out to ensure we always get clean, executable SQL.
    cleaned_sql = response.strip()
    if cleaned_sql.startswith("```sql"):
        cleaned_sql = cleaned_sql[6:]    # Remove the first 6 characters: ` `` `sql`
    if cleaned_sql.startswith("```"):
        cleaned_sql = cleaned_sql[3:]    # Remove the first 3 characters: ` `` ``
    if cleaned_sql.endswith("```"):
        cleaned_sql = cleaned_sql[:-3]   # Remove the last 3 characters: ` `` ``

    return cleaned_sql.strip()
