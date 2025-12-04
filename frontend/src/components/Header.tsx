import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';
import logoImage from '../assets/Logo.svg';
import chatIcon from '../assets/Chat.svg';
import { authService } from '../services/auth';

interface HeaderProps {
  showLoginButton?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ showLoginButton = true }) => {
  const isAuthenticated = authService.isAuthenticated();

  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="header-logo">
          <img src={logoImage} alt="Logo" className="header-logo-icon" />
          <span className="header-logo-text">Blur</span>
        </Link>
        {isAuthenticated ? (
          <div className="header-buttons">
            <Link to="/chat" className="header-btn chat-btn">
              <div className="chat-icon-frame">
                <img src={chatIcon} alt="Chat" className="header-chat-icon" />
              </div>
              <span className="chat-btn-text">Открыть чат</span>
            </Link>
            <Link to="/profile" className="header-btn profile-btn">
              Профиль
            </Link>
          </div>
        ) : (
          showLoginButton && (
            <Link to="/login" className="header-login-btn">
              Войти
            </Link>
          )
        )}
      </div>
    </header>
  );
};