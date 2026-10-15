// Pre-fills the quote request from the cart (?items=a,b) and shows a thank-you after sending.
(function () {
  var data = window.NOWAY_PLANS;
  var p = new URLSearchParams(location.search);
  var ids = (p.get('items') || '').split(',').filter(function (id) { return data.plans[id]; });
  if (!ids.length) return;
  var names = ids.map(function (id) { return data.plans[id].name; });
  var subject = document.getElementById('subject');
  if (subject && !subject.value) subject.value = 'Quote request: ' + names.join(', ');
  var hidden = document.getElementById('quote-items');
  if (hidden) hidden.value = ids.join(',');
  var note = document.getElementById('quote-note');
  if (note) { note.textContent = 'Your quote: ' + names.join(', ') + '.'; note.classList.remove('hidden'); }
})();
