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
    
    ds_nganh = ["IT", "Y học", "Kinh tế", "Logistics", "Marketing", "Du lịch", "Luật", "Xây dựng", "Giáo dục", "Tài chính"]
    nganh = st.selectbox("Chọn chuyên ngành:", ds_nganh)
    
    # Khởi tạo hoặc làm sạch danh sách từ vựng
    if 'vocab_list' not in st.session_state or not isinstance(st.session_state.vocab_list, list):
        st.session_state.vocab_list = []

    # 1. Khu vực tạo từ hoặc thêm từ
    col1, col2 = st.columns(2)
    
    # Nút tạo 5 từ bằng AI
    if col1.button("Tạo 5 từ vựng mới"):
        # Lưu ý: Bạn cần cấu hình Groq client ở đây
        # Ví dụ giả định: st.session_state.vocab_list = [{"tu": "Ship", "nghia": "Tàu"}, ...]
        st.session_state.vocab_list = [{"tu": "Example", "nghia": "Ví dụ"}] # Thay bằng kết quả từ AI
        st.rerun()
        
    # Nút thêm từ thủ công
    with col2.expander("Thêm từ thủ công"):
        tu_input = st.text_input("Từ tiếng Anh:")
        nghia_input = st.text_input("Nghĩa tiếng Việt:")
        if st.button("Thêm vào danh sách"):
            if tu_input and nghia_input:
                st.session_state.vocab_list.append({"tu": tu_input, "nghia": nghia_input})
                st.rerun()
            else:
                st.warning("Vui lòng nhập đầy đủ từ và nghĩa!")

    # 2. Hiển thị danh sách từ vựng an toàn
    if st.session_state.vocab_list:
        st.write("### Danh sách từ vựng của bạn:")
        for idx, item in enumerate(st.session_state.vocab_list):
            # Kiểm tra định dạng dictionary để tránh TypeError
            if isinstance(item, dict):
                st.write(f"{idx+1}. **{item.get('tu', 'N/A')}**: {item.get('nghia', 'N/A')}")
            else:
                st.write(f"{idx+1}. {item}") # Trường hợp cũ
    else:
        st.info("Danh sách từ vựng đang trống. Hãy tạo mới hoặc thêm từ thủ công.")

    # 3. Tạo bài tập (Dựa trên vocab_list đã chuẩn)
    if st.session_state.vocab_list:
        loai_bai = st.radio("Chọn dạng bài tập:", ["Điền khuyết", "Nối từ"])
        if st.button("Tạo bài tập từ danh sách trên"):
            # Gọi AI tạo bài tập với prompt truyền vào danh sách từ vựng
            st.success("Đang tạo bài tập...")
            # Logic tạo bài tập của bạn ở đây...
