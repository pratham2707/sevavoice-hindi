"""
Agentic workflow tools for sevavoice-hindi.
All user-facing strings are in Hindi (hi-IN).
Data is kept in-memory (dict/JSON-style stores); replace with a DB in production.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

# --- In-memory data stores (replace with a real database in production) ---
CITIZEN_CONTEXT: Dict[str, Dict[str, Any]] = {}
SERVICE_SLOTS: Dict[str, List[Dict[str, Any]]] = {}
BOOKINGS: Dict[str, Dict[str, Any]] = {}


def _seed_data() -> None:
    """Seed demo data so the hackathon demo works out of the box."""
    # Citizen context keyed by phone number
    CITIZEN_CONTEXT["+919876543210"] = {
        "name": "राम शर्मा",
        "language": "hi-IN",
        "last_service": "बिजली कनेक्शन",
        "last_interaction": "2024-01-15",
        "notes": "पिछली बार बिजली कनेक्शन की समस्या दर्ज की गई थी।",
    }
    CITIZEN_CONTEXT["+919123456789"] = {
        "name": "सीता वर्मा",
        "language": "hi-IN",
        "last_service": "पानी आपूर्ति",
        "last_interaction": "2024-02-10",
        "notes": "पानी आपूर्ति में अनियमितता की शिकायत दर्ज थी।",
    }

    # Service slots for the next 7 days
    today = datetime.now().date()
    for i in range(7):
        date_str = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        slots = []
        for hour in [10, 11, 12, 14, 15, 16]:
            slots.append({"time": f"{hour:02d}:00", "available": True})
        SERVICE_SLOTS[date_str] = slots


# Seed data on import
_seed_data()


def lookup_citizen_context(phone: str) -> str:
    """
    Look up prior context/history for a citizen by phone number.
    Returns a Hindi summary.
    """
    ctx = CITIZEN_CONTEXT.get(phone)
    if not ctx:
        return (
            "क्षमा करें, आपके फोन नंबर से जुड़ी कोई पूर्व जानकारी हमारे रिकॉर्ड में नहीं मिली। "
            "कृपया अपना नाम और सेवा का प्रकार बताएं ताकि हम आपकी मदद कर सकें।"
        )
    summary = (
        f"नमस्ते {ctx.get('name', 'ग्राहक')} जी, आपका पिछला रिकॉर्ड मिल गया है। "
        f"अंतिम सेवा: {ctx.get('last_service', 'अज्ञात')}, "
        f"अंतिम संपर्क: {ctx.get('last_interaction', 'अज्ञात')}. "
        f"टिप्पणी: {ctx.get('notes', 'कोई विशेष टिप्पणी नहीं।')}"
    )
    return summary


def check_service_slots(date_str: str) -> str:
    """
    Check available service/appointment slots for a given date (YYYY-MM-DD).
    Returns available slots in Hindi, or Hindi fallback suggestions if none/full.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return (
            "क्षमा करें, तारीख का फॉर्मेट गलत है। कृपया तारीख YYYY-MM-DD फॉर्मेट में दें "
            "(उदाहरण: 2024-02-20)।"
        )

    slots = SERVICE_SLOTS.get(date_str, [])
    if not slots:
        return (
            f"क्षमा करें, {date_str} के लिए कोई सेवा स्लॉट उपलब्ध नहीं है। "
            f"कृपया कोई अन्य तारीख चुनें।"
        )

    available = [s for s in slots if s.get("available")]
    if not available:
        suggestions = _suggest_next_available(after=date_str)
        return (
            f"क्षमा करें, {date_str} के सभी स्लॉट भर चुके हैं। "
            f"आप इन तारीखों पर कोशिश कर सकते हैं: {suggestions}"
        )

    slot_times = ", ".join(s["time"] for s in available)
    return (
        f"{date_str} के लिए उपलब्ध स्लॉट: {slot_times}. "
        f"कृपया बुकिंग करने से पहले पसंदीदा समय बताएं।"
    )


def _suggest_next_available(after: str, limit: int = 3) -> str:
    """Helper: suggest the next dates that have available slots."""
    suggestions = []
    try:
        start = datetime.strptime(after, "%Y-%m-%d").date()
    except ValueError:
        return "तारीख फॉर्मेट गलत है।"
    for i in range(1, 10):
        d = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        slots = SERVICE_SLOTS.get(d, [])
        if any(s.get("available") for s in slots):
            suggestions.append(d)
        if len(suggestions) >= limit:
            break
    return ", ".join(suggestions) if suggestions else "आने वाले दिनों में कोई स्लॉट उपलब्ध नहीं है।"


def book_service_slot(
    phone: str, date_str: str, slot_time: str, user_confirmed: bool = False
) -> str:
    """
    Book a service slot.
    Requires explicit confirmation (user_confirmed=True) before mutating state.
    If not confirmed, returns a Hindi confirmation prompt first.
    After booking, returns a booking reference ID and Hindi follow-up summary.
    """
    # Validate date format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return "क्षमा करें, तारीख का फॉर्मेट गलत है। कृपया YYYY-MM-DD फॉर्मेट में दें।"

    slots = SERVICE_SLOTS.get(date_str, [])
    slot = next((s for s in slots if s["time"] == slot_time), None)
    if not slot:
        return (
            f"क्षमा करें, {date_str} पर {slot_time} समय का कोई स्लॉट मौजूद नहीं है। "
            f"कृपया उपलब्ध स्लॉट में से चुनें।"
        )
    if not slot.get("available"):
        return (
            f"क्षमा करें, {date_str} पर {slot_time} स्लॉट पहले ही बुक हो चुका है। "
            f"कृपया दूसरा समय चुनें।"
        )

    # Explicit confirmation required before mutating state
    if not user_confirmed:
        return (
            f"कृपया पुष्टि करें: क्या आप {date_str} पर {slot_time} का स्लॉट बुक करना चाहते हैं? "
            f"पुष्टि के लिए user_confirmed=true के साथ अनुरोध भेजें।"
        )

    # Mutate state: mark slot unavailable and create booking
    slot["available"] = False
    booking_ref = f"SV{uuid.uuid4().hex[:8].upper()}"
    BOOKINGS[booking_ref] = {
        "phone": phone,
        "date": date_str,
        "time": slot_time,
        "status": "confirmed",
        "created_at": datetime.now().isoformat(),
    }

    # Update citizen context
    ctx = CITIZEN_CONTEXT.get(phone, {})
    ctx["last_booking"] = booking_ref
    ctx["last_service_date"] = date_str
    CITIZEN_CONTEXT[phone] = ctx

    return (
        f"आपकी बुकिंग सफलतापूर्वक हो गई है! बुकिंग संदर्भ संख्या: {booking_ref}. "
        f"तारीख: {date_str}, समय: {slot_time}. "
        f"कृपया इस संदर्भ संख्या को सुरक्षित रखें। धन्यवाद!"
    )