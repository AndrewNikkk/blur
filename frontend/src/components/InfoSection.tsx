import React from 'react';
import './InfoSection.css';
import shieldIcon from '../assets/Shield.svg';
import passportIcon from '../assets/Passport.svg';
import phoneIcon from '../assets/Phone.svg';
import cardIcon from '../assets/Card.svg';
import carIcon from '../assets/Car.svg';

export const InfoSection: React.FC = () => {
  return (
    <section className="info-section">
      <div className="info-icon-container">
      <img src={shieldIcon} alt="Щит" className="shield-icon-img" />
      <div className="info-icon-ellipse"></div>
      </div>
      
      <h1 className="info-title">
        Защитите свои конфиденциальные данные
      </h1>
      
      <p className="info-description">
        Автоматическая маскировка персональных данных на фотографиях и документах. 
        Паспорта, номера телефонов, автомобильные номера — всё под защитой.
      </p>
      
      <div className="info-cards">
        <div className="info-card">
          <div className="card-icon-frame">
            <img src={passportIcon} alt="Паспорта" className="card-icon-img" />
          </div>
          <span className="card-text">Паспорта</span>
        </div>
        
        <div className="info-card">
          <div className="card-icon-frame">
            <img src={phoneIcon} alt="Телефоны" className="card-icon-img" />
          </div>
          <span className="card-text">Телефоны</span>
        </div>
        
        <div className="info-card">
          <div className="card-icon-frame">
            <img src={cardIcon} alt="Карты" className="card-icon-img" />
          </div>
          <span className="card-text">Карты</span>
        </div>
        
        <div className="info-card">
          <div className="card-icon-frame">
            <img src={carIcon} alt="Авто номера" className="card-icon-img" />
          </div>
          <span className="card-text">Авто номера</span>
        </div>
      </div>
    </section>
  );
};