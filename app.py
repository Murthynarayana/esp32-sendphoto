
import streamlit as st
import requests
from datetime import datetime
from io import BytesIO

# ==========================================
# ESP32 CAMERA CONFIGURATION
# ==========================================

CAMERA_URL = "http://192.168.1.10/capture"

# ==========================================
# STREAMLIT PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="ESP32 Telegram Camera",
    page_icon="📷",
    layout="centered"
)

st.title("📷 ESP32-CAM Remote Telegram")
st.caption("Capture photographs and send them to Telegram")

st.divider()

# ==========================================
# TELEGRAM CONFIGURATION
# ==========================================

BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# ==========================================
# SESSION STATE
# ==========================================

if "photo" not in st.session_state:
    st.session_state.photo = None

if "photo_time" not in st.session_state:
    st.session_state.photo_time = None

# ==========================================
# CAMERA STATUS
# ==========================================

st.subheader("Camera Control")

st.write("Camera IP: `192.168.1.10`")

# ==========================================
# CAPTURE PHOTO FUNCTION
# ==========================================

def capture_photo():

    try:
        response = requests.get(
            CAMERA_URL,
            timeout=25
        )

        response.raise_for_status()

        photo = response.content

        # Check JPEG file signature
        if not photo.startswith(b"\xff\xd8"):
            st.error(
                "ESP32 did not return a valid JPEG photograph."
            )
            st.write("Response content type:",
                     response.headers.get("Content-Type"))
            return

        st.session_state.photo = photo

        st.session_state.photo_time = datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        st.success("Photograph captured successfully!")

    except requests.exceptions.Timeout:
        st.error("Camera response timed out.")

    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to ESP32-CAM. "
            "Check Wi-Fi and camera IP address."
        )

    except requests.exceptions.RequestException as e:
        st.error(f"Camera error: {e}")


# ==========================================
# SEND PHOTO TO TELEGRAM FUNCTION
# ==========================================

def send_to_telegram(photo):

    telegram_url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendPhoto"
    )

    try:

        files = {
            "photo": (
                "ESP32-CAM.jpg",
                BytesIO(photo),
                "image/jpeg"
            )
        }

        data = {
            "chat_id": CHAT_ID,
            "caption": (
                "ESP32-CAM Photograph\n"
                + datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            )
        }

        response = requests.post(
            telegram_url,
            data=data,
            files=files,
            timeout=45
        )

        result = response.json()

        if response.ok and result.get("ok"):

            st.success(
                "Photo successfully sent to Telegram!"
            )

            return True

        else:

            st.error(
                "Telegram error: "
                + result.get("description", "Unknown error")
            )

            return False

    except requests.exceptions.RequestException as e:

        st.error(f"Telegram connection error: {e}")

        return False


# ==========================================
# CAPTURE BUTTON
# ==========================================

if st.button(
    "📸 CAPTURE PHOTO",
    type="primary",
    use_container_width=True
):

    with st.spinner("Capturing photograph from ESP32-CAM..."):
        capture_photo()


# ==========================================
# DISPLAY CAPTURED PHOTO
# ==========================================

if st.session_state.photo is not None:

    st.divider()

    st.subheader("Captured Photograph")

    st.image(
        st.session_state.photo,
        caption="ESP32-CAM Photograph",
        use_container_width=True
    )

    st.caption(
        f"Captured at: {st.session_state.photo_time}"
    )

    # ======================================
    # SEND TO TELEGRAM BUTTON
    # ======================================

    if st.button(
        "📨 SEND TO TELEGRAM",
        type="primary",
        use_container_width=True
    ):

        with st.spinner("Sending photograph to Telegram..."):

            send_to_telegram(st.session_state.photo)

    # ======================================
    # RETAKE PHOTO BUTTON
    # ======================================

    if st.button(
        "🔄 CAPTURE ANOTHER PHOTO",
        use_container_width=True
    ):

        st.session_state.photo = None
        st.session_state.photo_time = None

        st.rerun()

st.divider()

st.caption("ESP32-CAM | Streamlit | Telegram Bot API")
