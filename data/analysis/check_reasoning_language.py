import json, glob, re
from collections import defaultdict

def japanese_fraction(text):
    if not text:
        return None
    # Hiragana, Katakana, CJK Unified Ideographs (covers kanji)
    jp_chars = re.findall(r'[぀-ヿ一-鿿]', text)
    # Rough denominator: all "letter-like" chars (jp + ascii letters)
    letters = re.findall(r'[぀-ヿ一-鿿A-Za-z]', text)
    if not letters:
        return None
    return len(jp_chars) / len(letters)

by_cond = defaultdict(list)

for f in sorted(glob.glob("data/raw/qwen3_5_local/*.json")):
    if f.endswith(".grade.json"):
        continue
    d = json.load(open(f, encoding="utf-8"))
    thinking = d.get("thinking", "")
    frac = japanese_fraction(thinking)
    cond = d["_meta"]["condition"]
    if frac is not None:
        by_cond[cond].append(frac)

order = ["en_human", "ja_raw", "ja_directive", "mt_en"]
print("Fraction of 'letter' characters in the THINKING trace that are Japanese")
print("(0.0 = thinking entirely in English/roman script, 1.0 = entirely Japanese)\n")
for c in order:
    vals = by_cond[c]
    if not vals:
        print(f"  {c:14s} no data")
        continue
    avg = sum(vals) / len(vals)
    mostly_jp = sum(1 for v in vals if v > 0.5)
    mostly_en = sum(1 for v in vals if v < 0.1)
    print(f"  {c:14s} n={len(vals):2d}  avg_jp_fraction={avg:.2f}  "
          f"mostly-Japanese={mostly_jp}  mostly-English={mostly_en}")
