import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import { fetchStats, fetchEvents } from './lib/api';

const defaultStats = {
  total_requests: 0,
  phi_detected: 0,
  requests_redacted: 0,
  requests_clean: 0,
  avg_risk_score: 0,
  by_service: {},
  by_severity: {},
  by_hour: [],
  recent_phi_types: {},
  timeline: [],
};

export default function App() {
  const [stats, setStats] = useState(defaultStats);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, eventsData] = await Promise.all([
          fetchStats(),
          fetchEvents({ limit: 200 }),
        ]);
        setStats(statsData);
        setEvents(eventsData);
      } catch (err) {
        console.error('Failed to load initial data:', err);
      }
    }
    loadData();
  }, []);

  return (
    <div className="min-h-screen p-4">
      <Header connected={false} totalEvents={events.length} />

      {/* Panels go here once the components exist */}
      <div className="glass-panel p-4 text-sm text-gray-400 font-mono">
        {stats.total_requests} requests logged · {stats.phi_detected} with PHI
      </div>
    </div>
  );
}
