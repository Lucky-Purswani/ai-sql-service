import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ConnectionsProvider } from '../context/ConnectionsContext';
import '../styles/app.css';

export default function AppLayout() {
  const { logout } = useAuth();
  const location = useLocation();
  const isQueryPage = location.pathname.startsWith('/connections/');

  return (
    <ConnectionsProvider>
      <div className="app-layout">
        <header className="app-header">
        <div className="app-header-left">
          <Link to="/dashboard" className="app-logo">
            <span className="app-logo-bracket">[</span>
            <span className="app-logo-text">AI SQL</span>
            <span className="app-logo-bracket">]</span>
          </Link>
        </div>
        <div className="app-header-right">
          <button onClick={logout} className="btn btn--outline btn--sm">
            Logout
          </button>
        </div>
      </header>
      
        <main className={`app-main${isQueryPage ? ' app-main--query' : ''}`}>
          <Outlet />
        </main>
      </div>
    </ConnectionsProvider>
  );
}
