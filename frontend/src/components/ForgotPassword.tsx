import React, { useState } from 'react';
import './ForgotPassword.css';
import { Header } from './Header';
import { Footer } from './Footer';

export const ForgotPassword: React.FC = () => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
  };

  return (
    <>
      <Header showLoginButton={false} />
      <div className="forgot-password-page">
        <div className="forgot-password-container">
          <h2 className="forgot-password-title">Восстановление доступа</h2>
          
          <form className="forgot-password-form" onSubmit={handleSubmit}>
            <div className="forgot-password-fields">
              <input
                type="password"
                className="forgot-password-input"
                placeholder="Введите новый пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <input
                type="password"
                className="forgot-password-confirm-input"
                placeholder="Повторите новый пароль"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
            
            <button type="submit" className="forgot-password-button">
              <span className="forgot-password-button-text">Сохранить</span>
            </button>
          </form>
        </div>
      </div>
      <Footer />
    </>
  );
};