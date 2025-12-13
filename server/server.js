const http = require("http");

http.createServer((req, res) => {
  res.end("Minelink Oracle Server");
}).listen(3000, () => {
  console.log("Oracle server running on 3000");
});
