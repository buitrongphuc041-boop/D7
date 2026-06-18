import streamlit as st
import random
from groq import Groq

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="AI ENGLISH TUTOR", layout="wide")

st.title("🎓 AI ENGLISH TUTOR")

# Nhập API Key
api_key = st.sidebar.text_input("Groq API Key", type="password")

# Tabs cho các chức năng
tab1, tab2, tab3 = st.tabs(["💬 Chat", "✍️ Luyện Viết", "📚 Từ Vựng"])

with tab1:
    st.subheader("Trợ lý Giao Tiếp")
    prompt = st.text_input("Nhập câu hỏi của bạn:")
    if st.button("Gửi"):
        if api_key:
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            st.write(response.choices[0].message.content)
        else:
            st.warning("Vui lòng nhập API Key ở menu bên trái.")

with tab2:
    st.subheader("Luyện Viết")
    cau_mau = {"vi": "Tôi rất mong được hợp tác với công ty của bạn.", "en": "I look forward to cooperating with your company."}
    st.write(f"Dịch câu: **{cau_mau['vi']}**")
    user_trans = st.text_input("Nhập bản dịch:")
    if st.button("Kiểm tra"):
        if user_trans.lower().strip() == cau_mau['en'].lower().strip():
            st.success("Chính xác! 🎉")
        else:
            st.error("Chưa khớp, thử lại nhé!")

with tab3:
    st.subheader("Từ Vựng Chuyên Ngành")
    nganh = st.selectbox("Chọn chuyên ngành:", ["IT", "Y học", "Kinh tế"])
    if st.button("Tạo bài học"):
        st.info(f"Đang tạo nội dung cho ngành {nganh}...")
        # Ở đây bạn có thể gọi hàm Groq tương tự như tab 1
