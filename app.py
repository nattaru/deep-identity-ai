import streamlit as st
import google.generativeai as genai
import json

# --- 1. การตั้งค่าหน้าตาแอป (UI Configuration) ---
st.set_page_config(page_title="Deep Identity AI", page_icon="🔮", layout="centered")

# แก้ไขจุดที่เคย Error: เปลี่ยนเป็น unsafe_allow_html=True
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        font-size: 16px;
        margin-bottom: 10px;
        background-color: #ffffff;
        border: 2px solid #1E88E5;
        color: #1E88E5;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1E88E5;
        color: white;
    }
    .question-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-top: 10px solid #1E88E5;
        font-size: 20px;
        color: #333;
        margin-bottom: 25px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ส่วนหลังบ้าน: เชื่อมต่อ API ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("ไม่พบ API Key! กรุณาใส่ GEMINI_API_KEY ในหน้า Settings > Secrets ของ Streamlit Cloud")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# กำหนดบทบาทของ AI
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

หมายเหตุ: ใน JSON ให้ใช้ true/false ตัวพิมพ์เล็กตามมาตรฐาน JSON แต่ใน Python Code เราจะจัดการเอง
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=instruction
)

# --- 3. การจัดการสถานะของแอป (Session State) ---
# แก้ไขจุดที่เคย Error: ใช้ True/False ตัวพิมพ์ใหญ่สำหรับ Python
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.last_response = {
        "question": "สวัสดีครับ ยินดีต้อนรับสู่การวิเคราะห์ตัวตนแบบเจาะลึก... คุณพร้อมจะเริ่มค้นหาคำตอบหรือยัง?",
        "options": ["เริ่มกันเลย!", "ยังไม่พร้อม"],
        "is_final": False
    }

# ฟังก์ชันส่งคำตอบ
def send_answer(selected_option):
    with st.spinner("AI กำลังวิเคราะห์คำตอบของคุณ..."):
        try:
            response = st.session_state.chat.send_message(selected_option)
            # แปลง JSON string จาก AI มาเป็น Python Dictionary
            clean_json = response.text.replace('```json', '').replace('
```', '').strip()
            st.session_state.last_response = json.loads(clean_json)
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")

# --- 4. ส่วนหน้าบ้าน (Display) ---
st.title("🔮 Deep Identity AI")
st.write("ระบบวิเคราะห์บุคลิกภาพ Adaptive ขั้นสูง")

res = st.session_state.last_response

# เช็คว่าเป็นคำถามทั่วไปหรือผลลัพธ์สุดท้าย
if not res.get("is_final"):
    # แสดงคำถาม
    st.markdown(f'<div class="question-box">{res["question"]}</div>', unsafe_allow_html=True)
    
    # สร้างปุ่มตัวเลือก
    cols = st.columns(1) # ปรับเป็น 1 คอลัมน์เพื่อให้กดง่ายในมือถือ
    for option in res.get("options", []):
        if st.button(option):
            send_answer(option)
            st.rerun()
else:
    # แสดงผลการวิเคราะห์สุดท้าย
    st.balloons()
    st.success("วิเคราะห์เสร็จสมบูรณ์!")
    st.markdown("### 📊 ผลการวิเคราะห์อย่างละเอียด")
    st.info(res.get("analysis"))
    
    if st.button("ทำแบบทดสอบใหม่อีกครั้ง"):
        st.session_state.clear()
        st.rerun()

# แถบข้างด้านข้าง
with st.sidebar:
    st.write("### ข้อมูลแอป")
    st.caption("เวอร์ชัน: 1.2 (Stable)")
    st.caption("โมเดล: Gemini 1.5 Flash")
    if st.button("Reset Game"):
        st.session_state.clear()
        st.rerun()
