import React from 'react';
import './Settings.css';
import { ProfileHeader } from './profileHeader';
import { Footer } from './Footer';

export const Settings: React.FC = () => {
  return (
    <>
      <ProfileHeader />
      <div className="settings-page">
        <div className="settings-container">
          <h2 className="settings-title">Настройки</h2>
          
          <div className="settings-files">
            <div className="settings-file-item">
              <span className="settings-file-name">Сменить пароль</span>
            </div>
            <div className="settings-file-item settings-file-item-red">
              <span className="settings-file-name">Удалить аккаунт</span>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
};