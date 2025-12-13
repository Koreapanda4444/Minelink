const http = require("http");
const { createSession, getSession, joinSession } = require("./sessions");

const PORT = 3000;

function readBody(req, cb) {
  let data = "";
  req.on("data", chunk => data += chunk);
  req.on("end", () => cb(JSON.parse(data || "{}")));
}

const server = http.createServer((req, res) => {
  if (req.method === "POST" && req.url === "/create") {
    readBody(req, () => {
      const code = createSession("host");
      res.end(JSON.stringify({ code }));
    });
    return;
  }

  if (req.method === "POST" && req.url === "/join") {
    readBody(req, body => {
      const ok = joinSession(body.code, "peer");
      res.end(JSON.stringify({ ok }));
    });
    return;
  }

  res.writeHead(404);
  res.end();
});

server.listen(PORT, () => {
  console.log(`Oracle server running on ${PORT}`);
});
