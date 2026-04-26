import React from 'react';
import './Home.css';
import { Header } from './Header';
import { InfoSection } from './InfoSection';
import { UploadSection } from './UploadSection';
import { Footer } from './Footer';
import { PrivacyTipCard } from './PrivacyTipCard';
import { useSeo } from '../hooks/useSeo';

export const Home: React.FC = () => {
  useSeo({
    title: 'Blur - Защита персональных данных на фото и документах',
    description:
      'Blur автоматически маскирует персональные данные на изображениях и документах: паспорта, телефоны, банковские карты и номера авто.',
    canonicalPath: '/',
    ogType: 'website',
    jsonLd: {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: 'Blur',
      url: window.location.origin,
      description:
        'Сервис автоматической маскировки персональных данных на изображениях и документах.',
    },
  });

  return (
    <>
      <Header />
      <main className="home">
        <InfoSection />
        <PrivacyTipCard />
        <UploadSection />
      </main>
      <Footer />
    </>
  );
};