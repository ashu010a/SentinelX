export default function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-10 bg-[#1e1e2e] rounded w-full"></div>
      <div className="h-10 bg-[#1e1e2e] rounded w-full"></div>
      <div className="h-10 bg-[#1e1e2e] rounded w-full"></div>
    </div>
  );
}
