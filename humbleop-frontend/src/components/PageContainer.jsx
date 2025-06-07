import React from 'react';

export default function PageContainer({ children }) {
  return (
    <div
      className="min-h-screen px-1 py-3"
      style={{
        backgroundColor: '#1a1a1a',
      }}
    >
      {children}
    </div>
  );
}
