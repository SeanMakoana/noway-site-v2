#!/usr/bin/env python3
"""Generates the static Noway.net site into dist/.  Run: npm run build"""
import json, os, re, shutil, datetime, html

# ---------------- CONFIG: edit these, then rebuild ----------------
SITE_URL = "https://noway.net"
BRAND = "Noway.net"
EMAIL = "info@noway.net"   # must be an address you really receive mail on
WHATSAPP = ""              # e.g. "27821234567" (international format, no +). Empty = hidden.
LEGAL_NAME = ""            # e.g. "Sean Makoana t/a Noway.net". Empty = shows just "Noway.net".
REG_NUMBER = ""            # CIPC registration number, if any
VAT_NUMBER = ""            # only if VAT registered
REGION = "Gauteng, South Africa"
UPDATED = "14 October 2026"
YEAR = datetime.date.today().year
# -------------------------------------------------------------------

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
catalog = json.load(open(os.path.join(ROOT, "plans.json")))
P = catalog["plans"]
OWNER = LEGAL_NAME or BRAND
e = html.escape
MAIL = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'

CHECK = '<svg aria-hidden="true" class="w-5 h-5 text-brand mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>'
ARROW = '<svg aria-hidden="true" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>'
ICONS = {
    "design": '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2h-2"/>',
    "hosting": '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/>',
    "maint": '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>',
    "priority": '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>',
}

NAV = [("booking.html", "Booking"), ("hosting.html", "Hosting"), ("maintenance.html", "Maintenance"),
       ("priority.html", "Priority"), ("about.html", "About"), ("contact.html", "Contact"), ("faq.html", "FAQ")]


def money(n):
    return "R " + f"{n:,.0f}"


def nav(current):
    links = "".join(f'<a href="{h}" class="nav-link"{" aria-current=page" if h == current else ""}>{t}</a>' for h, t in NAV)
    return f'''<div class="retro-stripe"></div>
<header class="bg-white/90 backdrop-blur-md border-b border-line sticky top-0 z-40 shadow-sm">
<nav aria-label="Main" class="container mx-auto px-4 py-3 flex items-center justify-between gap-4">
  <a href="index.html" class="flex items-center gap-2 text-xl font-bold tracking-tight text-ink shrink-0">
    <img src="logo.png" alt="" width="32" height="24" class="h-6 w-auto"><span>{BRAND}</span></a>
  <div class="hidden lg:flex items-center flex-1 justify-center gap-1">{links}</div>
  <a href="booking.html" class="btn text-sm !py-1.5 !px-5 hidden lg:inline-flex shrink-0">Start a project</a>
  <button id="menu-btn" type="button" class="lg:hidden p-2 rounded-md text-ink" aria-controls="menu" aria-expanded="false" aria-label="Menu">
    <svg aria-hidden="true" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/></svg></button>
</nav>
<div id="menu" class="hidden lg:hidden border-t border-line bg-white px-4 py-3 flex flex-col">{links}<a href="booking.html" class="btn mt-3">Start a project</a></div>
</header>'''


def cart_widget():
    return '''<aside id="cart" aria-label="Your quote" class="hidden fixed bottom-4 right-4 z-30 bg-paper rounded-[28px] shadow-2xl border border-line p-5 w-[min(20rem,calc(100vw-2rem))]">
  <h2 class="text-sm font-semibold mb-2">Your quote <span id="cart-count">(0)</span></h2>
  <ul id="cart-items" class="text-xs text-brown space-y-1 max-h-48 overflow-y-auto mb-2"></ul>
  <p class="font-bold border-t border-line pt-2 text-sm">Total: <span id="cart-total">R 0</span></p>
  <button id="cart-clear" type="button" class="text-rust text-xs underline mt-1">Clear all</button>
  <div class="grid gap-2 mt-3"><a id="cart-checkout" href="checkout.html" class="btn !py-2 text-sm">Checkout</a>
  <a id="cart-quote" href="contact.html" class="btn-outline !py-1.5 text-sm">Request a quote instead</a></div>
</aside>'''


def footer(cart):
    contact = f'<a class="underline hover:text-rust" href="mailto:{EMAIL}">{EMAIL}</a>'
    if WHATSAPP:
        contact += f' &middot; <a class="underline hover:text-rust" href="https://wa.me/{WHATSAPP}" rel="noopener">WhatsApp</a>'
    bits = [e(OWNER)]
    if REG_NUMBER: bits.append(f"Reg. {e(REG_NUMBER)}")
    if VAT_NUMBER: bits.append(f"VAT {e(VAT_NUMBER)}")
    bits.append(REGION)
    lnk = "hover:text-rust underline"
    return f'''<footer class="bg-white/80 border-t border-line py-10 mt-auto">
<div class="container mx-auto px-4 text-center text-sm text-brown space-y-3">
  <div class="retro-stripe w-28 mx-auto mb-5 rounded-full"></div>
  <p>{" &middot; ".join(bits)}</p><p>{contact}</p>
  <p class="space-x-4"><a class="{lnk}" href="privacy.html">Privacy Policy</a><a class="{lnk}" href="terms.html">Terms of Service</a><a class="{lnk}" href="refund.html">Refund Policy</a><a class="{lnk}" href="cookies.html">Cookie Policy</a><a class="{lnk}" href="data-request.html">Data Request</a><a class="{lnk}" href="#" id="cookie-settings">Cookie settings</a></p>
  <p>Payments are processed securely by PayFast. We never see or store your card details.</p>
  <p>&copy; {YEAR} {BRAND}. All rights reserved.</p>
</div></footer>
<div id="toast" role="status" aria-live="polite" class="hidden fixed top-20 left-1/2 -translate-x-1/2 z-50 bg-ink text-white text-sm rounded-full px-5 py-2 shadow-xl"></div>
{cart_widget() if cart else ""}
<div id="cookie-banner" role="region" aria-label="Cookie notice" class="hidden fixed bottom-0 inset-x-0 z-50 bg-white border-t border-line shadow-2xl p-4">
  <div class="container mx-auto flex flex-col md:flex-row md:items-center gap-4">
    <p class="text-sm text-ink flex-1">This site only uses what it needs to work and to remember this choice. We don't run advertising or tracking cookies. If we add analytics later, it will only switch on if you accept. <a class="link" href="cookies.html">Cookie Policy</a></p>
    <div class="flex gap-3"><button id="cookie-decline" type="button" class="btn-outline">Essential only</button><button id="cookie-accept" type="button" class="btn-outline">Accept</button></div>
  </div></div>'''


def page(fname, title, desc, body, current=None, scripts=(), noindex=False, schema=False, cart=False, need_plans=False):
    canon = f"{SITE_URL}/" if fname == "index.html" else f"{SITE_URL}/{fname}"
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex else ""
    ld = ""
    if schema:
        ld = '<script type="application/ld+json">' + json.dumps({
            "@context": "https://schema.org", "@type": "ProfessionalService", "name": BRAND, "url": SITE_URL,
            "email": EMAIL, "description": desc, "areaServed": "ZA",
            "address": {"@type": "PostalAddress", "addressRegion": "Gauteng", "addressCountry": "ZA"}}) + "</script>"
    allscripts = ["site.js"]
    if cart or need_plans: allscripts.insert(0, "plans.js")
    if cart: allscripts.append("cart.js")
    allscripts += list(scripts)
    if any(s in allscripts for s in ("checkout.js", "contact.js", "thanks.js")) and "plans.js" not in allscripts: allscripts.insert(0, "plans.js")
    if "checkout.js" in allscripts and "cart.js" not in allscripts: allscripts.insert(allscripts.index("checkout.js"), "cart.js")
    js = "".join(f'<script src="{s}" defer></script>' for s in dict.fromkeys(allscripts))
    full_title = title if title.startswith(BRAND) else f"{title} | {BRAND}"
    doc = f'''<!DOCTYPE html>
<html lang="en-ZA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
{robots}
<meta property="og:title" content="{e(full_title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{canon}">
<meta name="theme-color" content="#c13b1b">
<link rel="icon" href="favicon.png" type="image/png">
<link rel="preload" href="fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="styles.css">
{ld}
</head>
<body class="min-h-screen flex flex-col">
<a href="#main" class="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-white focus:p-3 focus:m-2 focus:rounded">Skip to content</a>
{nav(current)}
<main id="main" class="flex-grow">
{body}
</main>
{footer(cart)}
{js}
</body></html>'''
    open(os.path.join(DIST, fname), "w", encoding="utf-8").write(doc)


def heading(h1, sub, tag="h1"):
    return f'<div class="text-center mb-12 max-w-2xl mx-auto"><{tag} class="text-4xl md:text-5xl font-bold tracking-tight mb-5">{h1}</{tag}><p class="text-lg text-brown leading-relaxed">{sub}</p></div>'


def wrap(inner, cls="py-16"):
    return f'<section class="container mx-auto px-4 {cls}">{inner}</section>'


def consult(title, text, btn):
    return f'<div class="text-center mt-20"><div class="max-w-2xl mx-auto bg-white/40 rounded-3xl p-8 border-2 border-dashed border-line"><h2 class="text-2xl font-semibold mb-4">{title}</h2><p class="text-lg text-brown mb-6">{text}</p><a href="contact.html" class="btn text-lg px-8 py-3">{btn} {ARROW}</a></div></div>'


def tier(key, desc, feats, priority=False, note=""):
    p = P[key]
    suffix = ' <span class="text-lg font-normal text-brown">/month</span>' if p["type"] == "monthly" else ""
    li = "".join(f'<li class="flex items-start">{CHECK}<span>{f}</span></li>' for f in feats)
    attr = f' data-priority-tier="{p["short"]}"' if priority else ""
    n = f'<p class="text-sm text-muted -mt-4 mb-6">{note}</p>' if note else ""
    return f'''<div class="retro-card p-8 justify-between"{attr}><div>
<h3 class="text-3xl font-bold mb-2">{p["short"] + " Priority" if priority else p["name"] if p["slot"] != "package" else p["short"] + " Package"}</h3>
<p class="text-brown mb-4">{desc}</p><p class="text-5xl font-semibold mb-6">{money(p["price"])}{suffix}</p>{n}
<ul class="text-left text-brown space-y-2 mb-8">{li}</ul></div>
<button type="button" data-add="{key}" class="btn w-full">Add to quote</button></div>'''


def grid(cols, items, cls=""):
    c = {2: "md:grid-cols-2 max-w-4xl mx-auto", 3: "md:grid-cols-3"}[cols]
    return f'<div class="grid {c} gap-8 {cls}">{"".join(items)}</div>'


# ---------------- pages ----------------
def build_pages():
    # HOME
    svc = [("Web Design", f"Custom websites from {money(P['bronze']['price'])}. Bronze, Silver and Gold packages.", "booking.html", "design"),
           ("Hosting", f"Reliable hosting from {money(P['hosting-basic']['price'])}/month with SSL and email.", "hosting.html", "hosting"),
           ("Maintenance", "Updates, security checks and support so your site stays healthy.", "maintenance.html", "maint"),
           ("Priority Service", "Need it sooner? Move your project up the queue.", "priority.html", "priority")]
    cards = "".join(f'''<a href="{h}" class="group block h-full"><div class="retro-card p-6"><div class="w-12 h-12 bg-line rounded-[20px] flex items-center justify-center mb-5 group-hover:bg-rust transition-colors"><svg aria-hidden="true" class="w-6 h-6 text-ink group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">{ICONS[i]}</svg></div><h2 class="text-xl font-semibold mb-2 tracking-tight">{t}</h2><p class="text-brown text-sm leading-relaxed">{d}</p></div></a>''' for t, d, h, i in svc)
    steps = [("Pick your services", "Add a package, hosting or maintenance to your quote. Prices are shown up front."),
             ("Pay a 50% deposit", "Secure checkout with PayFast, or request a quote first if you'd rather talk."),
             ("Review and refine", "See the design, give feedback, and use the revision rounds in your package."),
             ("Balance and launch", "Pay the remaining 50% and we take your site live.")]
    sh = "".join(f'<li class="bg-paper rounded-3xl border border-line p-6"><span class="inline-flex w-9 h-9 items-center justify-center rounded-full bg-rust text-white font-semibold mb-3" aria-hidden="true">{i+1}</span><h3 class="font-semibold mb-1">{t}</h3><p class="text-sm text-brown">{d}</p></li>' for i, (t, d) in enumerate(steps))
    body = f'''<div class="container mx-auto px-4 pt-20 pb-8 md:pt-28 text-center"><div class="max-w-3xl mx-auto">
<h1 class="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-[1.1]">Crafting Digital Experiences<br><span class="text-rust">built with care</span></h1>
<p class="text-lg md:text-xl text-brown mb-10 max-w-2xl mx-auto leading-relaxed">Beautifully designed, properly built websites for South African businesses, with clear prices and secure online payment. Let's bring your vision to life.</p>
<a href="booking.html" class="btn text-lg px-8 py-3">Start Your Project {ARROW}</a></div>
<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-7 mt-20 text-left">{cards}</div></div>
<section class="container mx-auto px-4 py-16"><h2 class="text-3xl md:text-4xl font-bold text-center mb-10">How it works</h2><ol class="grid md:grid-cols-4 gap-6 list-none">{sh}</ol></section>'''
    page("index.html", f"{BRAND} - Web design, hosting and maintenance",
         "Custom websites, hosting and maintenance for South African businesses. Clear prices and secure online payment.", body, schema=True, need_plans=True)

    # BOOKING
    b = [tier("bronze", "Ideal for personal blogs, small business landing pages or portfolio sites.", ["Custom design (1-2 pages)", "Mobile responsiveness", "Basic SEO setup", "1 revision round"], note="50% deposit to start"),
         tier("silver", "Perfect for growing businesses, online stores and service providers.", ["Custom design (up to 5 pages)", "Advanced mobile responsiveness", "Enhanced SEO and analytics setup", "Contact forms and integrations", "2 revision rounds"], note="50% deposit to start"),
         tier("gold", "For ambitious projects, large online stores and complex web apps.", ["Unlimited custom pages", "E-commerce functionality", "Advanced integrations (APIs, CRM)", "Content management system (CMS)", "Priority support and 3 revision rounds"], note="50% deposit to start")]
    body = wrap(heading("Choose Your Project Tier", "Select the tier that fits your project's scope. Add hosting, maintenance and priority to your quote too, then check out or request a quote.", "h1") + grid(3, b)
                + '<p class="text-center text-sm text-muted mt-8">Prices in South African rand. Third-party costs such as domain registration, premium plugins or paid stock images are quoted and agreed before anything is bought. See the <a class="link" href="terms.html">terms</a>.</p>'
                + consult("Not sure which tier is right for you?", "Tell us about your project and we'll help you choose the right solution for your needs and budget.", "Book a consultation"))
    page("booking.html", "Website packages and pricing", "Bronze, Silver and Gold website packages from R3,500. Pay a 50% deposit securely online to start your project.", body, "booking.html", cart=True)

    # HOSTING
    h = [tier("hosting-basic", "Perfect for personal websites, blogs and small portfolios.", ["10 GB SSD storage", "5 email accounts", "Free SSL certificate", "Basic DDoS protection", "Weekly backups"]),
         tier("hosting-pro", "Ideal for growing businesses and online stores.", ["50 GB SSD storage", "Unlimited email accounts*", "Free SSL certificate", "Daily backups with easy restore", "Priority email and chat support"]),
         tier("hosting-enterprise", "For large applications and sites that need more.", ["Unlimited SSD storage*", "Dedicated IP address", "Advanced firewall and DDoS protection", "Hourly backups and disaster recovery", "Priority phone and chat support (business hours)"])]
    body = wrap(heading("Hosting Plans", "Reliable, fast and secure hosting for your website. We monitor your site and respond quickly if something goes wrong.") + grid(3, h)
                + '<p class="text-center text-sm text-muted mt-8">*Unlimited items are subject to fair use. Support is provided on business days. We do not guarantee uninterrupted service unless agreed in writing. See the <a class="link" href="terms.html">terms</a>.</p>'
                + consult("Need a custom hosting solution?", "Contact us for dedicated servers, VPS or tailored plans.", "Contact us"))
    page("hosting.html", "Website hosting plans", "Monthly website hosting from R150 with SSL and email. South African web hosting with secure online payment.", body, "hosting.html", cart=True)

    # MAINTENANCE
    m = [tier("maintenance-weekly", "Intensive care for busy sites, online stores and sites that change often.",
              ["Weekly core and plugin updates", "Weekly security scans and malware cleanup if found", "Daily automated backups with offsite storage", "Priority support (target response within 4 business hours)", "Weekly performance and SEO reports", "Uptime monitoring with alerts"]),
         tier("maintenance-monthly", "Essential care for small to medium websites, blogs and portfolios.",
              ["Monthly core and plugin updates", "Security scans and malware cleanup if found", "Weekly backups (30-day retention)", "Email support (target response within 2 business days)", "Monthly performance report", "Uptime monitoring"])]
    body = wrap(heading("Maintenance Plans", "Keep your website secure, updated and performing at its best. Choose the frequency that fits your needs.") + grid(2, m)
                + '<p class="text-center text-sm text-muted mt-8">Monthly subscriptions. Cancel any time before your next billing date. Response times are targets on business days. See the <a class="link" href="refund.html">cancellation policy</a>.</p>'
                + consult("Need a custom maintenance schedule?", "Contact us to discuss tailored plans, one-time fixes or emergency support.", "Contact us"))
    page("maintenance.html", "Website maintenance plans", "Website maintenance from R500 a month: updates, security scans, backups and support.", body, "maintenance.html", cart=True)

    # PRIORITY
    pr = [tier("priority-bronze", "Ideal for small projects needing a faster start.", ["Moved to the front of the queue", "Earlier start date confirmed in writing", "Progress updates by email"], True),
          tier("priority-silver", "Perfect for growing businesses with moderate urgency.", ["Moved to the front of the queue", "Earlier start date confirmed in writing", "Faster review turnaround", "Status calls on request"], True),
          tier("priority-gold", "For projects where timing matters most.", ["Top of the queue", "Earlier start date confirmed in writing", "Direct line to the person building your site", "Post-launch check-in included"], True)]
    body = wrap(heading("Priority Service", "Accelerate your project. The tier you can buy depends on your chosen website package. Dates are confirmed in writing before you pay.")
                + '<p id="priority-warning" role="status" class="text-rust mb-6 text-center text-sm font-medium"></p>' + grid(3, pr)
                + '<p class="text-center text-sm text-muted mt-8 max-w-3xl mx-auto">Priority is an add-on to a booked project and is paid once. See the <a class="link" href="refund.html">refund policy</a>.</p>'
                + consult("Need a custom priority arrangement?", "Contact us for a personalised quote tailored to your timeline.", "Contact us"))
    page("priority.html", "Priority service", "Add priority scheduling to your website project for a once-off fee.", body, "priority.html", cart=True)

    # ABOUT
    vals = [("Our Mission", "To craft innovative, user-friendly web solutions that help businesses grow, strengthen their brand and give their customers a smooth experience."),
            ("Our Vision", "To be a web design and development partner that businesses trust for creativity, technical quality and a genuine commitment to their success."),
            ("Our Values", "<ul class='text-left space-y-1'><li>&#10003; Innovation</li><li>&#10003; Quality</li><li>&#10003; Collaboration</li><li>&#10003; Integrity</li></ul>")]
    vh = "".join(f'<div class="retro-card p-6 text-center"><h2 class="text-xl font-bold mb-3">{t}</h2><div class="text-brown">{d}</div></div>' for t, d in vals)
    body = wrap(heading("Our Journey in Digital Creation", f"Welcome to {BRAND}! We started with a simple idea: to give businesses and individuals a strong, professional online presence. We build, host and look after websites for clients across South Africa from {REGION}.")
                + f'<div class="grid md:grid-cols-3 gap-8 mb-16 max-w-4xl mx-auto">{vh}</div><div class="text-center"><a href="booking.html" class="btn text-lg px-8 py-3">Start Your Project {ARROW}</a></div>', "py-16 max-w-5xl")
    page("about.html", "About", f"{BRAND} is a web design and development business based in {REGION}.", body, "about.html", need_plans=True)

    # CONTACT
    wa = f'<p class="text-brown mb-6">Prefer WhatsApp? <a class="link" href="https://wa.me/{WHATSAPP}" rel="noopener">Message us</a>.</p>' if WHATSAPP else ""
    body = wrap(f'''<div class="max-w-4xl mx-auto bg-paper border border-line rounded-[32px] p-6 md:p-10">
<h1 class="text-3xl font-bold text-center mb-2">Get in Touch / Request a Quote</h1>
<p class="text-center text-brown mb-2">We aim to reply within 1-2 business days. You can also email <a class="link" href="mailto:{EMAIL}">{EMAIL}</a>.</p>{wa}
<p id="quote-note" class="hidden text-center font-semibold text-ink mb-6"></p>
<form name="contact" method="POST" action="thank-you.html?form=contact" data-netlify="true" netlify-honeypot="bot-field" class="space-y-5">
<input type="hidden" name="form-name" value="contact"><input type="hidden" name="quote-items" id="quote-items">
<p class="hidden"><label>Leave this empty: <input name="bot-field"></label></p>
<div><label for="name" class="block text-sm font-medium mb-1">Your name *</label><input class="form-input" type="text" id="name" name="name" required autocomplete="name" maxlength="100"></div>
<div><label for="email" class="block text-sm font-medium mb-1">Email *</label><input class="form-input" type="email" id="email" name="email" required autocomplete="email" maxlength="120"></div>
<div><label for="bizType" class="block text-sm font-medium mb-1">Business type <span class="font-normal text-muted">(optional)</span></label><input class="form-input" type="text" id="bizType" name="business-type" placeholder="e.g. Coffee shop, Clothing brand" maxlength="100"></div>
<div><label for="subject" class="block text-sm font-medium mb-1">Subject *</label><input class="form-input" type="text" id="subject" name="subject" required maxlength="150"></div>
<div><label for="message" class="block text-sm font-medium mb-1">Message *</label><textarea class="form-input" id="message" name="message" rows="5" required maxlength="3000"></textarea></div>
<div class="flex items-start gap-3"><input class="mt-1 w-5 h-5" type="checkbox" id="consent" name="consent" required><label for="consent" class="text-sm text-brown">I agree that {e(OWNER)} may use my details to reply to this enquiry, as described in the <a class="link" href="privacy.html" target="_blank" rel="noopener">Privacy Policy</a>. This does not sign me up to any marketing.</label></div>
<button type="submit" class="btn w-full">Send request</button></form></div>''', "py-12")
    page("contact.html", "Contact and quote requests", "Contact Noway.net or request a quote for a website project, hosting or maintenance.", body, "contact.html", scripts=("contact.js",))

    # FAQ
    A = lambda h, t: f'<a class="link" href="{h}">{t}</a>'
    faqs = [
        ("What services does Noway.net offer?", "Custom websites, e-commerce, SEO setup, hosting, maintenance and priority scheduling."),
        ("How long does it take to build a website?", "It depends on scope and how quickly content and feedback come back. As a guide: Bronze 2-4 weeks, Silver 4-8 weeks, Gold 8-12+ weeks. We confirm a timeline before you pay."),
        ("Do I need an account?", "No. Add what you want to your quote, then check out or request a quote. There is nothing to sign up for."),
        ("How does payment work?", "Website projects: a 50% deposit at checkout and the balance before launch. Priority is paid once. Hosting and maintenance are monthly subscriptions. Payments go through PayFast's secure checkout."),
        ("Which payment methods can I use?", "Whatever PayFast offers on its checkout page, such as cards and instant EFT. We never see or store your card details."),
        ("Do you offer maintenance after launch?", "Yes. Monthly maintenance (R500/month) and Weekly maintenance (R1,200/month) cover updates, security scans, backups and support."),
        ("Can I update content myself?", "The Gold package includes a content management system (CMS) such as WordPress for easy content management."),
        ("What is Priority Service?", "An optional once-off fee that moves your project up our queue: Bronze R2,000, Silver R1,500, Gold R1,000. Delivery dates are confirmed in writing before you pay."),
        ("Do you provide hosting?", "Yes: Basic (R150/month), Pro (R300/month) and Enterprise (R750/month). Cancel any time before your next billing date."),
        ("What is your revision policy?", "Bronze includes 1 revision round, Silver 2 and Gold 3. Extra revisions are quoted at an hourly rate before any work is done."),
        ("What is your refund policy?", f"Deposits are refundable before work starts; after that you pay for work done. Read the full {A('refund.html', 'refund policy')}."),
        ("Who owns my website?", "Once your project is paid in full, you own the custom design and content we create. Third-party items such as fonts, plugins and stock images stay under their own licences."),
        ("Do you help with SEO?", "Our packages include SEO setup such as page structure, titles and descriptions. We cannot promise specific search rankings."),
        ("Can I see examples of your work?", f"Send us a message and we'll share examples relevant to your industry. {A('contact.html', 'Contact us')}."),
        ("Do you work with clients outside South Africa?", "Yes, we work remotely. Prices are in South African rand."),
        ("How is my personal information handled?", f"In line with South Africa's Protection of Personal Information Act (POPIA). See the {A('privacy.html', 'Privacy Policy')} or use the {A('data-request.html', 'data request form')} to access, correct or delete your information."),
    ]
    items = "".join(f'<details class="faq-item bg-paper border border-line rounded-[20px] mb-4"><summary>{q}</summary><div class="p-4 text-brown">{a}</div></details>' for q, a in faqs)
    body = wrap(heading("Frequently Asked Questions", "Find answers about our web design, hosting, maintenance and payments.") + f'<div class="max-w-3xl mx-auto">{items}</div><div class="text-center mt-12"><h2 class="text-xl font-semibold mb-3">Still have questions?</h2><a href="contact.html" class="btn">Contact us {ARROW}</a></div>', "py-12")
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in faqs]}
    body += '<script type="application/ld+json">' + json.dumps(ld) + "</script>"
    page("faq.html", "FAQ", "Answers about website packages, payments, hosting, maintenance, revisions and refunds.", body, "faq.html")

    # CHECKOUT
    body = '''<section class="max-w-2xl mx-auto px-4 py-12 md:py-16">
<h1 class="text-3xl font-bold mb-6">Checkout</h1>
<div id="order-summary" class="bg-paper rounded-3xl border border-line p-6 mb-8"></div>
<form id="checkout-form" name="order" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="bg-paper rounded-3xl border border-line p-6 space-y-5" novalidate>
<input type="hidden" name="form-name" value="order"><input type="hidden" name="items" id="f-items"><input type="hidden" name="due-today" id="f-today"><input type="hidden" name="monthly-total" id="f-monthly"><input type="hidden" name="order-id" id="f-order">
<p class="hidden"><label>Leave this empty: <input name="bot-field"></label></p>
<h2 class="text-xl font-semibold">Your details</h2>
<div class="grid sm:grid-cols-2 gap-4">
<div><label for="first" class="block text-sm font-medium mb-1">First name</label><input class="form-input" id="first" name="first" required autocomplete="given-name" maxlength="60"></div>
<div><label for="last" class="block text-sm font-medium mb-1">Last name</label><input class="form-input" id="last" name="last" required autocomplete="family-name" maxlength="60"></div></div>
<div><label for="email" class="block text-sm font-medium mb-1">Email address</label><input class="form-input" type="email" id="email" name="email" required autocomplete="email" maxlength="120"></div>
<div><label for="cell" class="block text-sm font-medium mb-1">Mobile number <span class="font-normal text-muted">(optional)</span></label><input class="form-input" type="tel" id="cell" name="cell" autocomplete="tel" maxlength="20"></div>
<div><label for="ref" id="ref-label" class="block text-sm font-medium mb-1">Business or project name</label><input class="form-input" id="ref" name="ref" maxlength="120"></div>
<div class="flex items-start gap-3"><input class="mt-1 w-5 h-5" type="checkbox" id="agree" name="agree" required>
<label for="agree" class="text-sm text-brown">I have read and agree to the <a class="link" href="terms.html" target="_blank" rel="noopener">Terms of Service</a> and <a class="link" href="refund.html" target="_blank" rel="noopener">Refund Policy</a>, and I consent to my details being processed as set out in the <a class="link" href="privacy.html" target="_blank" rel="noopener">Privacy Policy</a>. I am 18 or older.</label></div>
<p id="checkout-error" role="alert" class="hidden text-red-800 bg-red-50 border border-red-200 rounded-2xl p-3 text-sm"></p>
<button id="pay-btn" type="submit" class="btn w-full text-lg">Pay securely with PayFast</button>
<p class="text-xs text-muted">You will be taken to PayFast to complete payment. Your name, email and mobile number are shared with PayFast for this purpose only. Prefer to talk first? <a class="link" href="contact.html">Request a quote instead</a>.</p>
</form></section>'''
    page("checkout.html", "Checkout", "Secure checkout.", body, scripts=("checkout.js",), noindex=True)

    # THANK YOU / CANCELLED / 404
    body = '''<section class="max-w-2xl mx-auto px-4 py-20 text-center"><h1 class="text-4xl font-bold mb-4">Thank you!</h1>
<p class="text-lg text-brown mb-8">If you just paid, PayFast has emailed you a receipt and we'll contact you within 1 business day to get started. If you sent a message, we'll reply within 1-2 business days.</p>
<div id="next-step" class="hidden bg-paper border border-line rounded-3xl p-6 mb-8 text-left"><h2 class="text-xl font-semibold mb-2">Next step: your monthly plan</h2><p class="text-brown mb-4"><span id="next-names"></span> isn't charged until you start it. Start it now, or when your site is ready (we'll remind you).</p><a id="next-link" class="btn" href="checkout.html">Set up monthly plan</a></div>
<a class="btn-outline" href="index.html">Back to home</a></section>'''
    page("thank-you.html", "Thank you", "Thank you.", body, scripts=("thanks.js",), noindex=True)
    page("payment-cancelled.html", "Payment cancelled", "Payment cancelled.", '<section class="max-w-2xl mx-auto px-4 py-20 text-center"><h1 class="text-4xl font-bold mb-4">Payment cancelled</h1><p class="text-lg text-brown mb-8">No payment was taken. Your quote is still saved in this browser, so you can pick up where you left off.</p><a class="btn" href="checkout.html">Back to checkout</a></section>', scripts=(), noindex=True)
    page("404.html", "Page not found", "Page not found.", '<section class="max-w-2xl mx-auto px-4 py-20 text-center"><h1 class="text-4xl font-bold mb-4">Page not found</h1><p class="text-lg text-brown mb-8">That page doesn\'t exist. Try the <a class="link" href="index.html">home page</a> or <a class="link" href="contact.html">contact us</a>.</p></section>', noindex=True)

    # DATA REQUEST
    body = wrap(heading("Data request", "Ask to see, correct or delete the personal information we hold about you, or object to how we use it (your rights under POPIA).") + f'''
<div class="max-w-xl mx-auto bg-paper p-8 rounded-3xl border border-line">
<form name="data-request" method="POST" action="thank-you.html?form=data-request" data-netlify="true" netlify-honeypot="bot-field" class="space-y-5">
<input type="hidden" name="form-name" value="data-request"><p class="hidden"><label>Leave this empty: <input name="bot-field"></label></p>
<div><label for="dr-name" class="block text-sm font-medium mb-1">Your name</label><input class="form-input" id="dr-name" name="name" required autocomplete="name"></div>
<div><label for="dr-email" class="block text-sm font-medium mb-1">Email address we hold for you</label><input class="form-input" type="email" id="dr-email" name="email" required autocomplete="email"></div>
<fieldset><legend class="block text-sm font-medium mb-2">What would you like to do?</legend><div class="space-y-2 text-brown">
<label class="flex items-center gap-2"><input type="radio" name="request" value="access" required> Get a copy of my information</label>
<label class="flex items-center gap-2"><input type="radio" name="request" value="correct"> Correct my information</label>
<label class="flex items-center gap-2"><input type="radio" name="request" value="delete"> Delete my information</label>
<label class="flex items-center gap-2"><input type="radio" name="request" value="object"> Object to how it is used</label></div></fieldset>
<div><label for="dr-details" class="block text-sm font-medium mb-1">Details <span class="font-normal text-muted">(optional)</span></label><textarea class="form-input" id="dr-details" name="details" rows="4" maxlength="2000"></textarea></div>
<div class="flex items-start gap-3"><input class="mt-1 w-5 h-5" type="checkbox" id="dr-confirm" name="confirm" required><label for="dr-confirm" class="text-sm text-brown">I confirm this request is about my own information. We may ask you to verify your identity before acting on it.</label></div>
<button class="btn w-full" type="submit">Submit request</button></form>
<p class="text-sm text-muted mt-4">We aim to respond within 30 days. You can also email {MAIL}. Some records (such as invoices) must be kept by law and can't be deleted until the retention period ends.</p></div>''', "py-12")
    page("data-request.html", "Data request", "Request access to, correction or deletion of your personal information held by Noway.net.", body)


# ---------------- legal ----------------
def legal(fname, title, desc, inner):
    body = f'<section class="max-w-3xl mx-auto px-4 py-12 md:py-16 prose-legal"><h1 class="text-4xl font-bold mb-2">{title}</h1><p class="text-sm text-muted mb-8">Last updated: {UPDATED}</p>{inner}</section>'
    page(fname, title, desc, body)


def build_legal():
    ro = f"{e(OWNER)} (&ldquo;{BRAND}&rdquo;, &ldquo;we&rdquo;, &ldquo;us&rdquo;)"
    legal("privacy.html", "Privacy Policy", "How Noway.net collects, uses and protects personal information under POPIA.", f'''
<p>This policy explains how {ro} handles personal information in line with South Africa's Protection of Personal Information Act (POPIA). We are the &ldquo;responsible party&rdquo;. Contact our Information Officer at {MAIL}.</p>
<h2>What we collect</h2>
<ul><li><strong>Enquiries and quote requests:</strong> your name, email address, message, subject and (optionally) your business type.</li>
<li><strong>Orders:</strong> your name, email address, optional mobile number, the business, project or domain name you give us, and which items you chose.</li>
<li><strong>Payments:</strong> you pay on PayFast's own page. We do not see or store your card or bank details. PayFast tells us whether a payment succeeded.</li>
<li><strong>Technical data:</strong> our host keeps standard server logs (such as IP address and pages requested) for security and reliability.</li>
<li><strong>In your browser:</strong> your quote (the items you added) and your cookie choice are stored on your own device. We don't receive them.</li></ul>
<p>We don't ask you to create an account, we don't collect more than we need, and we don't buy or sell personal information.</p>
<h2>Why we use it</h2>
<ul><li>To reply to your enquiry (with your consent).</li><li>To deliver the services you buy, issue receipts and provide support (to perform our contract with you).</li>
<li>To keep financial and tax records (a legal requirement).</li><li>To keep the website secure.</li></ul>
<h2>Who we share it with</h2>
<ul><li><strong>PayFast</strong> (payment processing).</li><li><strong>Netlify</strong> (website hosting, form handling and the payment-signing service). Their servers may be outside South Africa; we only use providers that protect data to a comparable standard.</li></ul>
<p>We share information with authorities only where the law requires it. Fonts on this site are served from our own domain, so your browser does not contact Google Fonts.</p>
<h2>How long we keep it</h2>
<ul><li>Enquiries that don't become projects: up to 24 months, then deleted.</li><li>Client and order records: for the duration of the service, then as long as the law requires for financial records (generally 5 years).</li></ul>
<h2>Your rights</h2>
<p>You can ask to access, correct or delete your information, or object to how we use it, using our <a href="data-request.html">data request form</a> or by emailing {MAIL}. You can withdraw consent at any time. If you are unhappy with how we handled a request, you can complain to the Information Regulator at <a href="https://inforegulator.org.za" rel="noopener">inforegulator.org.za</a>.</p>
<h2>Marketing email</h2><p>We only send marketing email if you opt in. Any marketing email will include a working unsubscribe link, and we stop on request.</p>
<h2>Children</h2><p>Our services are for businesses and adults. We don't knowingly collect personal information from anyone under 18. If you believe a child has given us information, contact us and we'll delete it.</p>
<h2>Security</h2><p>The site uses HTTPS, access to our systems is limited, and payments are handled by PayFast. No system is perfectly secure; if a breach affecting your information occurs we'll notify you and the Information Regulator as POPIA requires.</p>
<h2>Cookies</h2><p>See our <a href="cookies.html">Cookie Policy</a>.</p>
<h2>Changes</h2><p>We'll update this page when our practices change and show the date at the top.</p>''')

    legal("terms.html", "Terms of Service", "Terms for website projects, hosting and maintenance from Noway.net.", f'''
<p>These terms apply when you buy a service from {ro}. By ticking the box at checkout or by engaging us, you agree to them.</p>
<h2>1. Services and scope</h2><p>We provide website design and development, hosting, maintenance and related add-ons as described on this site or in a written quote. Anything outside the described scope is quoted separately before work starts.</p>
<h2>2. Prices and payment</h2><ul><li>Prices are in South African rand and are shown before you pay. Third-party costs (domains, premium plugins, paid stock images or fonts) are quoted and agreed first.</li>
<li>Website projects: a 50% deposit is paid at checkout and the 50% balance is due before the website goes live.</li>
<li>Priority add-ons are a once-off fee.</li><li>Hosting and maintenance are monthly subscriptions that renew automatically until cancelled.</li>
<li>Payments are processed by PayFast.</li></ul>
<h2>3. Timelines</h2><p>Timelines we give are estimates unless confirmed in writing. They depend on you providing content, feedback and approvals promptly. Delays caused by late content or feedback move the timeline.</p>
<h2>4. Revisions</h2><p>Each package includes the revision rounds listed on the booking page (Bronze 1, Silver 2, Gold 3). A round is a single consolidated set of change requests. Extra revisions or changes to the agreed scope are quoted at an hourly rate before work is done.</p>
<h2>5. Your content</h2><p>You must have the right to use all text, images, logos and other material you give us, and you are responsible for it. You agree that we may use it to build your website.</p>
<h2>6. Ownership</h2><p>When your project is paid in full you own the custom design and content we created for you. Third-party items (fonts, plugins, themes, stock images, frameworks) remain under their own licences. Until payment in full, ownership stays with us. We may show the finished site in our portfolio unless you tell us not to.</p>
<h2>7. Hosting and maintenance</h2><ul><li>We use reasonable efforts to keep hosted sites available but don't guarantee uninterrupted service unless agreed in writing. Support response times are targets on business days.</li>
<li>You can cancel a subscription at any time before your next billing date by emailing {MAIL}. See the <a href="refund.html">Refund Policy</a>.</li>
<li>If a subscription payment fails we'll tell you and may suspend the service after 7 days' notice. We may keep a copy of your site for 30 days after suspension so you can collect it.</li>
<li>Unlimited allowances are subject to fair use.</li></ul>
<h2>8. Acceptable use</h2><p>You may not use our services for anything unlawful, for spam or malware, or to infringe other people's rights. We may suspend a site that does.</p>
<h2>9. Liability</h2><p>We take care with our work, but we can't promise particular business results such as sales or search rankings. To the extent the law allows, our total liability for any claim is limited to the amount you paid us for the service concerned in the 3 months before the claim, and we are not liable for indirect or consequential loss. Nothing in these terms limits rights you have under the Consumer Protection Act or any other law that can't be excluded.</p>
<h2>10. Cancellation</h2><p>See the <a href="refund.html">Refund Policy</a>. Either party may end the agreement if the other seriously breaches it and doesn't fix the breach within 14 days of written notice.</p>
<h2>11. Privacy</h2><p>We handle your information as described in the <a href="privacy.html">Privacy Policy</a>.</p>
<h2>12. General</h2><p>These terms are governed by the laws of South Africa. If any part is unenforceable the rest continues to apply. We may update these terms; changes don't affect services already paid for. Questions: {MAIL}.</p>''')

    legal("refund.html", "Refund and Cancellation Policy", "Refund and cancellation rules for Noway.net website projects, priority add-ons, hosting and maintenance.", f'''
<p>We want this to be fair and easy to understand. Nothing here limits your rights under the Consumer Protection Act or the Electronic Communications and Transactions Act, including any statutory cooling-off right that applies to you.</p>
<h2>Website projects (50% deposit)</h2>
<ul><li><strong>Cancel before work starts:</strong> full refund of your deposit.</li>
<li><strong>Cancel after work has started:</strong> you pay for the work completed up to that point. If your deposit is more than that, we refund the difference. If it's less, we'll tell you the amount before you owe anything further.</li>
<li><strong>If we can't deliver what we agreed:</strong> you get a refund for the part not delivered.</li>
<li>The balance is only due when the site is ready for launch.</li></ul>
<h2>Priority add-ons</h2><p>Refundable in full until we've moved your project up the queue. Once your project has been fast-tracked, the priority fee is not refundable.</p>
<h2>Hosting and maintenance subscriptions</h2>
<ul><li>Cancel at any time before your next billing date by emailing {MAIL}. You won't be charged again.</li>
<li>The period you've already paid for isn't refunded part-way through, and your service continues until it ends.</li>
<li>If we fail to provide the service you paid for, we'll credit or refund the affected period.</li></ul>
<h2>How to ask</h2><p>Email {MAIL} with your name and order reference. We reply within 5 business days. Approved refunds are returned to the original payment method via PayFast, usually within 10 business days.</p>''')

    legal("cookies.html", "Cookie Policy", "What cookies and similar storage Noway.net uses.", f'''
<p>Cookies and similar storage keep small pieces of information in your browser. Here is what {BRAND} uses.</p>
<h2>What this site stores on your device</h2>
<ul><li><strong>Your cookie choice:</strong> remembers whether you accepted or chose essential-only. Essential.</li>
<li><strong>Your quote:</strong> the items you've added, so they're still there when you move between pages. Essential. It stays on your device and isn't sent to us until you check out or request a quote.</li></ul>
<p>We don't use advertising cookies, social media trackers or analytics. If we add analytics in future, we'll update this page and only switch it on if you accept.</p>
<h2>Third parties</h2><p>When you pay, you are sent to PayFast, which sets its own cookies on its own pages under its own policy. Our host, Netlify, may process standard request logs for security.</p>
<h2>Your choices</h2><p>You can change your choice at any time with the &ldquo;Cookie settings&rdquo; link in the footer, or clear this site's data in your browser settings.</p>
<p>See also the <a href="privacy.html">Privacy Policy</a>.</p>''')


# ---------------- assets ----------------
def build_assets():
    pages = ["index.html", "booking.html", "hosting.html", "maintenance.html", "priority.html", "about.html", "contact.html",
             "faq.html", "privacy.html", "terms.html", "refund.html", "cookies.html", "data-request.html"]
    urls = "".join(f"<url><loc>{SITE_URL}/{'' if p == 'index.html' else p}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>" for p in pages)
    open(os.path.join(DIST, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    open(os.path.join(DIST, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /checkout.html\nSitemap: {SITE_URL}/sitemap.xml\n")
    open(os.path.join(DIST, "plans.js"), "w").write("window.NOWAY_PLANS=" + json.dumps(catalog) + ";")
    for f in ("site.js", "cart.js", "checkout.js", "contact.js", "thanks.js"):
        shutil.copy(os.path.join(ROOT, "src", f), os.path.join(DIST, f))
    shutil.copy(os.path.join(ROOT, "src/assets/logo.png"), os.path.join(DIST, "logo.png"))
    shutil.copy(os.path.join(ROOT, "src/assets/favicon.png"), os.path.join(DIST, "favicon.png"))
    fdir = os.path.join(DIST, "fonts")
    os.makedirs(fdir, exist_ok=True)
    src = os.path.join(ROOT, "node_modules/@fontsource/inter/files")
    for w in (400, 500, 600, 700, 800):
        shutil.copy(os.path.join(src, f"inter-latin-{w}-normal.woff2"), fdir)


if __name__ == "__main__":
    if os.path.isdir(DIST):
        for f in os.listdir(DIST):
            p = os.path.join(DIST, f)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(DIST, exist_ok=True)
    build_assets(); build_pages(); build_legal()
    print("built", len(os.listdir(DIST)), "files")
