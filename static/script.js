// ===== Config: change this to your deployed FastAPI URL =====
const API_BASE_URL = "https://carworth-used-car-price-predictor.onrender.com"; 

// Fixed lists (the API has no endpoints for these). Match the values used in your training data.
const FUEL_TYPES = ["Petrol", "Diesel", "CNG", "Electric", "Hybrid", "Hybrid/CNG"];
const TRANSMISSIONS = ["Manual", "Automatic"];
const OWNER_OPTIONS = [
  { value: 1, label: "1 previous owner" },
  { value: 2, label: "2 previous owners" },
  { value: 3, label: "3 previous owners" },
  { value: 4, label: "4 or more" },
];
const OLDEST_YEAR = 2000;

// ===== Elements =====
const $ = (id) => document.getElementById(id);
const el = {
  brand: $("brand"), model: $("model"), variant: $("variant"),
  fuel: $("fuel"), transmission: $("transmission"),
  year: $("year"), km: $("km"), owners: $("owners"),
  form: $("form"), banner: $("banner"), price: $("price"),
  summary: $("summaryList"), resultTitle: $("resultTitle"), resultSub: $("resultSub"),
};
const panes = [...document.querySelectorAll(".pane")];
const stepEls = [...document.querySelectorAll(".step")];
let step = 1;

// ===== Helpers =====
async function api(path, options) {
  const res = await fetch(API_BASE_URL + path, options);
  if (!res.ok) {
    let detail = "";
    try { detail = (await res.json()).detail; } catch (_) {}
    const e = new Error(detail || `Request failed (${res.status})`);
    e.status = res.status;
    throw e;
  }
  return res.json();
}

function fillSelect(select, items, placeholder) {
  select.innerHTML = "";
  select.add(new Option(placeholder, ""));
  items.forEach((i) => {
    const o = typeof i === "object" ? new Option(i.label, i.value) : new Option(i, i);
    select.add(o);
  });
}

function resetSelect(select, placeholder) {
  fillSelect(select, [], placeholder);
  select.disabled = true;
}

function showBanner(msg) { el.banner.textContent = msg; el.banner.hidden = false; }
function hideBanner() { el.banner.hidden = true; }

const inr = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });

// ===== Summary card =====
function selectedText(select) {
  return select.value ? select.options[select.selectedIndex].text : "—";
}
function updateSummary() {
  const km = el.km.value ? Number(el.km.value).toLocaleString("en-IN") + " km" : "—";
  const rows = [
    ["Brand", selectedText(el.brand)], ["Model", selectedText(el.model)],
    ["Variant", selectedText(el.variant)], ["Fuel", selectedText(el.fuel)],
    ["Transmission", selectedText(el.transmission)], ["Year", selectedText(el.year)],
    ["Driven", km], ["Owners", selectedText(el.owners)],
  ];
  el.summary.innerHTML = "";
  rows.forEach(([k, v]) => {
    const row = document.createElement("div");
    const dt = document.createElement("dt"); dt.textContent = k;
    const dd = document.createElement("dd"); dd.textContent = v;
    row.append(dt, dd);
    el.summary.append(row);
  });
}
function clearPrice() { el.price.textContent = "—"; }

// ===== Step navigation =====
function goTo(n) {
  step = n;
  panes.forEach((p) => (p.hidden = Number(p.dataset.pane) !== n));
  stepEls.forEach((s) => {
    const i = Number(s.dataset.step);
    s.classList.toggle("is-active", i === n);
    s.classList.toggle("is-done", i < n);
  });
  const h = panes[n - 1].querySelector("h1");
  if (h) h.focus({ preventScroll: false });
}

function validate(n) {
  let ok = true;
  panes[n - 1].querySelectorAll("[required]").forEach((f) => {
    const field = f.closest(".field");
    const err = field.querySelector(".err");
    let msg = "";
    if (!f.value) msg = f.tagName === "SELECT" ? "Please choose an option." : "Please enter a value.";
    else if (f.type === "number" && Number(f.value) < 0) msg = "Enter a valid number.";
    field.classList.toggle("has-error", !!msg);
    err.textContent = msg;
    if (msg) ok = false;
  });
  if (!ok) panes[n - 1].querySelector(".has-error select, .has-error input")?.focus();
  return ok;
}

// ===== Dependent dropdowns =====
async function loadBrands() {
  try {
    const { brands } = await api("/brands");
    fillSelect(el.brand, brands, "Select brand");
    el.brand.disabled = false;
    hideBanner();
  } catch (e) {
    fillSelect(el.brand, [], "Unavailable");
    showBanner("Couldn't reach the price service. Please check your connection and refresh the page.");
  }
}

async function onBrandChange() {
  resetSelect(el.model, "Select a brand first");
  resetSelect(el.variant, "Select a model first");
  clearPrice(); updateSummary();
  if (!el.brand.value) return;
  fillSelect(el.model, [], "Loading…");
  try {
    const { models } = await api(`/models/${encodeURIComponent(el.brand.value)}`);
    fillSelect(el.model, models, "Select model");
    el.model.disabled = false;
  } catch (e) {
    resetSelect(el.model, "Unavailable");
    showBanner("Couldn't load models. Please try again.");
  }
}

async function onModelChange() {
  resetSelect(el.variant, "Select a model first");
  clearPrice(); updateSummary();
  if (!el.model.value) return;
  fillSelect(el.variant, [], "Loading…");
  const b = encodeURIComponent(el.brand.value), m = encodeURIComponent(el.model.value);
  try {
    let data;
    try {
      data = await api(`/variants/${b}/${m}`);   // preferred: variants for brand + model
    } catch (e) {
      if (e.status !== 404 && e.status !== 405) throw e;
      data = await api(`/variants/${b}`);        // fallback: brand-only endpoint
    }
    fillSelect(el.variant, data.variants, "Select variant");
    el.variant.disabled = false;
  } catch (e) {
    resetSelect(el.variant, "Unavailable");
    showBanner("Couldn't load variants. Please try again.");
  }
}

// ===== Predict =====
async function predict() {
  hideBanner();
  clearPrice();
  goTo(3);
  el.resultTitle.textContent = "Calculating…";
  el.resultSub.textContent = "Hang on, we're checking the numbers.";
  const payload = {
    brand: el.brand.value, model: el.model.value, variant: el.variant.value,
    make_year: Number(el.year.value), km_driven: Number(el.km.value),
    previous_owners: Number(el.owners.value),
    transmission: el.transmission.value, fuel_type: el.fuel.value,
  };
  try {
    const { predicted_price } = await api("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    el.price.textContent = inr.format(predicted_price);
    el.price.parentElement.classList.remove("is-new");
    void el.price.offsetWidth; // restart animation
    el.price.parentElement.classList.add("is-new");
    el.resultTitle.textContent = "Your estimate is ready";
    el.resultSub.textContent = "Based on the details shown. Change any detail to see how the price moves.";
  } catch (e) {
    el.resultTitle.textContent = "We couldn't get an estimate";
    el.resultSub.textContent = e.status === 404
      ? "We don't have this exact combination of variant, fuel type and transmission. Go back and try a different fuel type or transmission."
      : "Something went wrong while contacting the price service. Please try again in a moment.";
  }
}

// ===== Wire up =====
function init() {
  fillSelect(el.fuel, FUEL_TYPES, "Select fuel type");
  fillSelect(el.transmission, TRANSMISSIONS, "Select transmission");
  fillSelect(el.owners, OWNER_OPTIONS, "Select");
  const years = [];
  for (let y = new Date().getFullYear(); y >= OLDEST_YEAR; y--) years.push(y);
  fillSelect(el.year, years, "Select year");

  el.brand.addEventListener("change", onBrandChange);
  el.model.addEventListener("change", onModelChange);
  [el.variant, el.fuel, el.transmission, el.year, el.owners].forEach((f) =>
    f.addEventListener("change", () => { clearPrice(); updateSummary(); }));
  el.km.addEventListener("input", () => { clearPrice(); updateSummary(); });

  // clear a field's error once the user fixes it
  el.form.addEventListener("input", (e) => {
    const field = e.target.closest(".field");
    if (field && e.target.value) { field.classList.remove("has-error"); field.querySelector(".err").textContent = ""; }
  });

  document.querySelector("[data-next]").addEventListener("click", () => { if (validate(1)) goTo(2); });
  document.querySelector("[data-back]").addEventListener("click", () => goTo(1));
  el.form.addEventListener("submit", (e) => { e.preventDefault(); if (validate(2)) predict(); });
  $("editBtn").addEventListener("click", () => goTo(1));
  $("resetBtn").addEventListener("click", () => {
    el.form.reset();
    resetSelect(el.model, "Select a brand first");
    resetSelect(el.variant, "Select a model first");
    clearPrice(); updateSummary(); hideBanner(); goTo(1);
  });

  updateSummary();
  loadBrands();
}
init();
