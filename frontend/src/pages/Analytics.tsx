/**
 * VisionSpec QC — Analytics Page (Phase 4)
 */

import { useState, useEffect } from 'react';
import { getAnalytics } from '../services/api';
import { AlertTriangle, Activity, AlertCircle, CheckCircle, TrendingUp, Zap } from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

interface AnalyticsData {
  total_predictions: int;
  total_defects: int;
  total_pass: int;
  defect_rate: float;
  average_confidence: float;
  average_inference_time_ms: float;
  predictions_today: int;
}

export default function Analytics() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAnalytics();
      setData(res.data);
    } catch (err: any) {
      console.error('Error fetching analytics:', err);
      setError('Failed to load analytics. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '100px' }}>
        <div className="spinner" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="result-error" style={{ margin: '40px' }}>
        <AlertTriangle size={24} />
        <div>
          <strong>Error Loading Analytics</strong>
          <p>{error}</p>
          <button className="btn btn-outline btn-sm" onClick={fetchAnalytics} style={{ marginTop: '12px' }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Chart Data Configurations
  const passDefectData = {
    labels: ['Pass', 'Defect'],
    datasets: [
      {
        label: 'Total Predictions',
        data: [data.total_pass, data.total_defects],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)', // Success green
          'rgba(239, 68, 68, 0.8)'  // Danger red
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(239, 68, 68)'
        ],
        borderWidth: 1,
      },
    ],
  };

  return (
    <div>
      <div className="page-header">
        <h2>Analytics</h2>
        <p>Detection trends, accuracy charts, and performance monitoring</p>
      </div>

      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-icon info"><Activity size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{data.total_predictions}</div>
            <div className="stat-label">Total Inspections</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon success"><CheckCircle size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{data.total_pass}</div>
            <div className="stat-label">Total Passed</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon danger"><AlertCircle size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{data.total_defects}</div>
            <div className="stat-label">Total Defects</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon primary"><TrendingUp size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{data.defect_rate}%</div>
            <div className="stat-label">Defect Rate</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Pass vs Defect Ratio</span>
          </div>
          <div style={{ padding: '20px', height: '300px', display: 'flex', justifyContent: 'center' }}>
            <Doughnut 
              data={passDefectData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: 'bottom' }
                }
              }} 
            />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">System Performance</span>
          </div>
          <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Average Confidence</span>
                <span style={{ fontWeight: 700, color: 'var(--color-primary)' }}>
                  {(data.average_confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div className="confidence-bar" style={{ height: '8px' }}>
                <div 
                  className="confidence-fill" 
                  style={{ width: `${data.average_confidence * 100}%`, backgroundColor: 'var(--color-primary)' }} 
                />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Average Latency</span>
                <span style={{ fontWeight: 700, color: 'var(--color-info)' }}>
                  {data.average_inference_time_ms}ms
                </span>
              </div>
              <div className="confidence-bar" style={{ height: '8px' }}>
                <div 
                  className="confidence-fill" 
                  style={{ width: `${Math.min(100, (data.average_inference_time_ms / 1000) * 100)}%`, backgroundColor: 'var(--color-info)' }} 
                />
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
                <Zap size={12} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
                Optimal latency for real-time is &lt;100ms
              </p>
            </div>

            <div style={{ padding: '16px', backgroundColor: 'var(--bg-secondary)', borderRadius: '8px', marginTop: 'auto' }}>
              <span style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                Inspections Today
              </span>
              <span style={{ fontSize: '24px', fontWeight: 700 }}>
                {data.predictions_today}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
