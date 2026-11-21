"""
स्थानीय परीक्षण स्क्रिप्ट sevavoice-hindi उपकरणों के लिए।
नेटवर्क या API कुंजियों की आवश्यकता नहीं है।
"""

from datetime import datetime, timedelta
from tools import lookup_citizen_context, check_service_slots, book_service_slot


def print_section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_lookup_existing_citizen() -> None:
    print_section("परीक्षण 1: मौजूदा नागरिक का संदर्भ खोजना")
    result = lookup_citizen_context("+919876543210")
    print(result)
    assert "राम शर्मा" in result, "नागरिक का नाम सारांश में होना चाहिए"
    assert "बिजली कनेक्शन" in result, "अंतिम सेवा सारांश में होनी चाहिए"
    print("✓ पास")


def test_lookup_unknown_citizen() -> None:
    print_section("परीक्षण 2: अज्ञात नागरिक के लिए विनम्र हिंदी त्रुटि")
    result = lookup_citizen_context("+910000000000")
    print(result)
    assert "क्षमा करें" in result, "त्रुटि क्षमापूर्वक होनी चाहिए"
    assert "पूर्व जानकारी" in result, "कोई पूर्व जानकारी न होने का उल्लेख होना चाहिए"
    print("✓ पास")


def test_check_slots_available() -> None:
    print_section("परीक्षण 3: सेवा स्लॉट जाँचना (उपलब्ध)")
    from datetime import datetime, timedelta

    tomorrow = (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")
    result = check_service_slots(tomorrow)
    print(result)
    assert "उपलब्ध स्लॉट" in result, "उपलब्ध स्लॉट सूचीबद्ध होने चाहिए"
    print("✓ पास")


def test_check_slots_full() -> None:
    print_section("परीक्षण 4: सेवा स्लॉट जाँचना (भरा हुआ / सुझाव)")
    # एक तारीख चुनें और सभी स्लॉट बुक करें
    from datetime import datetime, timedelta

    target = (datetime.now().date() + timedelta(days=2)).strftime("%Y-%m-%d")
    slots = __import__("tools").SERVICE_SLOTS[target]
    for s in slots:
        s["available"] = False
    try:
        result = check_service_slots(target)
        print(result)
        assert "भर चुके हैं" in result, "भरे हुए स्लॉट का उल्लेख होना चाहिए"
        assert "तारीखों पर कोशिश कर सकते हैं" in result, "विनम्र सुझाव होना चाहिए"
    finally:
        # स्लॉट्स को अगले परीक्षणों के लिए रीसेट करें
        for s in slots:
            s["available"] = True
    print("✓ पास")


def test_check_slots_invalid_date() -> None:
    print_section("परीक्षण 5: अमान्य तारीख फॉर्मेट")
    result = check_service_slots("20-02-2024")
    print(result)
    assert "फॉर्मेट गलत है" in result, "फॉर्मेट त्रुटि हिंदी में होनी चाहिए"
    print("✓ पास")


def test_book_without_confirmation() -> None:
    print_section("परीक्षण 6: बिना पुष्टि के बुकिंग (आवश्यक स्पष्ट पुष्टि)")
    tomorrow = (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")
    from tools import SERVICE_SLOTS
    slot_time = SERVICE_SLOTS[tomorrow][0]["time"]
    result = book_service_slot("+919876543210", tomorrow, slot_time, user_confirmed=False)
    print(result)
    assert "पुष्टि करें" in result, "पुष्टि संकेत लौटाना चाहिए"
    assert "user_confirmed=true" in result, "पुष्टि निर्देश शामिल होना चाहिए"
    # स्लॉट अभी भी उपलब्ध होना चाहिए (कोई उत्परिवर्तन नहीं)
    assert SERVICE_SLOTS[tomorrow][0]["available"] is True, "स्थिति नहीं बदलनी चाहिए"
    print("✓ पास")


def test_book_with_confirmation() -> None:
    print_section("परीक्षण 7: पुष्टि के साथ बुकिंग (स्थिति उत्परिवर्तन)")
    tomorrow = (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")
    from tools import SERVICE_SLOTS
    slot_time = SERVICE_SLOTS[tomorrow][1]["time"]
    result = book_service_slot("+919876543210", tomorrow, slot_time, user_confirmed=True)
    print(result)
    assert "सफलतापूर्वक" in result, "सफलता संदेश हिंदी में होना चाहिए"
    assert "संदर्भ संख्या" in result, "बुकिंग संदर्भ संख्या शामिल होनी चाहिए"
    assert "SV" in result, "संदर्भ संख्या SV से शुरू होनी चाहिए"
    # स्लॉट अब उपलब्ध नहीं होना चाहिए
    assert SERVICE_SLOTS[tomorrow][1]["available"] is False, "स्लॉट चिह्नित unavailable होना चाहिए"
    print("✓ पास")


def test_book_already_booked() -> None:
    print_section("परीक्षण 8: पहले से बुक स्लॉट बुक करने का प्रयास")
    tomorrow = (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")
    from tools import SERVICE_SLOTS
    slot_time = SERVICE_SLOTS[tomorrow][1]["time"]  # उपरोक्त परीक्षण से बुक किया गया
    result = book_service_slot("+919876543210", tomorrow, slot_time, user_confirmed=True)
    print(result)
    assert "पहले ही बुक हो चुका है" in result, "डुप्लीकेट बुकिंग अस्वीकृत होनी चाहिए"
    print("✓ पास")


if __name__ == "__main__":
    test_lookup_existing_citizen()
    test_lookup_unknown_citizen()
    test_check_slots_available()
    test_check_slots_full()
    test_check_slots_invalid_date()
    test_book_without_confirmation()
    test_book_with_confirmation()
    test_book_already_booked()
    print("\n" + "=" * 60)
    print("सभी परीक्षण पास हो गए हैं! ✅")
    print("=" * 60)