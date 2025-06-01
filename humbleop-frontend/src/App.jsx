import { BrowserRouter as Router, Routes, Route, Navigate, NavLink } from "react-router-dom";
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import CreatePost from './pages/CreatePost';
import PostList from './pages/PostList';
import PostDetail from './pages/PostDetail';
import PostVictoryPage from "./pages/PostVictoryPage";
import CompletedPosts from "./pages/CompletedPosts";
import DuelPage from './pages/DuelPage';
import TestTools from './pages/TestTools';
import Navbar from "./components/Navbar";
import { Toaster } from 'react-hot-toast';




function RoutesWithAuth() {
  const { token } = useAuth();

  return (
    <Routes>
      <Route path="/" element={token ? <Navigate to="/profile" /> : <LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/profile" element={token ? <ProfilePage /> : <Navigate to="/" />} />
      <Route path="/create" element={token ? <CreatePost /> : <Navigate to="/" />} />
      <Route path="/posts" element={<PostList />} />
      <Route path="/post/:id" element={<PostDetail />} />
      <Route path="/victory/:id" element={<PostVictoryPage />} />
      <Route path="/completed" element={<CompletedPosts />} />
      <Route path="/duel/:id" element={token ? <DuelPage /> : <Navigate to="/" />} />
      <Route path="/test" element={<TestTools />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Toaster position="top-right" />
          <Navbar />
        <RoutesWithAuth />
      </Router>
    </AuthProvider>
  );
}


export default App;
