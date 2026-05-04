import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Settings.css';
import { ProfileHeader } from './ProfileHeader';
import { Footer } from './Footer';
import { authService } from '../services/auth';
import { getApiErrorDetail } from '../utils/getApiErrorDetail';
import { useSeo } from '../hooks/useSeo';

export const Settings: React.FC = () => {
  useSeo({
    title: 'Настройки профиля - Blur',
    description: 'Закрытая страница настроек профиля пользователя.',
    canonicalPath: '/settings',
    noindex: true,
  });

  const navigate = useNavigate();
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false);
  const [showDeleteConfirmModal, setShowDeleteConfirmModal] = useState(false);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogout = async () => {
    await authService.logout();
    navigate('/');
  };

  const handleChangePassword = () => {
    setShowChangePasswordModal(true);
    setError('');
    setOldPassword('');
    setNewPassword('');
    setConfirmPassword('');
  };

  const handleSubmitChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Валидация
    if (!oldPassword || !newPassword || !confirmPassword) {
      setError('Все поля обязательны для заполнения');
      setLoading(false);
      return;
    }

    if (newPassword.length < 8) {
      setError('Новый пароль должен содержать минимум 8 символов');
      setLoading(false);
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Новые пароли не совпадают');
      setLoading(false);
      return;
    }

    try {
      await authService.changePassword(oldPassword, newPassword);
      setShowChangePasswordModal(false);
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
      alert('Пароль успешно изменен');
    } catch (err: unknown) {
      setError(getApiErrorDetail(err) || 'Ошибка при смене пароля');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = () => {
    setShowDeleteConfirmModal(true);
    setError('');
  };

  const handleConfirmDeleteAccount = async () => {
    setLoading(true);
    setError('');

    try {
      await authService.deleteAccount();
      navigate('/');
      alert('Аккаунт успешно удален');
    } catch (err: unknown) {
      setError(getApiErrorDetail(err) || 'Ошибка при удалении аккаунта');
      setLoading(false);
    }
  };

  return (
    <>
      <ProfileHeader />
      <div className="settings-page">
        <div className="settings-container">
          <h2 className="settings-title">Настройки</h2>
          
          <div className="settings-files">
            <div className="settings-file-item" onClick={handleChangePassword}>
              <span className="settings-file-name">Сменить пароль</span>
            </div>
            <div className="settings-file-item" onClick={handleLogout}>
              <span className="settings-file-name">Выйти из аккаунта</span>
            </div>
            <div className="settings-file-item settings-file-item-red" onClick={handleDeleteAccount}>
              <span className="settings-file-name">Удалить аккаунт</span>
            </div>
          </div>
        </div>
      </div>

      {/* Модальное окно смены пароля */}
      {showChangePasswordModal && (
        <div className="settings-modal-overlay" onClick={() => !loading && setShowChangePasswordModal(false)}>
          <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
            <h3 className="settings-modal-title">Сменить пароль</h3>
            <form className="settings-modal-form" onSubmit={handleSubmitChangePassword}>
              {error && <div className="settings-modal-error">{error}</div>}
              <div className="settings-modal-fields">
                <input
                  type="password"
                  className="settings-modal-input"
                  placeholder="Старый пароль"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  disabled={loading}
                  required
                />
                <input
                  type="password"
                  className="settings-modal-input"
                  placeholder="Новый пароль"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  disabled={loading}
                  required
                  minLength={8}
                />
                <input
                  type="password"
                  className="settings-modal-input"
                  placeholder="Подтвердите новый пароль"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={loading}
                  required
                />
              </div>
              <div className="settings-modal-buttons">
                <button
                  type="button"
                  className="settings-modal-button-cancel"
                  onClick={() => setShowChangePasswordModal(false)}
                  disabled={loading}
                >
                  <span className="settings-modal-button-cancel-text">Отмена</span>
                </button>
                <button
                  type="submit"
                  className="settings-modal-button-submit"
                  disabled={loading}
                >
                  <span className="settings-modal-button-submit-text">
                    {loading ? 'Сохранение...' : 'Сохранить'}
                  </span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модальное окно подтверждения удаления */}
      {showDeleteConfirmModal && (
        <div className="settings-modal-overlay" onClick={() => !loading && setShowDeleteConfirmModal(false)}>
          <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
            <h3 className="settings-modal-title">Удалить аккаунт</h3>
            <p className="settings-modal-text">
              Вы уверены, что хотите удалить аккаунт? Это действие нельзя отменить.
              Все ваши данные будут безвозвратно удалены.
            </p>
            {error && <div className="settings-modal-error">{error}</div>}
            <div className="settings-modal-buttons">
              <button
                type="button"
                className="settings-modal-button-cancel"
                onClick={() => setShowDeleteConfirmModal(false)}
                disabled={loading}
              >
                <span className="settings-modal-button-cancel-text">Отмена</span>
              </button>
              <button
                type="button"
                className="settings-modal-button-delete"
                onClick={handleConfirmDeleteAccount}
                disabled={loading}
              >
                <span className="settings-modal-button-delete-text">
                  {loading ? 'Удаление...' : 'Удалить аккаунт'}
                </span>
              </button>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </>
  );
};