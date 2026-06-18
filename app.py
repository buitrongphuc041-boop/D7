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
    
    # Dữ liệu bài tập
    cau_goc = {
        "vi": "Tôi rất mong được hợp tác với công ty của bạn.",
        "en": "I look forward to cooperating with your company.",
        "goi_y": ["look forward to", "cooperating", "company"]
    }
    
    st.write(f"Dịch câu: **{cau_goc['vi']}**")
    
    # Hiển thị gợi ý từ vựng
    st.markdown("💡 **Gợi ý từ vựng:**")
    cols = st.columns(len(cau_goc['goi_y']))
    for i, word in enumerate(cau_goc['goi_y']):
        cols[i].code(word)
        
    user_trans = st.text_input("Nhập bản dịch của bạn:")
    
    if st.button("Kiểm tra"):
        if user_trans.lower().strip() == cau_goc['en'].lower().strip():
            st.success("Chính xác! 🎉")
        else:
            st.error(f"Chưa chính xác. Đáp án đúng là: {cau_goc['en']}")

with tab3:
    st.subheader("Từ Vựng Chuyên Ngành")
    nganh = st.selectbox("Chọn chuyên ngành:", ["IT", "Y học", "Kinh tế"])
    if st.button("Tạo bài học"):
        st.info(f"Đang tạo nội dung cho ngành {nganh}...")
        # Ở đây bạn có thể gọi hàm Groq tương tự như tab 1
