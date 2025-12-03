import React, { useState } from 'react';
import './Register.css';
import { Header } from './Header';
import { Footer } from './Footer';

export const Register: React.FC = () => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
  };

  return (
    <>
      <Header showLoginButton={false} />
      <div className="register-page">
        <div className="register-container">
          <h2 className="register-title">Регистрация</h2>
          
          <form className="register-form" onSubmit={handleSubmit}>
            <div className="register-fields">
              <input
                type="text"
                className="register-input"
                placeholder="Введите логин"
                value={login}
                onChange={(e) => setLogin(e.target.value)}
              />
              <input
                type="password"
                className="register-password-input"
                placeholder="Введите пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <input
                type="password"
                className="register-confirm-password-input"
                placeholder="Повторите пароль"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
            
            <button type="submit" className="register-button">
              <span className="register-button-text">Зарегистрироваться</span>
            </button>
          </form>
        </div>
      </div>
      <Footer />
    </>
  );
};