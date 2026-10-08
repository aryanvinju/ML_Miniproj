let model;
const form = document.getElementById('predict-form');

function probability(values) {
  let z = model.intercept;
  let offset = 0;
  model.numeric.forEach((name, i) => {
    const raw = Number(values.get(name));
    const x = Number.isFinite(raw) ? raw : model.numeric_medians[i];
    z += ((x - model.numeric_means[i]) / model.numeric_scales[i]) * model.coefficients[offset++];
  });
  model.categorical.forEach((name, i) => {
    model.categories[i].forEach(category => {
      z += (values.get(name) === category ? 1 : 0) * model.coefficients[offset++];
    });
  });
  return 1 / (1 + Math.exp(-z));
}

function update() {
  if (!model || !form.reportValidity()) return;
  const p = probability(new FormData(form));
  document.getElementById('probability').textContent = (p * 100).toFixed(1);
  document.getElementById('meter-fill').style.width = `${p * 100}%`;
  document.getElementById('classification').textContent = p >= .5
    ? 'Above the demo decision threshold'
    : 'Below the demo decision threshold';
}

form.addEventListener('submit', event => { event.preventDefault(); update(); });
document.getElementById('reset').addEventListener('click', () => { form.reset(); update(); });
fetch('model.json').then(response => {
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}).then(data => { model = data; update(); }).catch(() => {
  document.getElementById('classification').textContent =
    'Model unavailable. Run the training command in the README, then serve this folder locally.';
});
