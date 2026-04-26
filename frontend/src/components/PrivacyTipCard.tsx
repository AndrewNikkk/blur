import React, { useEffect, useState } from 'react';
import { externalService } from '../services/external';
import type { ExternalTipResponse } from '../types';
import './PrivacyTipCard.css';

export const PrivacyTipCard: React.FC = () => {
  const [tip, setTip] = useState<ExternalTipResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadTip = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await externalService.getPrivacyTip();
        setTip(response);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Не удалось загрузить внешний совет');
      } finally {
        setLoading(false);
      }
    };

    loadTip();
  }, []);

  return (
    <section className="privacy-tip-card" aria-label="Совет по защите данных">
      <h2 className="privacy-tip-title">Совет по безопасности</h2>
      {loading && <p className="privacy-tip-loading">Загрузка внешних данных...</p>}
      {!loading && error && (
        <p className="privacy-tip-error">{error}. Продолжаем работу в стандартном режиме.</p>
      )}
      {!loading && !error && !tip && (
        <p className="privacy-tip-empty">Внешний источник не вернул данных.</p>
      )}
      {tip && (
        <article className="privacy-tip-body">
          <h3 className="privacy-tip-item-title">{tip.title}</h3>
          <p className="privacy-tip-item-content">{tip.content}</p>
          <p className="privacy-tip-meta">
            Источник: {tip.source}
            {tip.fallback ? ' (резервный ответ)' : ''}
          </p>
        </article>
      )}
    </section>
  );
};

