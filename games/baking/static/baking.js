// The oven window: the muffins brown as the seconds pass. The timing comes
// from the recipe (through data attributes) and the server measures the real
// time when you take them out; this only shows how they look right now.
(() => {
  const LOOKS = {
    raw: "still raw",
    pale: "pale",
    golden: "golden!",
    brown: "getting dark",
    dark: "burning!",
  };
  let ticker = null;

  function setUp() {
    clearInterval(ticker);
    const oven = document.getElementById("oven");
    if (!oven) return;
    const time = document.getElementById("oven-time");
    const look = document.getElementById("oven-look");
    const n = (key) => Number(oven.dataset[key]);
    const began = performance.now() - n("seconds") * 1000;
    let dinged = false;

    function update() {
      const s = (performance.now() - began) / 1000;
      let stage = "raw";
      if (s >= n("burnt")) stage = "dark";
      else if (s > n("to")) stage = "brown";
      else if (s >= n("from")) stage = "golden";
      else if (s >= n("pale")) stage = "pale";
      oven.dataset.stage = stage;
      if (time) time.textContent = Math.floor(s);
      if (look) look.textContent = LOOKS[stage];
      if (stage === "golden" && !dinged) {
        dinged = true;
        if (window.scenes) window.scenes.play("ding");
      }
    }
    update();
    ticker = setInterval(update, 250);
  }

  setUp();
  document.addEventListener("scene:updated", setUp);
})();
