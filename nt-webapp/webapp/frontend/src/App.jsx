import { useState, useEffect } from 'react';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  // --- Original State ---
  const [allData, setAllData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [selectedBird, setSelectedBird] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);

  // --- New Analytics State ---
  const [currentView, setCurrentView] = useState('summary'); // 'summary' or 'analytics'
  const [dailyStats, setDailyStats] = useState([]);
  const [speciesTotals, setSpeciesTotals] = useState([]);
  const [hourlyPatterns, setHourlyPatterns] = useState([]);

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

  // Derived state for the original dropdown
  const birdTotals = allData.reduce((acc, item) => {
    acc[item.bird] = (acc[item.bird] || 0) + item.count;
    return acc;
  }, {});
  const uniqueBirdsSorted = Object.keys(birdTotals).sort((a, b) => birdTotals[b] - birdTotals[a]);

  return (
    <div className="dashboard">
      <header>
        <h1>NatureThrive: Bird Monitor</h1>
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
                <label htmlFor="bird-select">Select Bird Species: </label>
                <select id="bird-select" value={selectedBird} onChange={handleBirdChange}>
                  {uniqueBirdsSorted.map(bird => (
                    <option key={bird} value={bird}>{bird} ({birdTotals[bird]} total)</option>
                  ))}
                </select>
              </div>

              <div className="chart-container">
                <h3>{selectedBird} Detections</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={filteredData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="count" stroke="#2e7d32" fill="#a5d6a7" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="stats-grid">
                {filteredData.map((item, index) => (
                  <div key={index} className="stat-card">
                    <h4>{item.bird}</h4>
                    <p className="count">{item.count} calls</p>
                    <p className="date">{item.date}</p>
                  </div>
                ))}
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

export default App;