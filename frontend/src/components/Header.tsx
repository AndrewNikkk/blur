import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';
import logoImage from '../assets/Logo.svg';

export const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-logo">
          <img src={logoImage} alt="Logo" className="header-logo-icon" />
          <span className="header-logo-text">Blur</span>
        </div>
        <Link to="/login" className="header-login-btn">
          Войти
        </Link>
      </div>
    </header>
  );
};