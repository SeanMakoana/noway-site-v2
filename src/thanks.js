// After a successful payment: clear the cart and offer to start any monthly plans.
(function () {
  var data = window.NOWAY_PLANS, p = new URLSearchParams(location.search);
  if (p.get('order')) { try { localStorage.removeItem('noway_cart'); } catch (e) {} }
  var next = (p.get('next') || '').split(',').filter(function (id) { return data.plans[id] && data.plans[id].type === 'monthly'; });
  var box = document.getElementById('next-step');
  if (!next.length || !box) return;
  var total = next.reduce(function (s, id) { return s + data.plans[id].price; }, 0);
  document.getElementById('next-names').textContent = next.map(function (id) { return data.plans[id].name; }).join(' + ') + ' (R ' + total.toLocaleString('en-ZA') + '/month)';
  document.getElementById('next-link').href = 'checkout.html?items=' + encodeURIComponent(next.join(','));
  box.classList.remove('hidden');
})();
