from .base import IntentHandler
from constants.app_constants import DEFAULT_REPLY
from enums.intent_enum import IntentEnum

class GratitudeHandler(IntentHandler):
    def handle(self, transcription, intent_info, service) -> dict:
        order_is_valid = False
        reply_text = intent_info.get("reply_text", DEFAULT_REPLY)
        lower_trans = transcription.lower()
        intent_name_arabic =IntentEnum.GRATITUDE.code
        # Handle different types of gratitude expressions
        if any(word in lower_trans for word in ["شكرا", "شكراً", "مشكور", "مشكورة", "أشكرك", "أشكركم"]):
            reply_text = "نحنا بخدمتك دايماً! إن شاء الله يعجبك طلبك الجاي."
        elif any(word in lower_trans for word in ["أهلا", "أهلاً", "مرحبا", "مرحباً"]):
            reply_text = "أهلاً وسهلاً بك! كيف يمكنني مساعدتك اليوم؟"
            intent_name_arabic = "ترحيب"
        elif any(word in lower_trans for word in ["ممتاز", "رائع", "جميل", "حلو"]):
            reply_text = "شكراً لك! نحن سعداء أن نقدم لك أفضل خدمة ممكنة."
        else:
            reply_text = "نحنا بخدمتك دايماً! إن شاء الله يعجبك طلبك الجاي."
        
        return {
            "intent": intent_name_arabic,
            "name": intent_info.get("name"),
            "items": [],  # Gratitude doesn't need order items
            "reply_text": reply_text,
            "order_is_valid": order_is_valid
        } 