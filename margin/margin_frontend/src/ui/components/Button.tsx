import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'default' | 'outline' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
  ...props
}) => {
  const baseClasses = "inline-flex items-center justify-center font-medium transition-colors rounded-full";
  
  const variantClasses = {
    default: "bg-blue-600 hover:bg-blue-700 text-white",
    outline: "bg-gray-800/50 border-grayborder hover:bg-[#333] text-gray-400",
    secondary: "bg-gray-800 hover:bg-gray-700 text-gray-300"
  };
  
  const sizeClasses = {
    sm: "py-1 px-3 text-sm",
    md: "py-2 px-4 text-sm",
    lg: "py-3 px-6 text-base"
  };
  
  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button; 