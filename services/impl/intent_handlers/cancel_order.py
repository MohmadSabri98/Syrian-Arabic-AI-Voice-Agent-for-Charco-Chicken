from .base import IntentHandler
from constants.app_constants import DEFAULT_REPLY
from enums.intent_enum import IntentEnum

class CancelOrderHandler(IntentHandler):
    def handle(self, transcription, intent_info, service) -> dict:
        order_is_valid = False
        reply_text = intent_info.get("reply_text", DEFAULT_REPLY)
        lower_trans = transcription.lower()
        
        # Handle different types of order cancellation
        if any(word in lower_trans for word in ["إلغاء", "إلغي", "ألغى", "ألغيت"]):
            reply_text = "تم إلغاء طلبك. إذا كنت تريد إعادة الطلب، يمكنك طلب جديد في أي وقت."
        elif any(word in lower_trans for word in ["لا أريد", "لا اريد", "بدي ألغى", "بدي إلغاء"]):
            reply_text = "فهمت! تم إلغاء طلبك. إذا غيرت رأيك، يمكنك طلب جديد في أي وقت."
        elif any(word in lower_trans for word in ["تغيير", "غير", "بدل"]):
            reply_text = "إذا كنت تريد تغيير طلبك، يمكنك طلب جديد بالتفاصيل المطلوبة."
        else:
            reply_text = "تم إلغاء طلبك. شكراً لك!"
        
        return {
            "intent": IntentEnum.CANCEL_ORDER.code,
            "name": intent_info.get("name"),
            "items": [],  # Cancellation doesn't need order items
            "reply_text": reply_text,
            "order_is_valid": order_is_valid
        } 