#!/usr/bin/env python3
"""Générateur de visuels Azimut Média (PNG 1080x1350) à partir d'un fichier JSON.

Usage : python3 visuels.py spec.json
spec.json = {"dossier": "sortie", "images": [
   {"nom": "s1", "theme": "marine" | "sable", "etiquette": "Conseil pratique",
    "corps": "<HTML avec les classes ci-dessous>", "pied": "1/6", "source": "Source : ..."}]}

Classes pour "corps" : h1.big (grand titre), p.t (grande phrase), p.s (phrase secondaire),
em (mot en accent), b (gras), div.date > span (petite ligne d'accent) + texte gras,
ol > li (liste numérotée), div.bar2 (barre de graphique, voir plus bas),
icones : {{icone:coche}} {{icone:horloge}} {{icone:lieu}} {{icone:etoile}} {{icone:fleche}}
Graphique à barres : <div class="bar2"><i style="width:62%"></i><span>Libellé 62 %</span></div>
Charte : marine #10263B, sable #F5EFE6, accent #E07A5F ; polices Bricolage Grotesque et Figtree (dossier fonts).
"""
import base64, json, sys, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
def b64(p): return base64.b64encode(open(p, 'rb').read()).decode()
CSS = ''
for fam, pre, ws in [('Bricolage', 'bricolage-grotesque', [700, 800]), ('Figtree', 'figtree', [400, 500, 600, 700])]:
    for w in ws:
        CSS += f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b64(os.path.join(HERE,'fonts',f'{pre}-latin-{w}-normal.woff2'))})}}"
ICONS = {
 'coche': '<svg class="ic" viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 6.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 'horloge': '<svg class="ic" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M12 7v5l3.5 2" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>',
 'lieu': '<svg class="ic" viewBox="0 0 24 24"><path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="12" cy="9.5" r="2.6" fill="currentColor"/></svg>',
 'etoile': '<svg class="ic" viewBox="0 0 24 24"><path d="M12 3l2.8 5.8 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.3l1.1-6.2L3 9.7l6.2-.9z" fill="currentColor"/></svg>',
 'fleche': '<svg class="ic" viewBox="0 0 24 24"><path d="M4 12h15M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}
def page(im):
    sand = im.get('theme') == 'sable'
    bg, fg, acc = ('#F5EFE6', '#10263B', '#C8553D') if sand else ('#10263B', '#F5EFE6', '#E07A5F')
    sec = 'rgba(16,38,59,.78)' if sand else 'rgba(245,239,230,.82)'
    ring = 'rgba(16,38,59,.07)' if sand else 'rgba(245,239,230,.08)'
    body = im['corps']
    for k, v in ICONS.items(): body = body.replace('{{icone:%s}}' % k, v)
    src = f'<div class="src">{im["source"]}</div>' if im.get('source') else ''
    return f'''<html><head><style>{CSS}
*{{box-sizing:border-box}} body{{margin:0}}
.p{{width:1080px;height:1350px;background:{bg};color:{fg};font-family:Figtree;position:relative;overflow:hidden;padding:120px 100px}}
.top{{position:absolute;left:0;top:0;width:100%;height:14px;background:{acc}}}
.c1{{position:absolute;right:-220px;top:-220px;width:620px;height:620px;border:3px solid {ring};border-radius:50%}}
.c2{{position:absolute;right:-120px;top:-120px;width:420px;height:420px;border:3px solid rgba(224,122,95,.25);border-radius:50%}}
.lab{{position:relative;font-weight:700;font-size:30px;letter-spacing:.14em;text-transform:uppercase;color:{acc};margin-top:40px}}
.body{{position:relative;margin-top:60px}}
h1.big{{font-family:Bricolage;font-weight:800;font-size:96px;line-height:1.08;letter-spacing:-.015em;margin:0}}
em{{font-style:normal;color:{acc}}}
.t{{font-family:Bricolage;font-weight:700;font-size:62px;line-height:1.18;margin:0;letter-spacing:-.01em}}
.t b{{font-weight:800}}
.s{{font-size:42px;line-height:1.38;font-weight:500;margin:44px 0 0;color:{sec}}}
.date{{font-family:Bricolage;font-weight:800;font-size:64px;line-height:1.15;margin:44px 0 0}}
.date span{{display:block;font-family:Figtree;font-weight:600;font-size:36px;color:{acc};letter-spacing:.04em;margin-bottom:6px}}
ol{{margin:0;padding:0;list-style:none;counter-reset:n}}
li{{counter-increment:n;position:relative;padding-left:100px;font-size:42px;line-height:1.35;font-weight:500;margin-bottom:44px}}
li:before{{content:counter(n);position:absolute;left:0;top:0;width:64px;height:64px;border-radius:50%;background:{acc};color:{bg};font-family:Bricolage;font-weight:800;font-size:38px;text-align:center;line-height:64px}}
.ic{{width:1.1em;height:1.1em;vertical-align:-.15em;color:{acc}}}
.bar2{{position:relative;height:84px;border-radius:42px;background:rgba(128,128,128,.18);margin-top:30px;overflow:hidden}}
.bar2 i{{position:absolute;left:0;top:0;bottom:0;background:{acc};border-radius:42px}}
.bar2 span{{position:relative;display:block;line-height:84px;padding-left:36px;font-weight:700;font-size:34px;color:{'#fff' if not sand else '#10263B'}}}
.src{{position:absolute;left:100px;bottom:150px;font-size:28px;color:{sec}}}
.foot{{position:absolute;left:100px;right:100px;bottom:80px;display:flex;justify-content:space-between;align-items:center;font-weight:600;font-size:28px;color:{sec}}}
.foot .n{{font-family:Bricolage;font-weight:700;color:{fg}}}
.sw{{font-size:34px;color:{acc};font-weight:700}}
</style></head><body><div class="p"><div class="top"></div><div class="c1"></div><div class="c2"></div>
<div class="lab">{im.get('etiquette','')}</div><div class="body">{body}</div>{src}
<div class="foot"><span class="n">{im.get('marque','Azimut Média')}</span><span class="sw">{im.get('pied','')}</span></div></div></body></html>'''
def main(spec_path):
    spec = json.load(open(spec_path, encoding='utf-8'))
    out = spec.get('dossier', 'sortie'); os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for im in spec['images']:
            pg.set_content(page(im)); pg.wait_for_timeout(400)
            pg.screenshot(path=os.path.join(out, im['nom'] + '.png'))
        b.close()
if __name__ == '__main__': main(sys.argv[1])
