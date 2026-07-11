# dcs-conllu — a pinned mirror of the DCS CoNLL-U distribution

_Created: 14-06-2026 · Last updated: 11-07-2026_

This repository is a **faithful snapshot** of the CoNLL-U distribution of the
**Digital Corpus of Sanskrit (DCS)** by **Oliver Hellwig**. It exists so the large
corpus can live on GitHub (and be pinned by commit) without bloating the
[VisualDCS](https://github.com/gasyoun/VisualDCS) repository, which mounts it as a
git submodule at `src/DCS-data-2026/conllu`.

## Source & pin

| | |
|---|---|
| Upstream | <https://github.com/OliverHellwig/sanskrit> → `dcs/data/conllu` |
| Pinned commit | `04e0778d3dc971030229179e25eea043d06ff397` |
| Pin date | **2026-03-05** |
| Format epoch | UD-compliant since the **2022-08-09** upstream release |

## Contents

| Path | What |
|---|---|
| [`files/`](https://github.com/gasyoun/dcs-conllu/tree/main/files) | 270 texts / 15,900 `.conllu` files — one folder per text, one file per chapter (verified via `git ls-files`, 11-07-2026) |
| [`lookup/`](https://github.com/gasyoun/dcs-conllu/tree/main/lookup) | exactly 5 files: [`dictionary.csv`](https://github.com/gasyoun/dcs-conllu/blob/main/lookup/dictionary.csv) (`LemmaId → lemma`), [`word-senses.csv`](https://github.com/gasyoun/dcs-conllu/blob/main/lookup/word-senses.csv), [`sembank-relations.csv`](https://github.com/gasyoun/dcs-conllu/blob/main/lookup/sembank-relations.csv), [`sembank-attestations.xml`](https://github.com/gasyoun/dcs-conllu/blob/main/lookup/sembank-attestations.xml), [`chapter-info.xml`](https://github.com/gasyoun/dcs-conllu/blob/main/lookup/chapter-info.xml) |
| [`readme.md`](https://github.com/gasyoun/dcs-conllu/blob/main/readme.md) | **Upstream readme** — the authoritative description of the format, columns, and license; kept verbatim (do not edit — the refresh procedure below overwrites it from upstream) |

Per the upstream readme: **744,757 lines / 5,464,818 words**. Morphology is Universal
Dependencies (`UPOS` + `FEATS`); `HEAD`/`DEPREL` are populated only for chapters in the
**Vedic Treebank** (e.g. the `Ṛgveda` text folder under `files/`).

**Snapshot caveats (upstream readme vs. this snapshot).** The verbatim upstream
[`readme.md`](https://github.com/gasyoun/dcs-conllu/blob/main/readme.md) references two lookup
files that are **not present** in this snapshot: a `pos.csv` (POS-tag glossary) and a
`sembank-attestations.csv` — here the attestations ship as
[`sembank-attestations.xml`](https://github.com/gasyoun/dcs-conllu/blob/main/lookup/sembank-attestations.xml)
instead. These are upstream-readme/distribution discrepancies preserved as-is, not local edits.

## License & citation

Licensed **CC BY 4.0** (Oliver Hellwig). This repository redistributes the data under
those terms with attribution; it is not affiliated with or endorsed by the DCS.

```bibtex
@Manual{dcs,
  title  = {{The Digital Corpus of Sanskrit (DCS)}},
  author = {Hellwig, Oliver},
  year   = {2010--2024}
}
```

## Refreshing the snapshot

A companion script under [VisualDCS](https://github.com/gasyoun/VisualDCS)
(`src/DCS-data-2026/check_conllu_updates.py`) checks whether upstream has new commits to
`dcs/data/conllu` after the pin. To re-snapshot:

1. `git clone --depth 1 https://github.com/OliverHellwig/sanskrit`
2. Copy `sanskrit/dcs/data/conllu/*` over this repo's contents.
3. Commit; update the pin SHA/date above and in the VisualDCS docs + tracker baseline.
4. In VisualDCS: `git -C src/DCS-data-2026/conllu pull` and commit the bumped submodule pointer.

_Dr. Mārcis Gasūns_
