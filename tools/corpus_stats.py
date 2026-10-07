#!/usr/bin/env python3
"""Corpus statistics for the DCS CoNLL-U dump (gasyoun/dcs-conllu).

One deterministic single pass over ./files/**/*.conllu producing:
  stats/lemma_freq_full.tsv          - frequency dictionary (lemma x UPOS)
  stats/upos_xpos_distribution.tsv   - POS distributions
  stats/feats_distribution.tsv       - morphological feature values
  stats/sandhi_junctions.tsv         - sandhi junction signatures (left-end x right-start chars)
  stats/text_distribution.tsv        - per-text distributions
  stats/summary.md                   - key tables + totals

Stdlib only. Usage: python3 tools/corpus_stats.py [--files-dir files] [--out stats]
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

RANGE_RE = re.compile(r"^(\d+)-(\d+)$")
WORD_RE = re.compile(r"^\d+$")


def parse_misc(misc: str) -> dict:
    out = {}
    if misc and misc != "_":
        for part in misc.split("|"):
            if "=" in part:
                k, v = part.split("=", 1)
                out[k] = v
            else:
                out[part] = True
    return out


VOWELS = set("aAiIuUeOoāĀīĪūŪṛṚṝṞḷḸḹḹ")


def junction_class(left: str, right: str) -> str:
    """Coarse deterministic sandhi class label for a junction signature."""
    if left == "ḥ":
        return "visarga-final"
    if left == "ṃ":
        return "anusvāra-final"
    if left in ("s", "r", "ṣ", "ś", "s̄"):
        return "sibilant/r-final"
    if left in VOWELS and right in VOWELS:
        return "vowel+vowel (hiatus)"
    if left in VOWELS:
        return "vowel-final"
    if right in VOWELS:
        return "vowel-initial"
    return "consonant+consonant"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files-dir", default="files")
    ap.add_argument("--out", default="stats")
    args = ap.parse_args()

    files_dir = Path(args.files_dir)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()

    # aggregates
    lemma_freq: Counter = Counter()          # (lemma, upos) -> word count
    upos_c: Counter = Counter()
    xpos_c: Counter = Counter()
    feats_c: Counter = Counter()             # (attr, value) -> count
    junctions: Counter = Counter()           # (left_char, right_char) -> count
    junction_label: dict = {}                # (l, r) -> class label
    texts: dict = defaultdict(lambda: {
        "chapters": 0, "sentences": 0, "tokens": 0, "words": 0,
        "sandhi_groups": 0, "junctions": 0, "lemmas": set(),
        "unsandhied_words": 0, "wordsem_words": 0,
    })

    n_files = 0
    n_sentences = 0
    n_range_tokens = 0
    n_word_rows = 0
    n_single_tokens = 0
    n_sandhi_groups = 0
    n_junctions = 0
    misc_flag_c: Counter = Counter()

    for text_dir in sorted(p for p in files_dir.iterdir() if p.is_dir()):
        text_name = text_dir.name
        tstat = texts[text_name]
        for conllu in sorted(text_dir.glob("*.conllu")):
            n_files += 1
            tstat["chapters"] += 1
            # active multiword-token group: {"end": <range end id>, "words": [(form, unsandhied), ...]}
            group = None
            with conllu.open(encoding="utf-8") as fh:
                for raw in fh:
                    line = raw.rstrip("\n")
                    if not line:
                        group = None            # sentence boundary closes the group
                        continue
                    if line.startswith("#"):
                        if line.startswith("# sent_id"):
                            n_sentences += 1
                            tstat["sentences"] += 1
                        continue
                    cols = line.split("\t")
                    if len(cols) < 10:
                        continue
                    wid, form = cols[0], cols[1]
                    lemma, upos, xpos, feats = cols[2], cols[3], cols[4], cols[5]
                    misc = cols[9]

                    m = RANGE_RE.match(wid)
                    if m:
                        # new multiword (sandhi) surface token closes any open group
                        group = {"end": int(m.group(2)), "words": []}
                        n_range_tokens += 1
                        n_sandhi_groups += 1
                        tstat["tokens"] += 1
                        tstat["sandhi_groups"] += 1
                        continue

                    if not WORD_RE.match(wid):
                        continue  # empty nodes etc.

                    n_word_rows += 1
                    tstat["words"] += 1
                    mflag = parse_misc(misc)
                    if lemma != "_":
                        lemma_freq[(lemma, upos)] += 1
                        tstat["lemmas"].add(lemma)
                    upos_c[upos] += 1
                    xpos_c[xpos] += 1
                    if "Unsandhied" in mflag:
                        tstat["unsandhied_words"] += 1
                    if "WordSem" in mflag:
                        tstat["wordsem_words"] += 1
                    for k in mflag:
                        misc_flag_c[k] += 1
                    if feats and feats != "_":
                        for fv in feats.split("|"):
                            if "=" in fv:
                                a, v = fv.split("=", 1)
                                feats_c[(a, v)] += 1

                    word_str = mflag.get("Unsandhied") or form
                    if group is not None and int(wid) <= group["end"]:
                        if group["words"]:
                            prev = group["words"][-1]
                            l = prev[-1] if prev else "?"
                            r = word_str[0] if word_str else "?"
                            junctions[(l, r)] += 1
                            n_junctions += 1
                            tstat["junctions"] += 1
                            junction_label.setdefault((l, r), junction_class(l, r))
                        group["words"].append(word_str)
                    else:
                        group = None            # word outside the group = standalone token
                        n_single_tokens += 1
                        tstat["tokens"] += 1

    elapsed = time.time() - t0

    # ---- write outputs
    def w(path: Path, rows, header: str) -> None:
        with path.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(header + "\n")
            for row in rows:
                fh.write("\t".join(str(c) for c in row) + "\n")

    rows = sorted(lemma_freq.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1]))
    total_lemma_tokens = sum(lemma_freq.values())
    w(out_dir / "lemma_freq_full.tsv",
      [(i + 1, lem, upos, cnt, f"{cnt / total_lemma_tokens:.6f}")
       for i, ((lem, upos), cnt) in enumerate(rows)],
      "rank\tlemma\tupos\tcount\tshare")

    w(out_dir / "upos_xpos_distribution.tsv",
      [("UPOS", u, c, f"{c / n_word_rows:.6f}") for u, c in upos_c.most_common()] +
      [("XPOS", x, c, f"{c / n_word_rows:.6f}") for x, c in xpos_c.most_common()],
      "axis\ttag\tcount\tshare")

    w(out_dir / "feats_distribution.tsv",
      [(a, v, c, f"{c / n_word_rows:.6f}")
       for (a, v), c in sorted(feats_c.items(), key=lambda kv: (kv[0][0], -kv[1], kv[0][1]))],
      "attribute\tvalue\tcount\tshare_of_words")

    jrows = sorted(junctions.items(), key=lambda kv: -kv[1])
    w(out_dir / "sandhi_junctions.tsv",
      [(l, r, junction_label.get((l, r), junction_class(l, r)), c, f"{c / max(n_junctions, 1):.6f}")
       for (l, r), c in jrows],
      "left_end\tright_start\tclass\tcount\tshare")

    w(out_dir / "text_distribution.tsv",
      [(t, s["chapters"], s["sentences"], s["tokens"], s["words"], len(s["lemmas"]),
        s["sandhi_groups"], s["junctions"],
        f"{s['unsandhied_words'] / max(s['words'], 1):.4f}",
        f"{s['wordsem_words'] / max(s['words'], 1):.4f}")
       for t, s in sorted(texts.items(), key=lambda kv: -kv[1]["words"])],
      "text\tchapters\tsentences\ttokens\twords\tunique_lemmas\tsandhi_groups\tjunctions\tunsandhied_cov\twordsem_cov")

    # summary.md
    top_lemmas = rows[:50]
    L = []
    L.append("# DCS-conllu corpus statistics\n")
    L.append("_Generated by `tools/corpus_stats.py` (deterministic, stdlib-only, single pass). "
             f"Run time {elapsed:.1f}s. All numbers recomputed from `files/` in this repo._\n")
    L.append("## Totals\n")
    L.append("| metric | value |")
    L.append("|---|---|")
    L.append(f"| texts | {len(texts)} |")
    L.append(f"| chapter files | {n_files} |")
    L.append(f"| sentences | {n_sentences:,} |")
    L.append(f"| surface tokens (strings) | {n_range_tokens + n_single_tokens:,} |")
    L.append(f"| — of which sandhi-univerbated groups | {n_sandhi_groups:,} "
             f"({n_sandhi_groups / max(n_range_tokens + n_single_tokens, 1) * 100:.1f}%) |")
    L.append(f"| annotated words | {n_word_rows:,} |")
    L.append(f"| sandhi junctions (internal boundaries) | {n_junctions:,} |")
    L.append(f"| unique lemma×POS entries | {len(lemma_freq):,} |")
    L.append(f"| lemma-annotated tokens | {total_lemma_tokens:,} |")
    L.append(f"| distinct junction signatures | {len(junctions):,} |\n")

    L.append("## Top 50 lemmas\n")
    L.append("| rank | lemma | UPOS | count | share |")
    L.append("|---|---|---|---|---|")
    for i, ((lem, upos), cnt) in enumerate(top_lemmas):
        L.append(f"| {i+1} | {lem} | {upos} | {cnt:,} | {cnt/total_lemma_tokens:.4%} |")
    L.append("")

    L.append("## UPOS distribution\n")
    L.append("| UPOS | count | share |")
    L.append("|---|---|---|")
    for u, c in upos_c.most_common():
        L.append(f"| {u} | {c:,} | {c/n_word_rows:.4%} |")
    L.append("")

    L.append("## Top 30 sandhi junction signatures\n")
    L.append("(left_end = last char of the preceding word inside a multiword token, "
             "right_start = first char of the next word; from sandhi-univerbated groups.)\n")
    L.append("| left_end | right_start | class | count | share |")
    L.append("|---|---|---|---|---|")
    for (l, r), c in jrows[:30]:
        L.append(f"| {l} | {r} | {junction_label.get((l, r), junction_class(l, r))} | {c:,} | {c/max(n_junctions,1):.4%} |")
    L.append("")

    L.append("## Junction classes (aggregated)\n")
    cls_c = Counter()
    for (l, r), c in junctions.items():
        cls_c[junction_label.get((l, r), junction_class(l, r))] += c
    L.append("| class | count | share |")
    L.append("|---|---|---|")
    for cl, c in cls_c.most_common():
        L.append(f"| {cl} | {c:,} | {c/max(n_junctions,1):.4%} |")
    L.append("")

    L.append("## Morphology: top 40 feature values\n")
    L.append("| attribute | value | count | share of words |")
    L.append("|---|---|---|---|")
    for (a, v), c in sorted(feats_c.items(), key=lambda kv: -kv[1])[:40]:
        L.append(f"| {a} | {v} | {c:,} | {c/n_word_rows:.4%} |")
    L.append("")

    L.append("## Top 20 texts by annotated words\n")
    L.append("| text | chapters | sentences | tokens | words | unique lemmas | sandhi groups | unsandhied cov. |")
    L.append("|---|---|---|---|---|---|---|---|")
    for t, s in sorted(texts.items(), key=lambda kv: -kv[1]["words"])[:20]:
        L.append(f"| {t} | {s['chapters']} | {s['sentences']:,} | {s['tokens']:,} | {s['words']:,} | "
                 f"{len(s['lemmas']):,} | {s['sandhi_groups']:,} | "
                 f"{s['unsandhied_words']/max(s['words'],1):.2%} |")
    L.append("")

    L.append("## MISC flag coverage\n")
    L.append("| flag | words | share |")
    L.append("|---|---|---|")
    for k, c in misc_flag_c.most_common():
        L.append(f"| {k} | {c:,} | {c/n_word_rows:.4%} |")
    L.append("")

    (out_dir / "summary.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")

    print(f"files={n_files} sentences={n_sentences} words={n_word_rows} "
          f"tokens={n_range_tokens + n_single_tokens} sandhi_groups={n_sandhi_groups} "
          f"junctions={n_junctions} lemmas={len(lemma_freq)} elapsed={elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
