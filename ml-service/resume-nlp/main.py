from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from io import BytesIO
from typing import List, Optional
import os
import logging
from functools import lru_cache
import re

# Optional OCR availability flags
try:
    from PIL import Image  # type: ignore
    import pytesseract  # type: ignore
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

# PDF and DOCX extractors
def extract_text_from_pdf(data: bytes) -> str:
    """Extract text from PDF with a quality heuristic.

    We try both PyPDF and pdfminer.six and choose the one with better quality.
    Some PDFs render with missing glyphs (e.g., 'u' disappearing) in PyPDF; in
    those cases pdfminer.six typically performs better.
    """
    # Allow override via env: PDF_EXTRACTOR=pdfminer|pypdf|auto
    mode = os.getenv("PDF_EXTRACTOR", "auto").lower()
    pypdf_text = ""
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(data))
        pages = [p.extract_text() or "" for p in reader.pages]
        pypdf_text = "\n".join(pages)
    except Exception:
        pypdf_text = ""

    pdfminer_text = ""
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract
        pdfminer_text = pdfminer_extract(BytesIO(data)) or ""
    except Exception:
        pdfminer_text = ""

    # If explicit mode requested
    if mode == "pypdf" and pypdf_text:
        return pypdf_text
    if mode == "pdfminer" and pdfminer_text:
        return pdfminer_text

    # If only one succeeded, return it
    if pypdf_text and not pdfminer_text:
        return pypdf_text
    if pdfminer_text and not pypdf_text:
        return pdfminer_text

    # If both failed
    if not pypdf_text and not pdfminer_text:
        return ""

    def score_quality(t: str) -> float:
        # Heuristic: prefer longer text with balanced vowel distribution
        t_l = t.lower()
        vowels = sum(t_l.count(v) for v in "aeiou")
        u_count = t_l.count("u")
        e_count = t_l.count("e") or 1
        length = len(t_l)
        # Penalize when 'u' frequency is suspiciously low compared to 'e'
        u_penalty = 0.0
        if u_count < 0.05 * e_count:
            u_penalty = 0.3
        # Simple score: normalized length + vowel density - penalties
        vowel_density = vowels / max(length, 1)
        base = (length / 10000.0) + vowel_density
        return base - u_penalty

    # Choose text with higher score
    p_score = score_quality(pypdf_text)
    m_score = score_quality(pdfminer_text)
    # If PyPDF appears to drop 'u' characters, favor pdfminer
    p_l = pypdf_text.lower()
    m_l = pdfminer_text.lower()
    def u_ratio(s: str) -> float:
        l = len(s) or 1
        return s.count("u") / l
    if pdfminer_text and (u_ratio(p_l) < 0.002) and (u_ratio(m_l) >= u_ratio(p_l)):
        return pdfminer_text
    return pypdf_text if p_score >= m_score else pdfminer_text

def extract_text_from_docx(data: bytes) -> str:
    try:
        import docx
        doc = docx.Document(BytesIO(data))
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception:
        return ""

def extract_text_from_image(data: bytes) -> str:
    if not OCR_AVAILABLE:
        return ""
    try:
        img = Image.open(BytesIO(data))
        return pytesseract.image_to_string(img) or ""
    except Exception:
        return ""

logger = logging.getLogger("resume-nlp")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Resume NLP Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

BASE_DIR = os.path.dirname(__file__)
DEFAULT_CORPUS_FULL = os.path.join(BASE_DIR, "skill_corpus.txt")
DEFAULT_CORPUS_LEAN = os.path.join(BASE_DIR, "skill_corpus_lean.txt")

def select_corpus_path(mode: Optional[str] = None) -> str:
    env_path = os.getenv("SKILL_CORPUS_PATH")
    if env_path:
        return env_path
    selected = (mode or os.getenv("SKILL_CORPUS_MODE", "full")).lower()
    return DEFAULT_CORPUS_LEAN if selected in ("lean", "skills", "skills-only") else DEFAULT_CORPUS_FULL

def load_corpus(path: Optional[str] = None, mode: Optional[str] = None) -> List[str]:
    p = path or select_corpus_path(mode)
    try:
        with open(p, "r", encoding="utf-8") as f:
            corpus = [line.strip() for line in f if line.strip()]
        logger.info("Loaded skill corpus entries=%d path=%s", len(corpus), p)
        return corpus
    except Exception as e:
        logger.warning("Failed to load corpus at %s: %s", p, e)
        # fallback to minimal set
        return ["python", "java", "sql", "react"]

skill_corpus: List[str] = load_corpus()
compiled_patterns: List[tuple[str, re.Pattern]] = []

SHORT_SKILL_WHITELIST = {"c", "go", "r"}

def compile_patterns():
    global compiled_patterns
    compiled_patterns = []
    for s in sorted(skill_corpus, key=lambda x: len(x), reverse=True):
        sl = s.strip()
        if not sl:
            continue
        if len(sl) < 2 and sl.lower() not in SHORT_SKILL_WHITELIST:
            continue
        # Case-insensitive, ensure not part of a larger alphanumeric token
        pattern = re.compile(rf"(?<![A-Za-z0-9]){re.escape(sl)}(?![A-Za-z0-9])", re.IGNORECASE)
        compiled_patterns.append((s, pattern))
    logger.info("Compiled %d skill patterns", len(compiled_patterns))

compile_patterns()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/diagnostics")
def diagnostics():
    return {
        "corpus_size": len(skill_corpus),
        "spacy_enabled": bool(nlp),
        "ocr_available": OCR_AVAILABLE,
        "sample": skill_corpus[:10]
    }

@app.post("/reload-corpus")
def reload_corpus(mode: Optional[str] = Query(default=None, description="full|lean")):
    global skill_corpus
    skill_corpus = load_corpus(mode=mode)
    compile_patterns()
    return {"reloaded": True, "corpus_size": len(skill_corpus), "mode": (mode or os.getenv("SKILL_CORPUS_MODE", "full"))}

@app.post("/parse")
async def parse_resume(file: UploadFile = File(...)):
    data = await file.read()
    filename = (file.filename or "").lower()

    # Choose extractor by extension or content-type
    text = ""
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(data)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(data)
    elif filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
        if not OCR_AVAILABLE:
            # Make it explicit to callers that OCR is not available
            raise HTTPException(status_code=501, detail="OCR is not available on this service. Install Pillow+pytesseract or use PDF/DOCX.")
        text = extract_text_from_image(data)
    else:
        # fallback assume utf-8 text
        try:
            text = data.decode('utf-8', errors='ignore')
        except Exception:
            text = ""

    if not text:
        # Gracefully return empty results if extraction fails
        return {"skills": [], "projects": []}

    # Keep two versions: one compact for skill phrase matching, one with newlines for section parsing
    text_with_newlines = text.replace("\r\n", "\n")
    # normalize whitespace to make multi-word matches robust across line breaks for skills
    norm_text = re.sub(r"\s+", " ", text)

    # Prefer the SKILLS section if present to reduce false positives
    def slice_skills_section(t: str) -> str:
        tl = t
        # Use uppercase for heading scan but retain original for matching
        up = tl.upper()
        start = up.find("\nSKILLS")
        if start == -1:
            start = up.find(" SKILLS")
        if start == -1:
            return tl
        # Candidates for the next heading
        next_heads = [
            "\nPROJECTS", "\nEXPERIENCE", "\nWORK EXPERIENCE", "\nEDUCATION", "\nCERTIFICATIONS",
            "\nACHIEVEMENTS", "\nINTERNSHIP", "\nPUBLICATIONS", "\nAWARDS", "\nSUMMARY", "\nPROFILE"
        ]
        end_positions = [up.find(h, start + 1) for h in next_heads]
        end_positions = [p for p in end_positions if p != -1]
        end = min(end_positions) if end_positions else -1
        if end != -1 and end > start:
            return tl[start:end]
        return tl[start:]

    search_text = slice_skills_section("\n" + norm_text)  # add leading newline to help heading detection

    found_ordered = []
    seen = set()
    for original, pattern in compiled_patterns:
        m = pattern.search(search_text)
        if m:
            resume_case = m.group(0)
            key = resume_case.lower()
            if key not in seen:
                seen.add(key)
                found_ordered.append((m.start(), resume_case))
    found_ordered.sort(key=lambda x: x[0])
    skills_out = [s for _, s in found_ordered]
    logger.info("Extracted %d skills (exact exact-section match)", len(skills_out))

    # --- Project extraction (robust line-based) ---
    lines_all = [ln.rstrip() for ln in text_with_newlines.splitlines()]
    upper_all = [ln.upper() for ln in lines_all]

    header_patterns = [
        r"^PROJECTS?$",
        r"^KEY PROJECTS$",
        r"^PERSONAL PROJECTS$",
        r"^ACADEMIC PROJECTS$",
        r"^MAJOR PROJECTS$",
        r"^MINI PROJECTS$",
        r"^PROJECT DETAILS$",
        r"^PROJECT EXPERIENCE$",
        r"^SELECTED PROJECTS$",
        r"^PROJECTS[\s&/]+(INTERNSHIPS|TRAINING|CERTIFICATIONS|ACHIEVEMENTS)$",
        r"^PROJECTS AND (INTERNSHIPS|TRAINING)$",
        r"^ACADEMIC PROJECTS AND INTERNSHIPS$",
        r"^PROJECTS AND HACKATHONS$",
        r"^PROJECTS & HACKATHONS$",
        r"^PROJECTS AND ACHIEVEMENTS$",
        r"^PROJECTS & ACHIEVEMENTS$",
        r"^PROJECTS (?:AND|&) (?:AWARDS|ACCOMPLISHMENTS)$",
    ]
    header_res = [re.compile(p) for p in header_patterns]

    def normalize_heading(s: str) -> str:
        return re.sub(r"\s+", " ", s.strip().strip("-:•*\u2013")).upper()

    start_idx = -1
    for i, u in enumerate(upper_all):
        norm = normalize_heading(u)
        for rx in header_res:
            if rx.match(norm):
                start_idx = i + 1
                break
        if start_idx != -1:
            break

    # fallback: find first occurrence of the word PROJECT in any heading-like line
    if start_idx == -1:
        for i, line in enumerate(lines_all):
            raw = line.strip()
            if not raw:
                continue
            # Strip common decorations
            raw_norm = re.sub(r"^[\-*•\u2022\u25CF\s]+|\s*[-_*]{2,}\s*$", "", raw)
            up = raw_norm.upper()
            if ("PROJECT" in up) and (len(raw_norm) <= 120):
                start_idx = i + 1
                break

    def is_next_heading(line: str) -> bool:
        t = line.strip()
        if not t:
            return False
        # Known next section anchors
        anchors = [
            "EXPERIENCE", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "EDUCATION", "ACADEMICS",
            "QUALIFICATIONS", "CERTIFICATIONS", "ACHIEVEMENTS", "INTERNSHIP", "PUBLICATIONS",
            "AWARDS", "SUMMARY", "OBJECTIVE", "PROFILE", "SKILLS", "TECHNICAL SKILLS", "LANGUAGES",
            "HOBBIES", "INTERESTS", "CONTACT", "WORK HISTORY", "VOLUNTEERING", "EXTRACURRICULAR",
            "CO-CURRICULAR", "COURSES", "TRAININGS"
        ]
        u = t.upper()
        # Consider anchor if equals, starts with, or contains a known heading word
        if u in anchors or any(u.startswith(a) for a in anchors) or any(a in u for a in anchors):
            return True
        # Common education/degree patterns often used as first line under EDUCATION in extracted text
        degree_rx = re.compile(r"^(Bachelor|Master|B\.?E\.?|B\.?Tech|BTech|B\.?Sc|BSc|M\.?Tech|MTech|M\.?Sc|MBA|Diploma|PUC|Intermediate|XII|10th|12th)\b", re.IGNORECASE)
        if degree_rx.match(t):
            return True
        # Horizontal rules / separators
        if re.match(r"^\s*[-_=]{4,}\s*$", t):
            return True
        # Heuristic: line that is mostly uppercase and short looks like a heading
        letters = [ch for ch in t if ch.isalpha()]
        if letters:
            upper_ratio = sum(1 for ch in letters if ch.isupper()) / len(letters)
            if upper_ratio > 0.8 and 3 <= len(t) <= 60:
                return True
        return False

    projects_lines: list[str] = []
    if start_idx != -1:
        j = start_idx
        while j < len(lines_all) and not is_next_heading(lines_all[j]):
            projects_lines.append(lines_all[j])
            j += 1
    else:
        projects_lines = []

    projects_out: list[dict] = []
    if projects_lines:
        # Preserve original line breaks; minimal trimming
        lines = [ln.rstrip() for ln in projects_lines]
        while lines and not lines[0].strip():
            lines.pop(0)

        def push(current_title: str, desc_lines: list[str]):
            # Helpers
            months_rx = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\b\s*\d{2,4}", re.IGNORECASE)
            date_range_rx = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s*\d{2,4}\b\s*[–—\-]\s*(?:Present|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s*\d{2,4}\b)", re.IGNORECASE)
            def clean_title(t: str) -> str:
                t = t.strip().strip("-–—:•*·•")
                # Merge broken word case handled later
                # Prefer left side before pipe
                if "|" in t:
                    t = t.split("|")[0].strip()
                # Drop anything after 'GitHub'
                t = re.sub(r"\bGitHub\b.*$", "", t, flags=re.IGNORECASE)
                # Remove date ranges or single month-year tokens
                t = date_range_rx.sub("", t)
                t = months_rx.sub("", t)
                # Collapse extra punctuation/spaces
                t = re.sub(r"\s+", " ", t).strip("-–—:•* ·")
                return t.strip()

            def clean_desc_lines(lines: list[str]) -> list[str]:
                out = []
                for ln in lines:
                    if ln is None:
                        continue
                    # Preserve leading whitespace for indentation; trim only right side
                    s = ln.rstrip("\n\r")
                    if not s:
                        out.append("")
                        continue
                    # Skip standalone dates or github-only lines
                    if date_range_rx.fullmatch(s) or months_rx.fullmatch(s) or re.fullmatch(r"(?i)github\b.*", s):
                        continue
                    # Normalize common leading markers (bullets, numbers) to a single bullet while keeping indentation
                    s = re.sub(r"^(\s*)([\-\*•\u2022\u25CF]+)\s*", r"\1• ", s)
                    s = re.sub(r"^(\s*)\d+[\)\.]\s+", r"\1• ", s)
                    out.append(s)
                return out

            # Start with raw title
            title_raw = (current_title or "").strip()
            # If title looks too short (e.g., 'Fra'), try to merge first desc line
            if len(title_raw) < 10 and desc_lines:
                first = (desc_lines[0] or "").strip()
                if first and first[0].islower():
                    title_raw = f"{title_raw} {first}".strip()
                    desc_lines = desc_lines[1:]
            title = clean_title(title_raw)
            if not title and desc_lines:
                # Fallback: take first meaningful desc line as title
                title = clean_title(desc_lines[0])
                desc_lines = desc_lines[1:]
            if not title:
                return
            if len(title) > 150:
                title = title[:150] + "…"
            # Clean description
            desc_items = clean_desc_lines(desc_lines)
            # Remove leading/trailing blanks
            while desc_items and not desc_items[0]:
                desc_items.pop(0)
            while desc_items and not desc_items[-1]:
                desc_items.pop()
            desc = "\n".join(desc_items).strip()
            if len(desc) > 4000:
                desc = desc[:3997] + "…"
            projects_out.append({"title": title, "description": desc})

        current_title = ""
        current_desc: list[str] = []
        bullet_start = re.compile(r"^[\-\*•\u2022\u25CF]|^\d+[\)\.]\s+")
        title_desc_pair = re.compile(r"^(.{3,160}?)\s*[-–—:\\u2013\|]\s*(.{4,})$")
        months = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\b\s*\d{2,4}", re.IGNORECASE)
        GENERIC_LABELS = {"TECH STACK","RESPONSIBILITIES","ROLE","DURATION","TOOLS","ENVIRONMENT","TEAM SIZE","CONTRIBUTIONS","KEY FEATURES","ACHIEVEMENTS","LINKS","GITHUB","URL","WEBSITE","RESULT","OUTCOME","IMPACT"}

        def is_generic_label_line(s: str) -> bool:
            u = s.strip().upper()
            return any(u == g or u.startswith(g + ":") for g in GENERIC_LABELS)

        was_blank = True
        heading_like = re.compile(r"^[A-Z][A-Za-z0-9&/()\-]*?(?:\s+[A-Z][A-Za-z0-9&/()\-]*){2,}\s*$")
        for raw in lines:
            ln = raw.strip()
            if not ln:
                if current_title and (not current_desc or current_desc[-1] != ""):
                    current_desc.append("")
                was_blank = True
                continue

            m_pair = title_desc_pair.match(ln)
            if m_pair:
                if not current_title or was_blank:
                    if current_title:
                        push(current_title, current_desc)
                    current_title = m_pair.group(1)
                    current_desc = [m_pair.group(2)]
                else:
                    current_desc.append(raw)
                was_blank = False
                continue

            looks_like_title = (
                bullet_start.match(ln) is not None
                or re.match(r"^(Project|PROJECT)[^:]{0,20}[:\-]", ln) is not None
                or (not current_title and len(ln) >= 25 and len(ln.split()) >= 4)
                or ("|" in ln and len(ln) >= 12)
            )
            # If separated by a blank line, treat Title Case headings as titles
            if was_blank and heading_like.match(ln):
                looks_like_title = True
            if months.fullmatch(ln) or is_generic_label_line(ln) or (len(ln) < 10 and current_title):
                looks_like_title = False

            if looks_like_title and (not current_title or was_blank or bullet_start.match(ln)):
                if current_title:
                    push(current_title, current_desc)
                title_line = re.sub(r"^[\-\*•\u2022\u25CF\d\)\.\s]+", "", ln).strip()
                current_title = title_line
                current_desc = []
            else:
                if current_title:
                    current_desc.append(raw)
            was_blank = False

        if current_title:
            push(current_title, current_desc)

    # Filter out hackathon-related entries if present
    if projects_out:
        exclude_rx = re.compile(r"\b(hackathon|hack\-?a\-?thon|hackman|hack\s*fest|hackfest)\b", re.IGNORECASE)
        projects_out = [
            pr for pr in projects_out
            if not (exclude_rx.search(pr.get("title") or "") or exclude_rx.search(pr.get("description") or ""))
        ]

    # De-duplicate by normalized title to avoid splitting/duplicates
    if projects_out:
        seen_titles = set()
        unique = []
        for pr in projects_out:
            key = re.sub(r"\W+", "", (pr.get("title") or "").lower())
            if key and key not in seen_titles:
                seen_titles.add(key)
                unique.append(pr)
        projects_out = unique

    return {"skills": skills_out, "projects": projects_out}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
