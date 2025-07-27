import streamlit as st
import requests
import base64
from enums.intent_enum import IntentEnum
from services.impl.order_service_impl import OrderServiceImpl
from constants.app_constants import API_URL

def handle_order_placement(intent_info, name, dialog_history, user_input):
    """
    Handle order placement logic for both text and audio inputs.
    Returns updated reply_text, audio_base64, and success status.
    """
    order_is_valid = intent_info.get("order_is_valid", False)
    detected_intent = intent_info.get("intent")
    order_items = intent_info.get("items", [])
    
    print(f"DEBUG: handle_order_placement - order_is_valid: {order_is_valid}, detected_intent: {detected_intent}")
    print(f"DEBUG: intent_info: {intent_info}")
    print(f"DEBUG: name: {name}, order_items: {order_items}")
    
    # Check if we have a valid order (items and name)
    if detected_intent == "place_order" and order_items and name:
        # Override order_is_valid if we have items and name
        order_is_valid = True
        print(f"DEBUG: Valid order detected - items: {order_items}, name: {name}")
    
    if detected_intent == "place_order" and order_is_valid:
        payload = {
            "name": name,
            "order": order_items,
            "dialog_history": dialog_history + [user_input],
        }
        print(f"DEBUG: Submitting order with payload: {payload}")
        order_resp = requests.post(f"{API_URL}/submit-order", json=payload)
        if order_resp.ok:
            order_data = order_resp.json()
            items_str = f" ({', '.join(order_items)})" if order_items else ""
            reply_text = f"تم استلام طلبك{items_str}! رقم الطلب: {order_data['order_id']}, الوقت المتوقع: {order_data['eta']}"
            # Generate audio for the new reply_text
            tts_resp = requests.post(f"{API_URL}/tts", json={"text": reply_text})
            audio_base64 = tts_resp.json().get("audio_base64", "") if tts_resp.ok else ""
            return reply_text, audio_base64, True
        else:
            print(f"DEBUG: Order submission failed: {order_resp.status_code} - {order_resp.text}")
            reply_text = order_resp.json().get("error", "خطأ في معالجة الطلب.")
            return reply_text, "", False
    else:
        print(f"DEBUG: Order not valid - order_is_valid: {order_is_valid}, detected_intent: {detected_intent}")
        # Use the reply_text from intent_info (which already has the appropriate message)
        return intent_info.get("reply_text", ""), "", False

def is_name_request(reply_text):
    """
    Check if the agent is asking for the user's name
    """
    name_keywords = ["اسمك", "اسم", "أخبرني باسمك", "ممكن اسمك"]
    return any(keyword in reply_text for keyword in name_keywords)

def extract_name_from_audio(audio_bytes):
    """
    Extract name from audio using the voice agent API
    """
    try:
        files = {"file": ("name_audio.wav", audio_bytes, "audio/wav")}
        response = requests.post(f"{API_URL}/voice-agent", files=files)
        if response.ok:
            data = response.json()
            transcription = data.get("transcription", "")
            intent_info = data.get("intent", {})
            
            # Extract name from transcription using the improved method
            name = OrderServiceImpl.extract_name_from_transcription(transcription)
            
            # If no name found in transcription, check intent info
            if not name:
                name = intent_info.get("name")
            
            return name, transcription, intent_info
    except Exception as e:
        st.error(f"Error processing name audio: {e}")
    
    return None, "", {}

st.set_page_config(page_title="Syrian Arabic Voice Agent", layout="wide")
st.title("Syrian Arabic Voice Agent for Charco Chicken")

# Conversation history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Store pending name request
if "pending_name_request" not in st.session_state:
    st.session_state["pending_name_request"] = False

# Tabs for main UI and monitoring
tabs = st.tabs(["Agent", "Monitoring Dashboard"])

with tabs[0]:
    st.header("Interact with the Voice Agent")

    if st.session_state["pending_name_request"]:
        st.info("🎤 The system is asking for your name. Please provide your name via voice or text.")
        name_input_mode = st.radio("Name input mode", ["Voice", "Text"], key="name_input_mode_voice")
        if name_input_mode == "Voice":
            st.write("#### Record Your Name")
            try:
                from st_audiorec import st_audiorec
                name_audio_bytes = st_audiorec()
                if name_audio_bytes and st.button("Send Name Audio"):
                    extracted_name, transcription, intent_info = extract_name_from_audio(name_audio_bytes)
                    if extracted_name:
                        name = extracted_name
                        st.success(f"Name extracted: {name}")
                        st.session_state["pending_name_request"] = False
                        if st.session_state["history"]:
                            last_entry = st.session_state["history"][-1]
                            last_entry["intent"]["name"] = name
                            updated_reply_text, updated_audio_base64, order_success = handle_order_placement(
                                last_entry["intent"], name, [entry["input"] for entry in st.session_state["history"]], last_entry.get("transcription", "")
                            )
                            if order_success:
                                st.session_state["history"].append({
                                    "input": "[Voice Name]",
                                    "transcription": f"اسمي {name}",
                                    "intent": {
                                        "intent": "place_order",
                                        "name": name,
                                        "items": last_entry["intent"].get("items", []),
                                        "reply_text": updated_reply_text,
                                        "order_is_valid": True
                                    },
                                    "reply_text": updated_reply_text,
                                    "audio_base64": updated_audio_base64,
                                })
                                st.success("Order completed successfully!")
                            else:
                                st.error("Failed to complete order.")
                    else:
                        st.error("Could not extract name from audio. Please try again or use text input.")
            except ImportError:
                st.info("Please install streamlit-audiorec: pip install streamlit-audiorec")
        elif name_input_mode == "Text":
            name_text = st.text_input("Enter your name:", key="name_text_input")
            if st.button("Submit Name") and name_text:
                name = name_text
                st.session_state["pending_name_request"] = False
                if st.session_state["history"]:
                    last_entry = st.session_state["history"][-1]
                    last_entry["intent"]["name"] = name
                    updated_reply_text, updated_audio_base64, order_success = handle_order_placement(
                        last_entry["intent"], name, [entry["input"] for entry in st.session_state["history"]], last_entry.get("transcription", "")
                    )
                    if order_success:
                        st.session_state["history"].append({
                            "input": "[Text Name]",
                            "transcription": f"اسمي {name}",
                            "intent": {
                                "intent": "place_order",
                                "name": name,
                                "items": last_entry["intent"].get("items", []),
                                "reply_text": updated_reply_text,
                                "order_is_valid": True
                            },
                            "reply_text": updated_reply_text,
                            "audio_base64": updated_audio_base64,
                        })
                        st.success("Order completed successfully!")
                    else:
                        st.error("Failed to complete order.")
    else:
        input_mode = st.radio("Input mode", ["Audio", "Text"])
        name = st.text_input("Your Name (optional)")
        dialog_history = [entry["input"] for entry in st.session_state["history"]]
        # Main input section
        if input_mode == "Audio":
            st.write("#### Record or Upload Audio")
            try:
                from st_audiorec import st_audiorec
                audio_bytes = st_audiorec()
            except ImportError:
                st.info("Please install streamlit-audiorec: pip install streamlit-audiorec")
                audio_bytes = None
            audio_file = st.file_uploader("Upload audio", type=["wav", "mp3"])
            audio_to_send = None
            user_audio_base64 = None
            if audio_bytes:
                audio_to_send = ("recorded.wav", audio_bytes, "audio/wav")
                user_audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            elif audio_file:
                audio_to_send = audio_file
                user_audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8") if audio_file else None
            if audio_to_send and st.button("Send Audio"):
                files = {"file": audio_to_send}
                response = requests.post(f"{API_URL}/voice-agent", files=files)
                if response.ok:
                    data = response.json()
                    intent_info = data.get("intent", {})
                    reply_text = data.get("reply_text", "")
                    audio_base64 = data.get("audio_base64", "")
                    # Check if this is a name request
                    if is_name_request(reply_text):
                        st.session_state["pending_name_request"] = True
                    # Handle order placement using the unified function
                    updated_reply_text, updated_audio_base64, order_success = handle_order_placement(
                        intent_info, name, dialog_history, data.get("transcription", "[Audio]")
                    )
                    if order_success:
                        reply_text = updated_reply_text
                        audio_base64 = updated_audio_base64
                        intent_info["reply_text"] = reply_text
                        st.session_state["pending_name_request"] = False
                    st.session_state["history"].append({
                        "input": "[Audio]",
                        "transcription": data.get("transcription"),
                        "intent": intent_info,
                        "reply_text": reply_text,
                        "audio_base64": audio_base64,  # agent reply audio
                        "user_audio_base64": user_audio_base64,  # user's original audio
                    })
                    st.success("Audio processed!")
                else:
                    st.error("Error processing audio.")
        else:
            text_input = st.text_input("Type your message in Arabic")
            if st.button("Send Text") and text_input:
                payload = {"text": text_input}
                response = requests.post(f"{API_URL}/detect-intent", json=payload)
                if response.ok:
                    data = response.json()
                    intent_info = data.get("intent", {})
                    reply_text = data.get("reply_text", "")
                    audio_base64 = data.get("audio_base64", "")
                    # Check if this is a name request
                    if is_name_request(reply_text):
                        st.session_state["pending_name_request"] = True
                    # Handle order placement using the unified function
                    updated_reply_text, updated_audio_base64, order_success = handle_order_placement(
                        intent_info, name, dialog_history, text_input
                    )
                    if order_success:
                        reply_text = updated_reply_text
                        audio_base64 = updated_audio_base64
                        intent_info["reply_text"] = reply_text
                        st.session_state["pending_name_request"] = False
                    st.session_state["history"].append({
                        "input": text_input,
                        "transcription": data.get("transcription", text_input),
                        "intent": intent_info,
                        "reply_text": reply_text,
                        "audio_base64": audio_base64,
                    })
                    st.success("تم إرسال الرسالة!")
                else:
                    st.error("خطأ في الاتصال بالخادم أو معالجة النص.")

    # Display conversation history

    # Display conversation history
    st.write("### Conversation History")
    for entry in st.session_state["history"]:
        st.write(f"**Input:** {entry['input']}")
        st.write(f"**Transcription:** {entry['transcription']}")
        
        # Show user audio if available (for audio inputs)
        if entry.get("input") == "[Audio]" and entry.get("user_audio_base64"):
            st.write("**User Audio:**")
            st.audio(base64.b64decode(entry["user_audio_base64"]), format="audio/wav")
        
        # Extract intent info
        intent = entry.get("intent")
        if isinstance(intent, dict):
            intent_str = intent.get("intent", "")
            intent_arabic = IntentEnum.get_arabic(intent_str)
            name = intent.get("name")
            items = intent.get("items", [])
        else:
            intent_str = intent or ""
            intent_arabic = IntentEnum.get_arabic(intent_str)
            name = None
            items = []
        st.write(f"**Intent:** {intent_arabic}")
        if name:
            st.write(f"**Name:** {name}")
        if items:
            st.write(f"**Items:** {', '.join(items)}")
        st.write(f"**Agent Reply:** {entry['reply_text']}")
        if entry.get("audio_base64"):
            st.audio(base64.b64decode(entry["audio_base64"]), format="audio/wav")
        st.markdown("---")

with tabs[1]:
    st.header("Monitoring Dashboard")
    st.write("#### Conversation Logs")
    for i, entry in enumerate(st.session_state["history"]):
        intent = entry.get("intent")
        # If intent is a dict, extract fields; if string, just show it
        if isinstance(intent, dict):
            intent_str = intent.get("intent", "")
            intent_arabic = IntentEnum.get_arabic(intent_str)
            name = intent.get("name")
            items = intent.get("items", [])
            reply_text = intent.get("reply_text", entry.get("reply_text", ""))
        else:
            intent_str = intent or ""
            intent_arabic = IntentEnum.get_arabic(intent_str)
            name = None
            items = []
            reply_text = entry.get("reply_text", "")
        # User input (text transcription)
        st.markdown(f"**{i+1}. User Input (Text):** {entry.get('transcription', entry['input'])}")
        # User audio (if available)
        if entry.get("input") == "[Audio]" and entry.get("user_audio_base64"):
            st.markdown("**User Audio:**")
            st.audio(base64.b64decode(entry["user_audio_base64"]), format="audio/wav")
        # Detected intent
        st.markdown(f"**Detected Intent:** {intent_arabic}")
        # Agent reply (text)
        st.markdown(f"**Agent Reply (Text):** {reply_text}")
        # Agent reply (audio)
        if entry.get("audio_base64"):
            st.markdown("**Agent Reply (Audio):**")
            st.audio(base64.b64decode(entry["audio_base64"]), format="audio/wav")
        st.markdown("---")
    st.info("This dashboard shows all conversation logs, user input (text/audio), detected intent, and agent replies (text/audio).") 