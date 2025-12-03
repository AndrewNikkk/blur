import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Login.css';
import { Header } from './Header';
import { Footer } from './Footer';

export const Login: React.FC = () => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
  };

  return (
    <>
      <Header showLoginButton={false} />
      <div className="login-page">
        <div className="login-container">
          <h2 className="login-title">Вход в систему</h2>
          
          <form className="login-form" onSubmit={handleSubmit}>
            <div className="login-fields">
              <input
                type="text"
                className="login-input"
                placeholder="Введите логин"
                value={login}
                onChange={(e) => setLogin(e.target.value)}
              />
              <input
                type="password"
                className="password-input"
                placeholder="Введите пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            
            <button type="submit" className="login-button">
              <span className="login-button-text">Войти</span>
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