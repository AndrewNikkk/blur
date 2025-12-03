import React from 'react';
import './UploadSection.css';
import uploadIcon from '../assets/Upload.svg';

export const UploadSection: React.FC = () => {
  return (
    <div className="upload-section">
      <div className="upload-inner">
        <div className="upload-icon-container">
          <img src={uploadIcon} alt="Upload" className="upload-icon" />
        </div>
        <p className="upload-text">
          Нажмите для загрузки или перетащите файл Поддерживаются: JPG, PNG, PDF
        </p>
      </div>
    </div>
  );
};