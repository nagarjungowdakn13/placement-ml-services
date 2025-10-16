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
    # Try PyPDF first (usually faster), then fallback to pdfminer
    text = ""
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(data))
        pages = [p.extract_text() or "" for p in reader.pages]
        text = "\n".join(pages)
    except Exception:
        pass
    if not text:
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(BytesIO(data)) or ""
        except Exception:
            return ""
    return text

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
        # Gracefully return empty skills if extraction fails
        return {"skills": []}

    # normalize whitespace to make multi-word matches robust across line breaks
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
    return {"skills": skills_out}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
