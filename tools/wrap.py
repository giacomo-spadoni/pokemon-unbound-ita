"""Pixel-accurate word wrapping for the FireRed/Unbound normal font."""
import re, sys
sys.path.insert(0, '.')
from lib.gen3_font import text_pixel_width
from lib.pcs_text import Charmap

CM = Charmap('it')
LIMITS = {  # category: (max pixels per line, max lines)
    'move_descriptions': (122, 5),
    'item_descriptions': (196, 3),
    'pokedex_descriptions': (224, 3),
    'ability_descriptions': (191, 1),
}


def px(s):
    return text_pixel_width(s, CM)


def wrap(text, maxpx):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        cand = (cur + ' ' + w) if cur else w
        if px(cand) <= maxpx:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(text, cat):
    maxpx, maxl = LIMITS[cat]
    lines = wrap(text, maxpx)
    ok = len(lines) <= maxl and all(px(l) <= maxpx for l in lines)
    return '\n'.join(lines), ok, len(lines)


def check(text, cat):
    maxpx, maxl = LIMITS[cat]
    lines = re.split(r'\n|\\n', text)
    return len(lines) <= maxl and all(px(l) <= maxpx for l in lines)
