import streamlit as st
import random
from groq import Groq
import time
# Cấu hình giao diện Streamlit
st.set_page_config(page_title="AI ENGLISH TUTOR", layout="wide")

st.title("🎓 AI ENGLISH TUTOR")

# Nhập API Key
api_key = st.sidebar.text_input("Groq API Key", type="password")

# Tabs cho các chức năng
tab1, tab2, tab3 = st.tabs(["💬 Chat", "✍️ Luyện Viết", "📚 Từ Vựng"])

with tab1:
        st.subheader("💬 Trợ lý Giao Tiếp")

        # Khởi tạo cấu trúc dữ liệu quản lý nhiều phiên trò chuyện (Multi-session) nếu chưa có
        if 'sessions' not in st.session_state:
            st.session_state.sessions = {}
        if 'current_session_id' not in st.session_state:
            st.session_state.current_session_id = None

        # Nếu hệ thống hoàn toàn trống (lần đầu chạy), tự động tạo cuộc trò chuyện số 1
        if not st.session_state.sessions:
            first_id = str(time.time())
            st.session_state.sessions[first_id] = {
                "title": "Cuộc trò chuyện mới",
                "messages": []
            }
            st.session_state.current_session_id = first_id

        # Chia giao diện Tab 1 thành 2 cột: Cột trái (Lịch sử) & Cột phải (Khung Chat)
        col_hist, col_chat = st.columns([1, 3.2])

        # --- 📁 CỘT TRÁI: THANH QUẢN LÝ LỊCH SỬ CÁC CUỘC TRÒ CHUYỆN ---
        with col_hist:
            st.markdown("### 🗂️ Quản lý")
            
            # Nút bấm tạo cuộc hội thoại mới hoàn toàn, đẩy cuộc hội thoại cũ vào lịch sử lưu trữ
            if st.button("➕ Cuộc trò chuyện mới", use_container_width=True, type="primary"):
                new_id = str(time.time())
                st.session_state.sessions[new_id] = {
                    "title": "Cuộc trò chuyện mới",
                    "messages": []
                }
                st.session_state.current_session_id = new_id
                st.rerun()
            
            st.write("---")
            st.markdown("📜 **Lịch sử trò chuyện:**")
            
            # Vòng lặp hiển thị danh sách các phòng chat cũ để click chuyển đổi qua lại
            for sess_id, sess_data in list(st.session_state.sessions.items()):
                # Đánh dấu highlight cuộc trò chuyện bạn đang chọn mở
                if sess_id == st.session_state.current_session_id:
                    button_label = f"📍 {sess_data['title']}"
                else:
                    button_label = f"📄 {sess_data['title']}"
                    
                if st.button(button_label, key=f"sidebar_sess_{sess_id}", use_container_width=True):
                    st.session_state.current_session_id = sess_id
                    st.rerun()

        # --- 💬 CỘT PHẢI: KHUNG CHAT CỦA PHÒNG ĐANG CHỌN ---
        with col_chat:
            active_id = st.session_state.current_session_id
            # Phòng hờ lỗi ID không tồn tại, tự động lấy ID đầu tiên trong danh sách
            if active_id not in st.session_state.sessions:
                active_id = list(st.session_state.sessions.keys())[0]
                st.session_state.current_session_id = active_id
                
            active_session = st.session_state.sessions[active_id]
            
            # Hiển thị tiêu đề của phòng chat hiện tại
            st.markdown(f"### 💬 {active_session['title']}")
            
            # 1. Tạo khung cuộn cố định (height=400) để tin nhắn không đẩy giao diện xuống quá dài
            chat_container = st.container(height=400)
            with chat_container:
                if not active_session["messages"]:
                    st.info("👋 Bạn chưa nói gì trong phòng này. Hãy nhập câu hỏi đầu tiên bên dưới nhé!")
                else:
                    for message in active_session["messages"]:
                        with st.chat_message(message["role"]):
                            st.write(message["content"])

            # 2. Ô nhập câu hỏi mới cho phòng chat đang chọn
            # Key động kết hợp ID phòng và số lượng tin nhắn giúp xóa chữ trong ô ngay khi gửi thành công
            input_key = f"chat_input_{active_id}_{len(active_session['messages'])}"
            prompt = st.text_input("Nhập câu hỏi của bạn:", key=input_key)
            
            if st.button("Gửi câu hỏi", key=f"btn_send_{active_id}", use_container_width=True):
                if prompt.strip():
                    if api_key:
                        try:
                            client = Groq(api_key=api_key)
                            
                            # TỰ ĐỘNG ĐỔI TÊN TIÊU ĐỀ: Nếu đây là câu hỏi đầu tiên, lấy 20 ký tự đầu làm tên phòng chat
                            if not active_session["messages"]:
                                text_clean = prompt.strip()
                                truncated_title = text_clean[:22] + "..." if len(text_clean) > 22 else text_clean
                                active_session["title"] = truncated_title
                            
                            # Lấy đúng lịch sử hội thoại của riêng phòng này gửi lên cho AI hiểu bối cảnh
                            messages_to_send = active_session["messages"].copy()
                            messages_to_send.append({"role": "user", "content": prompt})
                            
                            with st.spinner("Trợ lý đang phản hồi..."):
                                response = client.chat.completions.create(
                                    model="llama-3.1-8b-instant",
                                    messages=messages_to_send
                                )
                                reply = response.choices[0].message.content
                            
                            # Lưu cặp câu hỏi - câu trả lời vào đúng phòng chat này
                            active_session["messages"].append({"role": "user", "content": prompt})
                            active_session["messages"].append({"role": "assistant", "content": reply})
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Lỗi kết nối AI: {str(e)}")
                    else:
                        st.warning("Vui lòng nhập API Key ở menu bên trái.")
                else:
                    st.warning("Vui lòng điền nội dung câu hỏi trước khi bấm Gửi.")

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
            
        if 'correct_answered' not in st.session_state:
            st.session_state.correct_answered = False
        if 'ai_explanation' not in st.session_state:
            st.session_state.ai_explanation = ""
        if 'correct_time' not in st.session_state:
            st.session_state.correct_time = None
        if 'stop_countdown' not in st.session_state:
            st.session_state.stop_countdown = False

        # Lấy câu hiện tại từ danh sách đã xáo trộn
        cau_hien_tai = st.session_state.shuffled_list[st.session_state.current_idx]
        words = cau_hien_tai["en"].split()

        if 'revealed' not in st.session_state or len(st.session_state.revealed) != len(words):
            st.session_state.revealed = [False] * len(words)

        st.write(f"Dịch câu: **{cau_hien_tai['vi']}**")

        # 3. Khu vực hiển thị gợi ý
        container = st.container(border=True)
        with container:
            cols = st.columns(len(words))
            for i, word in enumerate(words):
                if i < len(st.session_state.revealed) and st.session_state.revealed[i]:
                    cols[i].button(word, key=f"btn_{i}", disabled=True)
                else:
                    masked = word[0] + "*" * (len(word) - 1) if len(word) > 1 else "*"
                    if cols[i].button(masked, key=f"btn_{i}"):
                        st.session_state.revealed[i] = True
                        st.rerun()

        # 4. Kiểm tra câu trả lời (Áp dụng key động để tự động reset ô text khi sang câu mới)
        input_key = f"user_input_{st.session_state.current_idx}"
        user_input = st.text_input("Nhập câu hoàn chỉnh:", key=input_key)
        
        if st.button("Kiểm tra"):
            if user_input.strip().lower() == cau_hien_tai["en"].lower():
                st.session_state.correct_answered = True
                st.session_state.correct_time = time.time()  
                st.session_state.stop_countdown = False       
                
                try:
                    with st.spinner("Chính xác! Đang kết nối AI phân tích ngữ pháp câu này..."):
                        client = Groq(api_key=api_key)
                        prompt = f"""
                        Phân tích chi tiết cấu trúc ngữ pháp của câu tiếng Anh: "{cau_hien_tai['en']}" (Nghĩa là: "{cau_hien_tai['vi']}").
                        Hãy trình bày bằng tiếng Việt mạch lạc, định dạng markdown đẹp mắt bao gồm:
                        - Cấu trúc các thành phần chính (Chủ ngữ S, Vị ngữ V, Tân ngữ O nếu có).
                        - Thì (Tense) của câu và các điểm cấu trúc ngữ pháp quan trọng cần nhớ.
                        - Giải thích ngắn gọn bối cảnh hay lưu ý khi sử dụng câu/cụm từ này.
                        """
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3
                        )
                        st.session_state.ai_explanation = response.choices[0].message.content
                except Exception as e:
                    st.session_state.ai_explanation = "⚠️ Không thể tải phân tích cấu trúc từ AI lúc này, bạn hãy học tiếp câu sau nhé!"
                st.rerun()
            else:
                st.error("Chưa đúng, thử lại nhé!")
                st.session_state.correct_answered = False

        # 5. Khu vực hiển thị Giải thích & Đếm ngược tự động chuyển câu
        if st.session_state.correct_answered:
            st.success("🎉 Bạn đã viết chính xác câu này!")
            
            st.markdown("### 🧠 Phân Tích Cấu Trúc Ngữ Pháp")
            st.info(st.session_state.ai_explanation)
            
            if not st.session_state.stop_countdown:
                elapsed = time.time() - st.session_state.correct_time
                remaining = int(10 - elapsed)
                
                if remaining > 0:
                    st.write(f"⏱️ Hệ thống sẽ tự động chuyển câu mới sau **{remaining}** giây...")
                    if st.button("⏸️ Dừng đếm ngược (Để chép bài / Xem kỹ hơn)"):
                        st.session_state.stop_countdown = True
                        st.rerun()
                    time.sleep(1)
                    st.rerun()  
                else:
                    # Chuyển câu tự động khi hết 10 giây
                    st.session_state.correct_answered = False
                    st.session_state.current_idx += 1
                    
                    if st.session_state.current_idx >= len(st.session_state.shuffled_list):
                        random.shuffle(st.session_state.shuffled_list)
                        st.session_state.current_idx = 0
                    
                    st.session_state.revealed = [False] * len(st.session_state.shuffled_list[st.session_state.current_idx]["en"].split())
                    st.rerun()
            else:
                st.warning("⏸️ Đã dừng đếm ngược. Bạn có thể thong thả nghiên cứu cấu trúc câu.")
                if st.button("Chuyển sang câu tiếp theo ➡️"):
                    st.session_state.correct_answered = False
                    st.session_state.current_idx += 1
                    
                    if st.session_state.current_idx >= len(st.session_state.shuffled_list):
                        random.shuffle(st.session_state.shuffled_list)
                        st.session_state.current_idx = 0
                        
                    st.session_state.revealed = [False] * len(st.session_state.shuffled_list[st.session_state.current_idx]["en"].split())
                    st.rerun()
with tab3:
        st.subheader("📚 Từ Vựng Chuyên Ngành")
        
        ds_nganh = ["IT", "Y học", "Kinh tế", "Logistics", "Marketing", "Du lịch", "Luật", "Xây dựng"]
        nganh = st.selectbox("Chọn chuyên ngành:", ds_nganh)
        
        if 'vocab_list' not in st.session_state or not isinstance(st.session_state.vocab_list, list):
            st.session_state.vocab_list = []

        # 1. Nút tạo thêm từ (AI sẽ không lặp lại từ cũ)
        if st.button("Tạo thêm 5 từ vựng mới"):
            client = Groq(api_key=api_key)
            danh_sach_hien_tai = [item['tu'] for item in st.session_state.vocab_list]
            
            # Đổi cấu trúc prompt sang dạng JSON Object chứa key "vocab" để bật JSON Mode của Groq
            prompt = f"""
            Tạo 5 từ vựng tiếng Anh chuyên ngành {nganh} kèm thông tin chi tiết. 
            QUAN TRỌNG: Không trùng với các từ đã có: {danh_sach_hien_tai}.
            
            Bạn PHẢI trả về một JSON Object hợp lệ cấu trúc chính xác như sau:
            {{
              "vocab": [
                {{
                  "tu": "Từ vựng tiếng Anh",
                  "phien_am": "Phiên âm IPA (ví dụ: /kəmˈpjuː.tər/)",
                  "nghia": "Nghĩa tiếng Việt",
                  "cach_dung": "Giải thích ngắn gọn ngữ cảnh sử dụng",
                  "vi_du": "Câu ví dụ tiếng Anh",
                  "dich_vi_du": "Dịch câu ví dụ sang tiếng Việt"
                }}
              ]
            }}
            """
            
            try:
                with st.spinner("Đang tìm từ mới và biên soạn nội dung..."):
                    # Thêm cấu hình response_format để ép Groq trả về JSON chuẩn chỉnh
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant", 
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"},
                        temperature=0.7
                    )
                    import json
                    content = response.choices[0].message.content
                    
                    # Giải mã thẳng JSON không cần dùng Regex dò tìm như trước
                    data = json.loads(content)
                    them_tu = data.get("vocab", [])
                    
                    if them_tu:
                        st.session_state.vocab_list.extend(them_tu) 
                        st.rerun()
                    else:
                        st.warning("AI phản hồi trống, hãy thử bấm lại nhé!")
            except Exception as e:
                # Hiện chi tiết lỗi nếu có để dễ theo dõi khi code
                st.error(f"Lỗi hệ thống hoặc API quá tải: {str(e)}")

        # 2. Nút xóa toàn bộ (Reset)
        if st.button("Xóa danh sách (Làm mới)"):
            st.session_state.vocab_list = []
            st.rerun()

        # 3. Hiển thị danh sách từ vựng tích lũy
        if st.session_state.vocab_list:
            st.write(f"### Danh sách hiện có ({len(st.session_state.vocab_list)} từ):")
            
            for idx, item in enumerate(st.session_state.vocab_list):
                tieu_de = f"🔹 {idx+1}. {item.get('tu')} *{item.get('phien_am')}* — **{item.get('nghia')}**"
                
                with st.expander(tieu_de):
                    st.markdown(f"💡 **Cách dùng:** {item.get('cach_dung')}")
                    st.markdown(f"📝 **Ví dụ:** *{item.get('vi_du')}*")
                    st.markdown(f"🔻 **Dịch nghĩa:** {item.get('dich_vi_du')}")
