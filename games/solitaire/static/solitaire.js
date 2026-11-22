// Solitaire input: dragging cards between piles and double-clicking to send
// a card to a foundation. The rules live on the server (logic.py): this
// script only works out which move you meant and sends it. If the move
// isn't allowed, the server sends back the same table and the cards return.
(() => {
  const DRAG_START = 5; // pixels to move before a press becomes a drag

  let drag = null; // { cards, source, index, startX, startY, started }

  function moveForm() { return document.getElementById("sol-move"); }
  function autoForm() { return document.getElementById("sol-auto"); }

  function send(form, field, value) {
    if (!form) return;
    form.querySelector(`[name="${field}"]`).value = value;
    form.requestSubmit(); // scenes.js sends it in the background
  }

  // The card under the pointer plus, on the tableau, every card below it.
  function pickUp(card) {
    const source = card.dataset.src;
    if (!source.startsWith("T")) return [card];
    const index = Number(card.dataset.index);
    return [...card.parentElement.querySelectorAll(".card.face-up")]
      .filter((c) => Number(c.dataset.index) >= index);
  }

  function pileAt(x, y) {
    // look underneath the cards being dragged
    drag.cards.forEach((c) => { c.style.visibility = "hidden"; });
    const under = document.elementFromPoint(x, y);
    drag.cards.forEach((c) => { c.style.visibility = ""; });
    return under && under.closest("[data-drop]");
  }

  function moveFor(target) {
    const to = target.dataset.drop; // "T0".."T6" or "F"
    const { source, index } = drag;
    if (to === source) return null;
    if (to === "F") {
      if (drag.cards.length !== 1 || source.startsWith("F")) return null;
      return `${source}>F`;
    }
    if (source.startsWith("T")) return `${source}:${index}>${to}`;
    return `${source}>${to}`;
  }

  let highlighted = null;
  function highlight(pile) {
    if (pile === highlighted) return;
    if (highlighted) highlighted.classList.remove("drop-target");
    highlighted = pile;
    if (pile) pile.classList.add("drop-target");
  }

  document.addEventListener("pointerdown", (e) => {
    const card = e.target.closest(".card.movable[data-src]");
    if (!card || e.button !== 0) return;
    drag = {
      cards: pickUp(card),
      source: card.dataset.src,
      index: card.dataset.index,
      startX: e.clientX,
      startY: e.clientY,
      started: false,
    };
    card.setPointerCapture(e.pointerId);
  });

  document.addEventListener("pointermove", (e) => {
    if (!drag) return;
    const dx = e.clientX - drag.startX;
    const dy = e.clientY - drag.startY;
    if (!drag.started) {
      if (Math.hypot(dx, dy) < DRAG_START) return;
      drag.started = true;
      drag.cards.forEach((c) => c.classList.add("dragging"));
    }
    drag.cards.forEach((c) => { c.style.transform = `translate(${dx}px, ${dy}px)`; });
    const pile = pileAt(e.clientX, e.clientY);
    highlight(pile && moveFor(pile) ? pile : null);
  });

  function putBack(cards) {
    cards.forEach((c) => {
      c.classList.remove("dragging");
      c.classList.add("returning");
      c.style.transform = "";
      setTimeout(() => c.classList.remove("returning"), 200);
    });
  }

  function endDrag(e, cancelled) {
    if (!drag) return;
    const { cards, started } = drag;
    highlight(null);
    if (started && !cancelled) {
      const pile = pileAt(e.clientX, e.clientY);
      const move = pile && moveFor(pile);
      if (move) {
        drag = null;
        send(moveForm(), "move", move);
        return; // the new table replaces these cards
      }
    }
    drag = null;
    putBack(cards);
  }
  document.addEventListener("pointerup", (e) => endDrag(e, false));
  document.addEventListener("pointercancel", (e) => endDrag(e, true));

  // Double-click a card on the waste or the bottom of a tableau pile to
  // send it to a foundation.
  document.addEventListener("dblclick", (e) => {
    const card = e.target.closest(".card.movable[data-src]");
    if (!card) return;
    const source = card.dataset.src;
    if (source === "W" || source.startsWith("T")) send(autoForm(), "from", source);
  });
})();
