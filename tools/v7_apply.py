"""v7: add the new entries (out/v7_new.json) translated with out/v7_batches/t*.py to the translation JSON.
  python out/v7_apply.py SRC DST
Notation in the batches: @XX battle buffer (\\\\XX), @?XX / @CC.. / @qo @qc single-backslash codes,
… game ellipsis, {M:Move} {I:Item} {A:Ability} official Italian names, ¶ new box (lines wrapped automatically).
Identical English originals get the same translation."""
import json, sys, re, glob, collections
sys.path.insert(0, '.')
sys.path.insert(0, 'out')
import eng_tools as ET

BS = chr(92)
NAMES = json.load(open('out/v7_names.json', encoding='utf-8'))


def expand(t):
    t = re.sub(r'\{([MIA]):([^}]+)\}', lambda m: full(m.group(2)), t)
    t = re.sub(r'@(\?[0-9A-F]{2}|CC(?:[0-9A-F]{2})+|q[oc])', lambda m: BS + m.group(1), t)
    t = re.sub(r'@([0-9A-F]{2})', lambda m: BS * 2 + m.group(1), t)
    return t.replace('…', BS + '.').replace("'", '{B4}')


FULL = {'Soft-Boiled': 'Covauova', 'Teleport': 'Teletrasporto', 'Throat Chop': 'Colpo Infernale',
        'Escape Rope': 'Fune di fuga'}


def full(name):
    if name in FULL:
        return FULL[name]
    v = NAMES.get(name.lower())
    assert v, 'nome non trovato: ' + name
    return v[1]


def main(src, dst):
    d = json.load(open(src, encoding='utf-8'))
    new = json.load(open('out/v7_new.json', encoding='utf-8'))
    T, DROP = {}, set()
    for f in sorted(glob.glob('out/v7_batches/t*.py')):
        ns = {}
        exec(open(f, encoding='utf-8').read(), ns)
        T.update(ns['T'])
        DROP |= ns.get('DROP', set())
    by_orig = {}
    for k in sorted(T):
        by_orig.setdefault(new[k]['original'], k)
    have = {x['id'] for x in d['entries']}
    # a text whose slot contains the start of another new text (suffix pointer) must not be written in place
    starts = sorted(int(x['address'], 16) for x in new)
    for x in new:
        a = int(x['address'], 16)
        inner = [s for s in starts if a < s < a + x['byte_length']]
        if inner:
            x['byte_length'] = min(inner) - a
    ok = bad = miss = 0
    for k, x in enumerate(new):
        if x['id'] in have:
            continue
        src_k = k if k in T else by_orig.get(x['original'])
        if src_k is None:
            miss += 1
            print('MANCA', k, repr(x['original'][:70]))
            continue
        orig = x['original'][1:-1]
        final, W = ET.layout(expand(T[src_k]), orig)
        p = []
        to, tf = collections.Counter(ET.tokens(orig)), collections.Counter(ET.tokens(final))
        if src_k in DROP:
            if tf - to:
                p.append(f'token in più {dict(tf - to)}')
        elif to != tf:
            p.append(f'token {dict(tf)} != {dict(to)}')
        back = ET.decode_pcs(ET.INJ.encode_text(ET.CM, final), 0, 4096).text
        if ET.norm_rt(back) != ET.norm_rt(final):
            p.append('carattere non codificabile')
        if any(ET.px(l.strip()) > W for l in ET.BREAKS.split(final) if l.strip()) and BREAKS_OK(orig):
            p.append('riga troppo larga')
        if p:
            bad += 1
            print('NO', k, '; '.join(p), repr(final))
            continue
        e = {kk: vv for kk, vv in x.items() if kk != 'source_kinds'}
        e['translation_source'] = orig
        e['translated'] = final
        e['manual_fix'] = 'v7'
        d['entries'].append(e)
        ok += 1
    # Missing pointer owners: a translated text can also be reached by script operands the extractor never listed
    # (other trainerbattle slots, bufferstring, preparemsg, loadpointer) -> the game showed the English original.
    orig_rom = open('rom/unbound.gba', 'rb').read()

    def safe_kind(s):
        r = orig_rom
        if r[s - 2:s] == b'\x0f\x00' or r[s - 1] == 0x67 or (r[s - 2] == 0x85 and r[s - 1] < 0x10):
            return True
        if r[s - 5] == 0xFA and r[s - 2:s] == b'\x03\x02':
            return True
        if any(r[s - k] == 0x5C and r[s - k + 1] <= 0x0C for k in range(6, 34, 2)):
            return True
        if s % 4 == 0:   # pointer table: neighbours are pointers too
            nb = [int.from_bytes(r[s + o:s + o + 4], 'little') >> 24 for o in (-4, 4)]
            return any(b in (8, 9) for b in nb)
        return False
    import numpy as np
    arr = np.frombuffer(orig_rom, dtype=np.uint8)
    w = (arr[:-3].astype(np.uint32) | (arr[1:-2].astype(np.uint32) << 8) | (arr[2:-1].astype(np.uint32) << 16)
         | (arr[3:].astype(np.uint32) << 24))
    pos = np.nonzero((w >= 0x08000000) & (w < 0x0A000000))[0]
    byval = {}
    for p, v in zip(pos.tolist(), (w[pos] - 0x08000000).tolist()):
        byval.setdefault(v, []).append(p)
    added = 0
    for x in d['entries']:
        if not (x.get('translated') or x.get('translated_fixed')) or not x.get('pointer_sources'):
            continue
        if x['category'] in ('pointer_texts',) or x.get('no_relocation'):
            continue
        a = int(x['address'], 16)
        known = {int(s, 16) for s in x['pointer_sources']}
        extra = [s for s in byval.get(a, []) if s not in known and safe_kind(s)]
        if extra:
            x['pointer_sources'] = x['pointer_sources'] + ['0x%X' % s for s in extra]
            added += len(extra)
    print('riferimenti mancanti aggiunti:', added)

    # v7b: English strings never extracted (romscan2), declared by address in out/v7_batches/x*.py
    from lib.pcs_text import decode_pcs
    by_id = {x['id']: x for x in d['entries']}
    xb = 0
    for f in sorted(glob.glob('out/v7_batches/x*.py')):
        ns = {}
        exec(open(f, encoding='utf-8').read(), ns)
        for a, text in ns.get('X', {}).items():
            eid = 'v7b_%07X' % a
            if eid in by_id:
                continue
            r = decode_pcs(orig_rom, a, 2048)
            srcs = [s for s in byval.get(a, []) if safe_kind(s)]
            assert srcs, f'0x{a:X}: nessun riferimento sicuro'
            orig = r.text
            final, W = ET.layout(expand(text), orig)
            to, tf = collections.Counter(ET.tokens(orig)), collections.Counter(ET.tokens(final))
            bad_tok = (tf - to) if a in ns.get('X_DROP', set()) else (tf != to)
            back = ET.decode_pcs(ET.INJ.encode_text(ET.CM, final), 0, 4096).text
            assert not bad_tok, f'0x{a:X} token {dict(tf)} != {dict(to)}'
            assert ET.norm_rt(back) == ET.norm_rt(final), f'0x{a:X} carattere non codificabile'
            battle = any(orig_rom[s - 5] == 0xFA for s in srcs) or 0x880000 <= a < 0xA50000
            e = {'id': eid, 'category': 'battle_messages' if battle else 'v7_texts', 'address': '0x%X' % a,
                 'pointer_sources': ['0x%X' % s for s in srcs], 'byte_length': r.byte_length,
                 'is_pointer_based': True, 'table_name': 'v7b', 'original': '"' + orig + '"',
                 'translation_source': orig, 'translated': final, 'manual_fix': 'v7b'}
            d['entries'].append(e)
            by_id[eid] = e
            xb += 1
        for eid, text in ns.get('R', {}).items():
            x = by_id[eid]
            orig = x['original'].strip('"')
            final, W = ET.layout(expand(text), orig)
            assert collections.Counter(ET.tokens(final)) == collections.Counter(ET.tokens(orig)), (eid, ET.tokens(final), ET.tokens(orig))
            if x.get('translated_fixed') or x.get('no_relocation') or x['category'] == 'pointer_texts' or not x.get('pointer_sources'):
                n = len(ET.INJ.encode_text(ET.CM, final))
                assert n <= x['byte_length'], (eid, 'slot fisso', n, x['byte_length'])
            if x.get('translated_fixed'):
                x['translated_fixed'] = final
            x['translated'] = final
            x['manual_fix'] = 'v7b'
            xb += 1
        # literal-pool / table owners the scanners can't prove: explicit, checked against the original ROM
        def owned(s, a):
            return s % 4 == 0 and int.from_bytes(orig_rom[s:s + 4], 'little') == a + 0x08000000
        for eid, srcs in ns.get('SRC', {}).items():
            x = by_id[eid]
            a = int(x['address'], 16)
            assert all(owned(s, a) for s in srcs), eid
            x['pointer_sources'] = x['pointer_sources'] + ['0x%X' % s for s in srcs if '0x%X' % s not in x['pointer_sources']]
            xb += 1
        for eid, text in ns.get('RELOC', {}).items():   # fixed slot too small -> relocatable text
            x = by_id[eid]
            a = int(x['address'], 16)
            assert x['pointer_sources'] and all(owned(int(s, 16), a) for s in x['pointer_sources']), eid
            x.pop('translated_fixed', None)
            x.pop('no_relocation', None)
            x['category'] = 'v7_texts'
            x['translated'] = expand(text)
            x['manual_fix'] = 'v7b'
            xb += 1
        for a, (text, srcs) in ns.get('XP', {}).items():
            eid = 'v7b_%07X' % a
            assert all(owned(s, a) for s in srcs) and eid not in by_id, hex(a)
            r = decode_pcs(orig_rom, a, 2048)
            final, W = ET.layout(expand(text), r.text)
            assert collections.Counter(ET.tokens(final)) == collections.Counter(ET.tokens(r.text)), hex(a)
            e = {'id': eid, 'category': 'v7_texts', 'address': '0x%X' % a, 'pointer_sources': ['0x%X' % s for s in srcs],
                 'byte_length': r.byte_length, 'is_pointer_based': True, 'table_name': 'v7b', 'original': '"' + r.text + '"',
                 'translation_source': r.text, 'translated': final, 'manual_fix': 'v7b'}
            d['entries'].append(e)
            by_id[eid] = e
            xb += 1
    print('v7b: testi aggiunti/riscritti:', xb)

    # Signposts: one direction (\au \ad \al \ar) per line like the English; the starting translation ran them together.
    ARROW = re.compile('(?=' + re.escape(BS) + 'a[udlr])')
    signs = 0
    for x in d['entries']:
        if x['category'] not in ('scripts', 'v7_texts', 'plain_scripts'):
            continue
        o = x['original'].strip('"')
        t = x.get('translated')
        if not t or x.get('translated_fixed') or not re.search(re.escape(BS) + 'a[udlr]', o):
            continue
        en_lines = [l for l in re.split('\n\n|\n|' + re.escape(BS) + 'l', o)]
        arrow_lines = [l for l in en_lines if re.match(re.escape(BS) + 'a[udlr]', l.strip())]
        if len(arrow_lines) < 2:
            continue
        flat = re.sub(r'\s+', ' ', t.replace('\n', ' ').replace(BS + 'l', ' ')).strip()
        parts = ARROW.split(flat)
        head, units = parts[0].strip(), [p.strip() for p in parts[1:]]
        if len(units) != len(arrow_lines):
            continue
        cur_lines = [l.strip() for l in re.split('\n|' + re.escape(BS) + 'l', t) if l.strip()]
        if all(any(l.startswith(u[:6]) for l in cur_lines) for u in units):
            continue                      # already one direction per line
        head_lines = []
        if head:
            q = head.find(BS + 'qo')
            head_lines = [head[:q].strip(), head[q:].strip()] if q > 0 else [head]
        lines = []
        for u in units:                    # wrap a long direction over two lines
            words, cur = u.split(' '), ''
            for wd in words:
                cand = (cur + ' ' + wd).strip()
                if ET.px(cand) > 208 and cur:
                    lines.append(cur)
                    cur = wd
                else:
                    cur = cand
            lines.append(cur)
        box_break = '\n\n' in o.split(arrow_lines[0])[0] if head_lines else False
        out = ''
        if head_lines:
            out = '\n'.join(head_lines[:2])
            out += '\n\n' if box_break else '\n'
        seq = lines if box_break or not head_lines else lines
        first = not (head_lines and not box_break)
        for k, l in enumerate(seq):
            if k == 0:
                out += l
            else:
                out += ('\n' if first and k == 1 else BS + 'l') + l
        m = ET.TRAIL.search(o)
        x['translated'] = out + (m.group(0) if m else '')
        signs += 1
    print('cartelli con una direzione per riga:', signs)

    # Lines wider than the box: the starting translation lost all line breaks in hundreds of texts.
    # Rewrap them (spaces become breaks, same byte count) at the original width, 2 lines per box.
    rewrap = 0
    for x in d['entries']:
        if x['category'] not in ('scripts', 'v7_texts', 'plain_scripts', 'pointer_texts'):
            continue
        o = x['original'].strip('"')
        if not ET.BREAKS.search(o.rstrip()):
            continue
        for k in ('translated', 'translated_fixed'):
            t = x.get(k)
            if not t or t.startswith('§'):
                continue
            W = ET.wrap_width(o)
            if max([ET.px(l.strip()) for l in ET.BREAKS.split(t) if l.strip()] + [0]) <= max(W, 216) + 4:
                continue
            flat = re.sub(' *¶ *', '¶', t.replace(BS + 'p', '¶').replace('\n\n', '¶').replace('\n', ' ').replace(BS + 'l', ' '))
            flat = re.sub(' +', ' ', flat).strip(' ¶')
            final, _ = ET.layout(flat, o)
            boxes = []
            for box in final.replace(BS + 'p', '\n\n').split('\n\n'):
                lines = re.split('\n|' + re.escape(BS + 'l'), box)
                boxes += ['\n'.join(lines[i:i + 2]) for i in range(0, len(lines), 2)]
            new = '\n\n'.join(boxes)
            if (k == 'translated_fixed' or x['category'] == 'pointer_texts') and len(ET.INJ.encode_text(ET.CM, new)) > int(x['byte_length']):
                continue
            x[k] = new
            rewrap += 1
    print('testi reimpaginati (righe troppo larghe):', rewrap)
    # one-line English originals whose Italian no longer fits on one line: split in balanced lines, 2 per box
    one = 0
    for x in d['entries']:
        if x['category'] not in ('scripts', 'v7_texts', 'plain_scripts') or x.get('translated_fixed'):
            continue
        o = x['original'].strip('"')
        t = x.get('translated')
        if not t or ET.BREAKS.search(o.rstrip()) or ET.BREAKS.search(t.rstrip()) or BS + 'btn' in t or '.com' in t:
            continue
        if ET.px(t) <= 216 or not re.search('[a-zà-ù]{3,}', t):
            continue
        words, lines, cur = t.split(' '), [], ''
        n_lines = -(-ET.px(t) // 200)
        target = ET.px(t) / n_lines
        for wd in words:
            cand = (cur + ' ' + wd).strip()
            if cur and (ET.px(cand) > 208 or (ET.px(cur) >= target and len(lines) < n_lines - 1)):
                lines.append(cur)
                cur = wd
            else:
                cur = cand
        lines.append(cur)
        x['translated'] = '\n\n'.join('\n'.join(lines[i:i + 2]) for i in range(0, len(lines), 2))
        one += 1
    print('frasi di una riga divise:', one)

    # Trainer texts (trainerbattle intro/defeat...) are shown with the auto-scroll field message: a scroll (\l) there
    # draws the next line over the previous ones. Regroup every box into 2-line boxes joined by new-box breaks
    # (same byte count: each \l becomes \n or \n\n -> FE or FB).
    rom = open('rom/unbound.gba', 'rb').read()

    def trainer_src(s):
        return any(rom[s - k] == 0x5C and rom[s - k + 1] <= 0x0F for k in range(6, 34, 2))
    regroup = 0
    for x in d['entries']:
        if x['category'] not in ('scripts', 'v7_texts', 'pointer_texts', 'plain_scripts'):
            continue
        if not any(trainer_src(int(s, 16)) for s in x.get('pointer_sources') or []):
            continue
        for k in ('translated', 'translated_fixed'):
            t = x.get(k)
            if not t or BS + 'l' not in t:
                continue
            boxes = []
            for box in t.replace(BS + 'p', '\n\n').split('\n\n'):
                lines = re.split('\n|' + re.escape(BS + 'l'), box)
                boxes += ['\n'.join(lines[i:i + 2]) for i in range(0, len(lines), 2)]
            x[k] = '\n\n'.join(boxes)
            regroup += 1
    print('frasi degli Allenatori senza scorrimento:', regroup)
    # Italian thousands separator: 1,000 -> 1.000 (same length, safe for fixed slots)
    sep = 0
    for x in d['entries']:
        for k in ('translated', 'translated_fixed'):
            t = x.get(k)
            if t and re.search(r'\d,\d{3}(?!\d)', t):
                x[k] = re.sub(r'(?<=\d),(?=\d{3}(?!\d))', '.', t)
                sep += 1
    print('separatori delle migliaia corretti:', sep)
    json.dump(d, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'v7: aggiunte {ok} | da rivedere {bad} | senza traduzione {miss} | totale voci {len(d["entries"])}')


def BREAKS_OK(orig):
    # single-line originals are not wrapped by layout(): only multi-line texts are width-checked
    return bool(ET.BREAKS.search(orig.rstrip()))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
