import * as Plot from "npm:@observablehq/plot";

export function aqiBarChart(data, numCities, {width} = {}) {
  // Define the AQI levels and colors as an array of objects
  const aqiLevels = [
    { level: "Good", min: 0, max: 50, color: "#97C93D" },
    { level: "Moderate", min: 51, max: 100, color: "#FFCF01" },
    { level: "Unhealthy for Sensitive Groups", min: 101, max: 150, color: "#FF9933" },
    { level: "Unhealthy", min: 151, max: 200, color: "#FF3333" },
    { level: "Very Unhealthy", min: 201, max: 300, color: "#A35DB5" },
    { level: "Hazardous", min: 301, max: Infinity, color: "#8B3F3F" }
  ];

  const aqiColorScale = d => {
    const level = aqiLevels.find(l => d <= l.max);
    return level ? level.color : "#8B3F3F";
  }

  const aqiLevelText = d => {
    const level = aqiLevels.find(l => d <= l.max);
    return level ? level.level : "Hazardous";
  }

  // Format date for tooltip
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  }

  return Plot.plot({
    title: "Live Most Polluted Major City Ranking",
    width,
    height: 400,
    marginLeft: 120,
    marginRight: 150,
    x: {
      label: "Air Quality Index (AQI)",
      grid: true
    },
    color: {
      legend: true,
      domain: aqiLevels.map(d => d.level),
      range: aqiLevels.map(d => d.color)
    },
    marks: [
      Plot.barX(data.slice(0, numCities), {
        y: "city",
        x: "current_aqi",
        sort: {y: "x", reverse: true},
        fill: d => aqiColorScale(d.current_aqi),
        title: d => `Rank: ${d.rank}
  AQI: ${d.current_aqi}
  Level: ${aqiLevelText(d.current_aqi)}
  
  ${d.city}, ${d.country}
  Updated: ${formatDate(d.updated)}`,
        tip: true
      }),
      Plot.text(data.slice(0, numCities), {
        y: "city",
        x: "current_aqi",
        text: d => d.current_aqi,
        dx: -16,
        fill: "white",
        font: "bold",
        sort: {y: "x", reverse: true}
      }),
      Plot.ruleX([0])
    ]
  })
}