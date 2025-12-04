import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Login.css';
import { Header } from './Header';
import { Footer } from './Footer';
import { authService } from '../services/auth';

export const Login: React.FC = () => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!login || !password) {
      setError('Заполните все поля');
      return;
    }

    setIsLoading(true);

    try {
      await authService.login({ login, password });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка входа. Проверьте логин и пароль.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Header showLoginButton={false} />
      <div className="login-page">
        <div className="login-container">
          <h2 className="login-title">Вход в систему</h2>
          
          <form className="login-form" onSubmit={handleSubmit}>
            {error && <div className="login-error">{error}</div>}
            
            <div className="login-fields">
              <input
                type="text"
                className="login-input"
                placeholder="Введите логин"
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                disabled={isLoading}
                required
              />
              <input
                type="password"
                className="password-input"
                placeholder="Введите пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>
            
            <button type="submit" className="login-button" disabled={isLoading}>
              <span className="login-button-text">
                {isLoading ? 'Вход...' : 'Войти'}
              </span>
            </button>
            
            <div className="login-links">
              <Link to="/forgot-password" className="forgot-password-link">
                Забыли пароль?
              </Link>
              <Link to="/register" className="register-link">
                Зарегистрироваться
              </Link>
            </div>
          </form>
        </div>
      </div>
      <Footer />
    </>
  );
};