import React, { useState, useEffect, useMemo } from 'react';
import Header from './components/Header';
import StatsCards from './components/StatsCards';
import ThreatFeed from './components/ThreatFeed';
import AuditLog from './components/AuditLog';
import RedactionViewer from './components/RedactionViewer';
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
  const [selectedEvent, setSelectedEvent] = useState(null);

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

  // Derive stats from PHI-detected events only
  const phiStats = useMemo(() => {
    const phiEvents = events.filter((e) => e.phi_detected);
    const total = phiEvents.length;
    const avgRisk = total > 0
      ? parseFloat((phiEvents.reduce((s, e) => s + (e.risk_score || 0), 0) / total).toFixed(1))
      : 0;
    return {
      total_requests: events.length,
      phi_detected: total,
      requests_redacted: phiEvents.filter((e) => e.action === 'redacted').length,
      requests_clean: phiEvents.filter((e) => e.action === 'clean').length,
      avg_risk_score: avgRisk,
    };
  }, [events]);

  return (
    <div className="min-h-screen p-4">
      <Header connected={false} totalEvents={events.length} />

      <StatsCards stats={phiStats} callStats={{ total_calls: 0, completed_calls: 0, failed_calls: 0 }} />

      <div className="grid grid-cols-12 gap-4 mb-4">
        <div className="col-span-3">
          <ThreatFeed
            events={events}
            newEventIds={new Set()}
            onSelectEvent={setSelectedEvent}
          />
        </div>
      </div>

      <AuditLog events={events} onSelectEvent={setSelectedEvent} />

      {selectedEvent && (
        <RedactionViewer
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      )}
    </div>
  );
}
