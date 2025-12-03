import React from 'react';
import './Home.css';
import { Header } from './Header';
import { InfoSection } from './InfoSection';
import { UploadSection } from './UploadSection';
import { Footer } from './Footer';

export const Home: React.FC = () => {
  return (
    <>
      <Header />
      <div className="home">
        <InfoSection />
        <UploadSection />
      </div>
      <Footer />
    </>
  );
};