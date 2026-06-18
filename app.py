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

    # 1. Danh sách câu hỏi
    danh_sach_cau = [
        {"vi": "Tôi mang sách trong ba lô.", "en": "I carry books in my backpack"},
        {"vi": "Trời đang mưa rất to.", "en": "It is raining very hard"},
        {"vi": "Tôi thích học lập trình.", "en": "I like to learn programming"}
    ]

    # 2. Khởi tạo trạng thái cho câu hiện tại
    if 'current_idx' not in st.session_state:
        st.session_state.current_idx = 0
        st.session_state.revealed = [False] * len(danh_sach_cau[0]["en"].split())

    # Lấy câu hiện tại
    cau_hien_tai = danh_sach_cau[st.session_state.current_idx]
    words = cau_hien_tai["en"].split()

    st.write(f"Dịch câu: **{cau_hien_tai['vi']}**")

    # 3. Khu vực hiển thị gợi ý (Bấm vào mới hiện)
    container = st.container(border=True)
    with container:
        cols = st.columns(len(words))
        for i, word in enumerate(words):
            if st.session_state.revealed[i]:
                cols[i].button(word, key=f"btn_{i}", disabled=True)
            else:
                # Ẩn bằng dấu *
                masked = word[0] + "*" * (len(word) - 1) if len(word) > 1 else "*"
                if cols[i].button(masked, key=f"btn_{i}"):
                    st.session_state.revealed[i] = True
                    st.rerun()

    # 4. Kiểm tra và chuyển câu
    user_input = st.text_input("Nhập câu hoàn chỉnh:", key="user_input")
    if st.button("Kiểm tra"):
        if user_input.strip().lower() == cau_hien_tai["en"].lower():
            st.success("Chính xác! Đang tải câu mới...")
            
            # Reset trạng thái cho câu tiếp theo
            st.session_state.current_idx = (st.session_state.current_idx + 1) % len(danh_sach_cau)
            st.session_state.revealed = [False] * len(danh_sach_cau[st.session_state.current_idx]["en"].split())
            st.rerun() # Tải lại để hiển thị câu mới
        else:
            st.error("Chưa đúng, thử lại nhé!")
with tab3:
    st.subheader("Từ Vựng Chuyên Ngành")
    
    ds_nganh = ["IT", "Y học", "Kinh tế", "Logistics", "Marketing", "Du lịch", "Luật", "Xây dựng"]
    nganh = st.selectbox("Chọn chuyên ngành:", ds_nganh)
    
    # Khởi tạo bộ nhớ cho tab3
    if 'vocab_list' not in st.session_state:
        st.session_state.vocab_list = []
    
    # Bước 1: Tạo bộ từ vựng
    if st.button("1. Tạo danh sách từ vựng"):
        client = Groq(api_key=api_key)
        prompt = f"Liệt kê 5 từ vựng tiếng Anh chuyên ngành {nganh} quan trọng kèm nghĩa tiếng Việt. Trả về định dạng: Từ - Nghĩa."
        response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
        st.session_state.vocab_list = response.choices[0].message.content
        st.rerun()

    if st.session_state.vocab_list:
        st.write("### Danh sách từ vựng:")
        st.info(st.session_state.vocab_list)
        
        # Bước 2: Chọn dạng bài và tạo bài tập dựa trên danh sách trên
        loai_bai = st.radio("Chọn dạng bài tập:", ["Điền khuyết", "Nối từ"])
        if st.button("2. Tạo bài tập từ danh sách trên"):
            prompt_bai_tap = f"Dựa trên danh sách từ vựng này: {st.session_state.vocab_list}. Hãy tạo một bài tập {loai_bai}. Có kèm gợi ý cho từng từ."
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt_bai_tap}])
            st.session_state.bai_tap = response.choices[0].message.content
            st.rerun()

    # Bước 3: Hiển thị bài tập và làm bài
    if 'bai_tap' in st.session_state:
        st.write("---")
        st.write("### Làm bài tập:")
        st.markdown(st.session_state.bai_tap)
        tra_loi = st.text_area("Nhập đáp án của bạn:")
        if st.button("Kiểm tra đáp án"):
            st.write("AI đang chấm điểm...")
            # Bạn có thể gọi thêm prompt kiểm tra đáp án ở đây
