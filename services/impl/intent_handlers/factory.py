from .place_order import PlaceOrderHandler
from .provide_name import ProvideNameHandler
from .question import QuestionHandler
from .greeting_and_menu import GreetingAndMenuRequestHandler
from .complaint import ComplaintHandler
from .gratitude import GratitudeHandler
from .cancel_order import CancelOrderHandler
from .base import IntentHandler
from enums.intent_enum import IntentEnum
from constants.app_constants import DEFAULT_REPLY
from services.impl.order_service_impl import OrderServiceImpl

class DefaultHandler(IntentHandler):
    def handle(self, transcription, intent_info, service) -> dict:
        intent_type = intent_info.get("intent", "")
        
        # Only extract order items for order-related intents
        items = []
        if intent_type in ["place_order", "greeting_and_menu_request"]:
            items = OrderServiceImpl.extract_order_items(transcription)
        
        return {
            "intent": intent_type,
            "name": intent_info.get("name"),
            "items": items,
            "reply_text": intent_info.get("reply_text", DEFAULT_REPLY),
            "order_is_valid": False
        }

class IntentHandlerFactory:
    @staticmethod
    def get_handler(intent_type):
        match intent_type:
            case IntentEnum.PLACE_ORDER.code:
                return PlaceOrderHandler()
            case IntentEnum.PROVIDE_NAME.code:
                return ProvideNameHandler()
            case IntentEnum.QUESTION.code:
                return QuestionHandler()
            case IntentEnum.GREETING_AND_MENU_REQUEST.code:
                return GreetingAndMenuRequestHandler()
            case IntentEnum.COMPLAINT.code:
                return ComplaintHandler()
            case IntentEnum.GRATITUDE.code:
                return GratitudeHandler()
            case IntentEnum.CANCEL_ORDER.code:
                return CancelOrderHandler()
            case _:
                return DefaultHandler() 