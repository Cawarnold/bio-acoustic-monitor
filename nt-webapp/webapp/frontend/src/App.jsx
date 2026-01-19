import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  const [allData, setAllData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [selectedBird, setSelectedBird] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    // 1. Fetch heartbeat
    fetch('/api/time')
      .then(res => res.json())
      .then(data => setCurrentTime(data.time))
      .catch(err => console.error("Time fetch failed:", err));

    // 2. Fetch Parquet data
    fetch('/api/summary')
      .then((res) => res.json())
      .then((json) => {
        if (json && json.length > 0) {
          setAllData(json);

          // Calculate totals per bird to find the "Top Bird"
          const birdTotals = json.reduce((acc, item) => {
            acc[item.bird] = (acc[item.bird] || 0) + item.count;
            return acc;
          }, {});

          // Sort birds by total count descending
          const sortedBirds = Object.keys(birdTotals).sort((a, b) => birdTotals[b] - birdTotals[a]);
          const topBird = sortedBirds[0];

          // Set initial selection to the most frequent bird
          setSelectedBird(topBird);
          setFilteredData(json.filter(item => item.bird === topBird));
        }
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

  // Derived state for the dropdown list (Sorted by count)
  const birdTotals = allData.reduce((acc, item) => {
    acc[item.bird] = (acc[item.bird] || 0) + item.count;
    return acc;
  }, {});
  
  const uniqueBirdsSorted = Object.keys(birdTotals).sort((a, b) => birdTotals[b] - birdTotals[a]);

  return (
    <div className="dashboard">
      <header>
        <h1>NatureThrive: Bird Monitor</h1>
        <p className="status-bar">
          System Status: Connected | Server Time: {currentTime ? new Date(currentTime * 1000).toLocaleString() : 'Loading...'}
        </p>
      </header>

      {loading ? (
        <div className="loading">Gathering bird analytics...</div>
      ) : (
        <>
          <div className="filter-container">
            <label htmlFor="bird-select">Select Bird Species (Sorted by Frequency): </label>
            <select id="bird-select" value={selectedBird} onChange={handleBirdChange}>
              {uniqueBirdsSorted.map(bird => (
                <option key={bird} value={bird}>
                  {bird} ({birdTotals[bird]} total)
                </option>
              ))}
            </select>
          </div>

          <div className="chart-container">
            <h3>{selectedBird} Detections</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={filteredData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
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
        </>
      )}
    </div>
  );
}

export default App;