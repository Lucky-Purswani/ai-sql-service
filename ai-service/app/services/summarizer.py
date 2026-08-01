from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings

# json is a Python built-in library (no install needed).
# We use it to convert Python dictionaries/lists into a JSON-formatted string
# so the LLM can read the data rows in a structured, readable format.
import json


# Note the temperature is 0.3 here, unlike sql_generator.py which uses 0.0.
# For summarization, we WANT a little bit of natural language variation and warmth.
# 0.3 gives the model slight creative freedom in phrasing while keeping it grounded.
# If we used 0.0, the summaries would feel robotic and repetitive.
llm = ChatMistralAI(
    model=settings.MISTRAL_LLM_MODEL,
    mistral_api_key=settings.MISTRAL_API_KEY,
    temperature=0.3  # Slight creativity for natural-sounding summaries (vs 0.0 for SQL)
)


from app.core.prompts import SUMMARY_SYSTEM_PROMPT


# The prompt template defines how the conversation is structured before sending to the LLM.
# - "system" is the overall rule set we defined above.
# - "human" is the dynamic part where we inject the {question} and {rows} using f-string-like syntax.
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SUMMARY_SYSTEM_PROMPT),
    ("human", "QUESTION: {question}\n\nROW COUNT: {row_count}\n\nDATA ROWS:\n{rows}")
])


# LangChain chain pipeline: same pattern as sql_generator.py
# prompt → fills in placeholders → LLM → StrOutputParser → plain text string
summarization_chain = prompt_template | llm | StrOutputParser()


def generate_summary(question: str, rows: list[dict], row_count: int) -> str:
    """
    Converts raw database result rows into a friendly, plain-English summary.

    This is the last step in the query pipeline, called AFTER the SQL has been
    executed and results have been returned by Node.js.

    Args:
        question:  The original natural language question. e.g., "Who has the most late marks?"
        rows:      The result rows from the database as a list of dictionaries.
                   e.g., [{"name": "Amit", "late_marks": 6}, {"name": "Sara", "late_marks": 8}]
        row_count: The number of rows returned. Used to handle the empty-results edge case.

    Returns:
        A plain English string. e.g., "Amit and Sara have late arrivals, with 6 and 8 late marks."
    """
    # json.dumps() converts the Python list of dicts into a formatted JSON string.
    # This is necessary because LLMs receive text, not Python objects.
    # indent=2 adds pretty-printing (newlines and indentation) so the LLM can read it easily.
    # If there are no rows, we pass "[]" (an empty JSON array) to avoid sending "null" or "".
    rows_str = json.dumps(rows, indent=2) if row_count > 0 else "[]"

    # .invoke() runs the chain, filling in all the placeholders and calling the Mistral API.
    response = summarization_chain.invoke({
        "question": question,
        "row_count": row_count,
        "rows": rows_str
    })

    # .strip() removes any leading/trailing whitespace or newlines from the LLM's response.
    return response.strip()
