// Saves the table after every change (a moment later, so a quick run of
// changes is sent once). The server checks it and keeps it in the session,
// so the table is still set when you come back to the kitchen.
(() => {
  if (!window.tableEditor) return;
  const WAIT_MS = 350;
  let timer = null;

  function note(text) {
    const el = document.getElementById("table-saved");
    if (el) el.textContent = text;
  }

  function save(items, cloth) {
    const table = document.getElementById("table");
    if (!table) return;
    const body = JSON.stringify({ cloth, items });
    fetch(table.dataset.save, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      keepalive: true, // finish even if you leave right away
    })
      .then((r) => note(r.ok ? "Saved" : "Couldn't save that"))
      .catch(() => note("Couldn't save (are you offline?)"));
  }

  window.tableEditor.onChange((items, cloth) => {
    note("");
    clearTimeout(timer);
    timer = setTimeout(() => save(items, cloth), WAIT_MS);
  });
})();
