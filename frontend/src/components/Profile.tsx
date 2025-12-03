import React, { useState } from 'react';
import './Profile.css';
import { ProfileHeader } from './profileHeader.tsx';
import { Footer } from './Footer';
import filterIcon from '../assets/Filter.svg';
import uploadIcon from '../assets/Upload.svg';
import deleteIcon from '../assets/Delete.svg';
import arrowDownIcon from '../assets/ArrowDown.svg';

export const Profile: React.FC = () => {
  const [autoDelete] = useState('1 час');

  const files = [
    { id: 1, name: 'Документ_2025_07_13_43' },
    { id: 2, name: 'Jpeg_2025_07_13_13_57' },
    { id: 3, name: 'PDF_2025_06_11_15' },
  ];

  return (
    <>
      <ProfileHeader />
      <div className="profile-page">
        <div className="profile-storage">
          <h2 className="profile-storage-title">Мои файлы</h2>
          
          <div className="profile-content">
            <div className="profile-files">
              <div className="profile-filter">
                <span className="filter-text">Фильтр</span>
                <img src={filterIcon} alt="Filter" className="filter-icon" />
              </div>
              
              {files.map((file) => (
                <div key={file.id} className="profile-file-item">
                  <span className="file-name">{file.name}</span>
                  <div className="file-actions">
                    <button className="file-action-btn upload-btn">
                      <img src={uploadIcon} alt="Upload" className="action-icon" />
                    </button>
                    <button className="file-action-btn delete-btn">
                      <img src={deleteIcon} alt="Delete" className="action-icon" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="profile-storage-time">
              <span className="auto-delete-text">Авто удаление через</span>
              <div className="auto-delete-select">
                <span className="auto-delete-value">{autoDelete}</span>
                <img src={arrowDownIcon} alt="Arrow" className="arrow-icon" />
              </div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
};