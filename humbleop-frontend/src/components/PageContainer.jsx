// src/components/PageContainer.jsx

export default function PageContainer({ children }) {
  return (
    <div className="min-h-screen bg-[#101B13] text-[#E8E5DC] px-4 py-6">
      {children}
    </div>
  );
}
