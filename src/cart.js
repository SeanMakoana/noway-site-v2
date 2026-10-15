// Quote cart. Stores only plan ids in this browser; prices come from plans.js.
(function () {
  var data = window.NOWAY_PLANS, KEY = 'noway_cart';
  var fmt = function (n) { return 'R ' + n.toLocaleString('en-ZA', { maximumFractionDigits: 2 }); };
  window.NOWAY_CART = {
    get: function () {
      try { return (JSON.parse(localStorage.getItem(KEY) || '[]') || []).filter(function (id) { return data.plans[id]; }); } catch (e) { return []; }
    },
    set: function (ids) { try { localStorage.setItem(KEY, JSON.stringify(ids)); } catch (e) {} }
  };

  var toastEl = document.getElementById('toast'), toastTimer;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg; toastEl.classList.remove('hidden');
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { toastEl.classList.add('hidden'); }, 3500);
  }

  function add(id) {
    var p = data.plans[id], cart = window.NOWAY_CART.get();
    if (!p) return;
    var clash = cart.filter(function (c) { return data.plans[c].slot === p.slot; })[0];
    if (clash === id) { toast(p.name + ' is already in your quote.'); return; }
    if (clash) cart.splice(cart.indexOf(clash), 1); // replace same kind of item
    cart.push(id); window.NOWAY_CART.set(cart); render();
    toast(p.name + (clash ? ' replaced ' + data.plans[clash].name + ' in your quote.' : ' added to your quote.'));
  }
  function remove(id) { window.NOWAY_CART.set(window.NOWAY_CART.get().filter(function (c) { return c !== id; })); render(); }

  function priorityRules() {
    var cards = document.querySelectorAll('[data-priority-tier]');
    if (!cards.length) return;
    var pkg = window.NOWAY_CART.get().filter(function (c) { return data.plans[c].slot === 'package'; })[0];
    var tier = pkg ? data.plans[pkg].short : null;
    var warn = document.getElementById('priority-warning');
    if (warn) warn.textContent = tier ? '' : 'No website package in your quote yet. Priority applies to a website project, so we recommend choosing a package first (or tell us which existing project it is for at checkout).';
    cards.forEach(function (card) {
      var ok = !tier || card.getAttribute('data-priority-tier') === tier;
      var b = card.querySelector('[data-add]');
      card.classList.toggle('off', !ok); b.disabled = !ok;
      b.textContent = ok ? 'Add to quote' : 'Not available for your package';
      b.setAttribute('aria-disabled', String(!ok));
    });
  }

  function render() {
    priorityRules();
    var box = document.getElementById('cart'); if (!box) return;
    var ids = window.NOWAY_CART.get();
    box.classList.toggle('hidden', !ids.length);
    document.getElementById('cart-count').textContent = '(' + ids.length + ')';
    var list = document.getElementById('cart-items'); list.innerHTML = '';
    var today = 0, monthly = 0;
    ids.forEach(function (id) {
      var p = data.plans[id];
      if (p.type === 'monthly') monthly += p.price; else today += p.price;
      var li = document.createElement('li'); li.className = 'flex justify-between gap-2';
      var name = document.createElement('span'); name.textContent = p.name + (p.type === 'monthly' ? ' (monthly)' : '');
      var right = document.createElement('span'); right.className = 'whitespace-nowrap';
      right.textContent = fmt(p.price) + ' ';
      var x = document.createElement('button'); x.type = 'button'; x.className = 'text-rust font-bold px-1';
      x.setAttribute('aria-label', 'Remove ' + p.name); x.textContent = '✕';
      x.addEventListener('click', function () { remove(id); });
      right.appendChild(x); li.appendChild(name); li.appendChild(right); list.appendChild(li);
    });
    document.getElementById('cart-total').textContent = fmt(today) + (monthly ? ' + ' + fmt(monthly) + '/mo' : '');
    var q = 'items=' + encodeURIComponent(ids.join(','));
    document.getElementById('cart-checkout').href = 'checkout.html';
    document.getElementById('cart-quote').href = 'contact.html?' + q;
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-add]');
    if (b && !b.disabled) add(b.getAttribute('data-add'));
  });
  var clear = document.getElementById('cart-clear');
  if (clear) clear.addEventListener('click', function () { window.NOWAY_CART.set([]); render(); toast('Quote cleared.'); });
  window.addEventListener('storage', render);
  render();
})();
