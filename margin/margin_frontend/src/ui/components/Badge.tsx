import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  color?: string;
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({ children, color = "gray", className = "" }) => {
  const getColorClass = (color: string) => {
    switch (color.toLowerCase()) {
      case "green":
        return "text-green-500";
      case "yellow":
        return "text-yellow-500";
      case "red":
        return "text-red-500";
      case "blue":
        return "text-blue-500";
      default:
        return "text-gray-300";
    }
  };

  return (
    <span className={`px-2 inline-flex text-xs leading-5 font-semibold ${getColorClass(color)} ${className}`}>
      {children}
    </span>
  );
};

export default Badge; 