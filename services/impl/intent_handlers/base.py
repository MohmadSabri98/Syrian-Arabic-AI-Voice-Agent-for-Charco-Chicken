from abc import ABC, abstractmethod

class IntentHandler(ABC):
    @abstractmethod
    def handle(self, transcription, intent_info, service) -> dict:
        pass 