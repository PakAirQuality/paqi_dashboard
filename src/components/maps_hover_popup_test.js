//import * as Plot from "npm:@observablehq/plot";
import { aqiLevels } from "./aqi_levels.js";
import mapboxgl from "npm:mapbox-gl";



// Helper function to format tooltip content with optional comment and temperature
function formatTooltip(d) {
  let tooltip = `
    <strong>${d.station || d.city}, ${d.country}</strong><br>
    PM2.5: ${d.pm25} μg/m³<br>
    AQI (US): ${d.aqius}
    ${d.aqicn ? `<br>AQI (CN): ${d.aqicn}` : ''}
    ${d.tp ? `<br>Temperature: ${d.tp}°C` : ''}
    ${d.comment ? `<br><br>${d.comment}` : ''}
  `;
  return tooltip;
}

// Helper function to get AQI color based on AQIUS value
function getAqiColor(aqius) {
  const level = aqiLevels.find(l => aqius >= l.min && aqius <= l.max);
  return level ? level.color : "#8B3F3F";
}



export function stationMap(data, { width = 640, MAPBOX_ACCESS_TOKEN } = {}) {
  if (!MAPBOX_ACCESS_TOKEN) {
    throw new Error('Mapbox access token is required');
  }
  console.log("Map resize with width:", width); // Debug width
  
    // Filter for current readings from both stations and cities
  const stationData = data.filter(d => d.data_source === "station" && d.data_type === "current");
  const cityData = data.filter(d => d.data_source === "city" && d.data_type === "current");
  
  const div = document.createElement("div");
  div.style.width = "100%";
  div.style.height = "550px";
  
  const map = new mapboxgl.Map({
    container: div,
    accessToken: MAPBOX_ACCESS_TOKEN,
    style: 'mapbox://styles/mapbox/light-v11',
    center: [69.3451, 30.3753],  // Pakistan center coordinates
    zoom: 5,
    pitch: 0,
    bearing: 0
  });

  // Add navigation controls
  map.addControl(new mapboxgl.NavigationControl());
  map.addControl(new mapboxgl.FullscreenControl());

  // Create a single popup for all markers
  const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false,
    anchor: 'bottom-left',
    offset: [10, -10]
  });

  // Wait for map to load before adding markers
  map.on('load', () => {
    console.log("Map loaded, triggering resize");
    map.resize();
    console.log("Adding stations:", stationData.length);
    console.log("Adding cities:", cityData.length);
    
    // Add station markers (smaller)
    stationData.forEach(station => {
      const marker = document.createElement('div');
      const color = getAqiColor(station.aqius);
      marker.style = `
        background-color: ${color};
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: 2px solid white;
        cursor: pointer;
        box-shadow: 0 0 2px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 8px;
        color: ${getBrightnessForBackground(color) ? 'black' : 'white'};
      `;
      marker.innerHTML = Math.round(station.pm25);

      // Add hover events to marker
      marker.addEventListener('mouseenter', () => {
        map.getCanvas().style.cursor = 'pointer';
        popup
          .setLngLat([+station.longitude, +station.latitude])
          .setHTML(formatTooltip(station))
          .addTo(map);
      });

      marker.addEventListener('mouseleave', () => {
        map.getCanvas().style.cursor = '';
        popup.remove();
      });

      new mapboxgl.Marker(marker)
        .setLngLat([+station.longitude, +station.latitude])
        .addTo(map);
    });

    // Add city markers (larger)
    cityData.forEach(city => {
      const marker = document.createElement('div');
      const color = getAqiColor(city.aqius);
      marker.style = `
        background-color: ${color}99; /* Added 99 for 60% opacity */
        width: 34px;
        height: 34px;
        border-radius: 50%;
        border: 3px solid white;
        cursor: pointer;
        box-shadow: 0 0 3px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        color: ${getBrightnessForBackground(color) ? 'black' : 'white'};
      `;
      marker.innerHTML = Math.round(city.pm25);

      // Add hover events to marker
      marker.addEventListener('mouseenter', () => {
        map.getCanvas().style.cursor = 'pointer';
        popup
          .setLngLat([+city.longitude, +city.latitude])
          .setHTML(formatTooltip(city))
          .addTo(map);
      });

      marker.addEventListener('mouseleave', () => {
        map.getCanvas().style.cursor = '';
        popup.remove();
      });

      new mapboxgl.Marker(marker)
        .setLngLat([+city.longitude, +city.latitude])
        .addTo(map);
    });
  });

  setTimeout(() => {
    map.resize();
  }, 0);

  

  return div;
}

// Helper function to determine if text should be black or white based on background color
function getBrightnessForBackground(color) {
  // Convert hex to RGB
  const hex = color.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  // Calculate perceived brightness
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  
  // Return true for light backgrounds (should use black text)
  return brightness > 128;
}