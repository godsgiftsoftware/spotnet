import React from 'react';

interface PaginationProps {
  currentPage: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalItems,
  pageSize,
  onPageChange
}) => {
  const totalPages = Math.ceil(totalItems / pageSize);
  
  if (totalPages <= 1) return null;
    
  let pages: (number | string)[] = [];
  if (totalPages <= 5) {    
    pages = Array.from({ length: totalPages }, (_, i) => i + 1);
  } else {    
    pages = [1];
    
    if (currentPage > 3) {
      pages.push('...');
    }
        
    const start = Math.max(2, currentPage - 1);
    const end = Math.min(totalPages - 1, currentPage + 1);
    
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    
    if (currentPage < totalPages - 2) {
      pages.push('...');
    }
    
    pages.push(totalPages);
  }
  
  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-3 py-1 bg-gray-900 text-gray-400 rounded-md hover:bg-gray-800 disabled:opacity-50 disabled:pointer-events-none"
      >
        Previous
      </button>
      
      {pages.map((page, i) => (
        typeof page === 'number' ? (
          <button
            key={i}
            onClick={() => onPageChange(page)}
            className={`w-8 h-8 flex items-center justify-center rounded-md text-sm ${
              currentPage === page 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-900 border border-grayborder text-gray-300 hover:bg-gray-800'
            }`}
          >
            {page}
          </button>
        ) : (
          <span key={i} className="w-8 text-center text-gray-500">...</span>
        )
      ))}
      
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-3 py-1 bg-gray-900 text-gray-400 rounded-md hover:bg-gray-800 disabled:opacity-50 disabled:pointer-events-none"
      >
        Next
      </button>
    </div>
  );
};

export default Pagination; 