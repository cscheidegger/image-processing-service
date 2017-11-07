const fs = require("fs");
const { execFile } = require("child_process");
const request = require("request");
const Agenda = require("agenda");
const Agendash = require("agendash");

// Helper function to analyse results from script
function getAnalysisFromStdout(stdout) {
  // split lines
  var allLines = stdout.split("\n");

  // get line before last
  var jsonString = allLines[allLines.length - 2];

  return JSON.parse(jsonString);
}

// Setup and start agenda
module.exports = function(options) {
  const { mongoConnectionString } = options || {};

  if (!mongoConnectionString)
    throw new Error('Missing "mongoConnectionString" option.');

  var agenda = new Agenda({ db: { address: mongoConnectionString } });

  agenda.define("process image", processImageJob);

  agenda.on("ready", function() {
    agenda.start();
  });

  return Agendash(agenda);
};

// Define process image job
function processImageJob(job, done) {
  const { imageUrl } = job.attrs.data;

  // clear results if job was requeued
  job.attrs.data.results = {};

  const imagePath = `/images/${job.attrs._id}`;

  downloadImage()
    .then(analyse)
    .then(returnSucess)
    .catch(returnError);

  function downloadImage() {
    if (!imageUrl)
      return job.fail("'process image job': missing 'imageUrl'").save();

    return new Promise((resolve, reject) => {
      const writeStream = fs.createWriteStream(imagePath);
      writeStream.on("error", reject);

      request
        .get(imageUrl)
        .on("complete", resolve)
        .on("error", reject)
        .pipe(writeStream);
    });
  }

  function analyse() {
    return new Promise((resolve, reject) => {
      execFile(
        "python",
        ["/src/scripts/Application.py", imagePath],
        (err, stdout, stderr) => {
          if (err) reject(err);
          else {
            // get resulting analysis json
            const analysis = stdout.split("\n");

            job.attrs.data.results = {
              analysis: getAnalysisFromStdout(stdout)
            };
            job.save();
            resolve();
          }
        }
      );
    });
  }

  function returnError(err) {
    job.attrs.data.results.err = {
      name: err.name,
      message: err.message,
      stack: err.stack
    };
    job.fail(err).save();
  }

  function returnSucess() {
    done();
  }
}
