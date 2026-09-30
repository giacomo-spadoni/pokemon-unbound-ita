"""Phase 3 - dialogue (category 'scripts') review tools.

  python out/dlg_tools.py dump <start> [count]     -> print dialogues in ROM order for review
  python out/dlg_tools.py apply SRC DST            -> validate + apply out/dlg_batches/d*.py
Both accept --group generic|story: restrict to one group (out/dlg_generic_ids.json / dlg_story_ids.json,
built by out/dlg_classify.py). Indices are always the global positions of dlg_order.json (stable).
  dump --group generic <start> [count]  -> <start> counts positions inside the group; printed index is global
  apply --group generic SRC DST         -> batch entries outside the group are skipped (and counted)

Batch files define T = {index: 'italian text'} (index = position printed by dump).
Same text conventions as out/eng_tools.py:
  ¶ = new text box, lines are wrapped automatically at the original box width,
  '§' prefix = manual layout (¶ box, ⏎ newline, ↓ scroll), {B4} = apostrophe, '\\.' = ellipsis.
Dialogues are relocatable, so there is no byte limit per entry - but keep Italian about as long
as the current one: total free ROM space is limited (check 'Remaining free bytes' after build)."""
import json, re, sys, glob, os
sys.path.insert(0, '.')
sys.path.insert(0, 'out')
import eng_tools as ET

SRC_DEFAULT = 'out/it-eng.json'
ORDER_FILE = 'out/dlg_order.json'


def order(src=SRC_DEFAULT):
    if not os.path.exists(ORDER_FILE):
        E = json.load(open(src, encoding='utf-8'))['entries']
        xs = [x for x in E if x['category'] == 'scripts' and x.get('translated') and not x.get('manual_fix')]
        xs.sort(key=lambda x: int(x['address'], 16))
        json.dump([x['id'] for x in xs], open(ORDER_FILE, 'w'))
    return json.load(open(ORDER_FILE))


def group_ids(group):
    if not group:
        return None
    return json.load(open(f'out/dlg_{group}_ids.json'))


def dump(start, count=180, src=SRC_DEFAULT, group=None):
    ids = order(src)
    sel = group_ids(group) or list(range(len(ids)))
    E = {x['id']: x for x in json.load(open(src, encoding='utf-8'))['entries']}
    print(f'# dialoghi {start}..{min(len(sel), start + count) - 1} di {len(sel)}' + (f' (gruppo {group}; indici globali)' if group else ''))
    for n in sel[start:start + count]:
        x = E[ids[n]]
        BS = chr(92)
        o = x['original'].strip('"').replace('\n\n', '¶').replace('\n', ' ').replace(BS + 'l', ' ').replace(BS + 'p', '¶')
        t = (x.get('translated_fixed') or x['translated']).replace('\n\n', '¶').replace('\n', ' ').replace(BS + 'l', ' ')
        fixed = ' [SPAZIO FISSO %d byte]' % (int(x['byte_length']) - 1) if x.get('translated_fixed') or not x.get('pointer_sources') else ''
        print(f"{n}|{x['address']}{fixed}\n  EN {o}\n  IT {t}")


def apply(src, dst, group=None):
    ids = order(src)
    inside = set(group_ids(group)) if group else None
    d = json.load(open(src, encoding='utf-8'))
    by = {x['id']: x for x in d['entries']}
    T = {}
    for f in sorted(glob.glob('out/dlg_batches/d*.py')):
        ns = {}
        exec(open(f, encoding='utf-8').read(), ns)
        T.update(ns['T'])
    ok = bad = skipped = 0
    grow = 0
    debug = set(json.load(open('out/dlg_debug_ids.json'))) if os.path.exists('out/dlg_debug_ids.json') else set()
    for n, text in sorted(T.items()):
        if n in debug:
            print(f'NO {n}: testo escluso (debug/crediti/Sandbox): non si tocca')
            bad += 1
            continue
        if inside is not None and n not in inside:
            skipped += 1
            continue
        x = by[ids[n]]
        orig = x['original'].strip('"')
        final, W = ET.layout(text, orig)
        size = len(ET.INJ.encode_text(ET.CM, final))
        old = len(ET.INJ.encode_text(ET.CM, x.get('translated_fixed') or x['translated']))
        problems = []
        fixed = bool(x.get('translated_fixed')) or not x.get('pointer_sources') or x.get('no_relocation')
        if fixed and size > int(x['byte_length']):
            problems.append(f'spazio fisso: {size}>{x["byte_length"]} byte')
        if ET.tokens(final) != ET.tokens(orig):
            problems.append(f'token {ET.tokens(final)} != {ET.tokens(orig)}')
        back = ET.decode_pcs(ET.INJ.encode_text(ET.CM, final), 0, 4096).text
        if ET.norm_rt(back) != ET.norm_rt(final):
            problems.append(f'carattere non codificabile: {back!r}')
        lines = [l for l in ET.BREAKS.split(final) if l.strip()]
        if not text.startswith('§') and any(ET.px(l.strip()) > W for l in lines):
            problems.append('riga troppo larga')
        if problems:
            bad += 1
            print(f'NO {n} {ids[n]}: {"; ".join(problems)}\n   EN {orig!r}\n   IT {final!r}')
            continue
        x['translated'] = final
        if x.get('translated_fixed'):
            x['translated_fixed'] = final
        x['manual_fix'] = 'phase3-dialogue'
        grow += size - old
        ok += 1
    json.dump(d, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'applicati {ok} | da rivedere {bad} | variazione byte totale {grow:+d} | dialoghi in lista {len(ids)}' + (f' | fuori gruppo {group} saltati {skipped}' if group else ''))


if __name__ == '__main__':
    args = sys.argv[1:]
    grp = None
    if '--group' in args:
        k = args.index('--group')
        grp = args[k + 1]
        assert grp in ('generic', 'story'), grp
        del args[k:k + 2]
    if args[0] == 'dump':
        dump(int(args[1]), int(args[2]) if len(args) > 2 else 180, group=grp)
    else:
        apply(args[1], args[2], group=grp)
