const channels = {};

function openChannel(code) {
  if (!channels[code]) channels[code] = [];
}

function push(code, data) {
  if (!channels[code]) return;
  channels[code].push(data);
}

function pull(code) {
  if (!channels[code] || channels[code].length === 0) return null;
  return channels[code].shift();
}

module.exports = {
  openChannel,
  push,
  pull
};
