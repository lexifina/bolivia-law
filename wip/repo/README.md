# Bolivia: law history in git

The law of Bolivia as a git history. Each provision is one file, each law gets one commit on the day it took effect, and the law that made each change is the commit's author. `git blame` names the law behind every paragraph, `git log` lists every event on an article, and checking out a date gives the text in force that day.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `bo/`.

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitucion/` | Constitución Política del Estado (2009) | 4 (1 text) | As enacted, in force 7 February 2009. Its words have not been amended since. Three later events that changed no words are recorded as commits marked `Words-changed: no`: the rejected referendum of 21 February 2016 on art. 168, SCP 0084/2017 and SCP 1010/2023-S4 |
| `codigo-civil/` | Código Civil (Decreto Ley 12760 of 1975) | 1 | Today's consolidated text only, as SILEP published it (Internet Archive capture of 24 February 2024): 1,570 articles. One commit, "oldest version available", dated 2024-02-24. Its message names the 7 amending laws SILEP lists (1992 to 2010) and the 18 articles each last changed. Earlier wordings are not available as text |

The per-act `README.md` in each folder lists every provision.

**Why the Código Civil has one version.** SILEP, the Vice Presidency's legal information system, shows the Code's current wording and, on each changed article, only the last law that changed it. It never shows the earlier wording, and the 1975 Gaceta edition exists only as scanned pages, which this record does not transcribe. So the Code enters the history once, on the day the source first attests that text.

**Why the history is short.** Bolivia's Constitution of 2009 has never been amended in its words. The only attempt was a partial reform of art. 168, which would have allowed a second consecutive re-election, and voters rejected it in the referendum of 21 February 2016. A record that showed more versions would be inventing them.

## A lawyer's questions as git commands

| Question | Command |
| --- | --- |
| What did art. 168 of the Constitution say on 1 January 2017? | `python tools/en_vigor_el.py 2017-01-01 constitucion 168` |
| The same, with raw git (bash) | `git show $(git rev-list -1 --before="2017-01-01T23:59:59Z" main -- constitucion/art-168.md):constitucion/art-168.md` |
| The same, in PowerShell | `$r = git rev-list -1 --before="2017-01-01T23:59:59Z" main -- constitucion/art-168.md; git show "$($r):constitucion/art-168.md"` |
| Which law wrote each paragraph of art. 168? | `git blame constitucion/art-168.md` |
| Every event on art. 168, including the ones that changed no words | `git log --reverse --format="%ad %an: %s" --date=short --grep="168" main` (a commit that changed no words touches no file, so `git log -- <file>` does not list it) |
| Every change to an article, word by word | `git log -p --word-diff constitucion/art-168.md` |
| Every law and event in the record, in order | `git log --reverse --format="%ad %an" --date=short main` |
| Everything one law or ruling did | `git show law/scp-0084-2017` (tags `law/<key>` mark each law's commit) |
| The whole Constitution on a date | `python tools/en_vigor_el.py 2010-01-01 constitucion` |
| The act on the day of a version | `git show constitucion/2009-02-07` (tags `<act>/<in-force day>`) |
| One article of the Código Civil | `python tools/en_vigor_el.py 2025-01-01 codigo-civil 1570` |
| Laws passed but not yet in force | `git log main..futuro` (none yet) |

After a rebuild, refresh tags with `git fetch --force --tags`: a plain fetch keeps stale tags.

## Dates

- Each commit is dated at **noon, America/La_Paz, on the day the change took effect** (the in-force date). Enactment and publication dates are trailers (`Enacted:`, `Published:`), and the in-force day is in `In-force:`, which the tools read.
- **Default rule.** Constitución art. 164.II: "La ley será de cumplimiento obligatorio desde el día de su publicación, salvo que en ella se establezca un plazo diferente para su entrada en vigencia." Under art. 164.I a law is published in the Gaceta Oficial immediately after it is promulgated. A law's own vigencia clause overrides the rule.
- **The Constitution of 2009** was approved by referendum on 25 January 2009 and promulgated in El Alto on 7 February 2009. By its disposición final it "entrará en vigencia el día de su publicación en la Gaceta Oficial". The Gaceta's text is headed 7 February 2009, so the first commit is dated 2009-02-07. The Gaceta edition number was not verified.
- **The Código Civil** is dated 2024-02-24, the day of the Internet Archive capture of SILEP's page, because that is the earliest day the source attests this text. The last change SILEP records is Ley 060 of 25 November 2010. Its Gaceta publication day, which is the in-force day under art. 164.II, is in no source read here, so the text is not back-dated to it. The Code itself took effect on 2 April 1976 (art. 1570).
- **Events that changed no words** are dated by the vote (21 February 2016) or the decision (28 November 2017, 28 December 2023).
- `--before="YYYY-MM-DD"` alone uses your clock's time of day, so a change that took effect that day may be missed before noon. Use `T23:59:59Z` as above, or the tool.

## The events that changed no words

| Day | Event | Provisions | What it did |
| --- | --- | --- | --- |
| 2016-02-21 | Referendo constitucional aprobatorio | art. 168 | Voters were asked to approve a partial reform of art. 168 allowing the President and Vice President two consecutive re-elections. "No" won, so art. 168 kept its wording. |
| 2017-11-28 | SCP 0084/2017 (Tribunal Constitucional Plurinacional, acción de inconstitucionalidad abstracta) | arts. 156, 168, 285, 288 | Declared the "aplicación preferente" of art. 23 of the American Convention on Human Rights over the re-election limits in arts. 156, 168, 285.II and 288 ("por una vez de manera continua", "de manera continua por una sola vez"). It also struck the matching limits out of the Ley del Régimen Electoral (Ley 026). |
| 2023-12-28 | SCP 1010/2023-S4 (Sala Cuarta Especializada, acción de amparo constitucional) | arts. 156, 168 | Followed Inter-American Court Advisory Opinion OC-28/21 and held that art. 23 of the Convention is not contrary to art. 168. It records that the 2017 declaration "no tiene efectos derogatorios ni abrogatorios" on the constitutional provisions, and it reversed that line. |

These facts come only from the text of SCP 1010/2023-S4 and from the Inter-American Commission's Informe 121/24 (inadmissibility), both hosted by the Procuraduría General del Estado. That report gives the referendum result as 51.30 % "No" (2,682,517 votes), quoting the petitioners. No official electoral source (OEP) could be read from the build machine, so the record states only that "No" won. The number and date of the law that called the referendum are not stated, because its official text was not read.

## How it is checked

- **Against three official editions.** The text is the Gaceta Oficial's *texto de consulta* of the Constitution. Every article, and the transitional, abrogating and final provisions as one block, was compared with two other official editions: the Tribunal Constitucional Plurinacional's 2023 edition ("Autorización y publicación oficial: Ministerio de la Presidencia a través de la Gaceta Oficial") and the Cámara de Diputados edition of 2025. The comparison ignores whitespace, case, and quote and dash style. Results:
  - **Wording:** in all 412 units compared, the Gaceta's wording agrees with at least one of the other two editions. The 14 wording differences each occur in one edition only (two are artefacts of the Diputados PDF: a page number in art. 20 and an underscore in art. 284). Examples: TCP omits "se encuentren en" in art. 142, prints "alimentaria" for "alimentaría" (arts. 16, 402) and "ecorregiones" (art. 390); Diputados prints "macheneri" (art. 5), "la presidenta" (art. 169) and "sedé" (art. 211).
  - **Punctuation:** in 47 places both other editions print punctuation the Gaceta lacks. Most are a final period after items of a numbered list (for example arts. 298 to 304). One is a doubled period at the end of art. 156, and one is a period for a comma in art. 300. The Gaceta's text is kept as it prints it; nothing was corrected.
  - Every difference is listed in `REPRODUCE.md` (Decisions). `tools/parse.py` also writes them, with context, to `crosscheck.json`.
- **The preamble** is not in the Gaceta's text. It is taken from the TCP edition, and the build stops unless that preamble equals the Diputados edition's, ignoring whitespace.
- **The Código Civil** is SILEP's text exactly as printed, with spacing and quotes normalised. The parser checks that articles 1 to 1,570 all appear once and in order. SILEP replaced the text of repealed articles with its own notes, and those notes are kept as printed, including "EL ARTICULO 910 ESTA EROGADO POR LA LEY Nº 060." One such note has no article number. It sits between arts. 1536 and 1538, so it is art. 1537 (repealed by Ley 018 of 2010, as SILEP's marker says). No second official edition of the consolidated Code was found to compare it with.
- Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`), and both must match `corpus.json`. Results are in `REPRODUCE.md`.
- Health checks: no merge commits on `main`, commit dates never go backwards, nothing is dated in the future, and every commit's trailers parse with `git interpret-trailers --parse`.
- The repository is rebuilt a second time from the same data and must give identical hashes.

## What "author" means

The author of a commit is the law, referendum or ruling, with an e-mail address that cannot exist (`scp-0084-2017@gacetaoficialdebolivia.invalid`), so `git blame` and `git log --author` name them. The committer is always Lexifina.

- The Constitution's first commit is credited to its approval and promulgation in 2009 (`CPE 2009`, kind `referendum`).
- A referendum or ruling that changed no words gets a commit of its own that changes no files. Its message says what happened and names the provisions, and its trailers say `Words-changed: no`.
- Changes that no source explains would be committed by the publisher, the Gaceta Oficial, and labelled "unexplained". There are none.
- The Código Civil's single commit is credited to the publisher as the "oldest version available", because no law produced that text on that day. The repository has one publisher identity, the Gaceta Oficial. SILEP's page gives its own source as "Fuente: Gaceta" and is headed "Datos de la Gaceta Oficial del Estado Plurinacional de Bolivia".

## What it does not show

- **The Código Civil before 2024.** The record does not show how its wording changed between 1976 and 2010, only which laws SILEP says last changed which articles.
- **Amendments SILEP did not record.** SILEP stopped applying amendments to its consolidated codes around 2019 or 2020. Its Código Penal page reads the same in every capture from September 2020 to January 2024 and lacks Ley 1390 of 27 August 2021, which rewrote about 35 of that Code's articles. We know of no law after 2010 that changes the Código Civil's words (Ley 1071 of 2018 gave it the rank of law and changed none), but a change SILEP missed would also be missing here.
- **The Código Penal and other codes.** The Código Penal is not in the record. Its only consolidated official text with a text layer (SILEP) lacks Ley 1390 of 2021, so it is not today's text, and with no current official text a replay of later laws could not be checked. The Ministerio de Justicia's 2010 *texto ordenado* is older still. The Gaceta Oficial's own site times out from the build machine and is read only through Internet Archive copies. The Cámara de Diputados' copies of laws from 2010 on are scans.
- **The Constitutions before 2009.** The Constitution of 1967 and its reforms, abrogated by the 2009 text, are not in the record.
- **Rulings on other norms.** The TCP's lists of norms declared unconstitutional concern laws, not the Constitution, and are not used yet.
- **Headings** (Partes, Títulos, Capítulos, Secciones) are in one file, `constitucion/estructura.md`, each with the first article under it, so article files hold only article text. Headings were not cross-checked against the other editions.
- **Paragraph breaks** follow the Gaceta's layout and were not cross-checked.

## How it is built

`tools/fetch.py` downloads every source response once through curl (one request per second per host, cached by the sha256 of the URL). The Gaceta Oficial is read through Internet Archive raw (`id_`) captures, pinned by timestamp in the URLs. `tools/parse.py` turns the cache into `corpus.json`, and the shared builder `tools/build.py` writes the history with `git fast-import`. The same corpus always gives the same hashes. `REPRODUCE.md` records every command, tool version, data hash and decision, and the result of a hash-for-hash rebuild.

No AI model wrote or changed legal text. Claude Opus 5.5 wrote the scripts and chose the sources. See `REPRODUCE.md`.

## Sources

| Source | Kind | Past versions | Names the amending act | Bulk | Notes |
| --- | --- | --- | --- | --- | --- |
| [Gaceta Oficial del Estado Plurinacional de Bolivia](https://www.gacetaoficialdebolivia.gob.bo) | Official gazette | no consolidated versions | n/a | no | Used for the Constitution's text (`/app/webroot/archivos/CONSTITUCION.pdf`, *texto de consulta*). The live site times out from the build machine, so it is read through the Internet Archive capture of 6 October 2026. Index pages: `/normas/listadonor/10` (5,617 leyes), `/normas/buscar_comp/<n>` (the norms that cite a law). |
| [Tribunal Constitucional Plurinacional](https://tcpbolivia.bo) | Official edition, rulings | no | n/a | no | 2023 edition of the Constitution (preamble and cross-check). Lists of norms declared unconstitutional. The search at buscador.tcpbolivia.bo is an app over a JSON API that was not explored. |
| [Cámara de Diputados](https://diputados.gob.bo) | Official edition | no | n/a | no | 2025 edition of the Constitution (cross-check). |
| [Procuraduría General del Estado](https://www.procuraduria.gob.bo) | Official (State's counsel) | n/a | n/a | no | Hosts SCP 1010/2023-S4 and CIDH Informe 121/24, the sources for the events above. |
| [SILEP](http://www.silep.gob.bo) (Sistema de Información Legal del Estado Plurinacional, Vicepresidencia) | Official legal information system | no (current text only; Internet Archive captures over time) | last law per article | no | Used for the Código Civil (`/norma/4451/ley_actualizada`, capture 20240224013706). The site does not resolve from the build machine, so it is read only through Internet Archive raw captures. Its footer says its documents are not a legal reference; that role belongs to the Gaceta. Its consolidations stop around 2019-2020. |
| Senado, Órgano Electoral Plurinacional | Official | | | | Did not resolve or reset the connection from the build machine. |

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).

## Licence

The legal texts are official texts of the Estado Plurinacional de Bolivia. Fuente: Gaceta Oficial del Estado Plurinacional de Bolivia (texto de consulta); Tribunal Constitucional Plurinacional; Cámara de Diputados; SILEP, Vicepresidencia del Estado Plurinacional (Código Civil), read through the Internet Archive. The Gaceta marks its text "TEXTO DE CONSULTA" and "Derechos Reservados © Gaceta Oficial de Bolivia", and no source publishes a licence. Their copyright status is therefore not confirmed here, and they are reproduced with that attribution. The arrangement, tables, commit messages and tools are by Lexifina, under the terms in `LICENSE`.

This repository is not legal advice and not an official publication.

## En español

Historia del derecho boliviano en git: un archivo por disposición y un commit por norma, fechado el día de su entrada en vigencia y firmado por la norma que hizo el cambio (`git blame` nombra la norma de cada párrafo). Por ahora contiene la Constitución Política del Estado de 2009, tal como fue promulgada el 7 de febrero de 2009, y el Código Civil (Decreto Ley 12760) en su texto actualizado según el SILEP (captura del 24 de febrero de 2024; una sola versión, porque el SILEP no publica las redacciones anteriores). El texto de la Constitución no ha sido modificado desde entonces. Tres hechos que no cambiaron palabras tienen su propio commit (`Words-changed: no`): el referendo de 21 de febrero de 2016 sobre el art. 168, en el que ganó el "No"; la SCP 0084/2017, que declaró la aplicación preferente del art. 23 de la Convención Americana sobre los arts. 156, 168, 285.II y 288; y la SCP 1010/2023-S4, que reencauzó esa línea.

- Texto vigente en una fecha: `python tools/en_vigor_el.py 2017-01-01 constitucion 168`
- Fechas: regla supletoria del art. 164.II de la Constitución (obligatoria desde el día de su publicación, salvo plazo distinto).
- Texto: el de la Gaceta Oficial (texto de consulta), cotejado artículo por artículo con las ediciones del Tribunal Constitucional Plurinacional y de la Cámara de Diputados. El preámbulo, que el texto de la Gaceta no incluye, proviene de la edición del TCP.
- Ningún modelo de IA escribió texto legal.
