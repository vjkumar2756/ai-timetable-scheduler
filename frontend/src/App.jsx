import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DashboardPage from './pages/DashboardPage';
import TimetableViewPage from './pages/TimetableViewPage';
import GeneratePage from './pages/GeneratePage';
import OperationsPage from './pages/OperationsPage';
import WorkloadPage from './pages/WorkloadPage';
import BenchmarkPage from './pages/BenchmarkPage';
import ManageEntitiesPage from './pages/ManageEntitiesPage';
import { api } from './services/api';
import { Bell, RefreshCw, Zap } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [overview, setOverview] = useState({});
  const [classes, setClasses] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [settings, setSettings] = useState({ days: ["Mon", "Tue", "Wed", "Thu", "Fri"], periods_per_day: 6, default_lunch_period: 4 });
  const [scheduleData, setScheduleData] = useState({ sessions: [], metadata: {} });
  const [notificationCount, setNotificationCount] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setIsRefreshing(true);
    try {
      const [
        overviewRes, classesRes, teachersRes, subjectsRes, roomsRes, settingsRes, scheduleRes, notifRes
      ] = await Promise.all([
        api.getOverview(),
        api.getClasses(),
        api.getTeachers(),
        api.getSubjects(),
        api.getRooms(),
        api.getSettings(),
        api.getSchedule(),
        api.getNotifications()
      ]);

      if (overviewRes.data) setOverview(overviewRes.data);
      if (classesRes.data) setClasses(classesRes.data);
      if (teachersRes.data) setTeachers(teachersRes.data);
      if (subjectsRes.data) setSubjects(subjectsRes.data);
      if (roomsRes.data) setRooms(roomsRes.data);
      if (settingsRes.data) setSettings(settingsRes.data);
      if (scheduleRes.data) setScheduleData(scheduleRes.data);
      if (notifRes.data) setNotificationCount(notifRes.data.length);
    } catch (err) {
      console.error("Error loading application state:", err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handlePresetLoad = async (presetName) => {
    try {
      const res = await api.loadDataset(presetName);
      if (res.success) {
        await loadAllData();
        alert(`Loaded preset: ${presetName.toUpperCase()} dataset. You can now generate a timetable!`);
      }
    } catch (err) {
      alert("Failed to load preset: " + err.message);
    }
  };

  const getPageTitle = () => {
    switch (activeTab) {
      case 'dashboard': return { title: 'Academic Operations Dashboard', subtitle: 'Real-time overview of scheduling health, infrastructure, and metrics' };
      case 'timetable': return { title: 'Institutional Timetable Grid', subtitle: 'Day-by-period conflict-free schedule visual matrix' };
      case 'generate': return { title: 'Automatic Schedule Generator', subtitle: 'Select AI algorithm and solve Constraint Satisfaction Problem' };
      case 'operations': return { title: 'Operations & Academic Rescheduling', subtitle: 'Manage missed lectures, faculty class swaps, and class closures' };
      case 'workload': return { title: 'Faculty Teaching Load Analytics', subtitle: 'Contractual workload utilization and capacity distribution' };
      case 'benchmarks': return { title: 'Algorithm Comparison & Experiments', subtitle: 'Assignment benchmarks, 10-trial metrics, and convergence curves' };
      case 'entities': return { title: 'Entity & Infrastructure Setup', subtitle: 'Configure teachers, classes, subject curriculum, and classrooms' };
      default: return { title: 'SchedulAI', subtitle: 'AI Timetable Scheduler' };
    }
  };

  const headerInfo = getPageTitle();

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onPresetLoad={handlePresetLoad}
        notificationCount={notificationCount}
      />

      {/* Main View Area */}
      <main className="main-content">
        {/* Sticky Top Header Bar */}
        <header className="top-bar">
          <div className="top-bar-title">
            <h1>{headerInfo.title}</h1>
            <p>{headerInfo.subtitle}</p>
          </div>

          <div className="top-bar-actions">
            <button 
              className="btn btn-secondary" 
              onClick={loadAllData} 
              disabled={isRefreshing}
              title="Refresh all data from backend"
            >
              <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} />
              <span>Refresh</span>
            </button>

            {activeTab !== 'generate' && (
              <button className="btn btn-primary" onClick={() => setActiveTab('generate')}>
                <Zap size={14} />
                <span>Generate Schedule</span>
              </button>
            )}
          </div>
        </header>

        {/* Dynamic Page Views */}
        {activeTab === 'dashboard' && (
          <DashboardPage
            overview={overview}
            onNavigate={setActiveTab}
            onGenerateClick={() => setActiveTab('generate')}
          />
        )}

        {activeTab === 'timetable' && (
          <TimetableViewPage
            scheduleData={scheduleData}
            classes={classes}
            teachers={teachers}
            rooms={rooms}
            settings={settings}
            onScheduleUpdated={loadAllData}
          />
        )}

        {activeTab === 'generate' && (
          <GeneratePage
            onGenerated={() => loadAllData()}
            onNavigate={setActiveTab}
          />
        )}

        {activeTab === 'operations' && (
          <OperationsPage
            sessions={scheduleData.sessions || []}
            classes={classes}
            teachers={teachers}
            onDataUpdated={loadAllData}
          />
        )}

        {activeTab === 'workload' && (
          <WorkloadPage />
        )}

        {activeTab === 'benchmarks' && (
          <BenchmarkPage />
        )}

        {activeTab === 'entities' && (
          <ManageEntitiesPage
            teachers={teachers}
            classes={classes}
            subjects={subjects}
            rooms={rooms}
            onDataUpdated={loadAllData}
          />
        )}
      </main>
    </div>
  );
}
