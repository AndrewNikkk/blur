import React, { useRef, useState } from 'react';
import './UploadSection.css';
import uploadIcon from '../assets/Upload.svg';
import removeIcon from '../assets/RemoveIcon.svg';
import { fileService } from '../services/files';
import type { FileResponse } from '../types';

export const UploadSection: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadedFiles, setUploadedFiles] = useState<FileResponse[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);

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

  const handleRemoveFile = (fileId: number) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const handleProcess = async () => {
    if (uploadedFiles.length === 0) return;

    setProcessing(true);
    setError('');

    try {
      const filesToProcess = uploadedFiles.filter(file => file.status === 'uploaded');
      const processPromises = filesToProcess.map(file => fileService.processFile(file.id));
      await Promise.all(processPromises);
      
      const updatedFiles = await fileService.getFiles();
      const currentFileIds = uploadedFiles.map(f => f.id);
      setUploadedFiles(updatedFiles.filter(f => currentFileIds.includes(f.id)));
      
      alert('Файлы успешно обработаны');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при обработке файлов');
    } finally {
      setProcessing(false);
    }
  };

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
            {uploadedFiles.map((file) => (
              <div key={file.id} className="upload-file-item">
                <span className="upload-file-name">{file.original_filename}</span>
                <button
                  className="upload-file-remove"
                  onClick={() => handleRemoveFile(file.id)}
                  disabled={loading || processing}
                >
                  <img src={removeIcon} alt="Remove" className="upload-file-remove-icon" />
                </button>
              </div>
            ))}
          </div>
          {error && <div className="upload-error">{error}</div>}
        </>
      )}
      {uploadedFiles.length > 0 && (
        <button
          className="upload-process-button"
          onClick={handleProcess}
          disabled={loading || processing || uploadedFiles.every(f => f.status !== 'uploaded')}
        >
          {processing ? 'Обработка...' : 'Обработать'}
        </button>
      )}
    </div>
  );
};