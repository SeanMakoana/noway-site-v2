# Noway.net website

## Put it online (GitHub + Netlify)

1. GitHub: open your repo `SeanMakoana/noway-site` > **Add file > Upload files**. Drag in everything from this folder EXCEPT `node_modules`, `dist` and `private-not-deployed`. Same file names overwrite the old ones. Tip: delete old files you no longer use (the repo should match this folder). Click **Commit changes**.
2. Netlify: **Add new site > Import from GitHub** > pick `noway-site`. Settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Functions directory: `netlify/functions`
3. Click **Deploy**. Wait for "Published". Open the link.

## Payments (PayFast)
Until you add keys, checkout runs in SANDBOX (test money only).
Netlify > Site configuration > Environment variables:
- `PAYFAST_MERCHANT_ID`, `PAYFAST_MERCHANT_KEY`, `PAYFAST_PASSPHRASE` (from your PayFast account; turn on subscriptions and set the same passphrase there)
- `PAYFAST_SANDBOX` = `false` (only when going live)
- `SITE_URL` = your final address, e.g. `https://noway.net`
Then redeploy (Deploys > Trigger deploy).

## Emails for forms
Netlify > Forms > Notifications > add your email for the `contact`, `order` and `data-request` forms.

## Go-live checklist
- [ ] Edit the CONFIG block at the top of `build.py`: EMAIL, WHATSAPP, LEGAL_NAME, REG_NUMBER, VAT_NUMBER
- [ ] `info@noway.net` (or your chosen email) really receives mail
- [ ] Have a lawyer read Terms, Refund and Privacy pages
- [ ] Register as Information Officer with the Information Regulator (POPIA)
- [ ] Hosting/maintenance promises (backups, response times, security) are things you can actually deliver
- [ ] PayFast live keys + passphrase set, sandbox off
- [ ] Do one real R150 hosting purchase, then refund it
- [ ] Connect custom domain (Netlify > Domain management)
- [ ] Submit `/sitemap.xml` in Google Search Console
- [ ] Never upload `private-not-deployed/` (Reachr, register, progress pages) to a public site

## Editing
Prices: `plans.json`. Pages/text: `build.py`. Styles: `src/input.css`. Then commit to GitHub; Netlify rebuilds automatically.
