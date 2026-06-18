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
    
    # Khởi tạo hoặc làm sạch bộ nhớ
    if 'vocab_list' not in st.session_state:
        st.session_state.vocab_list = []

    col1, col2 = st.columns(2)
    
    # Nút tạo 5 từ - Cải tiến: dùng response json chuẩn
    if col1.button("Tạo 5 từ vựng mới"):
        client = Groq(api_key=api_key)
        prompt = f"Tạo 5 từ vựng chuyên ngành {nganh} kèm nghĩa. Chỉ trả về định dạng JSON danh sách, ví dụ: [{'tu': 'A', 'nghia': 'B'}, {'tu': 'C', 'nghia': 'D'}]"
        
        try:
            response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            import json
            raw_text = response.choices[0].message.content
            # Lọc nội dung để chỉ lấy chuỗi JSON
            json_text = raw_text[raw_text.find("["):raw_text.rfind("]")+1]
            st.session_state.vocab_list = json.loads(json_text)
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi định dạng: Hãy thử lại hoặc thêm thủ công.")

    # Thêm từ thủ công
    with col2.expander("Thêm từ thủ công"):
        tu_input = st.text_input("Từ:")
        nghia_input = st.text_input("Nghĩa:")
        if st.button("Lưu từ"):
            st.session_state.vocab_list.append({"tu": tu_input, "nghia": nghia_input})
            st.rerun()

    # Hiển thị danh sách và tạo bài tập
    if st.session_state.vocab_list:
        st.write("### Danh sách từ vựng:")
        for idx, item in enumerate(st.session_state.vocab_list):
            st.write(f"{idx+1}. **{item['tu']}**: {item['nghia']}")
            
        loai_bai = st.radio("Chọn dạng bài tập:", ["Điền khuyết", "Nối từ"])
        
        if st.button("Tạo bài tập"):
            prompt_bt = f"Dựa trên các từ vựng: {st.session_state.vocab_list}. Tạo bài tập {loai_bai}. Với mỗi câu bài tập, hãy thêm một nút để dịch câu đó sang tiếng Việt."
            # Gọi AI tạo bài tập và lưu vào session_state.bai_tap
            st.session_state.bai_tap = "Nội dung bài tập từ AI..." 
            st.rerun()

    # Hiển thị bài tập và nút dịch
    if 'bai_tap' in st.session_state:
        st.write("---")
        # Giả lập hiển thị câu bài tập
        for i in range(3):
            st.write(f"Câu {i+1}: ... (nội dung bài tập)")
            if st.button(f"Dịch câu {i+1}", key=f"dich_{i}"):
                st.info("Bản dịch tiếng Việt của câu này...")
