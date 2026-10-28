# How this repository was made (Bolivia)

This file is written by the build on 2026-10-28, the day the source data was retrieved. Everything below is enough to rebuild this repository hash for hash.

## Sources

| Source | Address | Retrieved | Requests | Licence |
| --- | --- | --- | ---: | --- |
| Gaceta Oficial del Estado Plurinacional de Bolivia (Internet Archive raw captures) | <https://www.gacetaoficialdebolivia.gob.bo> | 2026-10-28 | 6 | Marked "TEXTO DE CONSULTA" and "Derechos Reservados © Gaceta Oficial de Bolivia"; no open licence stated. |
| Tribunal Constitucional Plurinacional | <https://tcpbolivia.bo> | 2026-10-28 | 16 | No licence stated. |
| Cámara de Diputados | <https://diputados.gob.bo> | 2026-10-28 | 6 | No licence stated. |
| Procuraduría General del Estado | <https://www.procuraduria.gob.bo> | 2026-10-28 | 2 | No licence stated. |
| Other official sites probed (Presidencia, Órgano Judicial, SEPDEP, Senado, SILEP, OEP) | <https://www.presidencia.gob.bo> | 2026-10-28 | 7 | No licence stated. |

Every response is cached by the sha256 of its URL, and the table above lists every source with its retrieval date. Lexifina keeps its fetch scripts privately; `tools/parse.py` reads only the cache and writes `corpus.json`, so the same cache always gives the same corpus.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitucion` | Constitución Política del Estado | 4 | 2009-02-07 to 2023-12-28 |

The build made 4 commits:

| Commits | Kind |
| ---: | --- |
| 1 | first version of an act |
| 3 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `futuro`: laws not yet in force on 2026-10-28.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 4 laws in the record.
- 8 tags.

## Dates

Each commit is dated at noon (America/La_Paz) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Constitución Política del Estado art. 164.II: "La ley será de cumplimiento obligatorio desde el día de su publicación, salvo que en ella se establezca un plazo diferente para su entrada en vigencia." (art. 164.I: the law is published in the Gaceta Oficial immediately after promulgation). A law's own vigencia clause overrides this. http://www.gacetaoficialdebolivia.gob.bo/app/webroot/archivos/CONSTITUCION.pdf

## Commands, in order

```sh
# fill the cache from the sources listed above (network; Lexifina's fetch scripts are kept privately)
python -X utf8 tools/parse.py                  # cache -> corpus.json (no network)
python -X utf8 tools/build.py <folder> --repo <empty folder> --docs-date 2026-10-28
python -X utf8 tools/check_repo.py <repo> --corpus <folder>/corpus.json --write
python -X utf8 tools/build.py <folder> --repo <another empty folder> --docs-date 2026-10-28 --compare <repo>
```

In the main Lexifina repository these files live as follows:
- `fetch.py`, `parse.py` and `repo/`: in `scripts/bolivia-law/`.
- `build.py`, `check_repo.py` (`check.py` there) and `on.py`: in `scripts/gitlaw_common/`, with the corpus format in `SCHEMA.md`.

## Exact inputs

- `corpus.json` sha256 `f5df47b2789dacc92961a2b096afd645773262f588981c16b4e24718b923521c` (1281739 bytes)
- Script blob hashes (`git hash-object`):

| Script | Blob |
| --- | --- |
| build.py | `393620efbfbe0a04540926b2d8f0a75ed749d600` |
| check.py | `741bd38ee6a4a25cfcecc28ccb2b93ce4e8b3fb2` |
| on.py | `668b24bbcd37efdfa1b60429c0d2b2c940ca9fff` |
| fetch.py | `b754b5499c7caca45440fe24abebca17763ccf1c` |
| parse.py | `90f5f38dead53d1aeff52b3a6ddc0fca613cb5da` |

- Tools:
  - Python 3.14.0
  - git version 2.52.0.windows.1
  - curl 8.21.0 (Windows) libcurl/8.21.0 Schannel zlib/1.3.2 WinIDN WinLDAP

## Checks

Not yet run for this build.

Not yet run for this build.

These results are from the check run on the build before this one, from the same corpus.

## Decisions made by hand

- The Constitution's articles and transitional, abrogating and final provisions are taken from the Gaceta Oficial's texto de consulta (pinned Internet Archive capture of 6 October 2026), because the Gaceta is the official journal.
- The Gaceta text has no preamble, so the preamble is taken from the Tribunal Constitucional Plurinacional's 2023 edition; parse.py stops unless it equals the Cámara de Diputados edition ignoring whitespace.
- Every article of the Gaceta text is compared, ignoring whitespace, case and quote/dash style, with the TCP and Diputados editions; the result is in crosscheck.json and verification notes in PROGRESS.md.
- The Constitution is one version as enacted, in force 7 February 2009 under its disposición final (in force on publication in the Gaceta Oficial) and credited to its approving referendum of 25 January 2009 as promulgated.
- The Constitution's words have not been amended since 2009, so the three later events (the rejected 2016 referendum, SCP 0084/2017 and SCP 1010/2023-S4) are recorded as versions with identical text, each credited to the provisions it concerns so that it gets a commit marked Words-changed: no; their dates are the vote and the decision dates.
- The facts of those events are taken only from SCP 1010/2023-S4 and CIDH Informe 121/24, both hosted by the Procuraduría General del Estado; vote counts and the number of the reform law are not stated because no official source for them was read.
- Headings (Parte, Título, Capítulo, Sección) are kept in one structure file, estructura.md, with the first article under each, so that article files hold only article text.
- Typesetting is normalised once: ligature glyphs from the TCP PDF, NBSP, soft hyphens, quote and dash styles; page numbers and running headers are dropped.
- Cross-check of 412 units (every article, and the closing provisions as one block) against the TCP and Diputados editions: the Gaceta wording agrees with at least one of them everywhere (0 units where both disagree with it).
- 14 wording differences occur in one other edition only (shown without spaces as ...context[Gaceta>other]context...): art. 5, diputados: ...llawaya,mach[i>e]neri,mar...; art. 12, tcp: ...gablesentres[i>í]....; art. 16, tcp: ...dadalimentar[í>i]a,atravé...; art. 20, diputados: ...choshumanos,[>20]nosonobj...; art. 142, tcp: ...tranjerosque[seencuentrenen>]unadelas...; art. 169, diputados: ...rlapresident[e>a]oelpresi...; art. 211, diputados: ...spropios,sed[e>é]estricto...; art. 284, diputados: ...onesopueblos[>_]indígena...; art. 298, tcp: ...ndoalcanceam[a>á]sdeundep...; art. 390, tcp: ...osyporlaseco[>r]regiones...; art. 402, diputados: ...bligaciónde:[1>i].fomenta...; art. 402, tcp: ...dadalimentar[í>i]ayproduc...; art. 402, diputados: ...dioambiente.[2>ii].promove...; closing provisions, tcp: ...sderechospre[->]constitu....
- In 47 places, in art. 108, art. 144, art. 150, art. 156, art. 178, art. 182, art. 298, art. 299, art. 300, art. 302, art. 304, art. 316, art. 410, both other editions print punctuation the Gaceta text lacks (mostly a period after a list item); the Gaceta text is kept as printed.

## What AI did and did not do

The fetch, parse and check scripts were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above, through code that anyone can rerun.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- none: no model wrote, summarised or corrected legal text. The parser and this metadata were written with a coding assistant (Claude) and every value was read from the official sources named.
