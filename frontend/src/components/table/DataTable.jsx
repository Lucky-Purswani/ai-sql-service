import React from 'react';

export default function DataTable({ columns, rows, totalRows }) {
  if (!columns || columns.length === 0) {
    return null;
  }

  return (
    <div className="data-table-container">
      <div className="data-table-header">
        <h3 className="data-table-title">Results</h3>
        <span className="data-table-badge">
          Showing {rows.length} of {totalRows} rows
        </span>
      </div>
      
      <div className="data-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((col, idx) => (
                <th key={idx}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="data-table-empty">
                  No results found
                </td>
              </tr>
            ) : (
              rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {columns.map((col, colIndex) => {
                    const val = row[col];
                    // Handle booleans, nulls, objects beautifully
                    let displayVal = val;
                    if (val === null) displayVal = <span className="val-null">NULL</span>;
                    else if (typeof val === 'boolean') displayVal = <span className="val-bool">{val ? 'TRUE' : 'FALSE'}</span>;
                    else if (typeof val === 'object') displayVal = JSON.stringify(val);
                    
                    return <td key={colIndex}>{displayVal}</td>;
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
