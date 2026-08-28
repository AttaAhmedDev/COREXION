const services = document.querySelectorAll(".service");
services.forEach(function (service) {
  service.addEventListener("mouseenter", function () {
    services.forEach(function (item) {
      item.classList.remove("active");
    });
    service.classList.add("active");
  });
});

// generate floating gold dust particles
const dustEl = document.getElementById("dust");
if (dustEl) {
  const count = 26;
  for (let i = 0; i < count; i++) {
    const s = document.createElement("span");
    const left = Math.random() * 100;
    const dur = 4 + Math.random() * 5;
    const delay = Math.random() * 6;
    const drift = Math.random() * 80 - 40 + "px";
    const size = 2 + Math.random() * 2.5;
    s.style.left = left + "%";
    s.style.width = size + "px";
    s.style.height = size + "px";
    s.style.animationDuration = dur + "s";
    s.style.animationDelay = delay + "s";
    s.style.setProperty("--drift", drift);
    dustEl.appendChild(s);
  }
}

const loaderEl = document.getElementById("loader");
if (loaderEl) {
  setTimeout(function () {
    loaderEl.classList.add("loader-hide");
  }, 4000);
  setTimeout(function () {
    loaderEl.remove();
  }, 4900);
}
