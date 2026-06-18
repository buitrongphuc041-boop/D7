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

    danh_sach_cau = [
        {"vi": "Tôi mang sách trong ba lô.", "en": "I carry books in my backpack", "exp": "Cấu trúc: S + V + O. 'Carry' là động từ chính, 'in' là giới từ chỉ nơi chốn."},
        {"vi": "Trời đang mưa rất to.", "en": "It is raining very hard", "exp": "Cấu trúc: Thì Hiện tại tiếp diễn (S + am/is/are + V-ing) dùng để diễn tả sự việc đang xảy ra."},
        {"vi": "Tôi thích học lập trình.", "en": "I like to learn programming", "exp": "Cấu trúc: 'Like + to Verb/V-ing'. 'Learn' là động từ nguyên mẫu có 'to' sau 'like'."}
    ]

    if 'current_idx' not in st.session_state:
        st.session_state.current_idx = 0
        st.session_state.revealed = [False] * len(danh_sach_cau[0]["en"].split())
        st.session_state.show_explanation = False # Trạng thái ẩn giải thích

    cau_hien_tai = danh_sach_cau[st.session_state.current_idx]
    words = cau_hien_tai["en"].split()

    st.write(f"Dịch câu: **{cau_hien_tai['vi']}**")

    # Hiển thị các từ gợi ý
    cols = st.columns(len(words))
    for i, word in enumerate(words):
        if st.session_state.revealed[i]:
            cols[i].button(word, key=f"btn_{i}", disabled=True)
        else:
            masked = word[0] + "*" * (len(word) - 1) if len(word) > 1 else "*"
            if cols[i].button(masked, key=f"btn_{i}"):
                st.session_state.revealed[i] = True
                st.rerun()

    user_input = st.text_input("Nhập câu hoàn chỉnh:", key="user_input")
    
    # Nút Kiểm tra
    if st.button("Kiểm tra"):
        if user_input.strip().lower() == cau_hien_tai["en"].lower():
            st.success("Chính xác!")
            st.session_state.show_explanation = True # Kích hoạt hiện giải thích
        else:
            st.error("Chưa đúng, thử lại nhé!")

    # Hiển thị giải thích nếu trả lời đúng
    if st.session_state.show_explanation:
        with st.expander("🔍 Xem giải thích chi tiết", expanded=True):
            st.write(f"**Cấu trúc câu:** {cau_hien_tai['exp']}")
            if st.button("Tiếp tục câu tiếp theo"):
                st.session_state.show_explanation = False
                st.session_state.current_idx = (st.session_state.current_idx + 1) % len(danh_sach_cau)
                st.session_state.revealed = [False] * len(danh_sach_cau[st.session_state.current_idx]["en"].split())
                st.rerun()
with tab3:
    st.subheader("Từ Vựng Chuyên Ngành")
    nganh = st.selectbox("Chọn chuyên ngành:", ["IT", "Y học", "Kinh tế"])
    if st.button("Tạo bài học"):
        st.info(f"Đang tạo nội dung cho ngành {nganh}...")
        # Ở đây bạn có thể gọi hàm Groq tương tự như tab 1
