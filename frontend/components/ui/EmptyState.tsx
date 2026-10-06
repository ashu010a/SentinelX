export default function EmptyState({ icon: Icon, title, description, action }: { icon: any, title: string, description: string, action?: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border-2 border-dashed border-[#1e1e2e] rounded-xl">
      <Icon className="w-12 h-12 text-gray-500 mb-4" />
      <h3 className="text-lg font-medium text-white">{title}</h3>
      <p className="mt-2 text-sm text-gray-400 max-w-sm">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
