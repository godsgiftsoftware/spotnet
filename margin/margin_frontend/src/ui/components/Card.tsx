import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

const Card: React.FC<CardProps> = ({ children, className = "" }) => {
  return (
    <div className={`bg-black border border-grayborder rounded-lg shadow-lg ${className}`}>
      {children}
    </div>
  );
};

export default Card; 