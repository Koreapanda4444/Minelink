const state = {
  sessions: {}
};

function initSession(code) {
  state.sessions[code] = {
    peers: []
  };
}

function addPeer(code, peerId) {
  if (!state.sessions[code]) return;
  state.sessions[code].peers.push(peerId);
}

function getPeers(code) {
  if (!state.sessions[code]) return [];
  return state.sessions[code].peers;
}

module.exports = {
  state,
  initSession,
  addPeer,
  getPeers
};