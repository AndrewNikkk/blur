import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Home } from './components/Home.tsx';
import './App.css';

function App() {
  return (
    <Router>
      {/* Router оборачивает все приложение и позволяет использовать роутинг */}
      <div className="app">
        <Routes>
          {/* Routes определяет, какой компонент показывать для каждого URL */}
          <Route path="/" element={<Home />} />
          {/* path="/" - это главная страница (корневой путь) */}
          {/* element={<Home />} - компонент, который будет отрендерен */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;