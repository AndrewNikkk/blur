import React from 'react';
import { Link } from 'react-router-dom';
import { Header } from './Header';
import { Footer } from './Footer';
import { useSeo } from '../hooks/useSeo';

export const NotFound: React.FC = () => {
  useSeo({
    title: 'Страница не найдена - Blur',
    description: 'Запрошенная страница не существует.',
    canonicalPath: '/404',
    noindex: true,
  });

  return (
    <>
      <Header />
      <main style={{ minHeight: '60vh', display: 'grid', placeItems: 'center', padding: '40px 16px' }}>
        <section aria-label="Страница не найдена" style={{ textAlign: 'center' }}>
          <h1>404</h1>
          <h2>Страница не найдена</h2>
          <p>Проверьте адрес или вернитесь на главную.</p>
          <Link to="/">На главную</Link>
        </section>
      </main>
      <Footer />
    </>
  );
};

