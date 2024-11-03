import * as Plot from "npm:@observablehq/plot";
import * as Inputs from "npm:@observablehq/inputs";
import * as d3 from "npm:d3";
import { aqiLevels } from "./aqi_levels.js";

const METRICS = {
  "PM2.5": "pm25",
  "AQI US": "aqius",
  "AQI CN": "aqicn"
};

// Helper function to get AQI color based on AQIUS value

function getAqiColor(aqius) {
const level = aqiLevels.find(l => aqius >= l.min && aqius <= l.max);
return level ? level.color : "#8B3F3F";
}


export function barChart(data, {width = 640} = {}) {
  const container = document.createElement("div");
  container.style.display = "flex";
  container.style.flexDirection = "column";
  container.style.gap = "1rem";
  
  // Title
  const title = document.createElement("h3");
  title.textContent = "City Data";
  title.style.margin = "0";
  title.style.textAlign = "left";
  
  // Controls container
  const controls = document.createElement("div");
  controls.style.display = "flex";
  controls.style.gap = "1rem";
  controls.style.alignItems = "center";

  // Create selectors
  const citySelect = Inputs.select([...new Set(data.map(d => d.city))].sort(), {
    value: "Karachi",
    label: "Select City"
  });

  const metricSelect = Inputs.select(Object.keys(METRICS), {
    value: "PM2.5",
    label: "Select Metric"
  });


function createPlot(selectedCity, selectedMetric) {
    const metric = METRICS[selectedMetric];
    
    const currentTs = data.find(d => d.data_type === "current")?.ts;

    const filteredData = data
        .filter(d => 
        d.city === selectedCity && 
        d.data_source === "city" && 
        d[metric] != null &&
        (d.data_type === "current" || 
         (d.data_type === "history" && d.ts !== currentTs)) // Only keep history rows that don't match current ts
    )
        .map(d => ({
            ...d,
            timestamp: new Date(d.ts),
            value: +d[metric]
        }))
        .sort((a, b) => a.timestamp - b.timestamp);

    return Plot.plot({
        width,
        height: 400,
        marginLeft: 60,
        marginBottom: 50,
        
        y: {
            grid: true,
            label: `↑ ${selectedMetric}`,
            domain: [0, d3.max(filteredData, d => d.value) * 1.1],
        },
        
        marks: [
            // Main bars with AQI colors
            Plot.barY(filteredData, {
                x: "timestamp",
                y: "value",
                fill: d => getAqiColor(d.aqius),
                fillOpacity: d => d.data_type === "forecast" ? 0.3 : 0.8,
                channels: {
                    //PM25: "pm25",
                    AQIUS: "aqius",
                    Reading: "data_type",
                    timestamp: "ts"
                },
                tip: {
                    format: {
                        timestamp: d => new Date(d).toLocaleString(),
                        dataType: true,
                        //value: d => `${selectedMetric}: ${d.toFixed(2)}`,
                        aqius: d => `AQI US: ${d}`,
                        pm25: d => `PM2.5: ${d} µg/m³`,
                        fillOpacity: false,
                        timestamp: false,
                        pm25: false
                    }
                }
            }),
            // // Add text labels on top of bars
            // Plot.text(filteredData.filter((d, i) => i % 2 === 1), {
            //     x: "timestamp",
            //     y: "value",
            //     text: d => d.value.toFixed(0), // Format number to 0 decimal place
            //     dy: -8, // Shift text vertically
            //     fontSize: 9,
            //     fill: "black",
            //     textAnchor: "middle",
            //     stroke: "white",
            //     strokeWidth: 2,
            //     paintOrder: "stroke",
            // }),
            // Highlight for current data
            Plot.barY(
                filteredData.filter(d => d.data_type === "current"), 
                {
                    x: "timestamp",
                    y: "value",
                    stroke: "black",
                    strokeWidth: 2,
                    fill: "none"
                }
            ),
            // X-axis with days
            Plot.axisX({
                ticks: "hour",
                tickSize: 4,
                tickFormat: (d, i) => {
                    // Only show format for every other tick
                    if (i % 2 === 0) {
                        return `${d.getMonth()+1}/${d.getDate()}\n${d.getHours()}:00`;
                    }
                    return ""; // Return empty string for ticks we want to hide
                }
                //text: null
            }),
            Plot.ruleY([0]),
            
        ],
        
     
    });
}







  // Initial chart
  let chart = createPlot(citySelect.value, metricSelect.value);

  // Update chart when selections change
  function updateChart() {
    const newChart = createPlot(citySelect.value, metricSelect.value);
    chart.replaceWith(newChart);
    chart = newChart;
  }

  citySelect.addEventListener("change", updateChart);
  metricSelect.addEventListener("change", updateChart);

  // Assemble the component
  container.appendChild(title);
  controls.appendChild(citySelect);
  controls.appendChild(metricSelect);
  container.appendChild(controls);
  container.appendChild(chart);

  return container;
}
