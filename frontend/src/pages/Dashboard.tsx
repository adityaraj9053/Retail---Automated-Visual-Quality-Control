/**
 * VisionSpec QC — Dashboard Page
 * Main overview with stats, recent predictions, and system status.
 */

import { useState, useEffect } from 'react';
import {
  ScanEye,
  ShieldCheck,
  ShieldAlert,
  Zap,
  TrendingUp,
  Clock,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { getAnalytics, getHistory, getHealth } from '../services/api';

interface AnalyticsData {
  total_predictions: number;
  total_defects: number;
  total_pass: number;
  defect_rate: number;
  average_confidence: number;
  average_inference_time_ms: number;
  predictions_today: number;
}

interface RecentPrediction {
  id: number;
  timestamp: string;
  predicted_label: string;
  confidence: number;
  source: string;
}

interface HealthData {
  model_loaded: boolean;
  database_connected: boolean;
}

export default function Dashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [recent, setRecent] = useState<RecentPrediction[]>([]);
  const [health, setHealth] = useState<HealthData | null>(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [dbReachable, setDbReachable] = useState(false);

  useEffect(() => {
    let active = true;

    const refresh = async () => {
      // Health / Backend + AI model status
      try {
        const res = await getHealth();
        if (!active) return;
        setHealth(res.data);
        setBackendOnline(true);
      } catch {
        if (!active) return;
        setBackendOnline(false);
        setHealth(null);
      }

      // Analytics — also our real signal that the database is reachable
      try {
        const res = await getAnalytics();
        if (!active) return;
        setAnalytics(res.data);
        setDbReachable(true);
      } catch {
        if (!active) return;
        setDbReachable(false);
      }

      // Recent predictions (last 5)
      try {
        const res = await getHistory(1, 5);
        if (!active) return;
        setRecent(res.data.predictions);
      } catch {
        if (!active) return;
        setRecent([]);
      }
    };

    refresh();
    const interval = setInterval(refresh, 5000); // real-time refresh
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const avgMs = analytics?.average_inference_time_ms ?? 0;
  const fps = avgMs > 0 ? (1000 / avgMs).toFixed(1) : '—';

  const statusItems = [
    {
      label: 'Backend API',
      text: backendOnline ? 'Online' : 'Offline',
      color: backendOnline ? 'var(--color-success)' : 'var(--color-danger)',
    },
    {
      label: 'AI Model',
      text: health?.model_loaded ? 'Loaded' : backendOnline ? 'Not loaded' : '—',
      color: health?.model_loaded ? 'var(--color-success)' : 'var(--color-danger)',
    },
    {
      label: 'Database',
      text: dbReachable ? 'Connected' : backendOnline ? 'Unavailable' : '—',
      color: dbReachable ? 'var(--color-success)' : 'var(--color-danger)',
    },
    {
      label: 'Webcam',
      text: 'Idle',
      color: 'var(--text-muted)',
    },
  ];

  return (
    <div>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Real-time overview of the PCB inspection system</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon primary"><ScanEye size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{analytics?.total_predictions ?? 0}</div>
            <div className="stat-label">Total Inspections</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon success"><ShieldCheck size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{analytics?.total_pass ?? 0}</div>
            <div className="stat-label">Passed</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon danger"><ShieldAlert size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{analytics?.total_defects ?? 0}</div>
            <div className="stat-label">Defects Found</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon accent"><TrendingUp size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{(analytics?.defect_rate ?? 0)}%</div>
            <div className="stat-label">Defect Rate</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon info"><Zap size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{avgMs > 0 ? `${avgMs} ms` : '— ms'}</div>
            <div className="stat-label">Avg. Inference Time</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon warning"><Clock size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{fps} FPS</div>
            <div className="stat-label">Live Speed</div>
          </div>
        </div>
      </div>

      {/* Grid: Recent Predictions + System Status */}
      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Recent Predictions</span>
            <span className="card-subtitle">Last 5 results</span>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Source</th>
                  <th>Result</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {recent.length === 0 ? (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                      No predictions yet. Upload an image or start live detection.
                    </td>
                  </tr>
                ) : (
                  recent.map((item) => {
                    const isPass = item.predicted_label.includes('Pass');
                    return (
                      <tr key={item.id}>
                        <td style={{ fontSize: '13px' }}>
                          {new Date(item.timestamp).toLocaleTimeString()}
                        </td>
                        <td>
                          <span className="badge" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                            {item.source}
                          </span>
                        </td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            {isPass ? (
                              <CheckCircle2 size={14} color="var(--color-success)" />
                            ) : (
                              <XCircle size={14} color="var(--color-danger)" />
                            )}
                            <span className={`badge ${isPass ? 'badge-pass' : 'badge-defect'}`}>
                              {item.predicted_label}
                            </span>
                          </div>
                        </td>
                        <td style={{ fontWeight: 600, color: item.confidence >= 0.9 ? 'var(--color-success)' : item.confidence >= 0.7 ? 'var(--color-warning)' : 'var(--color-danger)' }}>
                          {(item.confidence * 100).toFixed(1)}%
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">System Status</span>
            <span className="card-subtitle">Real-time health</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '8px' }}>
            {statusItems.map((item) => (
              <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: item.color }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: item.color, display: 'inline-block' }} />
                  {item.text}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
