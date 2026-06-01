/**
 * VisionSpec QC — Prediction History Page (Phase 4)
 * Displays a paginated log of all predictions made by the system.
 */

import { useState, useEffect } from 'react';
import { History, Download, ChevronLeft, ChevronRight, CheckCircle2, XCircle, AlertTriangle, Edit3 } from 'lucide-react';
import { getHistory, submitFeedback } from '../services/api';

interface PredictionHistoryItem {
  id: number;
  timestamp: string;
  image_filename: string | null;
  predicted_label: string;
  confidence: number;
  inference_time_ms: number;
  source: string;
}

export default function PredictionHistory() {
  const [history, setHistory] = useState<PredictionHistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const limit = 15;

  useEffect(() => {
    fetchHistory(page);
  }, [page]);

  const fetchHistory = async (pageNumber: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getHistory(pageNumber, limit);
      setHistory(res.data.predictions);
      setTotal(res.data.total);
    } catch (err: any) {
      console.error('Error fetching history:', err);
      setError('Failed to load prediction history. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (history.length === 0) return;
    
    const headers = ['ID', 'Timestamp', 'Image', 'Label', 'Confidence', 'Inference (ms)', 'Source'];
    const csvContent = [
      headers.join(','),
      ...history.map(item => [
        item.id,
        `"${new Date(item.timestamp).toLocaleString()}"`,
        `"${item.image_filename || 'N/A'}"`,
        item.predicted_label,
        (item.confidence * 100).toFixed(1) + '%',
        item.inference_time_ms,
        item.source
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `visionspec_history_page_${page}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleFeedback = async (id: number, currentLabel: string) => {
    const isPass = currentLabel.includes('Pass');
    const newLabel = isPass ? 'Defect' : 'Pass';
    if (window.confirm(`Human-in-the-Loop: Mark prediction #${id} as ${newLabel}?`)) {
      try {
        await submitFeedback(id, newLabel, 'Operator corrected');
        fetchHistory(page); // refresh
      } catch (e) {
        console.error(e);
        alert('Failed to submit feedback');
      }
    }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div>
      <div className="page-header">
        <h2>Prediction History</h2>
        <p>Complete log of all inspections performed by the system</p>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <span className="card-title">Inspection Log</span>
            <span className="card-subtitle">Total records: {total}</span>
          </div>
          <button 
            className="btn btn-outline btn-sm" 
            onClick={handleExport}
            disabled={loading || history.length === 0}
          >
            <Download size={14} />
            <span>Export CSV (Current Page)</span>
          </button>
        </div>
        
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Timestamp</th>
                <th>Source</th>
                <th>Image</th>
                <th>Result</th>
                <th>Confidence</th>
                <th>Latency</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
                    <div className="spinner" style={{ margin: '0 auto 16px auto' }} />
                    <p style={{ fontSize: '13px' }}>Loading history logs...</p>
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '48px', color: 'var(--color-danger)' }}>
                    <AlertTriangle size={32} style={{ margin: '0 auto 16px auto', opacity: 0.8 }} />
                    <p style={{ fontSize: '13px' }}>{error}</p>
                  </td>
                </tr>
              ) : history.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
                    <History size={32} style={{ margin: '0 auto 16px auto', opacity: 0.4 }} />
                    <p style={{ fontSize: '13px' }}>No predictions recorded yet.</p>
                  </td>
                </tr>
              ) : (
                history.map((item) => (
                  <tr key={item.id}>
                    <td style={{ color: 'var(--text-muted)', fontSize: '12px' }}>#{item.id}</td>
                    <td style={{ fontSize: '13px' }}>
                      {new Date(item.timestamp).toLocaleString()}
                    </td>
                    <td>
                      <span className="badge" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                        {item.source}
                      </span>
                    </td>
                    <td style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                      {item.image_filename ? (
                        <span style={{ maxWidth: '150px', display: 'inline-block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {item.image_filename}
                        </span>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        {item.predicted_label.includes('Pass') ? (
                          <CheckCircle2 size={14} color="var(--color-success)" />
                        ) : (
                          <XCircle size={14} color="var(--color-danger)" />
                        )}
                        <span className={`badge ${item.predicted_label.includes('Pass') ? 'badge-pass' : 'badge-defect'}`}>
                          {item.predicted_label}
                        </span>
                      </div>
                    </td>
                    <td style={{ fontWeight: 600, color: item.confidence >= 0.9 ? 'var(--color-success)' : item.confidence >= 0.7 ? 'var(--color-warning)' : 'var(--color-danger)' }}>
                      {(item.confidence * 100).toFixed(1)}%
                    </td>
                    <td style={{ fontSize: '13px' }}>{item.inference_time_ms.toFixed(1)}ms</td>
                    <td>
                      <button 
                        className="btn btn-outline btn-sm" 
                        onClick={() => handleFeedback(item.id, item.predicted_label)}
                        title="Mark as incorrect (Human-in-the-Loop)"
                        style={{ padding: '4px 8px' }}
                      >
                        <Edit3 size={12} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination Controls */}
        {!loading && !error && totalPages > 1 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', borderTop: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Showing {((page - 1) * limit) + 1} to {Math.min(page * limit, total)} of {total} entries
            </span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button 
                className="btn btn-outline btn-sm" 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeft size={14} />
                Prev
              </button>
              <button 
                className="btn btn-outline btn-sm" 
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
