import { useState, useEffect } from 'react';
import { Activity, Cpu, HardDrive, Thermometer, Clock } from 'lucide-react';
import { getSystemMetrics } from '../services/api';

interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  gpu_percent: number;
  uptime_seconds: number;
}

export default function SystemMonitor() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const res = await getSystemMetrics();
      setMetrics(res.data);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching system metrics:', err);
      setError('Unable to fetch system metrics.');
    }
  };

  const formatUptime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hrs}h ${mins}m ${secs}s`;
  };

  return (
    <div>
      <div className="page-header">
        <h2>System Monitor</h2>
        <p>Real-time hardware and API performance metrics</p>
      </div>

      {error && (
        <div className="result-error" style={{ marginBottom: '20px' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon info"><Cpu size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{metrics ? `${metrics.cpu_percent.toFixed(1)}%` : '—%'}</div>
            <div className="stat-label">CPU Usage</div>
          </div>
          {metrics && (
             <div className="confidence-bar" style={{ width: '100%', height: '4px', marginTop: '12px', gridColumn: 'span 2' }}>
                <div className="confidence-fill" style={{ width: `${metrics.cpu_percent}%`, backgroundColor: 'var(--color-info)' }} />
             </div>
          )}
        </div>

        <div className="stat-card">
          <div className="stat-icon accent"><HardDrive size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{metrics ? `${metrics.memory_percent.toFixed(1)}%` : '—%'}</div>
            <div className="stat-label">Memory Usage</div>
          </div>
          {metrics && (
             <div className="confidence-bar" style={{ width: '100%', height: '4px', marginTop: '12px', gridColumn: 'span 2' }}>
                <div className="confidence-fill" style={{ width: `${metrics.memory_percent}%`, backgroundColor: 'var(--color-accent)' }} />
             </div>
          )}
        </div>

        <div className="stat-card">
          <div className="stat-icon warning"><Thermometer size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{metrics ? `${metrics.gpu_percent.toFixed(1)}%` : '—%'}</div>
            <div className="stat-label">GPU Usage (Mock)</div>
          </div>
           {metrics && (
             <div className="confidence-bar" style={{ width: '100%', height: '4px', marginTop: '12px', gridColumn: 'span 2' }}>
                <div className="confidence-fill" style={{ width: `${metrics.gpu_percent}%`, backgroundColor: 'var(--color-warning)' }} />
             </div>
          )}
        </div>

        <div className="stat-card">
          <div className="stat-icon success"><Clock size={22} /></div>
          <div className="stat-content">
            <div className="stat-value" style={{ fontSize: '20px' }}>{metrics ? formatUptime(metrics.uptime_seconds) : '—'}</div>
            <div className="stat-label">API Uptime</div>
          </div>
        </div>
      </div>
    </div>
  );
}
