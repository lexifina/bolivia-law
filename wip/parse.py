"""Reads only .cache/ and writes corpus.json (scripts/gitlaw_common/SCHEMA.md).

Deterministic: the same cache gives the same bytes. No network, no model.

    python -X utf8 parse.py            # writes corpus.json and verification notes (crosscheck.json)
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

import fitz  # PyMuPDF

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
sys.path.insert(0, str(HERE))
import acts_meta as M  # noqa: E402  (law and act metadata typed by hand from the official sources)


def cpath(url: str) -> Path:
    p = CACHE / hashlib.sha256(url.encode("utf-8")).hexdigest()
    if not p.exists():
        raise SystemExit(f"not in cache: {url} (run fetch.py --manifest)")
    return p


def sha(url: str) -> str:
    return hashlib.sha256(cpath(url).read_bytes()).hexdigest()


# ------------------------------------------------------------------ normalisation

LIGATURES = {"昀椀": "fi", "昀氀": "fl", "ﬁ": "fi", "ﬂ": "fl"}
QUOTES = {"“": '"', "”": '"', "„": '"', "«": '"', "»": '"',
          "‘": "'", "’": "'", "´": "'"}
DASHES = dict.fromkeys(["‐", "‑", "‒", "–", "—", "―", "−"], "-")


def norm(s: str) -> str:
    for a, b in LIGATURES.items():
        s = s.replace(a, b)
    s = unicodedata.normalize("NFC", s)
    s = s.replace(" ", " ").replace("\t", " ").replace("­", "")
    for a, b in {**QUOTES, **DASHES}.items():
        s = s.replace(a, b)
    s = re.sub(r" {2,}", " ", s)
    return s.strip()


def squash(s: str) -> str:
    """Comparison key across editions: no whitespace, no case, no punctuation spacing artefacts."""
    s = norm(s).lower()
    s = re.sub(r"[\s ]+", "", s)
    s = s.replace("º", "°")
    return s


# ------------------------------------------------------------------ PDF lines

def pdf_lines(path: Path, drop: list[re.Pattern]) -> list[tuple[int, str]]:
    """Lines in reading order with their block number, page furniture removed."""
    out = []
    doc = fitz.open(path)
    bid = 0
    for page in doc:
        d = page.get_text("dict")
        for b in d["blocks"]:
            bid += 1
            for ln in b.get("lines", []):
                t = norm("".join(sp["text"] for sp in ln["spans"]))
                if not t or any(p.fullmatch(t) for p in drop):
                    continue
                out.append((bid, t))
    return out


ORD = ["Primera", "Segunda", "Tercera", "Cuarta", "Quinta", "Sexta", "Séptima", "Octava", "Novena", "Décima"]
RE_ART = re.compile(r"^(?:Artículo|ARTÍCULO)\s+(\d+)\s*[.°º]?\s*(.*)$")
RE_NUM = re.compile(r"^((?:[IVX]+|\d+)\.)(?:\s+(.*))?$")
RE_HEAD = re.compile(r"^(PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA) PARTE$|^(TÍTULO|CAPÍTULO|SECCIÓN)\b.*$")
RE_TRANS = re.compile(r"^(" + "|".join(ORD) + r")\.\s*(.*)$")


def is_caps(t: str) -> bool:
    letters = [c for c in t if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


# ------------------------------------------------------------------ the Constitution

GACETA_DROP = [re.compile(p) for p in (
    r"TEXTO DE CONSULTA", r"Derechos Reservados © Gaceta Oficial de Bolivia",
    r'"2022 AÑO DE LA REVOLUCIÓN CULTURAL.*', r"\d{1,3}")]


def parse_cpe_gaceta(path: Path) -> dict:
    """Gaceta Oficial 'texto de consulta' of the CPE (Word-made PDF). Returns units (without the preamble) in order."""
    lines = pdf_lines(path, GACETA_DROP)
    # start at the promulgation formula
    i = next(k for k, (_, t) in enumerate(lines) if t.startswith("EVO MORALES AYMA"))
    lines = lines[i:]
    units: dict[str, dict] = {}
    order: list[str] = []
    struct: list[str] = []      # heading lines for estructura
    cur: str | None = None
    paras: dict[str, list[str]] = {}
    pending_head: list[str] = []
    pending_num: str | None = None
    prev_block = None
    zone = "promulgacion"
    closing: list[str] = []

    def start(key: str, label: str):
        nonlocal cur
        cur = key
        order.append(key)
        units[key] = {"label": label}
        paras[key] = []

    def add(text: str, new: bool):
        nonlocal pending_num
        if pending_num:
            text = f"{pending_num} {text}".strip()
            pending_num = None
            new = True
        p = paras[cur]
        if new or not p:
            p.append(text)
        else:
            p[-1] = f"{p[-1]} {text}"

    start("promulgacion", "Promulgación")
    for blk, t in lines:
        if t in ("CONSTITUCION POLITICA DEL ESTADO", "CONSTITUCIÓN POLÍTICA DEL ESTADO") and zone == "promulgacion":
            zone = "body"
            continue
        if zone == "promulgacion":
            if t.startswith("EVO MORALES") or t.startswith("PRESIDENTE CONSTITUCIONAL"):
                add(t, True)
            else:
                add(t, False)
            continue
        if zone == "closing":
            closing.append(t)
            continue
        # structure headings
        if t == "DISPOSICIONES TRANSITORIAS":
            pending_head = []
            struct.append("DISPOSICIONES TRANSITORIAS")
            continue
        if t in ("DISPOSICIÓN ABROGATORIA", "DISPOSICIÓN FINAL"):
            struct.append(t)
            if t == "DISPOSICIÓN FINAL":
                start("disp-final", "Disposición final")
            continue
        if RE_HEAD.match(t) or (pending_head and is_caps(t) and not RE_NUM.match(t)):
            if RE_HEAD.match(t):
                pending_head.append(t)
            else:
                pending_head[-1] += (" | " if " | " not in pending_head[-1] else " ") + t
            continue
        m = RE_ART.match(t)
        if m:
            n = int(m.group(1))
            for h in pending_head:
                struct.append(f"{h}  [art. {n}]")
            pending_head = []
            start(f"art-{n:03d}", f"Art. {n}")
            if m.group(2):
                add(m.group(2), True)
            prev_block = blk
            continue
        m = RE_TRANS.match(t)
        if m and (cur.startswith("disp-transitoria") or cur == "art-411"):
            k = ORD.index(m.group(1)) + 1
            start(f"disp-transitoria-{k:02d}", f"Disposición transitoria {m.group(1).lower()}")
            if m.group(2):
                add(m.group(2), True)
            prev_block = blk
            continue
        if t.startswith("Disposición abrogatoria."):
            start("disp-abrogatoria", "Disposición abrogatoria")
            add(t[len("Disposición abrogatoria."):].strip(), True)
            continue
        if cur == "disp-final" and t.startswith("Remítase al Poder Ejecutivo"):
            zone = "closing"
            closing.append(t)
            continue
        m = RE_NUM.match(t)
        if m:
            if m.group(2):
                add(f"{m.group(1)} {m.group(2)}", True)
            else:
                pending_num = m.group(1)
            prev_block = blk
            continue
        # an unnumbered line: a new paragraph only when the previous paragraph ended a sentence in another block
        p = paras[cur]
        new = bool(p) and blk != prev_block and re.search(r"[.:;]$", p[-1]) and pending_num is None
        add(t, bool(new))
        prev_block = blk
    # closing formula belongs to the promulgation
    cl, buf = [], []
    for t in closing:
        if t.startswith(("Remítase", "Por tanto", "Ciudad de", "FDO.", "PRESIDENTE")):
            if buf:
                cl.append(" ".join(buf))
            buf = [t]
        else:
            buf.append(t)
    if buf:
        cl.append(" ".join(buf))
    paras["promulgacion"] += cl
    for k in order:
        units[k]["paras"] = paras[k]
    units["estructura"] = {"label": "Estructura", "paras": [s.replace(" | ", ": ") for s in struct]}
    return units


def preamble_from(path: Path, drop: list[re.Pattern]) -> list[str]:
    lines = [t for _, t in pdf_lines(path, drop)]
    # The preamble's first words; its heading can come later in reading order (TCP edition) or in the index.
    i = next(k for k, t in enumerate(lines) if t.startswith("En tiempos inmemoriales"))
    out, buf = [], []
    for t in lines[i:]:
        if t == "PREÁMBULO":
            continue
        if t.startswith(("EVO MORALES", "CONSTITUCIÓN POLÍTICA DEL ESTADO", "PRIMERA PARTE")):
            break
        buf.append(t)
        if t.endswith("."):
            out.append(" ".join(buf))
            buf = []
    assert not buf, buf
    return out


TCP_DROP = [re.compile(p) for p in (r"Constitución Política del Estado", r"Tribunal Constitucional Plurinacional de Bolivia",
                                    r"-?\d{1,3}-?")]
DIP_DROP = [re.compile(p) for p in (r"CONSTITUCIÓN POLÍTICA DEL ESTADO", r"LEGISLATURA DEL BICENTENARIO", r"\d{1,3}")]


def articles_by_edition(path: Path, drop) -> dict[int, str]:
    """Edition text split at article headings (for the cross-check only): squashed text per article."""
    lines = [t for _, t in pdf_lines(path, drop)]
    arts: dict[int, list[str]] = {}
    cur = None
    for t in lines:
        m = RE_ART.match(t)
        if m and (cur is None or int(m.group(1)) == cur + 1):
            cur = int(m.group(1))
            arts[cur] = [m.group(2)]
            continue
        if cur is None:
            continue
        if t.startswith(("DISPOSICIONES TRANSITORIAS",)) and cur == 411:
            cur = None
            continue
        if is_caps(t) and not RE_NUM.match(t):
            continue  # headings
        arts[cur].append(t)
    return {n: squash(" ".join(v)) for n, v in arts.items()}


def to_text(label_head: str, paras: list[str]) -> str:
    body = [p for p in paras if p]
    return "\n".join([f"# {label_head}", *body]) + "\n"


def build_constitution(report: dict) -> dict:
    g_url, t_url, d_url = M.CPE_GACETA, M.CPE_TCP, M.CPE_DIPUTADOS
    units = parse_cpe_gaceta(cpath(g_url))
    pre_t = preamble_from(cpath(t_url), TCP_DROP)
    pre_d = preamble_from(cpath(d_url), DIP_DROP)
    same_pre = [squash(a) for a in pre_t] == [squash(b) for b in pre_d]
    report["preamble"] = {"paragraphs_tcp": len(pre_t), "paragraphs_diputados": len(pre_d), "identical_ignoring_spaces": same_pre}
    if not same_pre:
        raise SystemExit("preamble differs between the TCP and Diputados editions")
    out = {"preambulo": {"label": "Preámbulo", "kind": "preamble", "text": to_text("Preámbulo", pre_t)}}
    for k, u in units.items():
        if k == "estructura":
            out[k] = {"label": "Estructura", "kind": "structure", "text": to_text("Estructura", u["paras"])}
            continue
        kind = "art" if k.startswith("art-") else "transitional" if "transitoria" in k else "provision"
        head = u["label"].replace("Art.", "Artículo")
        out[k] = {"label": u["label"], "kind": kind, "text": to_text(head, u["paras"])}
    # cross-check every article against the TCP and Diputados editions
    g = {int(k[4:]): squash(" ".join(u["paras"])) for k, u in units.items() if k.startswith("art-")}
    report["articles"] = len(g)
    for name, url, drop in (("tcp", t_url, TCP_DROP), ("diputados", d_url, DIP_DROP)):
        e = articles_by_edition(cpath(url), drop)
        diffs = []
        for n in sorted(set(g) | set(e)):
            if g.get(n) != e.get(n):
                a, b = g.get(n, ""), e.get(n, "")
                j = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
                diffs.append({"art": n, "gaceta": a[max(0, j - 40): j + 60], name: b[max(0, j - 40): j + 60]})
        report[f"vs_{name}"] = {"articles": len(e), "differing": len(diffs), "diffs": diffs}
    return out


# ------------------------------------------------------------------ corpus

def main():
    report: dict = {}
    cpe_units = build_constitution(report)
    versions = [{"from": "2009-02-07", "source_url": M.CPE_GACETA, "sha256": sha(M.CPE_GACETA),
                 "units": cpe_units, "credits": {}, "note": M.CPE_NOTE}]
    # Events that changed no words: the same text as a version of their own day, credited to the provisions concerned.
    for law, day, provs in M.CPE_EVENTS:
        missing = [k for k in provs if k not in cpe_units]
        if missing:
            raise SystemExit(f"{law}: unknown provisions {missing}")
        versions.append({"from": day, "source_url": M.CPE_GACETA, "sha256": sha(M.CPE_GACETA),
                         "units": cpe_units, "credits": {k: [law] for k in provs}})
    acts = [{
        "slug": "constitucion", "short": "CPE", "title": "Constitución Política del Estado",
        "url": M.CPE_GACETA_PAGE, "first_law": "cpe-2009", "earlier_laws": [],
        "versions": versions,
    }]
    corpus = {
        "country": M.COUNTRY,
        "sources": M.sources(),
        "laws": M.LAWS,
        "acts": acts,
        "applies": [],
        "decisions": M.DECISIONS,
        "ai_use": M.AI_USE,
    }
    if "--dry" not in sys.argv:  # --dry: write only crosscheck.json
        tmp = HERE / "corpus.json.tmp"
        tmp.write_text(json.dumps(corpus, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        tmp.replace(HERE / "corpus.json")  # atomic: autopush builds every corpus.json it sees
    (HERE / "crosscheck.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                          newline="\n")
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != "diffs"})
                      for k, v in report.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
