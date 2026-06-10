/**
 * VisionSpec QC — Sidebar Component
 * Premium navigation sidebar with active state indicators.
 */

import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanEye,
  SearchCheck,
  BarChart3,
  History,
  Activity,
  Settings,
  Home,
  Bell,
} from 'lucide-react';

const navItems = [
  { section: 'Main' },
  { path: '/', label: 'Home', icon: Home },
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/live-detection', label: 'Live Detection', icon: ScanEye },
  { path: '/defect-analysis', label: 'Defect Analysis', icon: SearchCheck },
  { section: 'Insights' },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/history', label: 'Prediction History', icon: History },
  { section: 'System' },
  { path: '/system-monitor', label: 'System Monitor', icon: Activity },
  { path: '/notifications', label: 'Notifications', icon: Bell },
];

export default function Sidebar() {
  return (
    <aside className="sidebar" id="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <div className="sidebar-logo">VQ</div>
        <div className="sidebar-brand">
          <h1>VisionSpec QC</h1>
          <span>PCB Inspection AI</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {navItems.map((item, idx) => {
          if ('section' in item && item.section) {
            return (
              <div className="nav-section-title" key={`section-${idx}`}>
                {item.section}
              </div>
            );
          }

          const Icon = item.icon!;
          return (
            <NavLink
              key={item.path}
              to={item.path!}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              end={item.path === '/'}
            >
              <Icon />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Status */}
      <div className="sidebar-footer">
        <div className="sidebar-status">
          <div className="status-dot" />
          <span>System Online</span>
        </div>
      </div>
    </aside>
  );
}
