import { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

const Home = lazy(() => import('./components/Home').then((m) => ({ default: m.Home })));
const Login = lazy(() => import('./components/Login').then((m) => ({ default: m.Login })));
const Register = lazy(() => import('./components/Register').then((m) => ({ default: m.Register })));
const ForgotPassword = lazy(() => import('./components/ForgotPassword').then((m) => ({ default: m.ForgotPassword })));
const Profile = lazy(() => import('./components/Profile').then((m) => ({ default: m.Profile })));
const Settings = lazy(() => import('./components/Settings').then((m) => ({ default: m.Settings })));
const NotFound = lazy(() => import('./components/NotFound').then((m) => ({ default: m.NotFound })));

function App() {
  return (
    <Router>
      <div className="app">
        <Suspense fallback={<div style={{ padding: '24px' }}>Загрузка страницы...</div>}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </div>
    </Router>
  );
}

export default App;