import React from 'react';
import './Home.css';
import { Header } from './Header';
import { InfoSection } from './InfoSection';

export const Home: React.FC = () => {
  return (
    <>
      <Header />
      <div className="home">
        <InfoSection />
      </div>
    </>
  );
};