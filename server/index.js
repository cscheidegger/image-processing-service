const express = require("express");
const scheduler = require("./scheduler");

const config = require("config");
const mongoConnectionString = config.get("mongoConnectionString");

const { ipsVersion } = require('../package.json');

var app = express();
app.use("/agenda", scheduler({ mongoConnectionString }));
app.use("/api/description", (req, res) => { return res.json({ ipsVersion }); });
app.use("/", (req, res) => { return res.redirect("/agenda"); })

app.listen(config.get("port"));
