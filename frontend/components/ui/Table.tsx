import React from 'react';

interface Column { key: string; label: string; render?: (val: any, row: any) => React.ReactNode }
export default function Table({ columns, data, onRowClick }: { columns: Column[], data: any[], onRowClick?: (row: any) => void }) {
  return (
    <div className="w-full overflow-x-auto rounded-lg border border-[#1e1e2e]">
      <table className="w-full text-sm text-left text-gray-300">
        <thead className="text-xs uppercase bg-[#111118] border-b border-[#1e1e2e] text-gray-400">
          <tr>{columns.map(c => <th key={c.key} className="px-6 py-3">{c.label}</th>)}</tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} onClick={() => onRowClick?.(row)} className="bg-[#0a0a0f] border-b border-[#1e1e2e] hover:bg-[#111118] cursor-pointer">
              {columns.map(c => (
                <td key={c.key} className="px-6 py-4">{c.render ? c.render(row[c.key], row) : row[c.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
