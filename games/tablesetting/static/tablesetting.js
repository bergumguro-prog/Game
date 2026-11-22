// The table decorating editor. Everything on the table is a list of
// { id, color, x, y, r } (x and y in art pixels from the table's top-left,
// r = quarter turns). Drag from the menu to add, drag on the table to move,
// drag off the table to remove; R rotates and Delete removes the picked one.
// Other scripts can listen for changes with window.tableEditor.onChange.
(() => {
  const DRAG_START = 4; // pixels to move before a press becomes a drag

  let table, items, selected, max;
  const listeners = [];

  function scale() {
    return table.getBoundingClientRect().width / Number(table.dataset.w);
  }

  function art(id, color) {
    const t = document.getElementById(`art-${id}-${color}`);
    return t ? t.innerHTML : "";
  }

  function sizeOf(id) {
    const button = document.querySelector(`.menu-item[data-item="${id}"]`);
    return { w: Number(button.dataset.w), h: Number(button.dataset.h) };
  }

  function clamp(item) {
    const { w, h } = sizeOf(item.id);
    item.x = Math.max(0, Math.min(Number(table.dataset.w) - w, Math.round(item.x)));
    item.y = Math.max(0, Math.min(Number(table.dataset.h) - h, Math.round(item.y)));
  }

  function changed() {
    render();
    listeners.forEach((fn) => fn(items, table.dataset.cloth));
  }

  function render() {
    table.querySelectorAll(".placed").forEach((el) => el.remove());
    items.forEach((item, i) => {
      const { w, h } = sizeOf(item.id);
      const el = document.createElement("div");
      el.className = "placed" + (i === selected ? " selected" : "");
      el.dataset.index = i;
      el.style.cssText = `--x: ${item.x}; --y: ${item.y}; --w: ${w}; --h: ${h}; --r: ${item.r};`;
      el.innerHTML = art(item.id, item.color);
      table.appendChild(el);
    });
    document.getElementById("rotate-item").disabled = selected === null;
    document.getElementById("remove-item").disabled = selected === null;
  }

  function select(i) {
    selected = i;
    render();
  }

  function rotate() {
    if (selected === null) return;
    items[selected].r = (items[selected].r + 1) % 4;
    changed();
  }

  function remove() {
    if (selected === null) return;
    items.splice(selected, 1);
    selected = null;
    changed();
    if (window.scenes) window.scenes.play("back");
  }

  function overTable(x, y) {
    const box = table.getBoundingClientRect();
    return x >= box.left && x <= box.right && y >= box.top && y <= box.bottom;
  }

  // --- Dragging ---
  let drag = null;

  document.addEventListener("pointerdown", (e) => {
    if (!table || e.button !== 0) return;
    const fromMenu = e.target.closest(".menu-item");
    const onTable = e.target.closest(".placed");
    if (!fromMenu && !onTable) {
      // clicking the bare table puts down what you picked (but swatches keep it)
      if (table.contains(e.target) && selected !== null) select(null);
      return;
    }
    e.preventDefault();
    drag = { startX: e.clientX, startY: e.clientY, started: false };
    if (fromMenu) {
      drag.kind = "new";
      drag.id = fromMenu.dataset.item;
      drag.color = fromMenu.dataset.color;
    } else {
      drag.kind = "move";
      drag.index = Number(onTable.dataset.index);
      drag.el = onTable;
      select(drag.index);
      drag.el = table.querySelector(`.placed[data-index="${drag.index}"]`);
    }
  });

  document.addEventListener("pointermove", (e) => {
    if (!drag) return;
    const dx = e.clientX - drag.startX;
    const dy = e.clientY - drag.startY;
    if (!drag.started) {
      if (Math.hypot(dx, dy) < DRAG_START) return;
      drag.started = true;
      if (drag.kind === "new") {
        const { w, h } = sizeOf(drag.id);
        const s = scale();
        drag.ghost = document.createElement("div");
        drag.ghost.className = "drag-ghost";
        drag.ghost.style.width = `${w * s}px`;
        drag.ghost.style.height = `${h * s}px`;
        drag.ghost.innerHTML = art(drag.id, drag.color);
        document.body.appendChild(drag.ghost);
      } else {
        drag.el.classList.add("dragging");
      }
    }
    if (drag.kind === "new") {
      const box = drag.ghost.getBoundingClientRect();
      drag.ghost.style.transform =
        `translate(${e.clientX - box.width / 2}px, ${e.clientY - box.height / 2}px)`;
    } else {
      drag.el.style.translate = `${dx}px ${dy}px`;
      drag.el.classList.toggle("leaving", !overTable(e.clientX, e.clientY));
    }
  });

  function endDrag(e) {
    if (!drag) return;
    const d = drag;
    drag = null;
    if (d.ghost) d.ghost.remove();
    if (!d.started) return; // just a click: the item stays picked
    const s = scale();
    const box = table.getBoundingClientRect();
    if (d.kind === "new") {
      if (!overTable(e.clientX, e.clientY)) return;
      if (items.length >= max) return;
      const { w, h } = sizeOf(d.id);
      const item = {
        id: d.id, color: d.color, r: 0,
        x: (e.clientX - box.left) / s - w / 2,
        y: (e.clientY - box.top) / s - h / 2,
      };
      clamp(item);
      items.push(item);
      selected = items.length - 1;
      if (window.scenes) window.scenes.play("move");
      changed();
    } else if (!overTable(e.clientX, e.clientY)) {
      selected = d.index;
      remove(); // dragged off the table: put it away
    } else {
      const item = items[d.index];
      item.x += (e.clientX - d.startX) / s;
      item.y += (e.clientY - d.startY) / s;
      clamp(item);
      // the moved item goes on top of the others
      items.push(items.splice(d.index, 1)[0]);
      selected = items.length - 1;
      if (window.scenes) window.scenes.play("move");
      changed();
    }
  }
  document.addEventListener("pointerup", endDrag);
  document.addEventListener("pointercancel", () => {
    if (drag && drag.ghost) drag.ghost.remove();
    drag = null;
    if (table) render();
  });

  // --- Colors and tablecloths ---
  // A swatch changes the color of that menu item (what you'll place next),
  // and of the picked item on the table if it's the same kind of thing.
  function chooseColor(swatch) {
    const id = swatch.dataset.item;
    const color = swatch.dataset.color;
    const button = document.querySelector(`.menu-item[data-item="${id}"]`);
    button.dataset.color = color;
    button.querySelector(".menu-art").innerHTML = art(id, color);
    swatch.parentElement.querySelectorAll(".swatch").forEach((s) =>
      s.classList.toggle("swatch-on", s === swatch));
    if (selected !== null && items[selected].id === id) {
      items[selected].color = color;
      changed();
    }
    if (window.scenes) window.scenes.play("select");
  }

  function chooseCloth(button) {
    table.dataset.cloth = button.dataset.cloth;
    document.querySelectorAll(".cloth-choice").forEach((b) =>
      b.classList.toggle("cloth-on", b === button));
    if (window.scenes) window.scenes.play("select");
    changed();
  }

  // Clear the table, with a moment to change your mind.
  let cleared = null;
  let undoTimer = null;
  function clearTable() {
    if (!items.length) return;
    cleared = items;
    items = [];
    selected = null;
    changed();
    const undo = document.getElementById("undo-clear");
    undo.hidden = false;
    clearTimeout(undoTimer);
    undoTimer = setTimeout(() => { undo.hidden = true; cleared = null; }, 6000);
    if (window.scenes) window.scenes.play("back");
  }
  function undoClear() {
    if (!cleared) return;
    items = cleared;
    cleared = null;
    document.getElementById("undo-clear").hidden = true;
    changed();
  }

  // --- Buttons and keys ---
  document.addEventListener("click", (e) => {
    if (e.target.closest("#rotate-item")) rotate();
    if (e.target.closest("#remove-item")) remove();
    if (e.target.closest("#clear-table")) clearTable();
    if (e.target.closest("#undo-clear")) undoClear();
    const swatch = e.target.closest(".swatch");
    if (swatch) chooseColor(swatch);
    const cloth = e.target.closest(".cloth-choice");
    if (cloth) chooseCloth(cloth);
  });
  document.addEventListener("keydown", (e) => {
    if (!table || e.ctrlKey || e.metaKey || e.altKey) return;
    const key = e.key.toLowerCase();
    if (key === "r") rotate();
    if (key === "delete" || key === "backspace") {
      e.preventDefault();
      remove();
    }
  });

  function setUp() {
    table = document.getElementById("table");
    if (!table) return;
    max = Number(table.dataset.max);
    items = JSON.parse(table.dataset.items || "[]");
    selected = null;
    render();
  }

  setUp();
  document.addEventListener("scene:updated", setUp);

  window.tableEditor = {
    onChange: (fn) => listeners.push(fn),
    items: () => items,
    setItems: (list) => { items = list; selected = null; changed(); },
    setCloth: (cloth) => { table.dataset.cloth = cloth; changed(); },
  };
})();
