const http = require("http");
const { createSession, joinSession } = require("./sessions");
const relay = require("./relay");
const peerState = require("./state");

const PORT = 3000;

function readBody(req, cb) {
  let data = "";
  req.on("data", c => data += c);
  req.on("end", () => cb(JSON.parse(data || "{}")));
}

const server = http.createServer((req, res) => {
  if (req.method === "POST" && req.url === "/create") {
    readBody(req, () => {
      const code = createSession("host");
      peerState.initSession(code);
      relay.openChannel(code);
      res.end(JSON.stringify({ code }));
    });
    return;
  }

  if (req.method === "POST" && req.url === "/join") {
    readBody(req, body => {
      const ok = joinSession(body.code, "peer");
      if (ok) peerState.addPeer(body.code, "peer");
      res.end(JSON.stringify({ ok }));
    });
    return;
  }

  if (req.method === "POST" && req.url === "/peers") {
    readBody(req, body => {
      const peers = peerState.getPeers(body.code);
      res.end(JSON.stringify({ peers }));
    });
    return;
  }

  if (req.method === "POST" && req.url === "/relay/push") {
    readBody(req, body => {
      relay.push(body.code, body.data);
      res.end(JSON.stringify({ ok: true }));
    });
    return;
  }

  if (req.method === "POST" && req.url === "/relay/pull") {
    readBody(req, body => {
      const data = relay.pull(body.code);
      res.end(JSON.stringify({ data }));
    });
    return;
  }

  res.writeHead(404);
  res.end();
});

server.listen(PORT, () => {
  console.log(`Oracle server running on ${PORT}`);
});
