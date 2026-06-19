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

with tab2:
    st.subheader("Luyện Viết")

    # 1. Danh sách 30 câu hỏi
    danh_sach_cau = [
        {"vi": "Tôi mang sách trong ba lô.", "en": "I carry books in my backpack"},
        {"vi": "Trời đang mưa rất to.", "en": "It is raining very hard"},
        {"vi": "Tôi thích học lập trình.", "en": "I like to learn programming"},
        {"vi": "Hôm nay thời tiết rất đẹp.", "en": "The weather is very nice today"},
        {"vi": "Cô ấy đang nấu bữa tối.", "en": "She is cooking dinner"},
        {"vi": "Họ đang chơi bóng đá.", "en": "They are playing soccer"},
        {"vi": "Tôi cần uống nước.", "en": "I need to drink water"},
        {"vi": "Anh ấy đang đọc một cuốn sách.", "en": "He is reading a book"},
        {"vi": "Chúng tôi đi làm bằng xe buýt.", "en": "We go to work by bus"},
        {"vi": "Con mèo đang ngủ trên ghế.", "en": "The cat is sleeping on the chair"},
        {"vi": "Bạn có khỏe không?", "en": "How are you doing"},
        {"vi": "Tôi yêu gia đình tôi.", "en": "I love my family"},
        {"vi": "Học tiếng Anh rất thú vị.", "en": "Learning English is very interesting"},
        {"vi": "Mặt trời mọc ở hướng Đông.", "en": "The sun rises in the East"},
        {"vi": "Tôi muốn đi du lịch thế giới.", "en": "I want to travel the world"},
        {"vi": "Hãy giúp tôi một tay.", "en": "Please give me a hand"},
        {"vi": "Đừng quên làm bài tập về nhà.", "en": "Don't forget to do your homework"},
        {"vi": "Tôi đang đợi bạn ở trạm xe.", "en": "I am waiting for you at the station"},
        {"vi": "Ngày mai là sinh nhật tôi.", "en": "Tomorrow is my birthday"},
        {"vi": "Cà phê này rất ngon.", "en": "This coffee is very delicious"},
        {"vi": "Bạn nói tiếng Anh rất tốt.", "en": "You speak English very well"},
        {"vi": "Tôi đi ngủ lúc 10 giờ.", "en": "I go to bed at 10 pm"},
        {"vi": "Cô ấy là một giáo viên giỏi.", "en": "She is a good teacher"},
        {"vi": "Chúng tôi đang thảo luận về dự án.", "en": "We are discussing the project"},
        {"vi": "Hãy mở cửa sổ ra.", "en": "Please open the window"},
        {"vi": "Tôi thích nghe nhạc cổ điển.", "en": "I like listening to classical music"},
        {"vi": "Con chó đang sủa ở ngoài.", "en": "The dog is barking outside"},
        {"vi": "Thời gian là vàng bạc.", "en": "Time is money"},
        {"vi": "Tôi không biết câu trả lời.", "en": "I don't know the answer"},
        {"vi": "Chúc bạn một ngày tốt lành.", "en": "Have a nice day"}
    ]

    # 2. Khởi tạo và Xáo trộn danh sách khi chạy lần đầu
    if 'shuffled_list' not in st.session_state:
        st.session_state.shuffled_list = danh_sach_cau.copy()
        random.shuffle(st.session_state.shuffled_list)
        st.session_state.current_idx = 0
        
    # Khởi tạo trạng thái cho câu hiện tại
    if 'revealed' not in st.session_state:
        st.session_state.revealed = [False] * len(st.session_state.shuffled_list[0]["en"].split())

    # Lấy câu hiện tại từ danh sách đã xáo trộn
    cau_hien_tai = st.session_state.shuffled_list[st.session_state.current_idx]
    words = cau_hien_tai["en"].split()

    st.write(f"Dịch câu: **{cau_hien_tai['vi']}**")

    # 3. Khu vực hiển thị gợi ý
    container = st.container(border=True)
    with container:
        cols = st.columns(len(words))
        for i, word in enumerate(words):
            if st.session_state.revealed[i]:
                cols[i].button(word, key=f"btn_{i}", disabled=True)
            else:
                masked = word[0] + "*" * (len(word) - 1) if len(word) > 1 else "*"
                if cols[i].button(masked, key=f"btn_{i}"):
                    st.session_state.revealed[i] = True
                    st.rerun()

    # 4. Kiểm tra và chuyển câu
    user_input = st.text_input("Nhập câu hoàn chỉnh:", key="user_input")
    if st.button("Kiểm tra"):
        if user_input.strip().lower() == cau_hien_tai["en"].lower():
            st.success("Chính xác! Đang tải câu mới...")
            
            # Chuyển sang câu kế tiếp
            st.session_state.current_idx += 1
            
            # Nếu hết danh sách thì xáo trộn lại từ đầu
            if st.session_state.current_idx >= len(st.session_state.shuffled_list):
                random.shuffle(st.session_state.shuffled_list)
                st.session_state.current_idx = 0
                
            st.session_state.revealed = [False] * len(st.session_state.shuffled_list[st.session_state.current_idx]["en"].split())
            st.rerun() 
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
            Tạo 5 từ vựng tiếng Anh chuyên ngành {nganh} kèm các thông tin chi tiết. 
            QUAN TRỌNG: Không được trùng với các từ đã có trong danh sách này: {danh_sach_hien_tai}.
            
            Yêu cầu trả về ĐÚNG định dạng JSON array với các key sau (bắt buộc dùng dấu nháy đôi " cho cả key và value, không kèm text giải thích bên ngoài):
            [
              {{
                "tu": "Từ vựng tiếng Anh",
                "phien_am": "Phiên âm chuẩn IPA (ví dụ: /kəmˈpjuː.tər/)",
                "nghia": "Nghĩa tiếng Việt",
                "cach_dung": "Giải thích ngắn gọn bằng tiếng Việt về bối cảnh hoặc khi nào nên dùng từ này",
                "vi_du": "Một câu ví dụ bằng tiếng Anh có chứa từ này",
                "dich_vi_du": "Bản dịch tiếng Việt của câu ví dụ đó"
              }}
            ]
            """
            
            try:
                with st.spinner("Đang tìm từ mới và biên soạn nội dung..."):
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant", 
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    import json, re
                    content = response.choices[0].message.content
                    match = re.search(r'\[.*\]', content, re.DOTALL)
                    
                    if match:
                        json_str = match.group()
                        them_tu = json.loads(json_str)
                        st.session_state.vocab_list.extend(them_tu) 
                        st.rerun()
            except Exception as e:
                st.error("AI đang bận hoặc có lỗi xử lý dữ liệu, bạn thử lại nhé!")

        # 2. Nút xóa toàn bộ (Reset)
        if st.button("Xóa danh sách (Làm mới)"):
            st.session_state.vocab_list = []
            st.rerun()

        # 3. Hiển thị danh sách từ vựng tích lũy
        if st.session_state.vocab_list:
            st.write(f"### Danh sách hiện có ({len(st.session_state.vocab_list)} từ):")
            
            for idx, item in enumerate(st.session_state.vocab_list):
                # Hiển thị Tiêu đề gọn gàng: Từ vựng [Phiên âm] — Nghĩa
                tieu_de = f"🔹 {idx+1}. {item.get('tu')} *{item.get('phien_am')}* — **{item.get('nghia')}**"
                
                # Bọc thông tin chi tiết vào expander, nhấn vào sẽ xổ xuống thông tin chi tiết
                with st.expander(tieu_de):
                    st.markdown(f"💡 **Cách dùng:** {item.get('cach_dung')}")
                    st.markdown(f"📝 **Ví dụ:** *{item.get('vi_du')}*")
                    st.markdown(f"🔻 **Dịch nghĩa:** {item.get('dich_vi_du')}")
