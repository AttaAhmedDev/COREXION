// 3. FILTERS
const filters = document.querySelectorAll(".filter");
const cards = document.querySelectorAll(".insight-card");
const noResult = document.getElementById("noResult");

filters.forEach((filter) => {
  filter.addEventListener("click", () => {
    filters.forEach((f) => f.classList.remove("active"));
    filter.classList.add("active");

    const selected = filter.dataset.filter;
    let visible = 0;

    cards.forEach((card) => {
      const show = selected === "all" || card.dataset.category === selected;
      card.style.display = show ? "" : "none";
      if (show) visible++;
    });

    noResult.style.display = visible ? "none" : "block";
  });
});
