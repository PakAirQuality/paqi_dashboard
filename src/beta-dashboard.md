---
theme: dashboard
title: Beta Graphs in development
toc: true
---

<!-- Load and transform the data -->

```js
import { aqiLegend } from "./components/aqi_legend.js";
const ranks = FileAttachment("data/aqi_ranks.csv").csv({ typed: true });
const aqi = FileAttachment("data/aqi.csv").csv({ typed: true });
const countryData = await FileAttachment("data/countries.csv").csv({
  typed: true,
});
const tokens = await FileAttachment("data/tokens.json").json({ typed: true });
//console.log("Loaded tokens:", tokens);
```

## 📊 Visualization Testing Lab

These charts are experimental visualizations we're testing for potential inclusion in our main dashboard. We welcome your feedback on which displays are most useful and intuitive. Some graphs may be placeholders or show sample data while we refine our visualization approaches.

## Pakistan City Comparisons

⚠️ Development Note: This experimental visualization attempts to show PM2.5 levels across all Pakistani cities simultaneously. While comprehensive, we recognize it's currently too dense to be practical. 

```js
import { cityComparison } from "./components/city.js";
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => cityComparison(aqi, { width }))}
  </div>
</div>

Note: The forecast data shown in these graphs (the right side of the chart) should be treated as experimental and may not be reliable for decision-making.

## Global City Rankings

This interactive table shows current air quality rankings across cities worldwide.

```js
function aqi_sparkbar() {
  const max = d3.max(ranks, (d) => d.current_aqi); // get max AQI value

  return (x) => {
    const aqiLevels = [
      { level: "Good", min: 0, max: 50, color: "#97C93D" },
      { level: "Moderate", min: 51, max: 100, color: "#FFCF01" },
      {
        level: "Unhealthy for Sensitive Groups",
        min: 101,
        max: 150,
        color: "#FF9933",
      },
      { level: "Unhealthy", min: 151, max: 200, color: "#FF3333" },
      { level: "Very Unhealthy", min: 201, max: 300, color: "#A35DB5" },
      { level: "Hazardous", min: 301, max: Infinity, color: "#8B3F3F" },
    ];

    const getColor = (d) => {
      const level = aqiLevels.find((l) => d <= l.max);
      return level ? level.color : "#8B3F3F";
    };

    return htl.html`<div style="
      background: ${getColor(x)};
      color: white;
      width: ${(100 * x) / max}%;
      padding: 4px 8px;
      border-radius: 4px;
      text-align: left;
      font-weight: bold;
      ">${x}</div>`;
  };
}
```

```js
// Search input
const search = view(Inputs.search(ranks, { placeholder: "Search cities..." }));
```

```js
// Display table
Inputs.table(search, {
  format: {
    rank: (d, i) => search[i].rank,
    city: (city, i) => `${search[i].city}, ${search[i].country}`,
    current_aqi: aqi_sparkbar(),
  },
  columns: ["rank", "city", "current_aqi"],
  header: {
    rank: "Rank",
    city: "Location",
    current_aqi: "AQI",
  },
  width: {
    rank: 36,
    city: "auto",
    //current_aqi: 300
  },
})
```

${aqiLegend()}

# Simpler City Ranking

```js
function aqiBox() {
  const aqiLevels = [
    { level: "Good", min: 0, max: 50, color: "#97C93D" },
    { level: "Moderate", min: 51, max: 100, color: "#FFCF01" },
    { level: "Unhealthy for Sensitive Groups", min: 101, max: 150, color: "#FF9933" },
    { level: "Unhealthy", min: 151, max: 200, color: "#FF3333" },
    { level: "Very Unhealthy", min: 201, max: 300, color: "#A35DB5" },
    { level: "Hazardous", min: 301, max: Infinity, color: "#8B3F3F" }
  ];

  const getColor = (d) => {
    const level = aqiLevels.find((l) => d <= l.max);
    return level ? level.color : "#8B3F3F";
  };

  return (x) => htl.html`<div style="
    background: ${getColor(x)};
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    text-align: center;
    font-weight: bold;
    display: inline-block;
    min-width: 40px;
    ">${x}</div>`;
}
```


```js
// Use in table
Inputs.table(search, {
  format: {
    rank: (d, i) => search[i].rank,
    city: (city, i) => `${search[i].city}, ${search[i].country}`,
    current_aqi: aqiBox()
  },
  columns: ["rank", "city", "current_aqi"],
  header: {
    rank: "Rank",
    city: "Location",
    current_aqi: "AQI"
  },
  width: {
    rank: 35,
    city: 150,
    //AQI: 50
  }
})
```

## Pakistan Cities

```js
Plot.plot({
  x: {
    value: d => d.ts,
    label: "Time",
  },
  y: {
    label: "Cities",
    domain: Array.from(new Set(aqi.map(d => d.city))),
  },
  marks: [
    Plot.cell(aqi, {
      x: "ts",
      y: "city",
      fill: d => d.aqi_color,
      title: d => `${d.city}\nPM2.5: ${d.pm25}\nTime: ${d3.timeFormat("%b %d, %H:%M")(d.ts)}` // Formatted tooltip
    }),
    
  ],
  height: 400,
  marginLeft: 100
})
```

```js
// Simple sort by city then timestamp
const sortedAqi = d3.sort(aqi, d => `${d.city}${d.ts}`);

Plot.plot({
  x: {
    value: d => d.ts,
    label: "Time",
  },
  y: {
    label: "Cities",
    domain: Array.from(new Set(sortedAqi.map(d => d.city))),
  },
  marks: [
    Plot.cell(sortedAqi, {
      x: "ts",
      y: "city",
      fill: d => d.aqi_color,
      title: d => `${d.city}\nPM2.5: ${d.pm25}\nTime: ${d3.timeFormat("%b %d, %H:%M")(d.ts)}`
    }),
  ],
  height: 400,
  marginLeft: 100
})
```