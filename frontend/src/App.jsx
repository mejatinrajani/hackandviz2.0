// App.jsx
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/LoginForm';
import Dashboard from './components/Dashboard';
import UserDetailForm from './components/UserDetailForm';
const App = () => {
  return (
    <Router>
      <Routes>
        {/* Default route redirects to login */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/user_detail" element={<UserDetailForm />} />
      </Routes>
    </Router>
  );
};

export default App;