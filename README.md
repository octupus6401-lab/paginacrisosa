# CRISOSA Logistic Solutions — sitio web

Sitio estático de **CRISOSA Logistic Solutions** (Tijuana, B.C.). HTML, CSS y
JavaScript, sin dependencias y sin build en Vercel: se publica la raíz del
repositorio. `tools/build.py` regenera el HTML a partir de `tools/parts/` y del
marco común (cabecera, pie, formulario).

Paleta oficial: `#008BBB`, `#009B8B`, `#13303C`, `#3D4F57`, `#7A8A92`,
`#EFF8FA` / `#F7FBFC`, `#D9E8EE`. La marca de esquina es el cuadrado verde y
la barra azul del membretado.

## Qué se promueve

1. **Almacenaje 3PL** (`/almacenaje/`) — la oferta principal.
2. **Empaque, EPP y cuarto limpio** (`/empaque/`).
3. **Shelter** (`/shelter/`) — arranque greenfield en menos de 90 días.

Comercio exterior (`/comercio-exterior/`) queda como apoyo. Cifras públicas:
fundada en 1994, 30+ años, CAGR 20% en dólares 1996–2025, cerca de 45,000 m²
en 8 inmuebles (Tijuana, Valle Redondo, Rosarito, Lerma, Piedras
Negras). IVA/IEPS AAA desde 2015, C-TPAT, IMMEX, OEA en proceso.

Contacto: Emilio Vives, ventas@crisosa.com, +52 (664) 607-2000,
US +1 (619) 710-7190. WhatsApp es otra línea: +52 664 693 3534
(`WA` en `tools/build.py`).

## Formulario

No hay backend ni credenciales. El formulario abre el correo del visitante
dirigido a ventas@crisosa.com con empresa, contacto, servicio, m²/tarimas/volumen
y mensaje. Teléfono, WhatsApp y correo quedan al lado.

Para recibir solicitudes sin cliente de correo, apunta `form.quote-form` a un
servicio de formularios y conserva los nombres de campo: `company`, `name`,
`email`, `phone`, `service`, `volume`, `message`.

## Casos prácticos

`/soluciones/` está en estado «próximamente». La ficha de ejemplo no es un caso
real: vive en `tools/parts/caso.ejemplo.html` y, marcada, dentro de la página.
Para publicar uno, copia el artículo dentro de `#casos`, quita la marca de
ejemplo y usa sólo datos confirmados. Luego:

```bash
python3 tools/build.py
```

## Editar

- Texto de una página: `tools/parts/<slug>.html`. Los dos idiomas van en
  `data-es` y `data-en`, en un elemento que no tenga hijos.
- Cabecera, pie, formulario, metas y sitemap: `tools/build.py`.
- Fotos publicadas: `assets/img/opt/` (WebP). No sustituirlas por imágenes
  generadas. Los JPG de `assets/img/generated/` no se publican.

```bash
python3 tools/build.py
python3 -m http.server 8080
```

## Vercel

No hay build. `vercel.json` fija `outputDirectory: "."`. La rama de producción
es `main`. `SITE_URL` (por defecto `https://www.crisosa.com`) alimenta
canonical, Open Graph y el sitemap; se puede fijar al correr `tools/build.py`.
