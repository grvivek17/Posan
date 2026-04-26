import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  Briefcase, 
  LineChart, 
  Settings, 
  LogOut,
  Bell,
  Search,
  ExternalLink,
  ChevronLeft
} from 'lucide-react';
import React, { useState } from 'react';

const apps = [
  {
    id: 'crm',
    name: 'Epiq CRM',
    desc: 'Manage clients, deals, and pipelines with your original CRM platform.',
    url: 'https://epiqcrm.vercel.app/dashboard',
    color: 'var(--brand-crm)',
    icon: <LineChart size={24} strokeWidth={1.5} />,
    path: '/app/crm'
  },
  {
    id: 'crm-v2',
    name: 'Epiq CRM V2',
    desc: 'Next-generation CRM with enhanced UI, analytics, and automation capabilities.',
    url: 'https://epiqapp.vercel.app/dashboard',
    color: 'var(--brand-crm-v2)',
    icon: <LayoutDashboard size={24} strokeWidth={1.5} />,
    path: '/app/crm-v2',
    badge: 'New'
  },
  {
    id: 'hrms',
    name: 'Epiq HRMS',
    desc: 'Human Resource Management — payroll, attendance, compliance, and employee records.',
    url: 'https://epiqhrms.vercel.app/',
    color: 'var(--brand-hrms)',
    icon: <Users size={24} strokeWidth={1.5} />,
    path: '/app/hrms'
  },
  {
    id: 'tms',
    name: 'Epiq Talent Mgmt.',
    desc: 'Recruit, track, and grow top talent with end-to-end talent management tools.',
    url: 'https://epiqtms.vercel.app/',
    color: 'var(--brand-tms)',
    icon: <Briefcase size={24} strokeWidth={1.5} />,
    path: '/app/tms'
  }
];

function Sidebar() {
  const location = useLocation();
  
  return (
    <aside className="sidebar">
      <div className="logo-container">
        <div className="logo-box">E</div>
        <div className="logo-text">Epiq Suite</div>
      </div>
      
      <div className="nav-section">
        <div className="nav-label">Main Applications</div>
        <Link to="/" className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}>
          <LayoutDashboard className="nav-icon" />
          <span>Dashboard</span>
        </Link>
        {apps.map(app => (
          <Link 
            key={app.id} 
            to={app.path} 
            className={`nav-item ${location.pathname === app.path ? 'active' : ''}`}
          >
            {React.cloneElement(app.icon, { className: 'nav-icon', size: 18 })}
            <span>{app.name}</span>
          </Link>
        ))}
      </div>
      
      <div style={{ flex: 1 }}></div>
      
      <div className="nav-section">
        <div className="nav-label">System</div>
        <Link to="#" className="nav-item">
          <Settings className="nav-icon" />
          <span>Settings</span>
        </Link>
        <Link to="#" className="nav-item">
          <LogOut className="nav-icon" />
          <span>Logout</span>
        </Link>
      </div>
    </aside>
  );
}

function Header() {
  const location = useLocation();
  const getHeaderTitle = () => {
    if (location.pathname === '/') return 'Enterprise Dashboard';
    const activeApp = apps.find(a => a.path === location.pathname);
    return activeApp ? activeApp.name : 'Dashboard';
  };

  return (
    <header className="header">
      <div className="header-title">{getHeaderTitle()}</div>
      <div className="header-actions">
        <div style={{ position: 'relative' }}>
          <Search size={18} style={{ color: 'var(--text-secondary)' }} />
        </div>
        <Bell size={18} style={{ color: 'var(--text-secondary)' }} />
        <div className="user-profile">
          <div className="avatar"></div>
          <span>Admin User</span>
        </div>
      </div>
    </header>
  );
}

function DashboardHome() {
  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>Welcome back, Admin.</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Launch any Epiq enterprise application from your centralized dashboard.</p>
      </div>
      
      <div className="dashboard-grid">
        {apps.map(app => (
          <div key={app.id} className="app-card" style={{ '--card-accent': app.color } as React.CSSProperties}>
            <div className="app-header">
              <div className="app-icon-wrapper">
                {app.icon}
              </div>
              {app.badge && (
                <div style={{ 
                  background: 'rgba(37, 99, 235, 0.1)', 
                  color: '#60a5fa', 
                  padding: '4px 8px', 
                  borderRadius: 12, 
                  fontSize: 11, 
                  fontWeight: 600,
                  textTransform: 'uppercase'
                }}>
                  {app.badge}
                </div>
              )}
            </div>
            <div>
              <h3 className="app-title">{app.name}</h3>
              <p className="app-desc">{app.desc}</p>
            </div>
            <div className="app-actions">
              <Link to={app.path} className="btn btn-primary" style={{ flex: 1 }}>
                Open Suite
              </Link>
              <a href={app.url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
                <ExternalLink size={16} />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AppViewer() {
  const location = useLocation();
  const app = apps.find(a => a.path === location.pathname);
  const [iframeError, setIframeError] = useState(false);

  if (!app) return <div>App not found</div>;

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Link to="/" className="back-link">
        <ChevronLeft size={16} /> Back to Dashboard
      </Link>
      
      {(app.id === 'crm' || app.id === 'crm-v2') && (
        <div className="iframe-notice">
            <p style={{ marginBottom: 12 }}>Some applications restrict embedding due to security policies (X-Frame-Options).</p>
            <a href={app.url} target="_blank" rel="noopener noreferrer" className="btn btn-primary">
              Open {app.name} in New Tab <ExternalLink size={16} />
            </a>
        </div>
      )}
      
      <div className="iframe-container">
        <iframe 
          src={app.url} 
          className="iframe-view"
          title={app.name}
          sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox"
        />
      </div>
    </div>
  );
}

function App() {
  return (
    <>
      <Sidebar />
      <div className="main-content">
        <Header />
        <main className="content-area">
          <Routes>
            <Route path="/" element={<DashboardHome />} />
            {apps.map(app => (
              <Route key={app.id} path={app.path} element={<AppViewer />} />
            ))}
          </Routes>
        </main>
      </div>
    </>
  );
}

export default App;
