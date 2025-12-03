import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Home } from './components/Home';
import { Login } from './components/Login';
import { Register } from './components/Register';
import { ForgotPassword } from './components/ForgotPassword';
import { Profile } from './components/Profile';
import { Settings } from './components/Settings';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;