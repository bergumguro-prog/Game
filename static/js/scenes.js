// Switching between scenes, plus sound effects. Loaded on every page.
//
// - scenes.goTo(url, sound, style): fade the scene out, then go to `url`. The
//   next page fades in and plays `sound` ("open", "back", "door", ...).
//   style "door" is a plain, slightly slower fade used between rooms.
// - Links (<a href>) to other scenes use the same fade automatically.
// - In a mini-game, Esc goes back to the room.
// - Any element with data-sound="name" plays that sound when the page loads
//   (games use it for "win", "lose", "move", ...).
// - After a form is sent in the background and the new <main> is swapped in,
//   a "scene:updated" event fires on document, so a game's own script can
//   set up the new content (the page's scripts don't run again by themselves).
// - The sound button in the corner mutes/unmutes; the choice is remembered.
(() => {
  const ENTER_KEY = "scene-enter";
  const MUTE_KEY = "sound-muted";
  const cssMs = (name, fallback) => parseFloat(getComputedStyle(document.documentElement)
    .getPropertyValue(name)) || fallback;

  // sessionStorage/localStorage can be unavailable (private mode etc.).
  const store = {
    get(area, key) { try { return window[area].getItem(key); } catch (e) { return null; } },
    set(area, key, value) { try { window[area].setItem(key, value); } catch (e) { /* ignore */ } },
    remove(area, key) { try { window[area].removeItem(key); } catch (e) { /* ignore */ } },
  };

  let muted = store.get("localStorage", MUTE_KEY) === "1";

  function play(name) {
    if (muted || !name) return;
    const audio = new Audio(`/static/sounds/${name}.wav`);
    // Browsers may block sound until the player has clicked or pressed a key.
    audio.play().catch(() => {});
  }

  let leaving = false;
  function goTo(url, sound, style) {
    if (leaving) return;
    leaving = true;
    const door = style === "door";
    store.set("sessionStorage", ENTER_KEY, JSON.stringify({ sound: sound || "", door }));
    document.body.classList.add(door ? "door-leave" : "scene-leave");
    const ms = door ? cssMs("--door-leave-ms", 220) : cssMs("--scene-leave-ms", 200);
    setTimeout(() => { window.location.href = url; }, ms);
  }

  // --- Fade in when we arrived through goTo() ---
  const entered = store.get("sessionStorage", ENTER_KEY);
  if (entered !== null) {
    store.remove("sessionStorage", ENTER_KEY);
    let info;
    try { info = JSON.parse(entered); } catch (e) { info = { sound: entered }; }
    document.body.classList.add(info.door ? "door-enter" : "scene-enter");
    play(info.sound);
  }

  // --- Sounds requested by the page itself ---
  document.querySelectorAll("[data-sound]").forEach((el) => play(el.dataset.sound));

  // --- Game moves without reloading the page ---
  // Every POST form (a move, a guess, "New game") is sent in the background.
  // The server answers with the full page as usual; we swap in its <main>.
  // No flicker, and sounds play reliably because the page never reloads.
  // If anything fails, the form is submitted the normal way instead.
  let busy = false;
  document.addEventListener("submit", async (e) => {
    const form = e.target;
    if (form.method.toLowerCase() !== "post" || form.dataset.noLive) return;
    if (new URL(form.action, window.location.href).origin !== window.location.origin) return;
    e.preventDefault();
    if (busy) return; // ignore double clicks while a move is on its way
    busy = true;
    const submitter = e.submitter;
    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form, submitter), // includes the clicked button's value
      });
      const page = new DOMParser().parseFromString(await response.text(), "text/html");
      const newMain = page.querySelector("main");
      const oldMain = document.querySelector("main");
      if (!response.ok || !newMain || !oldMain) throw new Error("unexpected response");
      document.body.classList.remove("scene-enter", "door-enter"); // don't replay the fade-in
      oldMain.replaceWith(document.adoptNode(newMain));
      if (response.url && response.url !== window.location.href) {
        window.history.replaceState(null, "", response.url);
      }
      newMain.querySelectorAll("[data-sound]").forEach((el) => play(el.dataset.sound));
      document.dispatchEvent(new CustomEvent("scene:updated", { detail: { main: newMain } }));
    } catch (err) {
      form.dataset.noLive = "1";
      form.requestSubmit(submitter);
    } finally {
      busy = false;
    }
  });

  // --- Links to other scenes fade too ---
  document.addEventListener("click", (e) => {
    const link = e.target.closest("a[href]");
    if (!link || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey) return;
    if (link.origin !== window.location.origin || link.target) return;
    e.preventDefault();
    const toRoom = link.pathname === "/";
    goTo(link.href, toRoom ? "back" : "open");
  });

  // --- Esc returns to the room ---
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && document.body.dataset.scene !== "room") {
      goTo("/", "back");
    }
  });

  // --- Mute button ---
  const button = document.getElementById("mute-toggle");
  function showMute() {
    if (!button) return;
    button.setAttribute("aria-pressed", String(muted));
    button.textContent = muted ? "Sound: off" : "Sound: on";
  }
  if (button) {
    button.addEventListener("click", () => {
      muted = !muted;
      store.set("localStorage", MUTE_KEY, muted ? "1" : "0");
      showMute();
      play("select");
      button.blur(); // so Space/Enter don't toggle it again by accident
    });
    showMute();
  }

  window.scenes = { goTo, play };
})();
