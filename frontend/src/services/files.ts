import api from './api';
import { API_URL } from '../utils/constants';
import type { FileResponse } from '../types';

export const fileService = {
  async uploadFile(file: File): Promise<FileResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  async getFiles(): Promise<FileResponse[]> {
    const response = await api.get('/files');
    return response.data;
  },

  async getFile(fileId: number): Promise<FileResponse> {
    const response = await api.get(`/files/${fileId}`);
    return response.data;
  },

  async processFile(fileId: number): Promise<FileResponse> {
    const response = await api.post(`/files/${fileId}/process`);
    return response.data;
  },

  async deleteFile(fileId: number): Promise<void> {
    await api.delete(`/files/${fileId}`);
  },

  async downloadFile(fileId: number, filename: string): Promise<void> {
    const token = localStorage.getItem('access_token');
    const sessionId = localStorage.getItem('session_id');

    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    if (sessionId) {
      headers['X-Session-ID'] = sessionId;
    }

    const response = await fetch(`${API_URL}/files/${fileId}/download`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error('Ошибка при скачивании файла');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },
};