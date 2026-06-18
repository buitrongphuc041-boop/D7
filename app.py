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
    st.subheader("📚 Từ Vựng Chuyên Ngành")
    
    ds_nganh = ["IT", "Y học", "Kinh tế", "Logistics", "Marketing", "Du lịch", "Luật", "Xây dựng"]
    nganh = st.selectbox("Chọn chuyên ngành:", ds_nganh)
    
    if 'vocab_list' not in st.session_state or not isinstance(st.session_state.vocab_list, list):
        st.session_state.vocab_list = []

    # 1. Nút tạo thêm từ (AI sẽ không lặp lại từ cũ)
    if st.button("Tạo thêm 5 từ vựng mới"):
        client = Groq(api_key=api_key)
        # Truyền danh sách cũ vào prompt để AI né ra
        danh_sach_hien_tai = [item['tu'] for item in st.session_state.vocab_list]
        prompt = f"""
        Tạo 5 từ vựng chuyên ngành {nganh} kèm nghĩa tiếng Việt. 
        QUAN TRỌNG: Không được trùng với các từ đã có: {danh_sach_hien_tai}.
        Trả về đúng định dạng JSON: [{{'tu': 'word', 'nghia': 'meaning'}}, ...]
        """
        
        try:
            with st.spinner("Đang tìm từ mới..."):
                response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                import json, re
                content = response.choices[0].message.content
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    json_str = match.group().replace("'", '"')
                    them_tu = json.loads(json_str)
                    st.session_state.vocab_list.extend(them_tu) # Cộng dồn tiếp nối
                    st.rerun()
        except Exception as e:
            st.error("AI đang bận, thử lại nhé!")

    # 2. Nút xóa toàn bộ (Reset)
    if st.button("Xóa danh sách (Làm mới)"):
        st.session_state.vocab_list = []
        st.rerun()

    # 3. Hiển thị danh sách từ vựng tích lũy
    if st.session_state.vocab_list:
        st.write(f"### Danh sách hiện có ({len(st.session_state.vocab_list)} từ):")
        for idx, item in enumerate(st.session_state.vocab_list):
            st.write(f"{idx+1}. **{item.get('tu')}**: {item.get('nghia')}")
