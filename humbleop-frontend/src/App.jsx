import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';
import RegisterPage from './pages/RegisterPage';

const token = localStorage.getItem('token');

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={token ? <Navigate to="/profile" /> : <LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/profile" element={token ? <ProfilePage /> : <Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
