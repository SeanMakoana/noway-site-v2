// Builds a signed PayFast payment request from a cart of plan ids.
// All prices come from plans.json on the server, so a visitor cannot change
// the amount from their browser.
const crypto = require('crypto');
const catalog = require('../../plans.json');

const SANDBOX = { id: '10000100', key: '46f0cd694581a' };

function pfEncode(v) {
  return encodeURIComponent(String(v).trim())
    .replace(/%20/g, '+')
    .replace(/[!'()*~]/g, (c) => '%' + c.charCodeAt(0).toString(16).toUpperCase());
}

function sign(fields, passphrase) {
  let str = fields.filter(([, v]) => v !== '' && v != null).map(([k, v]) => `${k}=${pfEncode(v)}`).join('&');
  if (passphrase) str += `&passphrase=${pfEncode(passphrase)}`;
  return crypto.createHash('md5').update(str).digest('hex');
}

const json = (statusCode, body) => ({ statusCode, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });

// Works out what is charged today and what is a monthly plan.
function priceCart(ids) {
  const list = [...new Set(Array.isArray(ids) ? ids : [])].map((id) => ({ id, ...catalog.plans[id] }));
  if (!list.length || list.length > 4 || list.some((p) => !p.price)) return { error: 'Your cart is empty or has an item we do not recognise.' };
  const slots = list.map((p) => p.slot);
  if (new Set(slots).size !== slots.length) return { error: 'You can only have one item of each kind in your cart.' };
  const by = (s) => list.find((p) => p.slot === s);
  const pkg = by('package'), pri = by('priority'), host = by('hosting'), maint = by('maintenance');
  const oneOff = (pkg ? pkg.price * catalog.depositRate : 0) + (pri ? pri.price : 0);
  const monthlyItems = [host, maint].filter(Boolean);
  const monthly = monthlyItems.reduce((s, p) => s + p.price, 0);
  return { list, pkg, pri, monthlyItems, oneOff, monthly };
}

exports.priceCart = priceCart;

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return json(405, { error: 'Method not allowed' });
  let d;
  try { d = JSON.parse(event.body || '{}'); } catch { return json(400, { error: 'Bad request' }); }

  const first = String(d.first || '').trim().slice(0, 60);
  const last = String(d.last || '').trim().slice(0, 60);
  const email = String(d.email || '').trim().slice(0, 120);
  const cell = String(d.cell || '').replace(/[^\d+]/g, '').slice(0, 15);
  const ref = String(d.ref || '').trim().slice(0, 120);
  if (!first || !last || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return json(400, { error: 'Please enter your name and a valid email address.' });
  if (d.agree !== true) return json(400, { error: 'You must accept the terms to continue.' });

  const cart = priceCart(d.items);
  if (cart.error) return json(400, { error: cart.error });

  const sandbox = process.env.PAYFAST_SANDBOX !== 'false';
  const merchantId = sandbox ? (process.env.PAYFAST_MERCHANT_ID || SANDBOX.id) : process.env.PAYFAST_MERCHANT_ID;
  const merchantKey = sandbox ? (process.env.PAYFAST_MERCHANT_KEY || SANDBOX.key) : process.env.PAYFAST_MERCHANT_KEY;
  if (!merchantId || !merchantKey) return json(500, { error: 'Payments are not configured yet.' });
  const passphrase = process.env.PAYFAST_PASSPHRASE || '';
  const site = (process.env.SITE_URL || 'https://noway.net').replace(/\/$/, '');

  const id = `NW-${Date.now().toString(36).toUpperCase()}-${crypto.randomBytes(2).toString('hex').toUpperCase()}`;
  const subscribeNow = cart.oneOff === 0; // monthly-only cart => start the subscription now
  const next = !subscribeNow && cart.monthlyItems.length ? `&next=${cart.monthlyItems.map((p) => p.id).join(',')}` : '';

  let itemName, desc, amount;
  if (subscribeNow) {
    amount = cart.monthly;
    itemName = cart.monthlyItems.map((p) => p.name).join(' + ');
    desc = 'Monthly subscription';
  } else {
    amount = cart.oneOff;
    const parts = [];
    if (cart.pkg) parts.push(`${cart.pkg.name} (50% deposit)`);
    if (cart.pri) parts.push(cart.pri.name);
    itemName = parts.join(' + ');
    desc = cart.pkg ? `Balance of R${(cart.pkg.price * (1 - catalog.depositRate)).toFixed(2)} due before launch` : 'Once-off payment';
  }

  const fields = [
    ['merchant_id', merchantId],
    ['merchant_key', merchantKey],
    ['return_url', `${site}/thank-you.html?order=${id}${next}`],
    ['cancel_url', `${site}/payment-cancelled.html`],
    ['name_first', first],
    ['name_last', last],
    ['email_address', email],
    ['cell_number', cell],
    ['m_payment_id', id],
    ['amount', amount.toFixed(2)],
    ['item_name', itemName.slice(0, 100)],
    ['item_description', desc.slice(0, 255)],
    ['custom_str1', ref],
    ['custom_str2', cart.list.map((p) => p.id).join(',')],
  ];
  if (subscribeNow) {
    fields.push(['subscription_type', '1'], ['recurring_amount', cart.monthly.toFixed(2)], ['frequency', '3'], ['cycles', '0']);
  }
  fields.push(['signature', sign(fields, passphrase)]);

  return json(200, {
    action: sandbox ? 'https://sandbox.payfast.co.za/eng/process' : 'https://www.payfast.co.za/eng/process',
    fields,
    orderId: id,
    dueToday: amount,
    mode: subscribeNow ? 'subscription' : 'once-off',
  });
};

exports.sign = sign;
