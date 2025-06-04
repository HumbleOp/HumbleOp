import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ProfilePage from "./pages/ProfilePage";
import PublicProfilePage from "./pages/PublicProfilePage";
import CreatePost from "./pages/CreatePost";
import PostList from "./pages/PostList";
import PostDetail from "./pages/PostDetail";
import PostVictoryPage from "./pages/PostVictoryPage";
import CompletedPosts from "./pages/CompletedPosts";
import DuelPage from "./pages/DuelPage";
import TestTools from "./pages/TestTools";
import SearchResults from "./pages/SearchResults";
import Navbar from "./components/Navbar";
import { Toaster } from "react-hot-toast";

function Protected({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/" />;
}

function NavbarWrapper() {
  const location = useLocation();
  const hide = ["/", "/register"].includes(location.pathname);
  return !hide ? <Navbar /> : null;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Toaster position="top-right" />
        <NavbarWrapper />
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/search" element={<Protected><SearchResults /></Protected>} />
          <Route path="/profile" element={<Protected><ProfilePage /></Protected>} />
          <Route path="/profile/:username" element={<Protected><PublicProfilePage /></Protected>} />
          <Route path="/create" element={<Protected><CreatePost /></Protected>} />
          <Route path="/posts" element={<Protected><PostList /></Protected>} />
          <Route path="/post/:id" element={<Protected><PostDetail /></Protected>} />
          <Route path="/victory/:id" element={<Protected><PostVictoryPage /></Protected>} />
          <Route path="/completed" element={<Protected><CompletedPosts /></Protected>} />
          <Route path="/duel/:id" element={<Protected><DuelPage /></Protected>} />
          <Route path="/test" element={<Protected><TestTools /></Protected>} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
