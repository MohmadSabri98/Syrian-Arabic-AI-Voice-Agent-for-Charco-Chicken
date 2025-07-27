from .base import IntentHandler
from constants.order_constants import ORDER_KEYWORDS, PRICING_MAPPING
from constants.app_constants import DEFAULT_REPLY, ORDER_ETA
from services.impl.order_service_impl import OrderServiceImpl

class PlaceOrderHandler(IntentHandler):
    def handle(self, transcription, intent_info, service) -> dict:
        name = intent_info.get("name")
        items = OrderServiceImpl.extract_order_items(transcription)
        order_is_valid = False
        reply_text = intent_info.get("reply_text", DEFAULT_REPLY)
        
        # Check if we found any valid items
        valid_items = [item for item in items if item in ORDER_KEYWORDS]
        missing_items = [item for item in items if item not in ORDER_KEYWORDS]
        
        if not valid_items and items:
            # No valid items found, show menu
            menu_list = "، ".join(ORDER_KEYWORDS)
            reply_text = f"عذراً، {', '.join(missing_items)} غير متوفر حالياً. الأطباق المتوفرة لدينا: {menu_list}. يرجى اختيار صنف من القائمة المتوفرة."
        elif not valid_items and not items:
            # No items detected at all
            menu_list = "، ".join(ORDER_KEYWORDS)
            reply_text = f"أهلاً! الأطباق المتوفرة لدينا: {menu_list}. من فضلك أخبرني ماذا تريد أن تطلب."
        elif not name and valid_items:
            # Valid items found but no name provided
            items_str = " و ".join(valid_items)
            reply_text = f"ممتاز! {items_str} متوفر لدينا. من فضلك أخبرني باسمك لإكمال الطلب."
        elif valid_items and name:
            # Both valid items and name provided
            items_str = " و ".join(valid_items)
            reply_text = f"تم استلام طلبك {items_str}! رقم الطلب: [سيتم تحديده], الوقت المتوقع: {ORDER_ETA}"
            order_is_valid = True
        else:
            reply_text = "يرجى تحديد الطلب واسمك لإكمال العملية."
        
        return {
            "intent": "place_order",
            "name": name,
            "items": items,
            "reply_text": reply_text,
            "order_is_valid": order_is_valid
        } 