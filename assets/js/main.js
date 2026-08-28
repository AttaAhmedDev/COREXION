// Navigation behaviour only. Page copy and images are rendered server side by
// the cms_* template tags, so there is nothing to fetch here.
(function () {
  function initNav() {
    const toggleWho = document.getElementById("dropdownToggleWho");
    const menuWho = document.getElementById("dropdownMenuWho");
    const toggleExpertise = document.getElementById("dropdownToggleExpertise");
    const menuExpertise = document.getElementById("dropdownMenuExpertise");
    const menuButton = document.getElementById("menuButton");
    const navMenu = document.getElementById("navMenu");
    const navOverlay = document.getElementById("navOverlay");

    if (
      !toggleWho ||
      !menuWho ||
      !toggleExpertise ||
      !menuExpertise ||
      !menuButton ||
      !navMenu
    ) {
      return;
    }

    const isMobile = function () {
      return window.getComputedStyle(menuButton).display !== "none";
    };

    function closeDropdowns() {
      menuWho.classList.remove("open");
      menuExpertise.classList.remove("open");
      toggleWho.classList.remove("open");
      toggleExpertise.classList.remove("open");
    }

    function openMobileMenu() {
      navMenu.classList.add("active", "open");
      if (navOverlay) navOverlay.classList.add("active");
      menuButton.classList.add("active");
      menuButton.setAttribute("aria-expanded", "true");
      document.body.classList.add("nav-open");
    }

    function closeMobileMenu() {
      navMenu.classList.remove("active", "open");
      if (navOverlay) navOverlay.classList.remove("active");
      menuButton.classList.remove("active");
      menuButton.setAttribute("aria-expanded", "false");
      document.body.classList.remove("nav-open");
      closeDropdowns();
    }

    toggleWho.addEventListener("click", function (e) {
      e.preventDefault();
      const shouldOpen = !menuWho.classList.contains("open");
      closeDropdowns();
      if (shouldOpen) {
        menuWho.classList.add("open");
        toggleWho.classList.add("open");
      }
    });

    toggleExpertise.addEventListener("click", function (e) {
      e.preventDefault();
      const shouldOpen = !menuExpertise.classList.contains("open");
      closeDropdowns();
      if (shouldOpen) {
        menuExpertise.classList.add("open");
        toggleExpertise.classList.add("open");
      }
    });

    menuWho.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeDropdowns);
    });
    menuExpertise.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeDropdowns);
    });

    document.addEventListener("click", function (e) {
      if (isMobile()) return;
      const insideWho =
        toggleWho.contains(e.target) || menuWho.contains(e.target);
      const insideExpertise =
        toggleExpertise.contains(e.target) || menuExpertise.contains(e.target);
      if (!insideWho && !insideExpertise) closeDropdowns();
    });

    menuButton.addEventListener("click", function () {
      if (
        navMenu.classList.contains("active") ||
        navMenu.classList.contains("open")
      ) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    });

    if (navOverlay) {
      navOverlay.addEventListener("click", closeMobileMenu);
    }

    document
      .querySelectorAll(".nav-menu a:not(.dropdown-toggle)")
      .forEach(function (link) {
        link.addEventListener("click", function () {
          if (isMobile()) closeMobileMenu();
        });
      });

    window.addEventListener("resize", function () {
      if (!isMobile()) closeMobileMenu();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeMobileMenu();
    });
  }

  document.addEventListener("DOMContentLoaded", initNav);
})();
