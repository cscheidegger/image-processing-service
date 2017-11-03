const expressServerConfig = require("./config");
const expressMiddleware = require("./middleware");
const rest = require("feathers-rest");
const path = require("path");

const app = expressServerConfig()
  .configure(rest())
//   .configure(services)
  .configure(expressMiddleware);

const server = app.listen(3030);
server.on("listening", () =>
  console.log(`Feathers application started on port 3030`)
);