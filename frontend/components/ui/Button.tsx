import React from 'react';
import clsx from 'clsx';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export default function Button({ variant = 'primary', size = 'md', isLoading, children, className, ...props }: ButtonProps) {
  const baseStyle = 'inline-flex items-center justify-center font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0a0a0f] transition-colors';
  const variants = {
    primary: 'bg-[#6366f1] hover:bg-[#818cf8] text-white',
    secondary: 'bg-[#1e1e2e] hover:bg-[#2a2a3c] text-white',
    danger: 'bg-red-500 hover:bg-red-600 text-white'
  };
  const sizes = { sm: 'px-3 py-1.5 text-sm', md: 'px-4 py-2 text-sm', lg: 'px-6 py-3 text-base' };

  return (
    <button className={clsx(baseStyle, variants[variant], sizes[size], className)} disabled={isLoading || props.disabled} {...props}>
      {isLoading && <span className="mr-2 animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>}
      {children}
    </button>
  );
}
