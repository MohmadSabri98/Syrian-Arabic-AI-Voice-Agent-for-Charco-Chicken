from .base import IntentHandler
from constants.order_constants import ORDER_KEYWORDS, PRICING_MAPPING
from constants.app_constants import DEFAULT_REPLY, CUSTOMER_SERVICE_NUMBER, CUSTOMER_SERVICE_HOURS, CUSTOMER_SERVICE_ADDRESS
from services.impl.order_service_impl import OrderServiceImpl

class QuestionHandler(IntentHandler):
    def handle(self, transcription, intent_info, service) -> dict:
        order_is_valid = False
        reply_text = intent_info.get("reply_text", DEFAULT_REPLY)
        lower_trans = transcription.lower()
        if "مواعيد" in lower_trans or "ساعات العمل" in lower_trans or "متى" in lower_trans:
            reply_text = CUSTOMER_SERVICE_HOURS
        elif "رقم" in lower_trans or "هاتف" in lower_trans or "اتصال" in lower_trans:
            reply_text = f"رقم خدمة العملاء هو {CUSTOMER_SERVICE_NUMBER}."
        elif "عنوان" in lower_trans or "موقع" in lower_trans or "اين" in lower_trans:
            reply_text = f"عنواننا: {CUSTOMER_SERVICE_ADDRESS}."
        elif "اسعار" in lower_trans or "سعر" in lower_trans or "التكلفة" in lower_trans or "كم يكلف" in lower_trans:
            pricing_items = []
            for item in ORDER_KEYWORDS:
                price = PRICING_MAPPING.get(item, '10,000 ليرة')
                pricing_items.append(f"🍽️ {item}: {price}")
            pricing_text = "، ".join(pricing_items)
            reply_text = f"أسعارنا كالتالي: {pricing_text}. الأسعار تشمل الضريبة!"
        elif "قائمة الاسعار" in lower_trans or "قائمة الاسعار" in lower_trans:
            pricing_lines = []
            for item in ORDER_KEYWORDS:
                price = PRICING_MAPPING.get(item, '10,000 ليرة')
                pricing_lines.append(f"🍽️ {item}: {price}")
            pricing_text = "\n".join(pricing_lines)
            reply_text = f"قائمة الأسعار الكاملة:\n{pricing_text}"
        else:
            reply_text = "سؤالك مهم! يرجى توضيح السؤال أو التواصل مع خدمة العملاء."
        return {
            "intent": "question",
            "name": intent_info.get("name"),
            "items": [],  # Questions don't need order items
            "reply_text": reply_text,
            "order_is_valid": order_is_valid
        } 