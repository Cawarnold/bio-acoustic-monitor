import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const SpeciesBarChart = () => {
  const svgRef = useRef();

  useEffect(() => {
    // 1. Fetch data from your updated api.py endpoint
    fetch('http://localhost:5000/api/species-totals')
      .then(res => res.json())
      .then(rawData => {
        // Since Flask sent JSON.stringify, we parse it if needed
        const data = typeof rawData === 'string' ? JSON.parse(rawData) : rawData;

        // 2. Setup Dimensions
        const margin = { top: 20, right: 30, bottom: 40, left: 100 };
        const width = 600 - margin.left - margin.right;
        const height = 400 - margin.top - margin.bottom;

        // 3. Clear the SVG to prevent "ghost" charts on refresh
        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const g = svg.append("g")
          .attr("transform", `translate(${margin.left},${margin.top})`);

        // 4. Create Scales (map counts to pixels)
        const x = d3.scaleLinear()
          .domain([0, d3.max(data, d => d.total_count)])
          .range([0, width]);

        const y = d3.scaleBand()
          .domain(data.map(d => d.label))
          .range([0, height])
          .padding(0.1);

        // 5. Draw the Bars
        g.selectAll(".bar")
          .data(data)
          .enter().append("rect")
          .attr("class", "bar")
          .attr("x", 0)
          .attr("y", d => y(d.label))
          .attr("width", d => x(d.total_count))
          .attr("height", y.bandwidth())
          .attr("fill", "#2e7d32");

        // 6. Add the Axis
        g.append("g").call(d3.axisLeft(y));
        g.append("g")
          .attr("transform", `translate(0,${height})`)
          .call(d3.axisBottom(x));
      })
      .catch(err => console.error("D3 Fetch Error:", err));
  }, []);

  return (
    <div className="chart-container">
      <svg ref={svgRef} width={600} height={400}></svg>
    </div>
  );
};

export default SpeciesBarChart;