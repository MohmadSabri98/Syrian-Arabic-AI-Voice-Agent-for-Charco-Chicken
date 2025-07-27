from .base import IntentHandler
from constants.order_constants import ORDER_KEYWORDS
from constants.app_constants import DEFAULT_REPLY, ORDER_ETA
from services.impl.order_service_impl import OrderServiceImpl

class ProvideNameHandler(IntentHandler):
    def handle(self, transcription, intent_info, service) -> dict:
        # Extract name from transcription if not already provided
        name = intent_info.get("name")
        if not name:
            name = OrderServiceImpl.extract_name_from_transcription(transcription)
        
        items = OrderServiceImpl.extract_order_items(transcription)
        order_is_valid = False
        reply_text = intent_info.get("reply_text", DEFAULT_REPLY)
        
        if name and items:
            valid_items = [item for item in items if item in ORDER_KEYWORDS]
            if valid_items:
                items_str = " و ".join(valid_items)
                reply_text = f"تم استلام طلبك {items_str}! رقم الطلب: [سيتم تحديده], الوقت المتوقع: {ORDER_ETA}"
                order_is_valid = True
                intent_type = "place_order"
            else:
                menu_list = "، ".join(ORDER_KEYWORDS)
                reply_text = f"عذراً، الصنف المطلوب غير متوفر. الأطباق المتوفرة لدينا: {menu_list}."
        elif name:
            menu_list = "، ".join(ORDER_KEYWORDS)
            reply_text = f"أهلاً {name}! الأطباق المتوفرة لدينا: {menu_list}. ما الذي ترغب بطلبه اليوم؟"
        else:
            reply_text = "يرجى تزويدي باسمك."
        
        return {
            "intent": "provide_name",
            "name": name,
            "items": items,
            "reply_text": reply_text,
            "order_is_valid": order_is_valid
        } 