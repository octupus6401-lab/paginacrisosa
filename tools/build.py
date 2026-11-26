#!/usr/bin/env python3
"""
CRISOSA Logistic Solutions — static site builder.

Plain HTML, no server, no runtime. Shared chrome lives here; page bodies
live in tools/parts/<slug>.html.

    python3 tools/build.py

The quote form is static: it opens the visitor's mail client addressed to
ventas@crisosa.com. There is no form backend and no API key in this repo.
To receive submissions without a mail client, point <form class="quote-form">
at a form service and keep the same field names (company, name, email,
phone, service, volume, message).

WhatsApp is a separate mobile line from the company phone. Change WA below
if that handset changes.
"""
import html
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PARTS = ROOT / "tools" / "parts"
sys.path.insert(0, str(ROOT / "tools"))
from plates import PLATES  # noqa: E402

EMAIL = "ventas@crisosa.com"
CONTACT = "Emilio Vives"
MX_TEL = "+526646072000"
MX_HUMAN = "+52 (664) 607-2000"
US_TEL = "+16197107190"
US_HUMAN = "+1 (619) 710-7190"
WA = "526646933534"
WA_HUMAN = "+52 664 693 3534"

# slug, directory, ES nav, EN nav
PAGES = [
    ("home",            "",                  "Inicio",            "Home"),
    ("almacenaje",      "almacenaje",        "Almacenaje",        "Warehousing"),
    ("empaque",         "empaque",           "Empaque",           "Packaging"),
    ("shelter",         "shelter",           "Shelter",           "Shelter"),
    ("soluciones",      "soluciones",        "Soluciones",        "Solutions"),
    ("servicios",       "servicios",         "Servicios",         "Services"),
    ("comercio",        "comercio-exterior", "Comercio exterior", "Foreign trade"),
    ("certificaciones", "certificaciones",   "Certificaciones",   "Certifications"),
    ("clientes",        "clientes",          "Clientes",          "Clients"),
    ("instalaciones",   "instalaciones",     "Instalaciones",     "Facilities"),
    ("nosotros",        "nosotros",          "Nosotros",          "About"),
    ("contacto",        "contacto",          "Contacto",          "Contact"),
]
PRIMARY = ["almacenaje", "empaque", "shelter", "soluciones", "nosotros"]
HAS_FORM = {"home", "almacenaje", "empaque", "shelter", "comercio", "contacto"}

# Default service pre-selected on the quote form and the header CTA.
SERVICE_FOR = {
    "home": "almacenaje",
    "almacenaje": "almacenaje",
    "empaque": "empaque",
    "shelter": "shelter",
    "comercio": "comercio",
    "servicios": "almacenaje",
    "contacto": "almacenaje",
    "soluciones": "almacenaje",
    "certificaciones": "almacenaje",
    "clientes": "almacenaje",
    "instalaciones": "almacenaje",
    "nosotros": "almacenaje",
}

# title ES, title EN, description ES, description EN
META = {
 "home": (
  "Almacenaje 3PL en Tijuana | CRISOSA Logistic Solutions",
  "3PL warehousing in Tijuana | CRISOSA Logistic Solutions",
  "Almacén 3PL y recinto fiscalizado en Tijuana y la frontera. Cerca de 45,000 m² en 8 inmuebles. IVA/IEPS AAA, C-TPAT e IMMEX. Solicita espacio o cotización.",
  "3PL and bonded warehousing in Tijuana and the border region. About 45,000 m² across 8 facilities. IVA/IEPS AAA, C-TPAT and IMMEX. Request space or a quote."),
 "almacenaje": (
  "Almacenaje 3PL y recinto fiscalizado en Tijuana | CRISOSA",
  "3PL warehousing and bonded storage in Tijuana | CRISOSA",
  "Pide m² o tarimas en Tijuana. Recepción, inventario y surtido en cerca de 45,000 m². Operador AAA, C-TPAT e IMMEX. Cotiza espacio de almacén 3PL.",
  "Request square meters or pallets in Tijuana. Receiving, inventory and picking across about 45,000 m². AAA, C-TPAT and IMMEX operator. Quote 3PL space."),
 "empaque": (
  "Material de empaque, EPP y cuarto limpio en Tijuana | CRISOSA",
  "Packaging materials, PPE and cleanroom products in Tijuana | CRISOSA",
  "Venta de material de empaque, productos de seguridad (EPP) y productos de cuarto limpio en Tijuana. Cotiza por volumen con CRISOSA.",
  "Packaging materials, safety products (PPE) and cleanroom products for sale in Tijuana. Quote by volume with CRISOSA."),
 "shelter": (
  "Shelter en México, arranque en menos de 90 días | CRISOSA",
  "Mexico shelter, greenfield start in under 90 days | CRISOSA",
  "Manufactura en México sin constituir tu propia empresa. Arranque greenfield en menos de 90 días, con IMMEX, aduana, almacén y personal.",
  "Manufacture in Mexico without incorporating your own company. Greenfield start in under 90 days, with IMMEX, customs, warehousing and staffing."),
 "soluciones": (
  "Casos prácticos y soluciones | CRISOSA Logistic Solutions",
  "Practical cases and solutions | CRISOSA Logistic Solutions",
  "Soluciones que CRISOSA diseña para una necesidad concreta de operación. Los casos se publicarán sólo con datos confirmados por la empresa.",
  "Solutions CRISOSA designs for a specific operational need. Cases will be published only with figures confirmed by the company."),
 "servicios": (
  "Servicios de logística en Tijuana | CRISOSA",
  "Logistics services in Tijuana | CRISOSA",
  "Almacenaje 3PL, venta de empaque y EPP, y shelter en la frontera norte. Comercio exterior IMMEX y C-TPAT como apoyo.",
  "3PL warehousing, packaging and PPE sales, and shelter on the northern border. IMMEX and C-TPAT foreign trade in support."),
 "comercio": (
  "Comercio exterior en Tijuana: IMMEX y C-TPAT | CRISOSA",
  "Foreign trade in Tijuana: IMMEX and C-TPAT | CRISOSA",
  "Importación y exportación en la frontera, con IMMEX, C-TPAT y envíos Section 321. Apoyo al almacenaje y al shelter de CRISOSA.",
  "Import and export on the border, with IMMEX, C-TPAT and Section 321 shipments. Support for CRISOSA warehousing and shelter."),
 "certificaciones": (
  "Certificaciones AAA, C-TPAT e IMMEX | CRISOSA",
  "AAA, C-TPAT and IMMEX certifications | CRISOSA",
  "IVA/IEPS nivel AAA desde 2015, C-TPAT, IMMEX y OEA en proceso. Qué cambia cada acreditación en una operación de frontera.",
  "IVA/IEPS AAA since 2015, C-TPAT, IMMEX and OEA in progress. What each accreditation changes in a border operation."),
 "clientes": (
  "Clientes y sectores | CRISOSA Logistic Solutions",
  "Clients and sectors | CRISOSA Logistic Solutions",
  "Relaciones de 15 a 25 años en dispositivos médicos, química, logística, empaque y automotriz. Operación en Tijuana y la frontera.",
  "Relationships of 15 to 25 years in medical devices, chemicals, logistics, packaging and automotive. Operations in Tijuana and the border region."),
 "instalaciones": (
  "Instalaciones: 45,000 m² en 8 inmuebles | CRISOSA",
  "Facilities: 45,000 m² across 8 buildings | CRISOSA",
  "Cerca de 45,000 m² en ocho inmuebles: Tijuana, Valle Redondo, Rosarito, Lerma y Piedras Negras.",
  "About 45,000 m² across eight facilities: Tijuana, Valle Redondo, Rosarito, Lerma and Piedras Negras."),
 "nosotros": (
  "Nosotros: CRISOSA desde 1994 en Tijuana",
  "About CRISOSA, in Tijuana since 1994",
  "Fundada en 1994 en Tijuana. Más de 30 años y un crecimiento compuesto de 20% en dólares entre 1996 y 2025. Contacto: Emilio Vives.",
  "Founded in 1994 in Tijuana. 30+ years and 20% compound growth in US dollars from 1996 to 2025. Contact: Emilio Vives."),
 "contacto": (
  "Cotizar almacenaje o shelter | Contacto CRISOSA",
  "Quote warehousing or shelter | Contact CRISOSA",
  "Solicita espacio o una cotización. Emilio Vives, ventas@crisosa.com, +52 (664) 607-2000 y US +1 (619) 710-7190.",
  "Request space or a quote. Emilio Vives, ventas@crisosa.com, +52 (664) 607-2000 and US +1 (619) 710-7190."),
}

SERVICES = [
    ("almacenaje", "Almacenaje 3PL", "3PL warehousing"),
    ("empaque", "Material de empaque, EPP y cuarto limpio", "Packaging, PPE and cleanroom"),
    ("shelter", "Shelter", "Shelter"),
    ("comercio", "Comercio exterior", "Foreign trade"),
    ("otro", "Otro", "Other"),
]

SITE = os.environ.get("SITE_URL", "https://www.crisosa.com").rstrip("/")

PLATE_PAGE = {}
SLOT_RE = re.compile(r"\{\{(BG|CARD|SHOT|PORTRAIT):([a-z0-9\-]+)\}\}")
SVG_RE = re.compile(r"\{\{SVG:([a-z0-9\-]+)\}\}")
FORM_RE = re.compile(r"\{\{FORM:([a-z0-9\-]+)\}\}")
CTA_RE = re.compile(r"\{\{CTA:([a-z0-9\-]+)\}\}")


def slot(kind, key, b):
    d = PLATES[key]
    src = f"{b}assets/img/generated/{d['file']}"
    ratio = d["ar"].replace("/", ":")
    eager = ' fetchpriority="high"' if kind == "BG" else ' loading="lazy"'
    img = {
        "BG": f'<img class="panel__bg" src="{src}" alt=""{eager} decoding="async">',
        "CARD": f'<img class="tcard__bg" src="{src}" alt=""{eager} decoding="async">',
        "SHOT": f'<img src="{src}" alt=""{eager} decoding="async">',
        "PORTRAIT": f'<img src="{src}" alt=""{eager} decoding="async">',
    }[kind]
    return img


def quote_form(default):
    opts = []
    for val, es, en in SERVICES:
        sel = " selected" if val == default else ""
        opts.append(
            f'<option value="{val}"{sel} data-es="{html.escape(es)}" data-en="{html.escape(en)}">{html.escape(es)}</option>'
        )
    options = "\n            ".join(opts)
    return f"""<form class="quote-form" id="cotizar" action="mailto:{EMAIL}" method="post" enctype="text/plain">
        <h2 data-es="Solicitar cotización" data-en="Request a quote">Solicitar cotización</h2>
        <p class="small" data-es="Empresa, contacto, servicio y una cifra. La propuesta sale de ahí." data-en="Company, contact, service and a number. The proposal starts there.">Empresa, contacto, servicio y una cifra. La propuesta sale de ahí.</p>
        <div class="form__row">
          <label for="f-company" data-es="Empresa" data-en="Company">Empresa</label>
          <input id="f-company" name="company" type="text" required autocomplete="organization" data-es-ph="Razón social" data-en-ph="Company name" placeholder="Razón social">
        </div>
        <div class="form__row">
          <label for="f-name" data-es="Contacto" data-en="Contact">Contacto</label>
          <input id="f-name" name="name" type="text" required autocomplete="name" data-es-ph="Nombre y apellido" data-en-ph="Full name" placeholder="Nombre y apellido">
        </div>
        <div class="form__row">
          <label for="f-email" data-es="Correo de trabajo" data-en="Work email">Correo de trabajo</label>
          <input id="f-email" name="email" type="email" required autocomplete="email" placeholder="nombre@empresa.com">
        </div>
        <div class="form__row">
          <label for="f-phone" data-es="Teléfono" data-en="Phone">Teléfono</label>
          <input id="f-phone" name="phone" type="tel" autocomplete="tel" placeholder="+52 664 000 0000">
        </div>
        <div class="form__row">
          <label for="f-service" data-es="Servicio de interés" data-en="Service of interest">Servicio de interés</label>
          <select id="f-service" name="service" required>
            {options}
          </select>
        </div>
        <div class="form__row">
          <label for="f-volume" data-es="m², tarimas o volumen" data-en="m², pallets or volume">m², tarimas o volumen</label>
          <input id="f-volume" name="volume" type="text" required data-es-ph="Ejemplo: 1,500 m² o 200 tarimas al mes" data-en-ph="Example: 1,500 m² or 200 pallets a month" placeholder="Ejemplo: 1,500 m² o 200 tarimas al mes">
        </div>
        <div class="form__row">
          <label for="f-msg" data-es="Mensaje" data-en="Message">Mensaje</label>
          <textarea id="f-msg" name="message" required data-es-ph="Producto, origen, destino y qué necesitas resolver." data-en-ph="Product, origin, destination and what you need solved." placeholder="Producto, origen, destino y qué necesitas resolver."></textarea>
        </div>
        <button class="btn btn--primary" type="submit" data-es="Enviar solicitud" data-en="Send request">Enviar solicitud</button>
        <p class="form__status" role="status" hidden data-es="Se abre tu correo para enviar la solicitud a {EMAIL}. Si no se abre, usa el teléfono o WhatsApp." data-en="Your email app opens to send the request to {EMAIL}. If it does not, use the phone or WhatsApp.">Se abre tu correo para enviar la solicitud a {EMAIL}. Si no se abre, usa el teléfono o WhatsApp.</p>
        <p class="form__note" data-es="Este sitio no guarda el formulario. El mensaje lo envías tú, desde tu correo, a {EMAIL}." data-en="This site does not store the form. You send the message yourself, from your email, to {EMAIL}.">Este sitio no guarda el formulario. El mensaje lo envías tú, desde tu correo, a {EMAIL}.</p>
        <div class="form__direct">
          <a href="tel:{MX_TEL}">{MX_HUMAN}</a>
          <a href="https://wa.me/{WA}" rel="noopener">WhatsApp {WA_HUMAN}</a>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
        </div>
      </form>"""


def cta_band(b, service):
    href = f"{b}contacto/?servicio={service}"
    return f"""<aside class="cta">
  <div class="wrap cta__in">
    <div>
      <p class="eyebrow" data-es="Cotización" data-en="Quote">Cotización</p>
      <h2 data-es="Dinos la empresa, el servicio y una cifra." data-en="Tell us the company, the service and a number.">Dinos la empresa, el servicio y una cifra.</h2>
      <p data-es="Espacio de almacén, volumen de empaque o un arranque shelter. Respondemos con una propuesta." data-en="Warehouse space, packaging volume or a shelter start. We reply with a proposal.">Espacio de almacén, volumen de empaque o un arranque shelter. Respondemos con una propuesta.</p>
    </div>
    <div class="cta__actions">
      <a class="btn btn--primary" href="{href}" data-es="Solicitar cotización" data-en="Request a quote">Solicitar cotización</a>
      <a class="btn btn--ghost" href="tel:{MX_TEL}">{MX_HUMAN}</a>
      <a class="btn btn--wa" href="https://wa.me/{WA}" rel="noopener">WhatsApp</a>
    </div>
  </div>
</aside>"""


def expand(body, b, page=""):
    def sub(m):
        PLATE_PAGE.setdefault(m.group(2), page)
        return slot(m.group(1), m.group(2), b)
    body = SLOT_RE.sub(sub, body)
    body = FORM_RE.sub(lambda m: quote_form(m.group(1)), body)
    body = CTA_RE.sub(lambda m: cta_band(b, m.group(1)), body)
    body = SVG_RE.sub(
        lambda m: (ROOT / "assets" / "svg" / f"{m.group(1)}.svg").read_text(encoding="utf-8").strip(),
        body)
    return body


SHELL = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_es}</title>
<meta name="description" content="{desc_es}">
<meta name="theme-color" content="#F7FBFC">
<meta name="robots" content="index,follow">
<link rel="icon" href="{b}assets/logos/crisosa.png">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="es" href="{canonical}">
<link rel="alternate" hreflang="en" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">
<meta property="og:site_name" content="CRISOSA Logistic Solutions">
<meta property="og:title" content="{title_es}">
<meta property="og:description" content="{desc_es}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{site}/assets/img/opt/og.jpg">
<meta property="og:locale" content="es_MX">
<meta property="og:locale:alternate" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="MX-BCN">
<meta name="geo.placename" content="Tijuana">
<link rel="preload" href="{b}assets/fonts/xn7gYHE41ni1AdIRggexSg.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<link rel="stylesheet" href="{b}assets/css/styles.css">
{ld}
</head>
<body data-es-doctitle="{title_es}" data-en-doctitle="{title_en}" data-es-docdesc="{desc_es}" data-en-docdesc="{desc_en}">
<a class="skip" href="#main" data-es="Ir al contenido" data-en="Skip to content">Ir al contenido</a>
{header}
<main id="main">
{body}
</main>
{footer}
<a class="float" href="https://wa.me/{wa}" rel="noopener" data-es-label="Escribir por WhatsApp a CRISOSA" data-en-label="Message CRISOSA on WhatsApp" aria-label="Escribir por WhatsApp a CRISOSA">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12.04 2C6.58 2 2.15 6.4 2.15 11.83c0 1.74.46 3.44 1.34 4.94L2 22l5.39-1.4a10 10 0 0 0 4.65 1.18h.01c5.46 0 9.89-4.4 9.89-9.83C21.94 6.4 17.5 2 12.04 2Zm5.76 14.12c-.24.68-1.4 1.3-1.94 1.38-.5.07-1.12.1-1.81-.11-.41-.13-.95-.31-1.63-.61-2.87-1.24-4.74-4.14-4.88-4.33-.14-.19-1.15-1.53-1.15-2.92 0-1.39.73-2.07.99-2.35.26-.28.57-.35.76-.35h.55c.17 0 .41-.07.64.49.24.58.82 2 .89 2.15.07.14.12.32.02.51-.09.19-.14.31-.28.48-.14.17-.29.37-.41.5-.14.14-.28.29-.12.56.16.28.71 1.17 1.52 1.9 1.05.93 1.93 1.22 2.2 1.36.28.14.44.12.6-.07.16-.19.7-.81.88-1.09.19-.28.37-.23.62-.14.26.09 1.62.76 1.9.9.28.14.46.21.53.32.07.12.07.68-.17 1.36Z"/></svg>
  <span>WhatsApp</span>
</a>
<script src="{b}assets/js/main.js"></script>
</body>
</html>
"""


def org_ld():
    return """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": ["Organization", "LocalBusiness"],
      "@id": "%(site)s/#org",
      "name": "CRISOSA Logistic Solutions",
      "url": "%(site)s/",
      "logo": "%(site)s/assets/logos/crisosa.png",
      "image": "%(site)s/assets/img/opt/og.jpg",
      "email": "ventas@crisosa.com",
      "telephone": "+52-664-607-2000",
      "foundingDate": "1994",
      "description": "Almacenaje 3PL, material de empaque, EPP, productos de cuarto limpio y shelter en Tijuana y la frontera norte de México.",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Tijuana",
        "addressRegion": "Baja California",
        "addressCountry": "MX"
      },
      "areaServed": ["Tijuana", "Valle Redondo", "Rosarito", "Lerma", "Piedras Negras"],
      "knowsAbout": ["Almacenaje 3PL", "Recinto fiscalizado", "IMMEX", "C-TPAT", "Shelter", "Material de empaque"],
      "contactPoint": [
        {
          "@type": "ContactPoint",
          "telephone": "+52-664-607-2000",
          "email": "ventas@crisosa.com",
          "contactType": "sales",
          "name": "Emilio Vives",
          "areaServed": "MX",
          "availableLanguage": ["Spanish", "English"]
        },
        {
          "@type": "ContactPoint",
          "telephone": "+52-664-693-3534",
          "contactType": "sales",
          "name": "WhatsApp",
          "areaServed": "MX",
          "availableLanguage": ["Spanish", "English"]
        },
        {
          "@type": "ContactPoint",
          "telephone": "+1-619-710-7190",
          "contactType": "sales",
          "areaServed": "US",
          "availableLanguage": ["English", "Spanish"]
        }
      ]
    }
  ]
}
</script>""" % {"site": SITE}


def page_by(slug):
    return next(p for p in PAGES if p[0] == slug)


def href_for(p, b, home):
    return home if p[1] == "" else f"{b}{p[1]}/"


def header(b, home, slug):
    service = SERVICE_FOR.get(slug, "almacenaje")
    cta = "#cotizar" if slug in HAS_FORM else f"{b}contacto/?servicio={service}"

    def link(s, extra=""):
        p = page_by(s)
        cur = ' aria-current="page"' if p[0] == slug else ""
        return f'<a href="{href_for(p, b, home)}"{cur}{extra} data-es="{p[2]}" data-en="{p[3]}">{p[2]}</a>'

    primary = "\n      ".join(link(s) for s in PRIMARY)
    menu_links = "\n        ".join(link(p[0]) for p in PAGES if p[0] != "home")
    return f"""<header class="hdr" id="hdr">
  <div class="brandmark" aria-hidden="true"><i></i><b></b></div>
  <div class="hdr__in">
    <a class="hdr__logo" href="{home}" aria-label="CRISOSA Logistic Solutions">
      <img src="{b}assets/logos/crisosa.png" alt="CRISOSA Logistic Solutions" width="107" height="34">
    </a>
    <nav class="hdr__nav" aria-label="Principal">
      {primary}
    </nav>
    <div class="hdr__tools">
      <a class="hdr__phone" href="tel:{MX_TEL}">{MX_HUMAN}</a>
      <div class="lang" role="group" aria-label="Idioma / Language">
        <button type="button" data-lang="es" class="is-on" aria-pressed="true">ES</button><i aria-hidden="true">/</i><button type="button" data-lang="en" aria-pressed="false">EN</button>
      </div>
      <a class="btn btn--primary" href="{cta}" data-es="Cotizar" data-en="Quote">Cotizar</a>
      <button class="mtrig" id="mtrig" type="button" aria-expanded="false" aria-controls="menu">
        <span data-es="Menú" data-en="Menu">Menú</span>
      </button>
    </div>
  </div>
  <div class="menu" id="menu" hidden>
    <nav aria-label="Secciones">
        {menu_links}
        <a class="btn btn--primary" href="{cta}" data-es="Cotizar" data-en="Get a quote">Cotizar</a>
    </nav>
  </div>
</header>"""


def footer(b, home):
    def li(slug):
        p = page_by(slug)
        return f'<li><a href="{href_for(p, b, home)}" data-es="{p[2]}" data-en="{p[3]}">{p[2]}</a></li>'
    col_svc = "\n          ".join(li(s) for s in ["almacenaje", "empaque", "shelter", "comercio", "servicios"])
    col_co = "\n          ".join(li(s) for s in ["instalaciones", "certificaciones", "clientes", "soluciones", "nosotros", "contacto"])
    return f"""<footer class="ftr">
  <div class="wrap ftr__top">
    <div>
      <img class="ftr__logo" src="{b}assets/logos/crisosa-white.png" alt="CRISOSA Logistic Solutions" width="100" height="32">
      <p data-es="Almacenaje 3PL, empaque y shelter en Tijuana y la frontera norte. Desde 1994." data-en="3PL warehousing, packaging and shelter in Tijuana and the northern border. Since 1994.">Almacenaje 3PL, empaque y shelter en Tijuana y la frontera norte. Desde 1994.</p>
    </div>
    <div>
      <h2 data-es="Servicios" data-en="Services">Servicios</h2>
      <ul>
          {col_svc}
      </ul>
    </div>
    <div>
      <h2 data-es="Empresa" data-en="Company">Empresa</h2>
      <ul>
          {col_co}
      </ul>
    </div>
    <div>
      <h2 data-es="Contacto" data-en="Contact">Contacto</h2>
      <ul>
        <li>{CONTACT}</li>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li><a href="tel:{MX_TEL}">MX {MX_HUMAN}</a></li>
        <li><a href="tel:{US_TEL}">US {US_HUMAN}</a></li>
        <li><a href="https://wa.me/{WA}" rel="noopener">WhatsApp {WA_HUMAN}</a></li>
        <li>Tijuana, Baja California</li>
      </ul>
    </div>
  </div>
  <div class="wrap ftr__bar">
    <span>© <span id="yr">2026</span> CRISOSA Logistic Solutions</span>
    <span data-es="IVA/IEPS AAA desde 2015 · C-TPAT · IMMEX" data-en="IVA/IEPS AAA since 2015 · C-TPAT · IMMEX">IVA/IEPS AAA desde 2015 · C-TPAT · IMMEX</span>
  </div>
</footer>"""


def build():
    written = []
    for p in PAGES:
        slug, directory = p[0], p[1]
        b = "" if directory == "" else "../" if directory.count("/") == 0 else "../../"
        # all current directories are one level deep
        b = "" if directory == "" else "../"
        home = "./" if directory == "" else "../"
        canonical = f"{SITE}/" + (f"{directory}/" if directory else "")
        raw = (PARTS / f"{slug}.html").read_text(encoding="utf-8")
        body = expand(raw, b, p[2])
        body = body.replace("{b}", b).replace("{home}", home)
        t_es, t_en, d_es, d_en = META[slug]
        preload = ""
        if slug == "home":
            preload = f'<link rel="preload" as="image" href="{b}assets/img/opt/warehouse.webp" fetchpriority="high">'
        page = SHELL.format(
            b=b, site=SITE, canonical=canonical, wa=WA,
            ld=org_ld() if slug == "home" else "",
            preload=preload,
            title_es=html.escape(t_es, quote=True), title_en=html.escape(t_en, quote=True),
            desc_es=html.escape(d_es, quote=True), desc_en=html.escape(d_en, quote=True),
            header=header(b, home, slug), footer=footer(b, home),
            body=body.rstrip(),
        )
        out = ROOT / (directory if directory else ".") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        written.append(str(out.relative_to(ROOT)))

    nf = PARTS / "404.html"
    if nf.exists():
        body = expand(nf.read_text(encoding="utf-8"), "/", "404").replace("{b}", "/").replace("{home}", "/")
        page = SHELL.format(
            b="/", site=SITE, canonical=f"{SITE}/404.html", wa=WA, ld="", preload="",
            title_es="Página no encontrada — CRISOSA", title_en="Page not found — CRISOSA",
            desc_es="La página que buscas no existe. Vuelve al almacenaje o al contacto.",
            desc_en="That page does not exist. Go back to warehousing or contact.",
            header=header("/", "/", ""), footer=footer("/", "/"),
            body=body.rstrip())
        (ROOT / "404.html").write_text(page, encoding="utf-8")
        written.append("404.html")

    write_sitemap()
    written += ["sitemap.xml", "robots.txt"]
    write_prompts()
    written.append("assets/img/PROMPTS.md")
    print("\n".join(written) + f"\n\n{len(written)} files written.")


def write_sitemap():
    pri = {
        "home": "1.0", "almacenaje": "0.9", "empaque": "0.8", "shelter": "0.8",
        "contacto": "0.8", "servicios": "0.7", "comercio": "0.6",
        "instalaciones": "0.7", "certificaciones": "0.6", "nosotros": "0.6",
        "clientes": "0.5", "soluciones": "0.4",
    }
    urls = []
    for p in PAGES:
        loc = f"{SITE}/" + (f"{p[1]}/" if p[1] else "")
        urls.append(
            f"  <url><loc>{loc}</loc><lastmod>2026-11-25</lastmod>"
            f"<changefreq>monthly</changefreq><priority>{pri.get(p[0], '0.5')}</priority></url>"
        )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


def write_prompts():
    have = {f.name for f in (ROOT / "assets" / "img" / "generated").glob("*")}
    L = [
        "# Imágenes del sitio",
        "",
        "El sitio publicado usa fotografías reales en `assets/img/opt/` (WebP).",
        "Los archivos de `assets/img/generated/` son material de archivo y ya no",
        "se insertan en las páginas. No sustituir las fotos de nave por imágenes generadas.",
        "",
    ]
    (ROOT / "assets" / "img" / "PROMPTS.md").write_text("\n".join(L), encoding="utf-8")
    # touch have so a future editor still sees the count in git diff context
    _ = have


if __name__ == "__main__":
    build()
