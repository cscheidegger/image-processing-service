const express = require("express");
const scheduler = require("./scheduler");

const config = require("config");
const mongoConnectionString = config.get("mongoConnectionString");

var app = express();
app.use("/agenda", scheduler({ mongoConnectionString }));
app.use("/", (req, res) => { return res.redirect("/agenda"); })

app.listen(3030);
