const fs = require("fs");
const path = require("path");
const request = require("request");

// Python runner
const { execFile } = require("child_process");

// Configuration
const config = require("config");
const imagesPath = config.get("imagesPath");

// Agenda modules
const Agenda = require("agenda");
const Agendash = require("agendash");

// Helper function to analyse results from script
function getAnalysisFromStdout(stdout) {
  // split lines
  var allLines = stdout.split("\n");

  // get line before last
  var jsonString = allLines[allLines.length - 2];

  var result;

  try {
    result = JSON.parse(jsonString);
  } catch (e) {
    result = {
      error: {
        message: "Não foi possível processar a imagem."
      }
    };
  }

  return result;
}

// Setup and start agenda
module.exports = function (options) {
  const { mongoConnectionString } = options || {};

  if (!mongoConnectionString)
    throw new Error('Missing "mongoConnectionString" option.');

  var agenda = new Agenda({ db: { address: mongoConnectionString } });
  agenda.defaultLockLifetime(120000);

  agenda.define("process image", processImageJob);

  agenda.on("ready", function () {
    agenda.start();
  });

  return Agendash(agenda);
};

// Define process image job
function processImageJob(job, done) {
  const { image } = job.attrs.data;

  const imagePath = `${imagesPath}/${job.attrs._id}`;

  function downloadImage() {
    const imageUrl = image && image.url;

    return new Promise((resolve, reject) => {
      if (!imageUrl)
        return reject(new Error("process image job: missing 'image.url'"));

      const writeStream = fs.createWriteStream(imagePath);
      writeStream.on("error", reject);

      request
        .get(imageUrl)
        .on("response", res => {
          if (res.statusCode !== 200 || res.headers['content-type'].indexOf("image") !== 0) {
            return reject(new Error("process image job: could not fetch image"));
          } else resolve();
        })
        .on("error", reject)
        .pipe(writeStream);
    });
  }

  function analyse() {
    return new Promise((resolve, reject) => {
      const analysisStartedAt = new Date();
      execFile(
        "python",
        ["scripts/Application.py", imagePath],
        (err, stdout) => {
          let results = {
            status: "valid"
          };

          // parse result and internal errors
          if (!err) {
            results = getAnalysisFromStdout(stdout);
          } else {
            results.error = {
              code: "500",
              name: err.name,
              message: "O processo de análise retornou um erro inválido.",
              internalMessage: err.message,
              stack: err.stack
            };
          }

          // analysis error
          results.status = results.error ? "invalid" : "valid";

          // set timestamps
          results.analysisStartedAt = analysisStartedAt;
          results.analysisFinishedAt = new Date();

          // load version from package.json
          let packageJson;
          try {
            packageJson = fs.readFileSync(path.resolve(__dirname, '../../package.json'), 'UTF-8');
            packageJson = JSON.parse(packageJson);
            results.ipsData = {
              ipsVersion: packageJson.ipsVersion
            };
          } catch (error) {
            results.error = {
              code: "500",
              message: "O processo de análise retornou um erro inválido."
            };
          }
        
          job.attrs.data = Object.assign(job.attrs.data, results);
          job.save();

          const { webhookUrl } = job.attrs.data;
          if (webhookUrl) {
            request
              .post(webhookUrl)
              .form({ results })
              .on("complete", resolve)
              .on("error", reject);
          } else resolve();
        }
      );
    });
  }

  function returnError(err) {
    job.attrs.data.error = {
      code: "500",
      name: err.name,
      message: "Erro interno no servidor de processamento de imagens.",
      internalMessage: err.message,
      stack: err.stack
    };
    job.fail(err).save();
    done(err);
  }

  function returnSucess() {
    done();
  }

  downloadImage()
    .then(analyse)
    .then(returnSucess)
    .catch(returnError);

}
