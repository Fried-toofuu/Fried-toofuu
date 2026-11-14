"""Generate self-contained SVG artwork and the GitHub-compatible profile README.

Standard library only. Existing badges, mascot geometry and contribution assets
remain the source of truth. Run from any directory with Python 3.10+.
"""
from pathlib import Path
from html import escape
import base64
import re
import sys
import subprocess
import textwrap
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
NS = '{http://www.w3.org/2000/svg}'
ET.register_namespace('', 'http://www.w3.org/2000/svg')
THEMES = {
    'dark': dict(bg='#171b22', surface='#252c36', ink='#fff0d5', muted='#adb6c4',
                 accent='#f2c078', second='#d89855', line='#414853', deep='#10151d',
                 sky='#17263a', wood='#886044', leaf='#7c9e89'),
    'light': dict(bg='#fff6e6', surface='#f2e5cf', ink='#392d2a', muted='#66594e',
                  accent='#85501f', second='#a66336', line='#cbb697', deep='#e4d1b1',
                  sky='#c9dfde', wood='#b98050', leaf='#537862'),
}
MOTION = '''
.blink { transform-box:fill-box; transform-origin:center; animation:blink 7s infinite; }
.typing { animation:typing 1.6s steps(2,end) infinite; }
.cursor { animation:cursor 1.2s steps(1,end) infinite; }
.screen { animation:screen 6s ease-in-out infinite; }
.lamp-glow { animation:glow 5s ease-in-out infinite; }
.star { animation:twinkle 5s ease-in-out infinite; }
.star.slow { animation-duration:7s; animation-delay:-3s; }
.bob { animation:bob 4s ease-in-out infinite; }
.leaf { transform-box:fill-box; transform-origin:bottom; animation:sway 6s ease-in-out infinite; }
@keyframes blink { 0%,43%,47%,100% { transform:scaleY(1); } 45% { transform:scaleY(.12); } }
@keyframes typing { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-2px); } }
@keyframes cursor { 0%,49% { opacity:1; } 50%,100% { opacity:0; } }
@keyframes screen { 0%,100% { opacity:1; } 50% { opacity:.85; } }
@keyframes glow { 0%,100% { opacity:.10; } 50% { opacity:.17; } }
@keyframes twinkle { 0%,100% { opacity:.45; } 50% { opacity:1; } }
@keyframes bob { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-3px); } }
@keyframes sway { 0%,100% { transform:rotate(-2deg); } 50% { transform:rotate(2deg); } }
@media (prefers-reduced-motion:reduce) { * { animation:none !important; } }
'''


def rect(x, y, w, h, fill, **attrs):
    extra = ''.join(f' {k.replace("_", "-")}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{extra}/>'


def text(x, y, value, size=20, color='#fff0d5', weight='normal', **attrs):
    extra = ''.join(f' {k.replace("_", "-")}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}"{extra}>{escape(value)}</text>'


def group(body, x=0, y=0, scale=1, cls=''):
    return f'<g transform="translate({x} {y}) scale({scale})" class="{cls}">{body}</g>'


def svg(w, h, title, body, animated=False):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            'role="img" aria-labelledby="title desc">'
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(title)}. Original Tofu pixel artwork.</desc>'
            '<style>text{font-family:"Courier New",monospace}'
            + (MOTION if animated else '') + '</style>' + body + '</svg>\n')


def frame(w, h, p):
    # Stepped corners and a single inset border keep every panel in one shape system.
    return (f'<path d="M12 0H{w-12}v6h6v6h6v{h-24}h-6v6h-6v6H12v-6H6v-6H0V12h6V6h6z" fill="{p["bg"]}"/>'
            f'<path d="M16 8H{w-16}M8 16V{h-16}M16 {h-8}H{w-16}M{w-8} 16V{h-16}" fill="none" stroke="{p["line"]}" stroke-width="2"/>'
            + rect(16, 16, 5, 5, p['second']) + rect(w-21, h-21, 5, 5, p['second']))


def tofu(animated=True):
    # Retain the exact silhouette, toasted edges, blush and face of the existing pet.
    source = ET.parse(ASSETS / 'tofu-idle.svg').getroot()
    parts = list(source.find(NS+'g'))
    out = ''
    for el in parts:
        if el.get('d', '').startswith('M32 40'):
            out += '<g class="blink">' + '<path d="M32 40h4v6h-4zM60 40h4v6h-4z" fill="#392d2a"/>' + '</g>'
            out += '<path d="M42 50h12v4H42z" fill="#392d2a"/>'
        else:
            out += ET.tostring(el, encoding='unicode').replace('ns0:', '').replace(':ns0', '')
    return '<g shape-rendering="crispEdges">'+out+'</g>'


def plant(p):
    leaves = (rect(20, 4, 4, 40, p['leaf']) + rect(8, 12, 12, 12, p['leaf'])
              + rect(24, 4, 12, 16, p['leaf']) + rect(24, 28, 16, 8, p['leaf'])
              + rect(4, 28, 16, 8, p['leaf']))
    return '<g class="leaf">'+leaves+'</g>'+rect(8, 44, 28, 4, '#f2c078')+rect(12, 48, 20, 20, '#d89855')


def room(p, light=False):
    out = rect(0, 0, 560, 340, p['deep']) + rect(8, 8, 544, 268, p['bg'])
    # Wall paneling, pixel floorboards and warm woven rug.
    out += rect(8, 272, 544, 4, p['line']) + rect(8, 276, 544, 56, p['surface'])
    for x in range(16, 550, 64):
        out += rect(x, 280, 2, 52, p['line'], opacity='.35')
    out += rect(90, 300, 372, 20, p['wood'], opacity='.35')
    for x in range(98, 460, 24):
        out += rect(x, 304, 8, 12, p['second'], opacity='.4')
    # Window: daytime sun / nighttime moon and staggered twinkling stars.
    out += rect(342, 32, 176, 144, p['line']) + rect(350, 40, 160, 128, p['sky'])
    if light:
        out += rect(454, 58, 28, 28, '#f2c078') + rect(450, 62, 36, 20, '#f2c078')
        out += rect(362, 80, 36, 8, '#fff6e6') + rect(374, 72, 16, 8, '#fff6e6')
        out += '<path d="M350 168h160L380 272H220z" fill="#f2c078" opacity=".07"/>'
    else:
        out += '<path d="M472 52h20v8h-8v20h-20V60h8z" fill="#fff0d5"/>'
        for i, (x, y) in enumerate([(370, 62), (414, 86), (494, 128), (382, 138), (438, 52)]):
            out += f'<g class="star {"slow" if i%2 else ""}">'+rect(x, y, 4, 12, '#fff0d5')+rect(x-4, y+4, 12, 4, '#fff0d5')+'</g>'
    out += rect(426, 40, 4, 128, p['line']) + rect(350, 102, 160, 4, p['line']) + rect(334, 172, 192, 8, p['wood'])
    # Bookshelf, stacked books, pinned programming note and a trailing plant.
    for y in [76, 148]:
        out += rect(32, y, 140, 8, p['wood']) + rect(40, y+8, 4, 8, p['line']) + rect(156, y+8, 4, 8, p['line'])
    for i, (height, color) in enumerate([(32, '#d89855'), (40, '#adb6c4'), (28, '#7c9e89'), (36, '#f2c078')]):
        out += rect(44+i*20, 76-height, 14, height, color) + rect(48+i*20, 80-height, 3, height-8, p['bg'], opacity='.25')
    out += rect(44, 126, 60, 10, p['second']) + rect(40, 138, 76, 10, p['muted'])
    out += group(plant(p), 124, 97, .75)
    out += rect(206, 44, 76, 56, p['surface']) + text(218, 77, '{ }', 24, p['accent'])
    out += rect(238, 40, 12, 8, p['second'])
    # Chair behind the recognizable mascot, then the desk and laptop in front.
    out += rect(244, 166, 100, 100, p['surface']) + rect(252, 174, 84, 68, p['line'])
    out += group(tofu(), 228, 108, 1.15)
    out += rect(80, 234, 352, 16, p['wood']) + rect(80, 234, 352, 4, '#f2c078')
    out += rect(96, 250, 12, 48, p['wood']) + rect(404, 250, 12, 48, p['wood'])
    out += rect(290, 268, 8, 32, p['line']) + rect(266, 298, 56, 4, p['line'])
    # Pixel lamp and a self-contained animated cone of warm light; no filters.
    out += '<path d="M366 172L298 234h142l-54-62z" fill="#f2c078" class="lamp-glow" opacity=".1"/>'
    out += rect(404, 176, 4, 54, p['second']) + rect(384, 230, 44, 4, p['second'])
    out += '<path d="M408 180v-40h-26v12" stroke="#d89855" stroke-width="4" fill="none"/>'
    out += '<path d="M362 152h32v8h8v12h-48v-12h8z" fill="#f2c078"/>'
    out += rect(362, 172, 32, 4, '#fff0d5')
    # The lid faces Tofu: the viewer sees its back, not the terminal display.
    # Lid and base end at the tabletop (y=234), well above the floor (y=276).
    out += '<g class="typing">'+rect(228, 222, 12, 8, '#fff0d5')+rect(356, 222, 12, 8, '#fff0d5')+'</g>'
    out += rect(242, 176, 112, 54, '#697483') + rect(248, 182, 100, 42, '#414853')
    out += rect(248, 178, 100, 2, '#f2c078', **{'class':'screen'})
    # Tiny Tofu emblem on the rear shell, with no outward-facing screen content.
    out += rect(286, 196, 24, 16, '#d89855') + rect(290, 194, 16, 20, '#d89855')
    out += rect(290, 198, 16, 12, '#fff0d5')
    out += rect(293, 201, 2, 2, '#392d2a') + rect(301, 201, 2, 2, '#392d2a')
    out += rect(297, 205, 4, 2, '#392d2a') + rect(234, 230, 128, 4, '#adb6c4')
    # Mug, floor plant and a tiny floppy disk.
    out += rect(178, 214, 24, 20, '#fff0d5') + rect(202, 218, 8, 12, '#d89855') + rect(182, 214, 16, 4, '#886044')
    out += group(plant(p), 474, 236, 1.1)
    out += rect(114, 216, 28, 18, p['surface']) + rect(120, 218, 12, 6, p['muted'])
    return '<g shape-rendering="crispEdges">'+out+'</g>'


def hero(p, light=False, mobile=False):
    w, h = (600, 670) if mobile else (1200, 400)
    out = frame(w, h, p)
    x = 36 if mobile else 52
    out += text(x, 56, "TOFU'S CODING CORNER", 19 if mobile else 20, p['accent'], 'bold', letter_spacing='2')
    out += text(x, 118 if mobile else 144, "Hi, I'm Khanh.", 40 if mobile else 48, p['ink'], 'bold')
    out += text(x, 158 if mobile else 190, 'Code, learn, repeat.', 23, p['muted'])
    if mobile:
        out += text(x, 205, 'Developer in progress', 20, p['muted']) + text(x, 235, 'PTIT Hanoi', 20, p['muted'])
        out += group(room(p, light), 20, 298)
    else:
        out += text(x, 248, 'Developer in progress', 22, p['muted']) + text(x, 280, 'PTIT Hanoi', 22, p['muted'])
        out += group(room(p, light), 608, 30)
        out += rect(x, 328, 36, 4, p['second']) + text(x+50, 336, 'a little world, one commit at a time.', 15, p['muted'])
    return svg(w, h, 'Tofu coding in a cozy daytime room' if light else 'Tofu coding in a cozy nighttime room', out, True)


def profile(p, mobile=False):
    w, h = (600, 430) if mobile else (1200, 260)
    out = frame(w, h, p)
    out += text(32, 48, '01 / PLAYER PROFILE', 20, p['accent'], 'bold', letter_spacing='2')
    if mobile:
        out += group(tofu(), 428, 62, 1.35)
        out += text(32, 102, 'Khanh', 38, p['ink'], 'bold')
        out += text(32, 145, 'Developer', 22, p['ink']) + text(32, 175, 'in Progress', 22, p['ink'])
        rows = [('LOCATION', 'Hanoi, Vietnam'), ('EDUCATION', 'PTIT Hanoi'), ('MOTTO', 'Code, learn, repeat.')]
        for i, (label, value) in enumerate(rows):
            y = 240+i*64
            out += text(32, y, label, 16, p['muted']) + text(32, y+28, value, 23, p['ink'])
    else:
        out += group(tofu(), 28, 64, 1.65)
        out += text(214, 112, 'Khanh', 36, p['ink'], 'bold')
        out += text(214, 150, 'Developer in Progress', 22, p['ink'])
        out += text(214, 212, 'Code, learn, repeat.', 21, p['muted'])
        out += rect(666, 70, 2, 150, p['line'])
        out += text(710, 100, 'LOCATION', 16, p['muted']) + text(710, 132, 'Hanoi, Vietnam', 24, p['ink'])
        out += text(710, 180, 'EDUCATION', 16, p['muted']) + text(710, 212, 'PTIT Hanoi', 24, p['ink'])
    return svg(w, h, 'Player profile: Khanh, Developer in Progress, Hanoi, Vietnam, PTIT Hanoi. Code, learn, repeat.', out)


def heading(p, number, title, subtitle):
    out = rect(0, 0, 1200, 120, p['bg'])
    out += text(24, 48, number+' / '+title, 25, p['accent'], 'bold', letter_spacing='2')
    out += text(24, 84, subtitle, 21, p['muted'])
    out += rect(24, 112, 1152, 2, p['line'])
    return svg(1200, 120, title+'. '+subtitle, out)


def mobile_heading(p, number, title, subtitle):
    out = rect(0, 0, 600, 140, p['bg']) + text(24, 44, number+' / '+title, 24, p['accent'], 'bold')
    for i, line in enumerate(textwrap.wrap(subtitle, 38)):
        out += text(24, 82+i*27, line, 21, p['muted'])
    out += rect(24, 130, 552, 2, p['line'])
    return svg(600, 140, title+'. '+subtitle, out)


def embedded_badge(name, x, y, scale, prefix):
    data = (ASSETS/'badges'/f'{name}.svg').read_text(encoding='utf-8')
    badge = ET.fromstring(data)
    # Shields stores vector logos in base64 image elements. Unpack those into
    # native nested SVG paths in new compositions, preserving original badge files.
    for parent in list(badge.iter()):
        for index, child in enumerate(list(parent)):
            if child.tag != NS+'image':
                continue
            href = child.get('href') or child.get('{http://www.w3.org/1999/xlink}href', '')
            assert href.startswith('data:image/svg+xml;base64,'), name
            logo = ET.fromstring(base64.b64decode(href.split(',', 1)[1]))
            for attr in ['x', 'y', 'width', 'height', 'opacity']:
                if child.get(attr) is not None:
                    logo.set(attr, child.get(attr))
            parent.remove(child)
            parent.insert(index, logo)
    data = ET.tostring(badge, encoding='unicode')
    # Inline native SVG content instead of forbidden external SVG image references.
    for ident in re.findall(r'\bid="([^"]+)"', data):
        data = data.replace('id="'+ident+'"', 'id="'+prefix+'-'+ident+'"').replace('url(#'+ident+')', 'url(#'+prefix+'-'+ident+')')
    data = re.sub(r'^<svg\b', f'<svg x="{x}" y="{y}"', data, count=1)
    return group(data, scale=scale)


INVENTORY = [
    ('languages', 'LANGUAGES', ['c', 'cpp', 'java', 'python']),
    ('web-database', 'WEB & DATABASE', ['html', 'css', 'javascript', 'mysql', 'postgresql']),
    ('creative', 'CREATIVE GEAR', ['adobe-photoshop', 'adobe-premiere-pro']),
    ('tools', 'EVERYDAY TOOLS', ['git', 'github', 'vs-code', 'linux']),
]


def inventory(p, key, title, badges):
    out = frame(380, 176, p) + rect(24, 29, 8, 8, p['second'])
    out += text(44, 40, title, 18, p['ink'], 'bold') + rect(24, 58, 332, 2, p['line'])
    x, y = 24, 86
    for i, name in enumerate(badges):
        width = float(ET.parse(ASSETS/'badges'/f'{name}.svg').getroot().get('width'))
        if x+width > 356:
            x, y = 24, y+40
        out += embedded_badge(name, x, y, 1, key+str(i))
        x += width+8
    return svg(380, 176, title+': '+', '.join(badges), out)


def footer(p, mobile=False):
    w, h = (600, 290) if mobile else (1200, 220)
    out = frame(w, h, p)
    if mobile:
        out += group(group(tofu(), cls='bob'), 244, 8, 1.2)
        out += text(36, 188, '> session complete', 24, p['muted'])
        out += text(36, 232, '> see you in the next commit', 23, p['ink'])
        out += rect(438, 237, 12, 3, p['accent'], **{'class':'cursor'})
    else:
        out += group(group(tofu(), cls='bob'), 104, 42, 1.3)
        out += rect(260, 66, 12, 64, p['second']) + rect(244, 130, 44, 4, p['second'])
        out += '<path d="M240 42h44v8h8v16h-60V50h8z" fill="#f2c078"/>'
        out += text(356, 92, '> session complete', 26, p['muted'])
        out += text(356, 140, '> see you in the next commit', 27, p['ink'])
        out += rect(810, 146, 16, 4, p['accent'], **{'class':'cursor'})
        out += rect(1054, 72, 6, 18, p['second'], **{'class':'star'})+rect(1048, 78, 18, 6, p['second'])
    return svg(w, h, 'Tofu resting. Session complete. See you in the next commit.', out, True)


def write(name, content):
    (ASSETS/name).write_text(content, encoding='utf-8')


def picture(stem, alt, width='100%', mobile=True):
    sources = ''
    if stem in ['hero-animated', 'footer-animated']:
        if mobile:
            sources += f'    <source media="(prefers-reduced-motion: reduce) and (max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/{stem}-still-mobile-dark.svg" />\n'
            sources += f'    <source media="(prefers-reduced-motion: reduce) and (max-width: 600px)" srcset="assets/{stem}-still-mobile-light.svg" />\n'
        sources += f'    <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="assets/{stem}-still-dark.svg" />\n'
        sources += f'    <source media="(prefers-reduced-motion: reduce)" srcset="assets/{stem}-still-light.svg" />\n'
    if mobile:
        sources += f'    <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/{stem}-mobile-dark.svg" />\n'
        sources += f'    <source media="(max-width: 600px)" srcset="assets/{stem}-mobile-light.svg" />\n'
    sources += f'    <source media="(prefers-color-scheme: dark)" srcset="assets/{stem}-dark.svg" />\n'
    return f'<picture>\n{sources}    <img src="assets/{stem}-light.svg" alt="{escape(alt, quote=True)}" width="{width}" />\n  </picture>'


def snake_stills():
    for theme, source in [('light', 'contribution-snake.svg'), ('dark', 'contribution-snake-dark.svg')]:
        data = (ASSETS/source).read_text(encoding='utf-8')
        # Freeze the real generated calendar at its initial keyframe, preserving
        # the original contribution colors and path rather than inventing a grid.
        boundary = data.index('>')+1
        label = '<title>GitHub contributions, motion paused</title><desc>The real contribution calendar frozen at the initial animation frame.</desc>'
        data = data[:boundary]+label+data[boundary:]
        data = data.replace('</svg>', '<style>*{animation-play-state:paused!important;animation-delay:0s!important}</style></svg>')
        write('contribution-snake-still-'+theme+'.svg', data)


def build():
    for theme, p in THEMES.items():
        light = theme == 'light'
        for mobile in [False, True]:
            suffix = ('mobile-' if mobile else '')+theme+'.svg'
            hero_svg = hero(p, light, mobile)
            write('hero-animated-'+suffix, hero_svg)
            write('hero-animated-still-'+suffix, hero_svg.replace(MOTION, ''))
            write('player-profile-'+suffix, profile(p, mobile))
            footer_svg = footer(p, mobile)
            write('footer-animated-'+suffix, footer_svg)
            write('footer-animated-still-'+suffix, footer_svg.replace(MOTION, ''))
            for key, number, title, subtitle in [
                ('inventory', '02', 'INVENTORY', 'A few tools in my backpack.'),
                ('activity', '03', 'ACTIVITY LOG', 'Every commit is another step in the journey.'),
            ]:
                write(key+'-header-'+suffix, (mobile_heading if mobile else heading)(p, number, title, subtitle))
        for key, title, badges in INVENTORY:
            write('inventory-'+key+'-'+theme+'.svg', inventory(p, key, title, badges))
    readme = '<!-- Artwork: python scripts/build-pixel-world.py. Maintenance: docs/profile-maintenance.md. All images are local. -->\n\n'
    def panel(content):
        return '<p align="center">\n  '+content+'\n</p>\n\n'
    readme += '<!-- room-time:start -->\n'+panel(picture('hero-animated', "Tofu's coding corner. Hi, I'm Khanh. Developer in progress at PTIT Hanoi.")).rstrip()+'\n<!-- room-time:end -->\n\n'
    readme += panel(picture('player-profile', 'Player profile: Khanh; Developer in Progress; Hanoi, Vietnam; PTIT Hanoi; Code, learn, repeat.'))
    readme += panel(picture('inventory-header', 'Inventory — a few tools in my backpack.'))
    for pair in [INVENTORY[:2], INVENTORY[2:]]:
        cards = '\n  '.join(picture('inventory-'+key, title+': '+', '.join(badges), '380', False) for key, title, badges in pair)
        readme += panel(cards)
    readme += panel(picture('activity-header', 'Activity log — every commit is another step in the journey.'))
    snake_stills()
    readme += panel('<picture>\n    <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="assets/contribution-snake-still-dark.svg" />\n    <source media="(prefers-reduced-motion: reduce)" srcset="assets/contribution-snake-still-light.svg" />\n    <source media="(prefers-color-scheme: dark)" srcset="assets/contribution-snake-dark.svg" />\n    <img src="assets/contribution-snake.svg" alt="A tofu-colored snake following my actual GitHub contribution history" width="100%" />\n  </picture>')
    readme += '<!-- Contribution images and daily update workflow are preserved from the original profile. -->\n\n'
    readme += panel(picture('footer-animated', 'Session complete — see you in the next commit.'))
    readme += panel('<a href="https://www.linkedin.com/in/nguy%E1%BB%85n-ho%C3%A0ng-kh%C3%A1nh-undefined-b1a942389/"><img src="assets/badges/linkedin.svg" alt="Connect on LinkedIn" width="143" height="44" /></a>\n  <a href="mailto:nghoangkhanh67@gmail.com"><img src="assets/badges/email.svg" alt="Send Khanh an email" width="134" height="44" /></a>')
    (ROOT/'README.md').write_text(readme.rstrip()+'\n', encoding='utf-8')
    subprocess.run([sys.executable, str(ROOT/'scripts/update-room-time.py')], check=True)
    print('Generated themed pixel world assets and README; original assets and workflow preserved.')


if __name__ == '__main__':
    if sys.argv[1:] == ['--snake-stills-only']:
        snake_stills()
    else:
        build()
