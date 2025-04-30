import React from 'react';

interface Column {
  header: string;
  accessor: string;
  cell?: (row: any) => React.ReactNode;
}

interface TableProps {
  data: any[];
  columns: Column[];
  loading?: boolean;
}

const Table: React.FC<TableProps> = ({ data, columns, loading }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse bg-black">
        <thead>
          <tr className="text-left py-4 border-b border-grayborder">
            {columns.map((column, i) => (
              <th key={i} className="text-sm font-semibold pb-4 px-4 text-tableHeads uppercase">
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-grayborder text-white">
          {loading ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-6 text-center text-gray-400">
                Loading...
              </td>
            </tr>
          ) : !data || data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-6 text-center text-gray-400">
                No data available
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr key={i} className="hover:bg-[#1a1a1a]">
                {columns.map((column, j) => (
                  <td key={j} className="px-4 py-4 whitespace-nowrap">
                    {column.cell && typeof column.cell === 'function' 
                      ? column.cell(row) 
                      : row[column.accessor] || '-'}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default Table; 