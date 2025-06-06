// src/components/PageContainer.jsx
import React from 'react';
import customBg from '../assets/bg_whole.png';

export default function PageContainer({ children }) {
  return (
    <div
      className="min-h-screen px-1 py-3"
      style={{
        backgroundImage: `url(${customBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {children}
    </div>
  );
}
