import os
import tempfile
import whisper

model = whisper.load_model("large")

class WhisperServiceImpl:
    async def transcribe_audio(self, audio_data: bytes) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        try:
            result = model.transcribe(tmp_path, language='ar')
            return result['text']
        finally:
            os.remove(tmp_path) 