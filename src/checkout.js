(function () {
  var data = window.NOWAY_PLANS;
  var fmt = function (n) { return 'R ' + n.toLocaleString('en-ZA', { maximumFractionDigits: 2 }); };
  var params = new URLSearchParams(location.search);
  var ids = (params.get('items') ? params.get('items').split(',') : window.NOWAY_CART.get()).filter(function (id) { return data.plans[id]; });
  var summary = document.getElementById('order-summary'), form = document.getElementById('checkout-form'), err = document.getElementById('checkout-error');

  if (!ids.length) {
    summary.innerHTML = '<p class="text-brown">Your quote is empty. <a class="link" href="booking.html">Choose a package</a>, <a class="link" href="hosting.html">hosting</a> or <a class="link" href="maintenance.html">maintenance</a> plan to continue.</p>';
    form.classList.add('hidden'); return;
  }

  var plans = ids.map(function (id) { return data.plans[id]; });
  var pkg = plans.filter(function (p) { return p.slot === 'package'; })[0];
  var pri = plans.filter(function (p) { return p.slot === 'priority'; })[0];
  var mon = plans.filter(function (p) { return p.type === 'monthly'; });
  var oneOff = (pkg ? pkg.price * data.depositRate : 0) + (pri ? pri.price : 0);
  var monthly = mon.reduce(function (s, p) { return s + p.price; }, 0);

  function row(a, b, strong) { return '<div class="flex justify-between gap-4' + (strong ? ' font-semibold text-ink border-t border-line pt-2 mt-2' : '') + '"><dt>' + a + '</dt><dd class="whitespace-nowrap">' + b + '</dd></div>'; }
  var h = '<h2 class="text-xl font-semibold mb-3">Your order</h2><dl class="space-y-1 text-brown">';
  if (pkg) { h += row(pkg.name, fmt(pkg.price)); }
  if (pri) { h += row(pri.name, fmt(pri.price)); }
  mon.forEach(function (p) { h += row(p.name + ' (monthly)', fmt(p.price) + '/mo'); });
  h += '</dl><dl class="space-y-1 text-brown mt-4">';
  if (oneOff) {
    h += row('Due today' + (pkg ? ' (50% deposit' + (pri ? ' + priority' : '') + ')' : ''), fmt(oneOff), true);
    if (pkg) h += row('Balance, due before launch', fmt(pkg.price - pkg.price * data.depositRate));
    if (monthly) h += row('Monthly plans (not charged today)', fmt(monthly) + '/mo');
  } else {
    h += row('Due today, then every month', fmt(monthly), true);
  }
  h += '</dl>';
  if (oneOff && monthly) h += '<p class="text-sm text-muted mt-3">Your monthly plan only starts when you set it up. After paying you can start it straight away or when your site is ready. We will remind you.</p>';
  if (!oneOff) h += '<p class="text-sm text-muted mt-3">Recurring subscription. Cancel any time before your next billing date. See the <a class="link" href="refund.html">refund and cancellation policy</a>.</p>';
  h += '<p class="text-sm text-muted mt-3">Prices in South African rand. No hidden fees: the amount above is the amount you pay.</p>';
  summary.innerHTML = h;

  var label = document.getElementById('ref-label');
  label.textContent = monthly && !pkg ? 'Website address (domain) this is for' : (pri && !pkg ? 'Which project is this priority for?' : 'Business or project name');

  document.getElementById('f-items').value = ids.join(',');
  document.getElementById('f-today').value = oneOff || monthly;
  document.getElementById('f-monthly').value = monthly;

  function recordOrder(orderId, f) {
    document.getElementById('f-order').value = orderId;
    var body = new URLSearchParams(new FormData(form)); body.set('form-name', 'order');
    body.delete('agree');
    return fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body.toString() }).catch(function () {});
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault(); err.classList.add('hidden');
    if (!form.reportValidity()) return;
    var b = document.getElementById('pay-btn'); b.disabled = true; b.textContent = 'Redirecting to PayFast...';
    var f = new FormData(form);
    try {
      var res = await fetch('/.netlify/functions/payfast-sign', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: ids, first: f.get('first'), last: f.get('last'), email: f.get('email'), cell: f.get('cell'), ref: f.get('ref'), agree: f.get('agree') === 'on' })
      });
      var out = await res.json();
      if (!res.ok) throw new Error(out.error || 'Something went wrong.');
      await recordOrder(out.orderId);
      var pf = document.createElement('form'); pf.method = 'POST'; pf.action = out.action;
      out.fields.forEach(function (kv) {
        if (kv[1] === '' || kv[1] == null) return;
        var i = document.createElement('input'); i.type = 'hidden'; i.name = kv[0]; i.value = kv[1]; pf.appendChild(i);
      });
      document.body.appendChild(pf); pf.submit();
    } catch (ex) {
      err.textContent = ex.message + ' If this keeps happening, email us and we will sort it out.';
      err.classList.remove('hidden'); b.disabled = false; b.textContent = 'Pay securely with PayFast';
    }
  });
})();
