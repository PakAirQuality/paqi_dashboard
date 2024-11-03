//import * as Plot from "npm:@observablehq/plot";
import mapboxgl from "npm:mapbox-gl";


export function climateMap(data, { width = 640, MAPBOX_ACCESS_TOKEN } = {}) {
  if (!MAPBOX_ACCESS_TOKEN) {
    throw new Error('Mapbox access token is required');
  }
  console.log("Map resize with width:", width);
  console.log("Total rows before filtering:", data.length);

 // Filter the data - simple string includes check for '2022'
  const filteredData = data.filter(d => 
    d.start_time.includes('2022') && 
    d.gas.toLowerCase() === 'co2'
  );
  console.log("Rows after filtering for 2022 and CO2:", filteredData.length);
  console.log("Sample filtered row:", filteredData[0]); // Let's also see what a sample row looks like


  // Create container
  const div = document.createElement("div");
  div.style.width = "100%";
  div.style.height = "680px";

  // Initialize map
  const map = new mapboxgl.Map({
    container: div,
    accessToken: MAPBOX_ACCESS_TOKEN,
    style: 'mapbox://styles/mapbox/light-v11',
    center: [69.3451, 30.3753], // Pakistan center coordinates
    zoom: 5,
    pitch: 0,
    bearing: 0
  });

  // Add navigation controls
  map.addControl(new mapboxgl.NavigationControl());
  map.addControl(new mapboxgl.FullscreenControl());

  // Format tooltip for climate data
  function formatClimateTooltip(d) {
    return `
      <strong>${d.source_name}</strong><br>
      Type: ${d.source_type}<br>
      Emissions: ${d.emissions_quantity} ${d.emissions_factor_units}<br>
      Gas: ${d.gas}<br>
      Capacity: ${d.capacity}
    `;
  }

  // Wait for map to load before adding markers
  map.on('load', () => {
    console.log("Map loaded, triggering resize");
    map.resize();
    console.log("Adding emission sources:", filteredData.length);

    // Add emission source markers
    filteredData.forEach(source => {
      const marker = document.createElement('div');

      // Debug individual problematic records
      if (source.emissions_quantity == null || isNaN(source.emissions_quantity)) {
        console.log("Problem record:", source);
      }
      
       // Normalize size based on emissions_quantity, handling blank and negative values
      const maxEmissions = Math.max(...filteredData
        .filter(d => d.emissions_quantity != null)
        .map(d => Math.abs(d.emissions_quantity)));
        
      const size = source.emissions_quantity != null ? 
        Math.max(12, Math.min(34, (Math.abs(source.emissions_quantity) / maxEmissions) * 34)) :
        12; // Minimum size for blank emissions
      
      marker.style = `
        background-color: #FF4444AA;
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        border: 2px solid white;
        cursor: pointer;
        box-shadow: 0 0 2px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 8px;
        color: white;
      `;

      // Add emissions value to marker if available
      marker.innerHTML = source.emissions_quantity != null ? Math.round(Math.abs(source.emissions_quantity)) : '';


      const popup = new mapboxgl.Popup({ offset: 25 })
        .setHTML(formatClimateTooltip(source));

      new mapboxgl.Marker(marker)
        .setLngLat([+source.longitude, +source.latitude])
        .setPopup(popup)
        .addTo(map);
    });
  });

  setTimeout(() => {
    map.resize();
  }, 0);

  return div;
}
