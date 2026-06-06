# dcs-conllu — a pinned mirror of the DCS CoNLL-U distribution

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
| `files/` | 270 texts / 15,900 `.conllu` files — one folder per text, one file per chapter |
| `lookup/` | `dictionary.csv` (`LemmaId → lemma`), `word-senses.csv`, `sembank-relations.csv`, `sembank-attestations.xml`, `chapter-info.xml` |
| `readme.md` | **Upstream readme** — the authoritative description of the format, columns, and license |

Per the upstream readme: **744,757 lines / 5,464,818 words**. Morphology is Universal
Dependencies (`UPOS` + `FEATS`); `HEAD`/`DEPREL` are populated only for chapters in the
**Vedic Treebank** (e.g. `files/Ṛgveda`).

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

The companion script `VisualDCS/src/DCS-data-2026/check_conllu_updates.py` checks whether
upstream has new commits to `dcs/data/conllu` after the pin. To re-snapshot:

1. `git clone --depth 1 https://github.com/OliverHellwig/sanskrit`
2. Copy `sanskrit/dcs/data/conllu/*` over this repo's contents.
3. Commit; update the pin SHA/date above and in the VisualDCS docs + tracker baseline.
4. In VisualDCS: `git -C src/DCS-data-2026/conllu pull` and commit the bumped submodule pointer.
