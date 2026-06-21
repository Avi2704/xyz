/* ExoDetect — shared client-side behaviour */
(function () {
  "use strict";

  /* Mobile nav toggle */
  document.addEventListener("click", function (e) {
    var toggle = e.target.closest(".nav-toggle");
    if (toggle) {
      var links = document.querySelector(".nav-links");
      if (links) links.classList.toggle("open");
    }
  });

  /* Active link highlighting based on current file */
  function markActive() {
    var path = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".nav-links a").forEach(function (a) {
      var href = a.getAttribute("href");
      if (href === path || (path === "" && href === "index.html")) {
        a.classList.add("active");
      }
    });
  }

  /* Scroll reveal */
  function setupReveal() {
    var els = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window)) {
      els.forEach(function (el) { el.classList.add("in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    els.forEach(function (el) { io.observe(el); });
  }

  /* Count-up animation for stats */
  function setupCounters() {
    var nums = document.querySelectorAll("[data-count]");
    if (!nums.length) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var target = parseFloat(el.getAttribute("data-count"));
        var suffix = el.getAttribute("data-suffix") || "";
        var decimals = (el.getAttribute("data-decimals")) ? parseInt(el.getAttribute("data-decimals"), 10) : 0;
        var dur = 1400, start = null;
        function step(ts) {
          if (!start) start = ts;
          var p = Math.min((ts - start) / dur, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          var val = target * eased;
          el.textContent = val.toFixed(decimals) + suffix;
          if (p < 1) requestAnimationFrame(step);
          else el.textContent = target.toFixed(decimals) + suffix;
        }
        requestAnimationFrame(step);
        io.unobserve(el);
      });
    }, { threshold: 0.5 });
    nums.forEach(function (n) { io.observe(n); });
  }

  /* Simulated pipeline run (upload page) */
  window.runPipeline = function () {
    var bar = document.getElementById("runBar");
    var log = document.getElementById("runLog");
    var btn = document.getElementById("runBtn");
    if (!bar || !log) return;
    btn && (btn.disabled = true, btn.textContent = "Running…");
    var steps = [
      "Ingesting TESS FITS light curves (sector 41)…",
      "Normalising flux & removing instrumental trends…",
      "Masking outliers (sigma-clip = 5.0)…",
      "Running Box Least Squares period search…",
      "Detecting periodic flux dips (SNR threshold = 7.1)…",
      "Extracting transit features for CNN classifier…",
      "Classifying: transit / eclipse / blend / variable…",
      "Fitting transit model (period, depth, duration)…",
      "Estimating uncertainties via MCMC sampling…",
      "Pipeline complete — 312 candidates flagged."
    ];
    log.innerHTML = "";
    var i = 0;
    var timer = setInterval(function () {
      var pct = Math.round(((i + 1) / steps.length) * 100);
      bar.style.width = pct + "%";
      var line = document.createElement("div");
      line.style.padding = "3px 0";
      line.innerHTML = '<span class="mono" style="color:var(--accent-3)">[' + pct + '%]</span> ' + steps[i];
      log.appendChild(line);
      log.scrollTop = log.scrollHeight;
      i++;
      if (i >= steps.length) {
        clearInterval(timer);
        btn && (btn.disabled = false, btn.textContent = "Run pipeline again");
        var done = document.getElementById("runDone");
        if (done) done.style.display = "flex";
      }
    }, 650);
  };

  /* Year in footer */
  function setYear() {
    document.querySelectorAll("[data-year]").forEach(function (el) {
      el.textContent = new Date().getFullYear();
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    markActive();
    setupReveal();
    setupCounters();
    setYear();
  });
})();
