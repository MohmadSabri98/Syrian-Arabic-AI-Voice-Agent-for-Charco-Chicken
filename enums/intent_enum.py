from enum import Enum

class IntentEnum(Enum):
    GREETING_AND_MENU_REQUEST = ("greeting_and_menu_request", "طلب قائمة الطعام / الترحيب")
    PROVIDE_NAME = ("provide_name", "تقديم الاسم")
    PLACE_ORDER = ("place_order", "تقديم طلب")
    GRATITUDE = ("gratitude", "شكر")
    GOODBYE = ("goodbye", "وداع")
    ASK_ETA = ("ask_eta", "سؤال عن الوقت المتوقع")
    CANCEL_ORDER = ("cancel_order", "إلغاء الطلب")
    QUESTION = ("question", "سؤال")
    COMPLAINT = ("complaint", "شكوى")
    # Add more intents as needed

    def __init__(self, code, arabic):
        self.code = code
        self.arabic = arabic

    @classmethod
    def get_arabic(cls, code):
        for intent in cls:
            if intent.code == code:
                return intent.arabic
        return code  # fallback to code if not found 