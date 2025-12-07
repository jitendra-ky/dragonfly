function Avatar({ name, size = 'md', className = '' }) {
  const initials = name
    ? name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : '?';

  const sizes = {
    sm: 'w-8 h-8 text-sm',
    md: 'w-10 h-10 text-base',
    lg: 'w-12 h-12 text-lg',
    xl: 'w-16 h-16 text-xl',
  };

  // Generate consistent color based on name
  const colors = [
    'bg-red-500',
    'bg-blue-500',
    'bg-green-500',
    'bg-yellow-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-teal-500',
  ];
  
  const colorIndex = name ? name.charCodeAt(0) % colors.length : 0;
  const bgColor = colors[colorIndex];

  return (
    <div
      className={`${sizes[size]} ${bgColor} rounded-full flex items-center justify-center text-white font-semibold ${className}`}
    >
      {initials}
    </div>
  );
}

export default Avatar;
