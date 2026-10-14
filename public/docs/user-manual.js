/* user manual tabs — moved out of an inline <script> and inline onclick attributes, which
   the CSP (script-src 'self') does not run */
"use strict";
(function () {
  function switchTab(tabId) {
    var panel = document.getElementById(tabId);
    if (!panel || !panel.classList.contains("tab-content")) return;
    var newUrl = window.location.pathname + "?tab=" + encodeURIComponent(tabId);
    window.history.pushState({ path: newUrl }, "", newUrl);
    document.querySelectorAll(".nav-item").forEach(function (n) { n.classList.toggle("active", n.getAttribute("data-tab") === tabId); });
    document.querySelectorAll(".tab-content").forEach(function (t) { t.classList.remove("active"); });
    panel.classList.add("active");
  }
  document.addEventListener("click", function (e) {
    var item = e.target.closest(".nav-item[data-tab]");
    if (!item) return;
    e.preventDefault();
    switchTab(item.getAttribute("data-tab"));
  });
  var tab = new URLSearchParams(window.location.search).get("tab");
  if (tab) switchTab(tab);
})();
