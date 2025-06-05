export default function PageContainer({ children }) {
  return (
    <div
      className="min-h-screen px-4 py-6"
      style={{
         background: 'linear-gradient(to right, #0f160f 0%, #222b22 100%)',
      }}
    >
      {children}
    </div>
  );
}
