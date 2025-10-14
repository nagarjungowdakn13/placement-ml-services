from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from rapidfuzz import process
import uvicorn
from io import BytesIO
from typing import List, Optional
import os
import logging
from functools import lru_cache

# PDF and DOCX extractors
def extract_text_from_pdf(data: bytes) -> str:
    # Try pdfminer first, fallback to pypdf
    text = ""
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(BytesIO(data)) or ""
    except Exception:
        pass
    if not text:
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(data))
            pages = [p.extract_text() or "" for p in reader.pages]
            text = "\n".join(pages)
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
    try:
        from PIL import Image
        import pytesseract
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

DEFAULT_CORPUS_PATH = os.getenv("SKILL_CORPUS_PATH", os.path.join(os.path.dirname(__file__), "skill_corpus.txt"))

def load_corpus(path: Optional[str] = None) -> List[str]:
    p = path or DEFAULT_CORPUS_PATH
    try:
        with open(p, "r", encoding="utf-8") as f:
            corpus = [line.strip() for line in f if line.strip()]
        logger.info("Loaded skill corpus entries=%d path=%s", len(corpus), p)
        return corpus
    except Exception as e:
        logger.warning("Failed to load corpus at %s: %s", p, e)
        # fallback to minimal set
        return ["python", "java", "sql", "react"]

skill_corpus = load_corpus()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/diagnostics")
def diagnostics():
    return {
        "corpus_size": len(skill_corpus),
        "spacy_enabled": bool(nlp),
        "sample": skill_corpus[:10]
    }

@app.post("/reload-corpus")
def reload_corpus():
    global skill_corpus
    skill_corpus = load_corpus()
    return {"reloaded": True, "corpus_size": len(skill_corpus)}

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

    tokens = []
    if nlp is not None:
        try:
            doc = nlp(text)
            tokens = [t.text for t in doc]
        except Exception:
            tokens = text.split()
    else:
        tokens = text.split()

    extracted_skills = set()
    lowered = [s.lower() for s in skill_corpus]
    # fuzzy match tokens against corpus (case-insensitive)
    for tok in tokens:
        match = process.extractOne(tok, lowered)
        if match and match[1] >= 85:
            # recover original casing by index lookup
            try:
                idx = lowered.index(match[0])
                extracted_skills.add(skill_corpus[idx])
            except ValueError:
                extracted_skills.add(match[0])
    logger.info("Extracted %d skills", len(extracted_skills))

    return {"skills": sorted(extracted_skills)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
