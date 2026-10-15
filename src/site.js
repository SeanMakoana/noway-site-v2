(function () {
  // Mobile menu
  var btn = document.getElementById('menu-btn');
  var menu = document.getElementById('menu');
  if (btn && menu) {
    btn.addEventListener('click', function () {
      var open = menu.classList.toggle('hidden') === false;
      btn.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.classList.contains('hidden')) {
        menu.classList.add('hidden');
        btn.setAttribute('aria-expanded', 'false');
        btn.focus();
      }
    });
  }

  // Cookie / privacy notice. The site sets no tracking cookies; this records the choice only.
  var KEY = 'noway_cookie_choice';
  var banner = document.getElementById('cookie-banner');
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function show() { if (banner) banner.classList.remove('hidden'); }
  function hide() { if (banner) banner.classList.add('hidden'); }
  if (banner) {
    if (!get()) show();
    document.getElementById('cookie-accept').addEventListener('click', function () { set('accepted'); hide(); });
    document.getElementById('cookie-decline').addEventListener('click', function () { set('essential-only'); hide(); });
  }
  var reopen = document.getElementById('cookie-settings');
  if (reopen) reopen.addEventListener('click', function (e) { e.preventDefault(); show(); });
  // If analytics is ever added, load it only when get() === 'accepted'.
})();
