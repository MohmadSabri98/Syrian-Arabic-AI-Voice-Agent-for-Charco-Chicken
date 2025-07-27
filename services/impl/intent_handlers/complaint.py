from .base import IntentHandler
from constants.app_constants import DEFAULT_REPLY, CUSTOMER_SERVICE_NUMBER, CUSTOMER_SERVICE_HOURS

class ComplaintHandler(IntentHandler):
    def handle(self, transcription, intent_info, service) -> dict:
        order_is_valid = False
        reply_text = intent_info.get("reply_text", DEFAULT_REPLY)
        lower_trans = transcription.lower()
        
        # Handle different types of complaints
        if any(word in lower_trans for word in ["تأخر", "بطيء", "بطيئة", "بطيئ", "بطيئين"]):
            reply_text = "عذراً على التأخير! نحن نعمل بجد لتسريع الطلبات. الوقت المتوقع للطلبات هو 15-20 دقيقة. إذا كان طلبك متأخر أكثر من ذلك، يرجى الاتصال بنا على الرقم: 011-123-4567"
        elif any(word in lower_trans for word in ["خطأ", "غلط", "مشكلة", "مشاكل"]):
            reply_text = "عذراً على المشكلة! نحن نعتذر عن أي إزعاج. يرجى الاتصال بنا على الرقم: 011-123-4567 وسنحل المشكلة فوراً"
        elif any(word in lower_trans for word in ["سيء", "رديء", "مزعج", "مزعجة"]):
            reply_text = "نعتذر بشدة عن التجربة السيئة! نحن نعمل على تحسين خدمتنا باستمرار. يرجى الاتصال بنا على الرقم: 011-123-4567 لنسمع منك ونحسن خدمتنا"
        elif any(word in lower_trans for word in ["سعر", "غالي", "مكلف", "تكلفة"]):
            reply_text = "نفهم قلقك بخصوص الأسعار! نحن نقدم أفضل جودة بأفضل سعر ممكن. يمكنك الاطلاع على قائمة الأسعار أو الاتصال بنا للمناقشة"
        elif any(word in lower_trans for word in ["جودة", "طعام", "مذاق", "طعم"]):
            reply_text = "نعتذر إذا لم تكن جودة الطعام كما توقعتم! نحن نستخدم أفضل المكونات الطازجة. يرجى الاتصال بنا على الرقم: 011-123-4567 لنسمع ملاحظاتكم"
        else:
            reply_text = "نعتذر عن أي إزعاج! نحن هنا لمساعدتك. يرجى الاتصال بنا على الرقم: 011-123-4567 أو زيارة مطعمنا مباشرة لنحل المشكلة"
        
        return {
            "intent": "complaint",
            "name": intent_info.get("name"),
            "items": [],  # Complaints don't need order items
            "reply_text": reply_text,
            "order_is_valid": order_is_valid
        } 