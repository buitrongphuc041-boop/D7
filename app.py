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

        # 1. Khởi tạo cấu trúc quản lý nhiều cuộc trò chuyện nếu chưa có
        if 'all_chats' not in st.session_state:
            st.session_state.all_chats = {
                "chat_1": {"title": "Cuộc trò chuyện 1", "history": []}
            }
        if 'current_chat_id' not in st.session_state:
            st.session_state.current_chat_id = "chat_1"
        if 'chat_counter' not in st.session_state:
            st.session_state.chat_counter = 1

        # 2. Thanh điều khiển hàng ngang
        col_new, col_hist, col_refresh = st.columns([1.2, 2, 1])

        with col_new:
            if st.button("➕ Trò chuyện mới", use_container_width=True, type="primary"):
                st.session_state.chat_counter += 1
                new_id = f"chat_{st.session_state.chat_counter}"
                st.session_state.all_chats[new_id] = {
                    "title": f"Cuộc trò chuyện {st.session_state.chat_counter}",
                    "history": []
                }
                st.session_state.current_chat_id = new_id
                st.rerun()

        with col_hist:
            chat_options = list(st.session_state.all_chats.keys())
            current_index = chat_options.index(st.session_state.current_chat_id)
            
            selected_chat_id = st.selectbox(
                "Lịch sử trò chuyện",
                options=chat_options,
                index=current_index,
                format_func=lambda x: st.session_state.all_chats[x]["title"],
                label_visibility="collapsed"
            )
            if selected_chat_id != st.session_state.current_chat_id:
                st.session_state.current_chat_id = selected_chat_id
                st.rerun()

        with col_refresh:
            if st.button("🔄 Làm mới", use_container_width=True):
                st.session_state.all_chats[st.session_state.current_chat_id]["history"] = []
                st.session_state.all_chats[st.session_state.current_chat_id]["title"] = f"Trò chuyện trống"
                st.rerun()

        st.write("---")

        active_id = st.session_state.current_chat_id
        active_chat = st.session_state.all_chats[active_id]

        # 3. Hiển thị nội dung tin nhắn cũ
        chat_placeholder = st.container()
        with chat_placeholder:
            if not active_chat["history"]:
                st.info("👋 Hãy nhập câu hỏi đầu tiên bên dưới để bắt đầu cuộc trò chuyện này nhé!")
            else:
                for message in active_chat["history"]:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

        # 4. Ô nhập câu hỏi mới
        chat_key = f"chat_prompt_{active_id}_{len(active_chat['history'])}"
        prompt = st.text_input("Nhập câu hỏi của bạn:", key=chat_key)
        
        if st.button("Gửi câu hỏi", key=f"btn_send_{active_id}"):
            if prompt.strip():
                if api_key:
                    try:
                        client = Groq(api_key=api_key)
                        
                        if not active_chat["history"]:
                            text_clean = prompt.strip()
                            truncated_title = text_clean[:25] + "..." if len(text_clean) > 25 else text_clean
                            active_chat["title"] = truncated_title
                        
                        # 🔥 ĐÂY LÀ KHU VỰC "BƠM NÃO" CHO AI: Định hình vai trò bằng System Message
                        system_message = {
                            "role": "system",
                            "content": (
                                "Bạn là một Trợ lý kiêm Gia sư Tiếng Anh (AI English Tutor) cực kỳ thông minh. "
                                "Nhiệm vụ của bạn là giúp người dùng học tập và giao tiếp tiếng Anh hiệu quả.\n"
                                "⚠️ QUAN TRỌNG CỐT LÕI: Hãy đọc thật kỹ yêu cầu hành động trong câu hỏi của người dùng. "
                                "Nếu họ yêu cầu 'viết bài văn bằng tiếng Anh', 'đặt câu bằng tiếng Anh', 'viết đoạn hội thoại bằng tiếng Anh'... "
                                "thì bạn PHẢI VIẾT PHẦN NỘI DUNG ĐÓ HOÀN TOÀN BẰNG TIẾNG ANH.\n"
                                "Sau khi hoàn thành nội dung tiếng Anh theo yêu cầu, bạn có thể bổ sung phần dịch nghĩa, giải thích cấu trúc "
                                "ngữ pháp hoặc từ vựng quan trọng bằng tiếng Việt ở phía dưới để người dùng học tập. Tuyệt đối không được "
                                "dịch toàn bộ bài văn/đoạn văn tiếng Anh thành tiếng Việt ngay từ đầu."
                            )
                        }
                        
                        # Gộp System Message vào đầu mảng để AI luôn ghi nhớ luật
                        messages_to_send = [system_message] + active_chat["history"].copy()
                        messages_to_send.append({"role": "user", "content": prompt})
                        
                        with st.spinner("Trợ lý đang suy nghĩ..."):
                            response = client.chat.completions.create(
                                model="llama-3.1-8b-instant",
                                messages=messages_to_send
                            )
                            reply = response.choices[0].message.content
                        
                        active_chat["history"].append({"role": "user", "content": prompt})
                        active_chat["history"].append({"role": "assistant", "content": reply})
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Lỗi kết nối AI: {str(e)}")
                else:
                    st.warning("Vui lòng nhập API Key ở menu bên trái.")
            else:
                st.warning("Vui lòng điền nội dung câu hỏi trước khi gửi.")
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
