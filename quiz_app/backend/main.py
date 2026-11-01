"""
AI Quiz App - Python Backend
Uses FLAN-T5 via Hugging Face Transformers to generate MCQs from text.
Run: pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import random
import re

app = FastAPI(title="AI Quiz Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MODELS ─────────────────────────────────────────────────────

class QuizRequest(BaseModel):
    text: str
    num_questions: int = 5
    difficulty: str = "medium"  # easy, medium, hard

class QuestionResponse(BaseModel):
    question: str
    options: List[str]
    correct_index: int

class QuizResponse(BaseModel):
    questions: List[QuestionResponse]

# ── FLAN-T5 LOADER ─────────────────────────────────────────────

_model = None
_tokenizer = None

def get_model():
    global _model, _tokenizer
    if _model is None:
        try:
            from transformers import T5ForConditionalGeneration, T5Tokenizer
            print("Loading FLAN-T5 model...")
            _tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
            _model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Warning: Could not load FLAN-T5: {e}. Using fallback generator.")
    return _model, _tokenizer

# ── QUESTION GENERATION ────────────────────────────────────────

def generate_with_flanT5(text: str, num_questions: int, difficulty: str) -> List[dict]:
    """Generate MCQs using FLAN-T5."""
    model, tokenizer = get_model()
    if model is None:
        return generate_fallback(text, num_questions)

    questions = []
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 40]

    for i in range(min(num_questions, len(sentences))):
        sentence = sentences[i % len(sentences)]
        prompt = (
            f"Generate a multiple choice question with 4 options and indicate "
            f"the correct answer from this text: {sentence[:300]}"
        )

        inputs = tokenizer(prompt, return_tensors="pt",
                           max_length=512, truncation=True)
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            num_beams=4,
            temperature=0.7,
        )
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        parsed = parse_generated_question(result, sentence)
        if parsed:
            questions.append(parsed)

    # Fill remaining with fallback if needed
    while len(questions) < num_questions:
        questions.extend(generate_fallback(text, num_questions - len(questions)))

    return questions[:num_questions]


def parse_generated_question(generated: str, context: str) -> dict | None:
    """Try to parse FLAN-T5 output into structured MCQ."""
    try:
        lines = [l.strip() for l in generated.split('\n') if l.strip()]
        if len(lines) >= 5:
            question = lines[0]
            options = lines[1:5]
            correct_index = 0
            return {
                "question": question,
                "options": options,
                "correct_index": correct_index
            }
    except Exception:
        pass
    return None


def generate_fallback(text: str, num_questions: int) -> List[dict]:
    """Rule-based fallback MCQ generation."""
    words = text.split()
    questions = []

    templates = [
        "What is the main concept described in the study material?",
        "Which of the following best describes the topic?",
        "According to the uploaded content, what is emphasized?",
        "What technology is mentioned in the study material?",
        "Which statement is TRUE based on the uploaded text?",
    ]

    for i in range(num_questions):
        # Extract a keyword from text
        keyword_idx = (i * 7) % max(1, len(words) - 5)
        keyword = ' '.join(words[keyword_idx:keyword_idx + 3]).strip('.,;:')

        correct = keyword if keyword else "The uploaded content"
        distractors = [
            "An unrelated concept",
            "A different framework",
            "None of the above",
        ]
        options = [correct] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct)

        questions.append({
            "question": templates[i % len(templates)],
            "options": options,
            "correct_index": correct_idx,
        })

    return questions

# ── ENDPOINTS ──────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "AI Quiz Backend running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/generate-quiz", response_model=QuizResponse)
def generate_quiz(req: QuizRequest):
    if not req.text or len(req.text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Text too short. Please provide at least 50 characters."
        )

    if req.num_questions < 1 or req.num_questions > 20:
        raise HTTPException(
            status_code=400,
            detail="num_questions must be between 1 and 20."
        )

    try:
        raw_questions = generate_with_flanT5(
            req.text,
            req.num_questions,
            req.difficulty
        )
        questions = [QuestionResponse(**q) for q in raw_questions]
        return QuizResponse(questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
