import React, { useRef, useState } from 'react';
import './UploadSection.css';
import uploadIcon from '../assets/Upload.svg';
import removeIcon from '../assets/RemoveIcon.svg';
import { fileService } from '../services/files';
import { authService } from '../services/auth';
import type { FileResponse } from '../types';

export const UploadSection: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadedFiles, setUploadedFiles] = useState<FileResponse[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [downloadingFileId, setDownloadingFileId] = useState<number | null>(null);
  const [viewingFileId, setViewingFileId] = useState<number | null>(null);
  const [savingAll, setSavingAll] = useState(false);
  const isAuthenticated = authService.isAuthenticated();

  const handleFileSelect = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    const filesArray = Array.from(files);
    
    const invalidFiles = filesArray.filter(file => !validTypes.includes(file.type));
    if (invalidFiles.length > 0) {
      setError('Поддерживаются только файлы: JPG, PNG, PDF');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const uploadPromises = filesArray.map(file => fileService.uploadFile(file));
      const results = await Promise.all(uploadPromises);
      
      // Сохраняем session_id для неавторизованных пользователей
      if (!isAuthenticated) {
        const fileWithSessionId = results.find(file => file.session_id);
        if (fileWithSessionId?.session_id && !localStorage.getItem('session_id')) {
          localStorage.setItem('session_id', fileWithSessionId.session_id);
        }
      }
      
      setUploadedFiles(prev => [...prev, ...results]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке файла');
    } finally {
      setLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(e.target.files);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleRemoveFile = async (fileId: number) => {
    try {
      await fileService.deleteFile(fileId);
      setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при удалении файла');
    }
  };

  const handleProcess = async () => {
    if (uploadedFiles.length === 0) return;

    setProcessing(true);
    setError('');

    try {
      const filesToProcess = uploadedFiles.filter(file => file.status === 'uploaded');
      
      if (filesToProcess.length === 0) {
        setError('Нет файлов для обработки');
        setProcessing(false);
        return;
      }

      // Обрабатываем файлы по очереди, чтобы видеть результаты
      const results = await Promise.allSettled(
        filesToProcess.map(file => fileService.processFile(file.id))
      );

      // Проверяем результаты обработки
      const successful = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.filter(r => r.status === 'rejected').length;

      // Обновляем список файлов с сервера
      const updatedFiles = await fileService.getFiles();
      const currentFileIds = uploadedFiles.map(f => f.id);
      const newFiles = updatedFiles.filter(f => currentFileIds.includes(f.id));
      
      // Обновляем состояние файлов
      setUploadedFiles(prev => {
        const fileMap = new Map(prev.map(f => [f.id, f]));
        // Обновляем существующие файлы из ответа сервера
        newFiles.forEach(newFile => {
          fileMap.set(newFile.id, newFile);
        });
        return Array.from(fileMap.values());
      });

      if (failed > 0) {
        setError(`Обработано: ${successful}, ошибок: ${failed}`);
      } else {
        // alert('Файлы успешно обработаны');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при обработке файлов');
    } finally {
      setProcessing(false);
    }
  };

  const handleViewFile = async (file: FileResponse) => {
    try {
      setViewingFileId(file.id);
      setError('');
      await fileService.viewFile(file.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при просмотре файла');
    } finally {
      setViewingFileId(null);
    }
  };

  const handleDownloadFile = async (file: FileResponse) => {
    try {
      setDownloadingFileId(file.id);
      setError('');
      
      // Определяем имя файла для скачивания
      const filename = (file.status === 'processed' || file.status === 'edited') && file.processed_file_path
        ? `${file.original_filename.replace(/\.[^/.]+$/, '')}_blured${file.original_filename.match(/\.[^/.]+$/)?.[0] || ''}`
        : file.original_filename;

      await fileService.downloadFile(file.id, filename);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при скачивании файла');
    } finally {
      setDownloadingFileId(null);
    }
  };

  const handleSaveAndDownloadAll = async () => {
    try {
      setSavingAll(true);
      setError('');
      
      // Получаем только успешно обработанные файлы
      const processedFiles = uploadedFiles.filter(
        file => (file.status === 'processed' || file.status === 'edited' || file.status === 'saved') && file.processed_file_path
      );

      // Сохраняем все файлы (если требуется авторизация)
      if (isAuthenticated) {
        for (const file of processedFiles) {
          try {
            await fileService.saveFile(file.id);
          } catch (err: any) {
            console.error(`Ошибка при сохранении файла ${file.id}:`, err);
          }
        }
      }

      // Обновляем список файлов
      const updatedFiles = await fileService.getFiles();
      const currentFileIds = uploadedFiles.map(f => f.id);
      setUploadedFiles(updatedFiles.filter(f => currentFileIds.includes(f.id)));

      // Скачиваем все обработанные файлы
      const filesToDownload = uploadedFiles.filter(
        file => (file.status === 'processed' || file.status === 'edited' || file.status === 'saved') && file.processed_file_path
      );

      for (const file of filesToDownload) {
        try {
          await handleDownloadFile(file);
          // Небольшая задержка между скачиваниями
          await new Promise(resolve => setTimeout(resolve, 300));
        } catch (err: any) {
          console.error(`Ошибка при скачивании файла ${file.id}:`, err);
        }
      }

      alert('Все файлы сохранены и скачаны');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при сохранении и скачивании файлов');
    } finally {
      setSavingAll(false);
    }
  };

  const hasProcessedFiles = uploadedFiles.some(
    file => (file.status === 'processed' || file.status === 'edited' || file.status === 'saved') && file.processed_file_path
  );

  return (
    <div className="upload-section">
      <input
        ref={fileInputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.pdf"
        multiple
        onChange={handleFileInputChange}
        style={{ display: 'none' }}
        disabled={loading || processing}
      />
      
      {uploadedFiles.length === 0 ? (
        <div
          className={`upload-inner ${dragActive ? 'upload-inner-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={handleClick}
        >
          <div className="upload-icon-container">
            <img src={uploadIcon} alt="Upload" className="upload-icon" />
          </div>
          <p className="upload-text">
            Нажмите для загрузки или перетащите файл Поддерживаются: JPG, PNG, PDF
          </p>
          {error && <div className="upload-error">{error}</div>}
        </div>
      ) : (
        <>
          <div className="upload-files-list">
            {uploadedFiles.map((file) => {
              const isError = file.status === 'processing' && !file.processed_file_path;
              const isSuccess = (file.status === 'processed' || file.status === 'edited' || file.status === 'saved') && file.processed_file_path;
              const filename = isSuccess
                ? `${file.original_filename.replace(/\.[^/.]+$/, '')}_blured${file.original_filename.match(/\.[^/.]+$/)?.[0] || ''}`
                : file.original_filename;

              return (
                <div key={file.id} className="upload-file-item">
                  <span className="upload-file-name">{filename}</span>
                  {isError ? (
                    <span className="upload-file-error">error</span>
                  ) : isSuccess ? (
                    <div className="upload-file-actions">
                      {isAuthenticated && (
                        <button
                          className="upload-file-view-btn"
                          onClick={() => handleViewFile(file)}
                          disabled={loading || processing || viewingFileId === file.id || downloadingFileId === file.id}
                          title="Просмотреть файл"
                        >
                          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="#6366F1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            <circle cx="12" cy="12" r="3" stroke="#6366F1" strokeWidth="2"/>
                          </svg>
                        </button>
                      )}
                      <button
                        className="upload-file-download-btn"
                        onClick={() => handleDownloadFile(file)}
                        disabled={loading || processing || viewingFileId === file.id || downloadingFileId === file.id}
                        title="Скачать файл"
                      >
                        <img src={uploadIcon} alt="Download" className="upload-file-action-icon" />
                      </button>
                    </div>
                  ) : (
                    <button
                      className="upload-file-remove"
                      onClick={() => handleRemoveFile(file.id)}
                      disabled={loading || processing}
                      title="Удалить файл"
                    >
                      <img src={removeIcon} alt="Remove" className="upload-file-remove-icon" />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
          {error && <div className="upload-error">{error}</div>}
        </>
      )}

      {/* Кнопка Обработать, если есть незагруженные файлы */}
      {uploadedFiles.length > 0 && uploadedFiles.some(f => f.status === 'uploaded') && (
        <button
          className="upload-process-button"
          onClick={handleProcess}
          disabled={loading || processing}
        >
          {processing ? 'Обработка...' : 'Обработать'}
        </button>
      )}

      {/* Кнопка Сохранить и скачать, если есть обработанные файлы И пользователь авторизован */}
      {isAuthenticated && hasProcessedFiles && (
        <button
          className="upload-save-all-button"
          onClick={handleSaveAndDownloadAll}
          disabled={loading || processing || savingAll}
        >
          {savingAll ? 'Сохранение и скачивание...' : 'Сохранить и скачать'}
        </button>
      )}
    </div>
  );
};