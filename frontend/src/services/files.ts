import api from './api';
import { API_URL } from '../utils/constants';
import type { FileResponse, PaginatedFileResponse } from '../types';

export const fileService = {
  async getFilesPaginated(params: {
    search?: string;
    date_filter?: 'today' | 'week' | 'month';
    size_filter?: 'small' | 'medium' | 'large';
    sort?: 'date_desc' | 'date_asc' | 'name_asc' | 'name_desc' | 'size_desc' | 'size_asc';
    page?: number;
    per_page?: number;
  }): Promise<PaginatedFileResponse> {
    const response = await api.get('/files/paginated', { params });
    return response.data;
  },

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

    if (!token && !sessionId) {
      throw new Error('Требуется авторизация или session_id для скачивания файла');
    }

    // Получаем presigned URL и скачиваем через ссылку (без fetch + redirect),
    // чтобы не упираться в CORS при чтении тела редиректа.
    const response = await fetch(`${API_URL}/files/${fileId}/download-url`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => '');
      throw new Error(errorText || 'Ошибка при скачивании файла');
    }

    const data: { url: string; filename: string } = await response.json();
    const downloadName = filename || data.filename;

    const a = document.createElement('a');
    a.href = data.url;
    a.download = downloadName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  },

  async viewFile(fileId: number): Promise<void> {
    const token = localStorage.getItem('access_token');
    const sessionId = localStorage.getItem('session_id');

    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    if (sessionId) {
      headers['X-Session-ID'] = sessionId;
    }

    if (!token && !sessionId) {
      throw new Error('Требуется авторизация или session_id для просмотра файла');
    }

    const response = await fetch(`${API_URL}/files/${fileId}/view-url`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || 'Ошибка при просмотре файла');
    }

    const data: { url: string } = await response.json();
    window.open(data.url, '_blank', 'noopener,noreferrer');
  },

  async saveFile(fileId: number): Promise<FileResponse> {
    const response = await api.post(`/files/${fileId}/save`);
    return response.data;
  },
};