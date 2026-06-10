/**
 * VisionSpec QC — Main Application
 * Standalone landing page at "/" (no sidebar); the dashboard app lives under
 * the sidebar layout on its own routes.
 */

import type { ReactNode } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import LiveDetection from './pages/LiveDetection';
import DefectAnalysis from './pages/DefectAnalysis';
import Analytics from './pages/Analytics';
import PredictionHistory from './pages/PredictionHistory';
import SystemMonitor from './pages/SystemMonitor';
import LandingPage from './pages/LandingPage';
import NotificationSettings from './pages/NotificationSettings';
import './index.css';

// App shell with sidebar — wraps every page except the landing page.
function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">{children}</main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Standalone landing page — separate main page, no dashboard sidebar */}
        <Route path="/" element={<LandingPage />} />

        {/* Main application — rendered inside the sidebar layout */}
        <Route path="/dashboard" element={<AppLayout><Dashboard /></AppLayout>} />
        <Route path="/live-detection" element={<AppLayout><LiveDetection /></AppLayout>} />
        <Route path="/defect-analysis" element={<AppLayout><DefectAnalysis /></AppLayout>} />
        <Route path="/analytics" element={<AppLayout><Analytics /></AppLayout>} />
        <Route path="/history" element={<AppLayout><PredictionHistory /></AppLayout>} />
        <Route path="/system-monitor" element={<AppLayout><SystemMonitor /></AppLayout>} />
        <Route path="/notifications" element={<AppLayout><NotificationSettings /></AppLayout>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
