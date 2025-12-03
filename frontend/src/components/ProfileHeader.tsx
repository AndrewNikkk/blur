import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './ProfileHeader.css';
import logoImage from '../assets/Logo.svg';
import settingsIcon from '../assets/Settings.svg';
import chatIcon from '../assets/Chat.svg';

export const ProfileHeader: React.FC = () => {
  const location = useLocation();
  const isSettingsPage = location.pathname === '/settings';

  return (
    <header className="profile-header">
      <div className={`profile-header-content ${isSettingsPage ? 'settings-page-header' : ''}`}>
        <Link to="/" className="profile-header-logo">
          <img src={logoImage} alt="Logo" className="profile-header-logo-icon" />
          <span className="profile-header-logo-text">Blur</span>
        </Link>
        
        <div className="profile-header-buttons">
          {!isSettingsPage && (
            <Link to="/settings" className="profile-header-btn profile-btn">
              <img src={settingsIcon} alt="Settings" className="settings-btn-icon" />
              <span className="profile-btn-text">Настройки</span>
            </Link>
          )}
          <button className="profile-header-btn logout-btn">
            <img src={chatIcon} alt="Chat" className="chat-btn-icon" />
            <span className="logout-btn-text">Открыть чат</span>
          </button>
          <Link to="/" className="profile-header-btn home-btn">
            <span className="home-btn-text">На главную</span>
          </Link>
        </div>
      </div>
    </header>
  );
};