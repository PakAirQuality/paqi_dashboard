/**
 * Data loader for API tokens in Observable Framework
 * 
 * This file:
 * 1. Runs at build time as a data loader
 * 2. Accesses environment variables via process.env
 * 3. Writes them to a JSON file that can be loaded client-side
 * 
 * Usage:
 * 1. Set environment variables in your system (not in .env)
 * 2. This loader creates tokens.json during build
 * 3. In index.md or other files, load the tokens:
 *    const tokens = await FileAttachment("data/tokens.json").json({ typed: true });
 * 4. Pass tokens to components that need them:
 *    stationMap(data, { mapboxToken: tokens.MAPBOX_ACCESS_TOKEN })
 * 
 * Note: 
 * - Tokens are only accessed at build time, keeping them secure
 * - If you update env variables, rebuild to refresh tokens.json
 * - Clean .observablehq cache if changes don't appear
 */

const configuration = {
  MAPBOX_ACCESS_TOKEN: process.env["MAPBOX_ACCESS_TOKEN"],
  AIRVISUAL_KEY: process.env["AIRVISUAL_KEY"],
  ANTHROPIC_API_KEY: process.env["ANTHROPIC_API_KEY"],
};

process.stdout.write(JSON.stringify(configuration));