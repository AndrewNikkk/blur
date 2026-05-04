import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Register.css';
import { Header } from './Header';
import { Footer } from './Footer';
import { authService } from '../services/auth';
import { getApiErrorDetail } from '../utils/getApiErrorDetail';
import { useSeo } from '../hooks/useSeo';

export const Register: React.FC = () => {
  useSeo({
    title: 'Регистрация - Blur',
    description: 'Страница регистрации нового пользователя в Blur.',
    canonicalPath: '/register',
    noindex: true,
  });

  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    if (password.length < 8) {
      setError('Пароль должен быть не менее 8 символов');
      return;
    }

    setIsLoading(true);

    try {
      await authService.register({ login, password });
      await authService.login({ login, password });
      navigate('/');
    } catch (err: unknown) {
      setError(getApiErrorDetail(err) || 'Ошибка регистрации');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Header showLoginButton={false} />
      <div className="register-page">
        <div className="register-container">
          <h2 className="register-title">Регистрация</h2>
          
          <form className="register-form" onSubmit={handleSubmit}>
            {error && <div className="register-error">{error}</div>}
            
            <div className="register-fields">
              <input
                type="text"
                className="register-input"
                placeholder="Введите логин"
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                required
                disabled={isLoading}
              />
              <input
                type="password"
                className="register-password-input"
                placeholder="Введите пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                disabled={isLoading}
              />
              <input
                type="password"
                className="register-confirm-password-input"
                placeholder="Повторите пароль"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                disabled={isLoading}
              />
            </div>
            
            <button 
              type="submit" 
              className="register-button"
              disabled={isLoading}
            >
              <span className="register-button-text">
                {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
              </span>
            </button>
          </form>
        </div>
      </div>
      <Footer />
    </>
  );
};