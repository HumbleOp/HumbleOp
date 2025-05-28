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
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
          <div className="bg-gray-100 p-4 flex gap-6 text-sm">
            <NavLink to="/" className={({ isActive }) => isActive ? "text-blue-900 underline" : "text-blue-700 hover:underline"}>Home</NavLink>
            <NavLink to="/profile" className={({ isActive }) => isActive ? "text-blue-900 underline" : "text-blue-700 hover:underline"}>Profile</NavLink>
            <NavLink to="/create" className={({ isActive }) => isActive ? "text-blue-900 underline" : "text-blue-700 hover:underline"}>New Post</NavLink>
            <NavLink to="/posts" className={({ isActive }) => isActive ? "text-blue-900 underline" : "text-blue-700 hover:underline"}>All Posts</NavLink>
            <NavLink to="/completed" className={({ isActive }) => isActive ? "text-blue-900 underline" : "text-blue-700 hover:underline"}>Completed Posts</NavLink>
          </div>
        <RoutesWithAuth />
      </Router>
    </AuthProvider>
  );
}


export default App;
