/**
 * VisionSpec QC — Dashboard Page
 * Main overview with stats, recent predictions, and system status.
 */

import {
  ScanEye,
  ShieldCheck,
  ShieldAlert,
  Zap,
  TrendingUp,
  Clock,
} from 'lucide-react';

export default function Dashboard() {
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
            <div className="stat-value">0</div>
            <div className="stat-label">Total Inspections</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon success"><ShieldCheck size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">0</div>
            <div className="stat-label">Passed</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon danger"><ShieldAlert size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">0</div>
            <div className="stat-label">Defects Found</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon accent"><TrendingUp size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">0%</div>
            <div className="stat-label">Defect Rate</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon info"><Zap size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">— ms</div>
            <div className="stat-label">Avg. Inference Time</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon warning"><Clock size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">— FPS</div>
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
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                    No predictions yet. Upload an image or start live detection.
                  </td>
                </tr>
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
            {[
              { label: 'Backend API', status: 'Connecting...' },
              { label: 'AI Model', status: 'Not loaded' },
              { label: 'Database', status: 'Initializing...' },
              { label: 'Webcam', status: 'Disconnected' },
            ].map((item) => (
              <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
                <span style={{ color: 'var(--text-muted)' }}>{item.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
