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
    st.write("Dịch câu: **Tôi mang sách trong ba lô.**")
    
    # Câu mẫu
    cau_en = "I carry books in my backpack"
    words = cau_en.split()
    
    # Khởi tạo trạng thái cho từng từ (chưa mở)
    if 'revealed' not in st.session_state:
        st.session_state.revealed = [False] * len(words)

    # Tạo một khung chứa các từ (giao diện đẹp hơn)
    container = st.container(border=True)
    with container:
        # Sử dụng số cột bằng với số từ
        cols = st.columns(len(words))
        
        for i, word in enumerate(words):
            # Logic hiển thị chữ: Nếu đã mở thì hiện chữ, chưa mở thì hiện 'ca***'
            if st.session_state.revealed[i]:
                cols[i].button(word, key=f"btn_{i}", disabled=True)
            else:
                # Tạo hiệu ứng ẩn chữ (giữ chữ cái đầu, thay còn lại bằng *)
                masked_word = word[0:1] + "*" * (len(word) - 1) if len(word) > 1 else "*"
                if cols[i].button(masked_word, key=f"btn_{i}"):
                    st.session_state.revealed[i] = True
                    st.rerun()

    # Nút "Hiện tất cả"
    if st.button("Hiện tất cả"):
        st.session_state.revealed = [True] * len(words)
        st.rerun()
        
    # Thêm ô nhập câu hoàn chỉnh
    st.write("---")
    user_input = st.text_input("Nhập câu hoàn chỉnh vào đây:")
    if st.button("Kiểm tra"):
        if user_input.strip().lower() == cau_en.lower():
            st.success("Chính xác! Bạn rất giỏi! 🎉")
        else:
            st.error(f"Chưa đúng. Đáp án đúng là: {cau_en}")
with tab3:
    st.subheader("Từ Vựng Chuyên Ngành")
    nganh = st.selectbox("Chọn chuyên ngành:", ["IT", "Y học", "Kinh tế"])
    if st.button("Tạo bài học"):
        st.info(f"Đang tạo nội dung cho ngành {nganh}...")
        # Ở đây bạn có thể gọi hàm Groq tương tự như tab 1
