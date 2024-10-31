export async function load() {
  const tokens = await FileAttachment("data/tokens.json").json();
  
  // Simple test API call to AirVisual
  const url = `https://api.airvisual.com/v2/city?city=Lahore&state=Punjab&country=Pakistan&key=${tokens.AIRVISUAL_KEY}`;
  
  console.log("Testing AirVisual token...");
  const response = await fetch(url);
  const data = await response.json();
  
  return {
    success: response.ok,
    status: response.status,
    data: data
  };
}