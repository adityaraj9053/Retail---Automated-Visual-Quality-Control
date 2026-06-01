/**
 * VisionSpec QC — Main Application
 * Root component with sidebar layout and client-side routing.
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import LiveDetection from './pages/LiveDetection';
import DefectAnalysis from './pages/DefectAnalysis';
import Analytics from './pages/Analytics';
import PredictionHistory from './pages/PredictionHistory';
import SystemMonitor from './pages/SystemMonitor';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/live-detection" element={<LiveDetection />} />
            <Route path="/defect-analysis" element={<DefectAnalysis />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/history" element={<PredictionHistory />} />
            <Route path="/system-monitor" element={<SystemMonitor />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
