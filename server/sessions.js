const sessions = {};

function generateCode() {
  return Math.random().toString(36).slice(2, 8).toUpperCase();
}

function createSession(hostId) {
  let code;
  do {
    code = generateCode();
  } while (sessions[code]);

  sessions[code] = {
    host: hostId,
    peers: []
  };

  return code;
}

function getSession(code) {
  return sessions[code] || null;
}

function joinSession(code, peerId) {
  const session = sessions[code];
  if (!session) return false;

  session.peers.push(peerId);
  return true;
}

module.exports = {
  createSession,
  getSession,
  joinSession
};
