import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import DashboardWelcome from './DashboardWelcome';
import './App.css';

function Dashboard() {
  // --- Original State ---
  const [allData, setAllData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [selectedBird, setSelectedBird] = useState('');
  const [selectedBird2, setSelectedBird2] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);

  // --- New Analytics State ---
  const [currentView, setCurrentView] = useState('summary'); // 'summary' or 'analytics'
  const [dailyStats, setDailyStats] = useState([]);
  const [speciesTotals, setSpeciesTotals] = useState([]);
  const [hourlyPatterns, setHourlyPatterns] = useState([]);
  const [lastFetchTime, setLastFetchTime] = useState(new Date());

  useEffect(() => {
    // 1. Fetch heartbeat
    fetch('/api/time')
      .then(res => res.json())
      .then(data => setCurrentTime(data.time))
      .catch(err => console.error("Time fetch failed:", err));

    // 2. Multi-fetch for original summary AND new analytics
    Promise.all([
      fetch('/api/summary').then(res => res.json()),
      fetch('/api/daily-stats').then(res => res.json()),
      fetch('/api/species-totals').then(res => res.json()),
      fetch('/api/hourly-patterns').then(res => res.json())
    ])
    .then(([summaryJson, dailyJson, speciesJson, hourlyJson]) => {
      // Process Summary (Original logic)
      if (summaryJson && summaryJson.length > 0) {
        setAllData(summaryJson);
        const birdTotals = summaryJson.reduce((acc, item) => {
          acc[item.bird] = (acc[item.bird] || 0) + item.count;
          return acc;
        }, {});
        const sortedBirds = Object.keys(birdTotals).sort((a, b) => birdTotals[b] - birdTotals[a]);
        setSelectedBird(sortedBirds[0]);
        setFilteredData(summaryJson.filter(item => item.bird === sortedBirds[0]));
      }

      // Process New Analytics (Parse JSON strings from Flask)
      setDailyStats(typeof dailyJson === 'string' ? JSON.parse(dailyJson) : dailyJson);
      setSpeciesTotals(typeof speciesJson === 'string' ? JSON.parse(speciesJson) : speciesJson);
      setHourlyPatterns(typeof hourlyJson === 'string' ? JSON.parse(hourlyJson) : hourlyJson);
      setLastFetchTime(new Date());
      
      setLoading(false);
    })
    .catch((err) => {
      console.error("Data fetch failed:", err);
      setLoading(false);
    });
  }, []);

  const handleBirdChange = (event) => {
    const bird = event.target.value;
    setSelectedBird(bird);
    setFilteredData(allData.filter(item => item.bird === bird));
  };

  const handleBirdChange2 = (event) => {
    const bird = event.target.value;
    setSelectedBird2(bird);
  };

  // Derived state for the original dropdown
  const birdTotals = allData.reduce((acc, item) => {
    acc[item.bird] = (acc[item.bird] || 0) + item.count;
    return acc;
  }, {});
  const uniqueBirdsSorted = Object.keys(birdTotals).sort((a, b) => birdTotals[b] - birdTotals[a]);

  // Calculate key metrics
  const totalSpecies = uniqueBirdsSorted.length;
  const totalDetections = Object.values(birdTotals).reduce((sum, count) => sum + count, 0);
  const mostCommonSpecies = uniqueBirdsSorted[0] || 'None';
  const lastUpdateMinutesAgo = Math.floor((new Date() - lastFetchTime) / 60000);

  return (
    <div className="dashboard">
      <header>
        <h1>NatureThrive: Bird Monitor</h1>
        
        {/* Key Metrics Cards */}
        <div className="metrics-grid">
          <div className="metric-card">
            <p className="metric-label">Total Species Detected</p>
            <p className="metric-value">{totalSpecies}</p>
          </div>
          <div className="metric-card">
            <p className="metric-label">Total Detections</p>
            <p className="metric-value">{totalDetections.toLocaleString()}</p>
          </div>
          <div className="metric-card">
            <p className="metric-label">Most Common Species</p>
            <p className="metric-value">{mostCommonSpecies}</p>
          </div>
          <div className="metric-card">
            <p className="metric-label">Last Update</p>
            <p className="metric-value">{lastUpdateMinutesAgo === 0 ? 'Now' : `${lastUpdateMinutesAgo}m ago`}</p>
          </div>
        </div>

        <div className="nav-controls">
            <button onClick={() => setCurrentView('summary')} className={currentView === 'summary' ? 'active' : ''}>Summary View</button>
            <button onClick={() => setCurrentView('analytics')} className={currentView === 'analytics' ? 'active' : ''}>Advanced Analytics</button>
        </div>
        <p className="status-bar">
          System Status: Connected | Server Time: {currentTime ? new Date(currentTime * 1000).toLocaleString() : 'Loading...'}
        </p>
      </header>

      {loading ? (
        <div className="loading">Gathering bird analytics...</div>
      ) : (
        <main>
          {currentView === 'summary' ? (
            /* --- ORIGINAL VIEW --- */
            <div className="view-summary">
              <div className="filter-container">
                <div className="bird-selector">
                  <label htmlFor="bird-select-1">Bird 1: </label>
                  <select id="bird-select-1" value={selectedBird} onChange={handleBirdChange}>
                    {uniqueBirdsSorted.map(bird => (
                      <option key={bird} value={bird}>{bird} ({birdTotals[bird]} total)</option>
                    ))}
                  </select>
                </div>
                <div className="bird-selector">
                  <label htmlFor="bird-select-2">Bird 2: </label>
                  <select id="bird-select-2" value={selectedBird2} onChange={handleBirdChange2}>
                    <option value="">-- Select to compare --</option>
                    {uniqueBirdsSorted.map(bird => (
                      <option key={bird} value={bird}>{bird} ({birdTotals[bird]} total)</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="chart-container">
                <h3>Species Comparison</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={filteredData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="count" stroke="#2e7d32" fill="#a5d6a7" name={selectedBird} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          ) : (
            /* --- NEW ANALYTICS VIEW --- */
            <div className="view-analytics">
              <div className="chart-container">
                <h3>Daily Diversity (Shannon Index)</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={dailyStats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="shannon_index" stroke="#1976d2" fill="#bbdefb" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-container">
                <h3>Overall Species Abundance</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={speciesTotals}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="label" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="total_count" fill="#2e7d32" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-container">
                <h3>Hourly Activity Pattern</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={hourlyPatterns}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#fb8c00" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </main>
      )}
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DashboardWelcome />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;