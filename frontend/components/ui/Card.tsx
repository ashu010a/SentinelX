export default function Card({ title, children, className = '' }: { title?: string, children: React.ReactNode, className?: string }) {
  return (
    <div className={`bg-[#111118] border border-[#1e1e2e] rounded-xl p-6 ${className}`}>
      {title && <h3 className="text-lg font-medium mb-4 text-white">{title}</h3>}
      {children}
    </div>
  );
}
