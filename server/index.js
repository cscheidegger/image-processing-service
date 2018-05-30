// Base modules
const fs = require('fs');
const path = require('path');
const logger = require('winston');

// Config
const config = require("config");
const mongoConnectionString = config.get("mongoConnectionString");

// Express & Agenda
const express = require("express");
const scheduler = require("./scheduler");

// Setup routes
var app = express();
app.use("/agenda", scheduler({ mongoConnectionString }));
app.use("/api/description", async (req, res) => {
  let packageJson;

  try {
    packageJson = fs.readFileSync(path.resolve(__dirname, '../package.json'), 'UTF-8');
    packageJson = JSON.parse(packageJson);
  } catch (error) {
    return res.status(500).send({ error: 'Could not read IPS settings, please contact support.' });
  }

  return res.json({ ipsVersion: packageJson.ipsVersion });
});
app.use("/", (req, res) => { return res.redirect("/agenda"); });

// Start server
const server = app.listen(config.get("port"));
server.on('listening', () => {
  logger.info('IPS started.');
});
