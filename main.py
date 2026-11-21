"""
FastAPI backend for sevavoice-hindi.

Endpoints:
  POST /session/start  - Start Agora + Murf session
  POST /session/stop   - Stop session
  POST /tts            - Synthesize Hindi text to speech
  POST /lookup         - Look up citizen context
  POST /slots          - Check service slots
  POST /book           - Book a service slot (requires explicit confirmation)
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel
from typing import Optional
import uvicorn
from pathlib import Path

from config import settings
from agent_service import AgentService
from tools import lookup_citizen_context, check_service_slots, book_service_slot

app = FastAPI(title="sevavoice-hindi", version="1.0.0")
agent = AgentService()


# --- Request / Response models ---
class StartSessionRequest(BaseModel):
    user_id: str


class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    locale: Optional[str] = None


class LookupRequest(BaseModel):
    phone: str


class SlotsRequest(BaseModel):
    date: str


class BookRequest(BaseModel):
    phone: str
    date: str
    time: str
    user_confirmed: bool = False


# --- Endpoints ---
@app.get("/")
def root():
    return {
        "service": "sevavoice-hindi",
        "language": settings.LANGUAGE,
        "status": "running",
        "message": "सेवा वॉइस हिंदी एजेंट सर्वर चल रहा है।",
    }


@app.get("/demo", response_class=HTMLResponse)
def demo_ui():
    """Serve the browser demo UI at GET /demo."""
    demo_path = Path(__file__).resolve().parent / "demo.html"
    return HTMLResponse(content=demo_path.read_text(encoding="utf-8"))


@app.post("/session/start")
def start_session(req: StartSessionRequest):
    result = agent.start_session(req.user_id)
    return JSONResponse(content=result)


@app.post("/session/stop")
def stop_session(session_id: str):
    result = agent.stop_session(session_id)
    return JSONResponse(content=result)


@app.post("/tts")
def tts(req: TTSRequest):
    audio = agent.speak(req.text)
    if audio is None:
        # No Murf API key -> return text for demo purposes
        return JSONResponse(
            content={
                "text": req.text,
                "audio": None,
                "note": "Murf API key not configured; returning text only.",
            }
        )
    return Response(content=audio, media_type="audio/mpeg")


@app.post("/lookup")
def lookup(req: LookupRequest):
    summary = lookup_citizen_context(req.phone)
    return JSONResponse(
        content={"phone": req.phone, "summary": summary, "language": "hi-IN"}
    )


@app.post("/slots")
def slots(req: SlotsRequest):
    result = check_service_slots(req.date)
    return JSONResponse(
        content={"date": req.date, "result": result, "language": "hi-IN"}
    )


@app.post("/book")
def book(req: BookRequest):
    result = book_service_slot(req.phone, req.date, req.time, req.user_confirmed)
    return JSONResponse(content={"result": result, "language": "hi-IN"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)