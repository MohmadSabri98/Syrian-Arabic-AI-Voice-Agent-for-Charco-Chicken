import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from constants.intent_constants import MODEL_DIR, MAX_INPUT_LENGTH, MAX_OUTPUT_LENGTH, NUM_BEAMS

class IntentServiceImpl:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def detect_intent(self, utterance: str) -> str:
        inputs = self.tokenizer(
            utterance,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=MAX_INPUT_LENGTH
        ).to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=MAX_OUTPUT_LENGTH,
                num_beams=NUM_BEAMS,
                early_stopping=True
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def process_intent_request(self, text: str, voice_agent_service) -> dict:
        transcription = text
        intent_info = voice_agent_service.extract_intent(transcription)
        reply_text = intent_info.get("reply_text", "")
        audio_base64 = voice_agent_service.generate_audio(reply_text)
        return {
            "transcription": transcription,
            "intent": intent_info,
            "reply_text": reply_text,
            "audio_base64": audio_base64
        } 