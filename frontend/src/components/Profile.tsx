import React, { useState, useEffect } from 'react';
import './Profile.css';
import { ProfileHeader } from './ProfileHeader';
import { Footer } from './Footer';
import filterIcon from '../assets/Filter.svg';
import uploadIcon from '../assets/Upload.svg';
import deleteIcon from '../assets/Delete.svg';
import arrowDownIcon from '../assets/ArrowDown.svg';
import { fileService } from '../services/files';
import type { FileResponse } from '../types';

export const Profile: React.FC = () => {
  const [autoDelete] = useState('1 час');
  const [files, setFiles] = useState<FileResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloadingFileId, setDownloadingFileId] = useState<number | null>(null);
  const [deletingFileId, setDeletingFileId] = useState<number | null>(null);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      setLoading(true);
      setError('');
      const allFiles = await fileService.getFiles();
      // Фильтруем только обработанные файлы (processed, edited)
      const processedFiles = allFiles.filter(
        file => file.status === 'processed' || file.status === 'edited'
      );
      setFiles(processedFiles);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке файлов');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFile = async (fileId: number) => {
    if (!window.confirm('Вы уверены, что хотите удалить этот файл?')) {
      return;
    }

    try {
      setDeletingFileId(fileId);
      setError('');
      await fileService.deleteFile(fileId);
      setFiles(files.filter(file => file.id !== fileId));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при удалении файла');
    } finally {
      setDeletingFileId(null);
    }
  };

  const handleDownloadFile = async (file: FileResponse) => {
    try {
      setDownloadingFileId(file.id);
      setError('');
      
      // Определяем имя файла для скачивания
      const filename = file.status === 'processed' && file.processed_file_path
        ? `processed_${file.original_filename}`
        : file.original_filename;

      await fileService.downloadFile(file.id, filename);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при скачивании файла');
    } finally {
      setDownloadingFileId(null);
    }
  };

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
              
              <div className="profile-files-list">
                {error && <div className="profile-error">{error}</div>}
                
                {loading ? (
                  <div className="profile-loading">Загрузка файлов...</div>
                ) : files.length === 0 ? (
                  <div className="profile-empty">Нет обработанных файлов</div>
                ) : (
                  files.map((file) => (
                    <div key={file.id} className="profile-file-item">
                      <span className="file-name">{file.original_filename}</span>
                      <div className="file-actions">
                        <button 
                          className="file-action-btn upload-btn"
                          onClick={() => handleDownloadFile(file)}
                          disabled={loading || downloadingFileId === file.id || deletingFileId === file.id}
                          title="Скачать файл"
                        >
                          <img 
                            src={uploadIcon} 
                            alt="Download" 
                            className="action-icon"
                            style={{ opacity: downloadingFileId === file.id ? 0.5 : 1 }}
                          />
                        </button>
                        <button 
                          className="file-action-btn delete-btn"
                          onClick={() => handleDeleteFile(file.id)}
                          disabled={loading || downloadingFileId === file.id || deletingFileId === file.id}
                          title="Удалить файл"
                        >
                          <img 
                            src={deleteIcon} 
                            alt="Delete" 
                            className="action-icon"
                            style={{ opacity: deletingFileId === file.id ? 0.5 : 1 }}
                          />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
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