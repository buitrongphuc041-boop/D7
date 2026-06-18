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
import random
import json
import re
from groq import Groq

# Cấu hình API Key an toàn
def get_groq_client():
    try:
        # Ưu tiên lấy từ secrets, nếu không có thì lấy từ biến môi trường
        api_key = st.secrets.get("GROQ_API_KEY")
        return Groq(api_key=api_key)
    except:
        st.error("Chưa cấu hình GROQ_API_KEY trong Secrets!")
        return None

with tab2:
    st.subheader("✍️ Luyện Viết (50 Câu từ AI)")
    client = get_groq_client()

    if client and 'danh_sach_50_cau' not in st.session_state:
        with st.spinner("AI đang tạo 50 câu, vui lòng đợi..."):
            try:
                prompt = "Tạo 50 câu tiếng Anh ngắn về đời sống. Trả về đúng định dạng JSON: [{\"vi\": \"nghĩa\", \"en\": \"câu\"}, ...]. Không giải thích."
                response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                
                content = response.choices[0].message.content
                # Regex để lọc đúng khối [...]
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    st.session_state.danh_sach_50_cau = json.loads(match.group())
                    random.shuffle(st.session_state.danh_sach_50_cau)
                    st.session_state.current_idx = 0
                    st.session_state.revealed = [False] * 20
                else:
                    st.error("AI không trả về đúng định dạng.")
            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")

    # Hiển thị bài tập nếu đã có dữ liệu
    if 'danh_sach_50_cau' in st.session_state:
        cau = st.session_state.danh_sach_50_cau[st.session_state.current_idx]
        st.write(f"Dịch: **{cau['vi']}**")
        
        user_input = st.text_input("Nhập câu:")
        if st.button("Kiểm tra"):
            if user_input.strip().lower() == cau['en'].lower():
                st.success("Chính xác!")
                # Giải thích
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": f"Giải thích ngắn gọn: {cau['en']}"}])
                st.info(res.choices[0].message.content)
                if st.button("Câu tiếp theo"):
                    st.session_state.current_idx += 1
                    st.rerun()
            else:
                st.error("Sai rồi, thử lại!")
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
