import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';

function RoutesWithAuth() {
  const { token } = useAuth();

  return (
    <Routes>
      <Route path="/" element={token ? <Navigate to="/profile" /> : <LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/profile" element={token ? <ProfilePage /> : <Navigate to="/" />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <RoutesWithAuth />
      </Router>
    </AuthProvider>
  );
}

export default App;
