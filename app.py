import streamlit as st
import google.generativeai as genai
import json

# --- 1. การตั้งค่าหน้าตาแอป ---
st.set_page_config(page_title="Deep Identity AI", page_icon="🔮", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        font-size: 16px;
        margin-bottom: 10px;
        background-color: #ffffff;
        border: 2px solid #1565C0;
        color: #1565C0;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1565C0;
        color: white;
    }
    .question-box {
        background-color: #e3f2fd;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #1565C0;
        font-size: 18px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ส่วนหลังบ้าน: การเชื่อมต่อ Gemini ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("กรุณาใส่ API Key ใน Settings > Secrets ก่อนครับ")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ปรับ Instruction ให้ AI ส่งข้อมูลกลับมาเป็น JSON เสมอ
instruction = """
คุณคือ Master Psychometrician หน้าที่คือวิเคราะห์ MBTI และ Enneagram
**กฎเหล็ก:** คุณต้องตอบกลับในรูปแบบ JSON เท่านั้น ห้ามมีข้อความอื่นนอก JSON

รูปแบบ JSON ที่ต้องส่ง:
{
  "question": "ข้อความคำถามที่นี่...",
  "options": ["ตัวเลือกที่ 1", "ตัวเลือกที่ 2", "ตัวเลือกที่ 3"],
  "is_final": false,
  "analysis": "ผลสรุปจะใส่ตรงนี้เมื่อ is_final เป็น true เท่านั้น"
}

เมื่อคุณมั่นใจในผลลัพธ์ (Accuracy > 85%) ให้ส่ง is_final: true และใส่บทวิเคราะห์เต็มๆ ในช่อง analysis
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=instruction
)

# --- 3. การจัดการ Session ---
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.last_response = {
        "question": "ยินดีต้อนรับสู่การค้นหาตัวตนที่แท้จริง พร้อมจะเริ่มการวิเคราะห์แบบเจาะลึกหรือยังครับ?",
        "options": ["เริ่มกันเลย!", "ขอข้อมูลเพิ่มเติม"],
        "is_final": false
    }

# --- 4. ฟังก์ชันการส่งข้อมูล ---
def send_answer(answer):
    with st.spinner("AI กำลังวิเคราะห์..."):
        response = st.session_state.chat.send_message(answer)
        try:
            # แปลงข้อความ JSON จาก AI เป็น Dictionary ของ Python
            st.session_state.last_response = json.loads(response.text)
        except:
            st.error("เกิดข้อผิดพลาดในการประมวลผล กรุณาลองใหม่อีกครั้ง")

# --- 5. ส่วนหน้าบ้าน (Frontend) ---
st.title("🔮 Deep Identity AI")
st.write("แตะเลือกคำตอบที่ตรงกับความเป็นคุณที่สุด")

res = st.session_state.last_response

if not res.get("is_final"):
    # แสดงคำถาม
    st.markdown(f'<div class="question-box">{res["question"]}</div>', unsafe_allow_status=True)
    
    # สร้างปุ่มจากตัวเลือกที่ AI ส่งมา
    for option in res["options"]:
        if st.button(option):
            send_answer(option)
            st.rerun()
else:
    # แสดงผลสรุปสุดท้าย
    st.balloons()
    st.success("วิเคราะห์เสร็จสมบูรณ์!")
    st.markdown("### 📊 ผลการวิเคราะห์ของคุณ")
    st.write(res["analysis"])
    
    if st.button("เริ่มทำแบบทดสอบใหม่"):
        st.session_state.clear()
        st.rerun()
