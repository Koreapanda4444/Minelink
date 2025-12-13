const sessions = {};

function createSession() {
  const code = Math.random().toString(36).substr(2, 6).toUpperCase();
  sessions[code] = { peers: [] };
  return code;
}

module.exports = { createSession };
