from .base import IntentHandler
from constants.order_constants import ORDER_KEYWORDS
from constants.app_constants import DEFAULT_REPLY, MENU_KEYWORDS, GREETING_KEYWORDS
from enums.intent_enum import IntentEnum
from services.impl.order_service_impl import OrderServiceImpl

class GreetingAndMenuRequestHandler(IntentHandler):
    def handle(self, transcription, intent_info, service) -> dict:
        order_is_valid = False
        reply_text = intent_info.get("reply_text", DEFAULT_REPLY)
        lower_trans = transcription.lower()
        has_menu_request = any(keyword in lower_trans for keyword in MENU_KEYWORDS)
        has_greeting = any(keyword in lower_trans for keyword in GREETING_KEYWORDS)
        if has_menu_request and has_greeting:
            menu_items = [f"🍽️ {item}" for item in ORDER_KEYWORDS]
            menu_text = "، ".join(menu_items)
            reply_text = f"أهلاً وسهلاً بك! عندنا قائمة متنوعة من الأطباق الشهية:\n\n{menu_text}\n\nشو بتحب تجرب؟"
        elif has_menu_request:
            menu_items = [f"🍽️ {item}" for item in ORDER_KEYWORDS]
            menu_text = "، ".join(menu_items)
            reply_text = f"أهلاً! عندنا قائمة متنوعة من الأطباق الشهية:\n\n{menu_text}\n\nشو بتحب تجرب؟"
        else:
            reply_text = "أهلاً وسهلاً بك في مطعمنا! كيف يمكنني مساعدتك اليوم؟"
        return {
            "intent": IntentEnum.GREETING_AND_MENU_REQUEST.code,
            "name": intent_info.get("name"),
            "items": OrderServiceImpl.extract_order_items(transcription),
            "reply_text": reply_text,
            "order_is_valid": order_is_valid
        } 