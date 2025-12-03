import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';
import logoImage from '../assets/Logo.svg';

interface HeaderProps {
  showLoginButton?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ showLoginButton = true }) => {
  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="header-logo">
          <img src={logoImage} alt="Logo" className="header-logo-icon" />
          <span className="header-logo-text">Blur</span>
        </Link>
        {showLoginButton && (
          <Link to="/login" className="header-login-btn">
            Войти
          </Link>
        )}
      </div>
    </header>
  );
};