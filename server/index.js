const express = require("express");
const scheduler = require("./scheduler");

const mongoConnectionString = "mongodb://mongo/agenda";

var app = express();
app.set("mongoConnectionString", mongoConnectionString);
app.use("/agenda", scheduler({ mongoConnectionString }));

app.listen(3030);
