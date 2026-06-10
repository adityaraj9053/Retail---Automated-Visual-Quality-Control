/**
 * VisionSpec QC — Notifications & Settings
 * Real-time notification feed (polls existing /history) + user preferences
 * persisted to localStorage. Purely additive: no backend or existing-page changes.
 */

import { useState, useEffect, useRef } from 'react';
import {
  Bell,
  BellOff,
  ShieldAlert,
  CheckCircle2,
  Volume2,
  Monitor,
  Trash2,
  Send,
  Settings as SettingsIcon,
} from 'lucide-react';
import { getHistory } from '../services/api';

interface NotifSettings {
  master: boolean;
  defectAlerts: boolean;
  passAlerts: boolean;
  sound: boolean;
  desktop: boolean;
  threshold: number; // 0..100
}

interface FeedItem {
  key: string;
  label: string;
  source: string;
  confidence: number;
  time: string;
  isDefect: boolean;
}

const STORAGE_KEY = 'vqc_notif_settings';

const DEFAULTS: NotifSettings = {
  master: true,
  defectAlerts: true,
  passAlerts: false,
  sound: false,
  desktop: false,
  threshold: 70,
};

function loadSettings(): NotifSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return { ...DEFAULTS, ...JSON.parse(raw) };
  } catch {
    /* ignore */
  }
  return DEFAULTS;
}

function beep() {
  try {
    const Ctx = window.AudioContext || (window as any).webkitAudioContext;
    const ctx = new Ctx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.frequency.value = 880;
    gain.gain.setValueAtTime(0.0001, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.18, ctx.currentTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.25);
    osc.start();
    osc.stop(ctx.currentTime + 0.26);
  } catch {
    /* audio not available */
  }
}

// ── Toggle switch (inline-styled to match the dark theme) ──
function Toggle({ checked, onChange, disabled }: { checked: boolean; onChange: () => void; disabled?: boolean }) {
  return (
    <button
      onClick={onChange}
      disabled={disabled}
      aria-pressed={checked}
      style={{
        width: '44px',
        height: '24px',
        borderRadius: '999px',
        border: 'none',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.4 : 1,
        background: checked ? 'var(--gradient-primary)' : 'var(--bg-elevated)',
        position: 'relative',
        transition: 'background var(--transition-base)',
        flexShrink: 0,
      }}
    >
      <span
        style={{
          position: 'absolute',
          top: '3px',
          left: checked ? '23px' : '3px',
          width: '18px',
          height: '18px',
          borderRadius: '50%',
          background: '#fff',
          transition: 'left var(--transition-base)',
        }}
      />
    </button>
  );
}

function Row({
  icon,
  title,
  desc,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  desc: string;
  children: React.ReactNode;
}) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        padding: '14px 0',
        borderBottom: '1px solid var(--border-color)',
      }}
    >
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        <span style={{ color: 'var(--color-accent-light)' }}>{icon}</span>
        <div>
          <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>{title}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{desc}</div>
        </div>
      </div>
      {children}
    </div>
  );
}

export default function NotificationSettings() {
  const [settings, setSettings] = useState<NotifSettings>(loadSettings);
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [lastChecked, setLastChecked] = useState<string>('—');
  const seenIds = useRef<Set<number>>(new Set());
  const initialized = useRef(false);
  const settingsRef = useRef(settings);

  // keep latest settings available inside the polling closure
  useEffect(() => {
    settingsRef.current = settings;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch {
      /* ignore */
    }
  }, [settings]);

  // ── Real-time polling of recent predictions ──
  useEffect(() => {
    let active = true;

    const poll = async () => {
      try {
        const res = await getHistory(1, 20);
        if (!active) return;
        const preds = res.data.predictions as any[];
        setLastChecked(new Date().toLocaleTimeString());

        // First pass: seed seen IDs without notifying (avoid flooding old items)
        if (!initialized.current) {
          preds.forEach((p) => seenIds.current.add(p.id));
          initialized.current = true;
          return;
        }

        const s = settingsRef.current;
        const fresh = preds.filter((p) => !seenIds.current.has(p.id));
        fresh.forEach((p) => seenIds.current.add(p.id));
        if (fresh.length === 0) return;

        const newItems: FeedItem[] = [];
        for (const p of fresh) {
          const isDefect = String(p.predicted_label).includes('Defect');
          const confPct = Math.round((p.confidence || 0) * 100);

          // Apply user filters
          if (!s.master) continue;
          if (isDefect && !s.defectAlerts) continue;
          if (!isDefect && !s.passAlerts) continue;
          if (confPct < s.threshold) continue;

          newItems.push({
            key: `${p.id}-${p.timestamp}`,
            label: p.predicted_label,
            source: p.source,
            confidence: p.confidence,
            time: new Date(p.timestamp).toLocaleTimeString(),
            isDefect,
          });

          // Side effects (sound + desktop) for defects primarily
          if (s.sound) beep();
          if (s.desktop && 'Notification' in window && Notification.permission === 'granted') {
            new Notification(`PCB ${p.predicted_label}`, {
              body: `${confPct}% confidence · ${p.source}`,
            });
          }
        }

        if (newItems.length > 0) {
          setFeed((prev) => [...newItems, ...prev].slice(0, 30));
        }
      } catch {
        /* backend offline — silently retry next tick */
      }
    };

    poll();
    const interval = setInterval(poll, 4000); // real-time feed
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const update = (patch: Partial<NotifSettings>) => setSettings((s) => ({ ...s, ...patch }));

  const toggleDesktop = () => {
    if (!settings.desktop && 'Notification' in window && Notification.permission !== 'granted') {
      Notification.requestPermission().then((perm) => {
        update({ desktop: perm === 'granted' });
      });
    } else {
      update({ desktop: !settings.desktop });
    }
  };

  const sendTest = () => {
    const item: FeedItem = {
      key: `test-${Date.now()}`,
      label: 'Defect',
      source: 'test',
      confidence: 0.97,
      time: new Date().toLocaleTimeString(),
      isDefect: true,
    };
    setFeed((prev) => [item, ...prev].slice(0, 30));
    if (settings.sound) beep();
    if (settings.desktop && 'Notification' in window && Notification.permission === 'granted') {
      new Notification('Test Notification', { body: 'Notifications are working ✓' });
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Notifications &amp; Settings</h2>
        <p>Real-time inspection alerts and notification preferences</p>
      </div>

      <div className="grid-2">
        {/* ── Live Feed ── */}
        <div className="card">
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="card-title">Live Notifications</span>
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '11px',
                  fontWeight: 700,
                  color: 'var(--color-success)',
                }}
              >
                <span className="status-dot" style={{ background: 'var(--color-success)' }} />
                LIVE
              </span>
            </div>
            <button className="btn btn-outline btn-sm" onClick={() => setFeed([])} disabled={feed.length === 0}>
              <Trash2 size={14} />
              <span>Clear</span>
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '8px', minHeight: '260px' }}>
            {feed.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '48px 16px', color: 'var(--text-muted)' }}>
                <Bell size={32} style={{ opacity: 0.4, marginBottom: '12px' }} />
                <p style={{ fontSize: '13px' }}>Listening for new inspections…</p>
                <p style={{ fontSize: '12px', marginTop: '4px' }}>
                  Run a prediction (upload or live) and alerts will appear here in real time.
                </p>
              </div>
            ) : (
              feed.map((n) => (
                <div
                  key={n.key}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px 14px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-surface)',
                    border: `1px solid ${n.isDefect ? 'rgba(239,68,68,0.3)' : 'var(--border-color)'}`,
                  }}
                >
                  {n.isDefect ? (
                    <ShieldAlert size={18} color="var(--color-danger)" />
                  ) : (
                    <CheckCircle2 size={18} color="var(--color-success)" />
                  )}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {n.isDefect ? 'Defect detected' : 'Pass verified'}
                      <span className={`badge ${n.isDefect ? 'badge-defect' : 'badge-pass'}`} style={{ marginLeft: '8px' }}>
                        {n.label}
                      </span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      {(n.confidence * 100).toFixed(1)}% confidence · {n.source} · {n.time}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '12px', textAlign: 'right' }}>
            Last checked: {lastChecked}
          </div>
        </div>

        {/* ── Settings ── */}
        <div className="card">
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <SettingsIcon size={16} color="var(--color-accent-light)" />
              <span className="card-title">Preferences</span>
            </div>
            <button className="btn btn-outline btn-sm" onClick={sendTest}>
              <Send size={14} />
              <span>Test</span>
            </button>
          </div>

          <div style={{ marginTop: '4px' }}>
            <Row
              icon={settings.master ? <Bell size={18} /> : <BellOff size={18} />}
              title="Enable Notifications"
              desc="Master switch for all real-time alerts"
            >
              <Toggle checked={settings.master} onChange={() => update({ master: !settings.master })} />
            </Row>
            <Row icon={<ShieldAlert size={18} />} title="Defect Alerts" desc="Notify when a defect is detected">
              <Toggle checked={settings.defectAlerts} onChange={() => update({ defectAlerts: !settings.defectAlerts })} disabled={!settings.master} />
            </Row>
            <Row icon={<CheckCircle2 size={18} />} title="Pass Alerts" desc="Notify on passing inspections too">
              <Toggle checked={settings.passAlerts} onChange={() => update({ passAlerts: !settings.passAlerts })} disabled={!settings.master} />
            </Row>
            <Row icon={<Volume2 size={18} />} title="Sound Alerts" desc="Play a chime on new notifications">
              <Toggle checked={settings.sound} onChange={() => update({ sound: !settings.sound })} disabled={!settings.master} />
            </Row>
            <Row icon={<Monitor size={18} />} title="Desktop Notifications" desc="Show OS pop-ups (asks permission)">
              <Toggle checked={settings.desktop} onChange={toggleDesktop} disabled={!settings.master} />
            </Row>

            <div style={{ padding: '16px 0 4px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Confidence Threshold
                </span>
                <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--color-primary-light)' }}>
                  {settings.threshold}%
                </span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={settings.threshold}
                onChange={(e) => update({ threshold: Number(e.target.value) })}
                disabled={!settings.master}
                style={{ width: '100%', accentColor: 'var(--color-primary)' }}
              />
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
                Only alert when prediction confidence is at or above this level.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
