/**
 * VisionSpec QC — Landing Page
 * Marketing-style entry screen with LIVE real-time system stats.
 * Purely additive: reuses existing /analytics and /health endpoints only.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Rocket,
  ScanEye,
  Sparkles,
  BarChart3,
  History,
  Camera,
  ShieldCheck,
  Zap,
  Cpu,
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';
import { getAnalytics, getHealth } from '../services/api';

interface LiveStats {
  total_predictions: number;
  defect_rate: number;
  average_inference_time_ms: number;
}

const FEATURES = [
  { icon: ScanEye, title: 'Real-Time Inference', text: 'Detect PCB defects instantly from uploads or a live webcam feed.' },
  { icon: Sparkles, title: 'Explainable AI', text: 'Grad-CAM heatmaps reveal exactly where the model found a defect.' },
  { icon: BarChart3, title: 'QA Analytics', text: 'Track defect rates, confidence and throughput trends over time.' },
  { icon: History, title: 'Inspection History', text: 'Every prediction is logged and auditable with CSV export.' },
  { icon: Camera, title: 'Live Detection', text: 'Stream frames from a camera for continuous on-the-fly inspection.' },
  { icon: ShieldCheck, title: 'Human-in-the-Loop', text: 'Operators can correct predictions to keep improving the model.' },
];

export default function LandingPage() {
  const [stats, setStats] = useState<LiveStats | null>(null);
  const [online, setOnline] = useState(false);
  const [modelLoaded, setModelLoaded] = useState(false);

  useEffect(() => {
    let active = true;

    const refresh = async () => {
      try {
        const [a, h] = await Promise.allSettled([getAnalytics(), getHealth()]);
        if (!active) return;
        if (a.status === 'fulfilled') setStats(a.value.data);
        if (h.status === 'fulfilled') {
          setOnline(true);
          setModelLoaded(!!h.value.data.model_loaded);
        } else {
          setOnline(false);
        }
      } catch {
        if (active) setOnline(false);
      }
    };

    refresh();
    const interval = setInterval(refresh, 5000); // real-time refresh
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const avgMs = stats?.average_inference_time_ms ?? 0;

  return (
    <div style={{ minHeight: '100vh', padding: '36px clamp(20px, 6vw, 80px)', maxWidth: '1280px', margin: '0 auto' }}>
      {/* ── Hero ───────────────────────────────────────── */}
      <div
        style={{
          position: 'relative',
          borderRadius: 'var(--radius-xl)',
          padding: '48px 40px',
          marginBottom: '28px',
          overflow: 'hidden',
          border: '1px solid var(--border-color)',
          background:
            'radial-gradient(120% 140% at 0% 0%, rgba(139,92,246,0.18), transparent 55%), radial-gradient(120% 140% at 100% 0%, rgba(236,72,153,0.18), transparent 55%), var(--bg-card)',
        }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 12px',
            borderRadius: '999px',
            border: '1px solid var(--border-color)',
            background: 'var(--bg-surface)',
            fontSize: '12px',
            fontWeight: 600,
            color: online ? 'var(--color-success)' : 'var(--color-danger)',
            marginBottom: '20px',
          }}
        >
          <span className="status-dot" style={{ background: online ? 'var(--color-success)' : 'var(--color-danger)' }} />
          {online ? 'LIVE · System Online' : 'Offline · Start the backend'}
        </div>

        <h1
          style={{
            fontSize: '42px',
            lineHeight: 1.1,
            fontWeight: 800,
            margin: 0,
            background: 'var(--gradient-multicolor)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            maxWidth: '720px',
          }}
        >
          VisionSpec QC
        </h1>
        <p style={{ fontSize: '18px', color: 'var(--text-secondary)', maxWidth: '620px', marginTop: '14px', lineHeight: 1.5 }}>
          AI-powered visual inspection for Printed Circuit Boards — real-time defect
          detection with Explainable AI, analytics and live monitoring.
        </p>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '28px' }}>
          <Link to="/dashboard" className="btn btn-primary">
            <Rocket size={16} />
            <span>Launch Dashboard</span>
            <ArrowRight size={16} />
          </Link>
          <Link to="/live-detection" className="btn btn-outline">
            <Camera size={16} />
            <span>Start Live Detection</span>
          </Link>
        </div>
      </div>

      {/* ── Live Stats Strip ───────────────────────────── */}
      <div className="stats-grid" style={{ marginBottom: '28px' }}>
        <div className="stat-card">
          <div className="stat-icon primary"><ScanEye size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{stats?.total_predictions ?? 0}</div>
            <div className="stat-label">Total Inspections</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon danger"><BarChart3 size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{stats?.defect_rate ?? 0}%</div>
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
          <div className="stat-icon accent"><Cpu size={22} /></div>
          <div className="stat-content">
            <div className="stat-value" style={{ fontSize: '20px', color: modelLoaded ? 'var(--color-success)' : 'var(--text-muted)' }}>
              {modelLoaded ? 'Ready' : online ? 'Loading' : '—'}
            </div>
            <div className="stat-label">AI Model</div>
          </div>
        </div>
      </div>

      {/* ── Feature Cards ──────────────────────────────── */}
      <div className="page-header">
        <h2>Capabilities</h2>
        <p>Everything you need for automated PCB quality control</p>
      </div>
      <div className="grid-3">
        {FEATURES.map((f) => {
          const Icon = f.icon;
          return (
            <div className="card" key={f.title} style={{ padding: '22px' }}>
              <div className="stat-icon accent" style={{ marginBottom: '14px' }}>
                <Icon size={22} />
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 8px 0' }}>
                {f.title}
              </h3>
              <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                {f.text}
              </p>
            </div>
          );
        })}
      </div>

      {/* ── CTA Footer ─────────────────────────────────── */}
      <div
        className="card"
        style={{
          marginTop: '28px',
          padding: '28px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <CheckCircle2 size={22} color="var(--color-success)" />
          <div>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Ready to inspect</div>
            <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              Upload a PCB image or open the live dashboard to begin.
            </div>
          </div>
        </div>
        <Link to="/defect-analysis" className="btn btn-primary">
          <span>Analyze a PCB</span>
          <ArrowRight size={16} />
        </Link>
      </div>
    </div>
  );
}
