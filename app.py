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

import streamlit as st

with tab2:
    st.subheader("Luyện Viết")
    
    # Câu mẫu
    cau_en = "I carry books in my backpack"
    words = cau_en.split()
    
    # Khởi tạo trạng thái cho từng từ (chưa mở)
    if 'revealed' not in st.session_state:
        st.session_state.revealed = [False] * len(words)

    st.write("Dịch câu: **Tôi mang sách trong ba lô.**")
    
    # Hiển thị các ô từ
    cols = st.columns(len(words))
    for i, word in enumerate(words):
        if st.session_state.revealed[i]:
            cols[i].button(word, key=f"btn_{i}", disabled=True)
        else:
            # Tạo hiệu ứng ẩn chữ (ví dụ: 'ca***')
            masked_word = word[0:2] + "*" * (len(word) - 2) if len(word) > 2 else "*" * len(word)
            if cols[i].button(masked_word, key=f"btn_{i}"):
                st.session_state.revealed[i] = True
                st.rerun()

    if st.button("Hiện tất cả"):
        st.session_state.revealed = [True] * len(words)
        st.rerun()
with tab3:
    st.subheader("Từ Vựng Chuyên Ngành")
    nganh = st.selectbox("Chọn chuyên ngành:", ["IT", "Y học", "Kinh tế"])
    if st.button("Tạo bài học"):
        st.info(f"Đang tạo nội dung cho ngành {nganh}...")
        # Ở đây bạn có thể gọi hàm Groq tương tự như tab 1
