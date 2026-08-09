export function usePolling(fn, interval = 2000) {
  let id = null;

  function start() {
    if (id) return;
    id = setInterval(fn, interval);
  }

  function stop() {
    if (id) {
      clearInterval(id);
      id = null;
    }
  }

  function isRunning() {
    return id !== null;
  }

  return { start, stop, isRunning };
}
