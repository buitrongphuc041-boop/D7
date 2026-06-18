import sys
import os
import traceback
import random
import json
import re
import datetime
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image, ImageTk
from gtts import gTTS
import docx
import PyPDF2

# =====================================================================
# BẪY BẮT LỖI KHỞI ĐỘNG HỆ THỐNG THƯ VIỆN
# =====================================================================
try:
    try:
        from groq import Groq
    except ImportError:
        import subprocess
        print("[HỆ THỐNG] Đang tiến hành nạp cài đặt thư viện Groq nền...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "groq", "Pillow", "gTTS", "python-docx", "PyPDF2"])
        from groq import Groq

except Exception as e:
    print("\n" + "="*60)
    print("❌ LỖI KHỞI ĐỘNG: Trình cài đặt thư viện hoặc môi trường Python bị lỗi!")
    print("="*60)
    traceback.print_exc()
    print("="*60)
    input("\n👉 Vui lòng chụp lại dòng chữ báo lỗi ở trên gửi cho tôi.\nẤn Enter để đóng...")
    sys.exit(1)

# =====================================================================
# CẤU HÌNH BỘ NHỚ FILE VÀ KHO CÂU DỰ PHÒNG
# =====================================================================
CONFIG_FILE = "api_config.txt"

def doc_api_key_da_luu():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                key = f.read().strip()
                if key and key.startswith("gsk_"):  
                    return key
        except:
            pass
    return "gsk_..."  

def luu_api_key_vao_file(key_text):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(key_text.strip())
    except Exception as e:
        print(f"Không thể lưu bộ nhớ Key: {e}")

KHO_CAU_DU_PHONG = [
    {"vi": "Vui lòng ký tài liệu bằng bút bi xanh.", "en": "Please sign the document with a blue ballpoint pen."},
    {"vi": "Tôi rất mong được hợp tác với công ty của bạn trong tương lai.", "en": "I am looking forward to cooperating with your company in the future."},
    {"vi": "Hãy gửi cho tôi báo cáo tiến độ công việc trước năm giờ chiều nay.", "en": "Please send me the work progress report before five PM today."},
    {"vi": "Học một ngôn ngữ mới mở ra nhiều cơ hội nghề nghiệp tuyệt vời.", "en": "Learning a new language opens up many great career opportunities."},
    {"vi": "Bạn có thể giải thích lại thuật ngữ chuyên ngành này một lần nữa được không?", "en": "Could you please explain this technical term once again?"}
]

# =====================================================================
# LỚP ĐỒ HỌA ỨNG DỤNG CHÍNH
# =====================================================================
class AppHocTiengAnhCungAI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ HỌC TIẾNG ANH CÙNG AI - STYLE LUYENTU.COM")
        self.root.geometry("1280x880") 
        self.root.configure(bg="#0b0c10") 

        self.images_ref = [] 
        self.cau_tra_loi_cuoi_cung = ""
        self.duong_dan_anh_cho = None
        self.noi_dung_tep_tin_tai_len = ""
        self.sidebar_visible = True 
        self.is_pinned = False 

        self.cau_vi_hien_tai = ""
        self.cau_en_hien_tai = ""
        self.cac_tu_en = []
        self.trang_thai_lat_mo_tu = [] 

        self.bo_nho_lich_su_chat = {
            "Phiên Tiếng Anh mặc định": "🤖 AI: Xin chào! Tôi là Trợ lý Tiếng Anh của bạn.\n👉 Hệ thống đã sẵn sàng. Hãy dán mã API Key của bạn vào ô phía trên và bắt đầu học tập thôi!\n\n"
        }
        self.phien_chat_hien_tai = "Phiên Tiếng Anh mặc định"

        self.setup_ui()
        self.refresh_khung_chat_tu_bo_nho()
        
        self.tai_cau_luyen_tap(KHO_CAU_DU_PHONG[0])

    def setup_ui(self):
        top_bar = tk.Frame(self.root, bg="#1f2833", height=65, bd=0)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        
        lbl_title = tk.Label(top_bar, text="🎓 AI ENGLISH TUTOR", fg="#45f3ff", bg="#1f2833", font=("Segoe UI", 14, "bold"))
        lbl_title.pack(side=tk.LEFT, padx=15, pady=15)

        self.btn_toggle_sidebar = tk.Button(top_bar, text="☲ Ẩn Lịch sử", font=("Segoe UI", 9, "bold"), bg="#151b24", fg="#66fcf1", bd=0, padx=10, pady=5, cursor="hand2", command=self.toggle_sidebar)
        self.btn_toggle_sidebar.pack(side=tk.LEFT, padx=10)

        lbl_api = tk.Label(top_bar, text="Groq API Key:", fg="#ffffff", bg="#1f2833", font=("Segoe UI", 9, "bold"))
        lbl_api.pack(side=tk.LEFT, padx=(10, 2))
        
        self.entry_api = tk.Entry(top_bar, bg="#0b0c10", fg="#45f3ff", font=("Consolas", 10), bd=1, relief="solid", width=35, insertbackground="#ffffff")
        self.entry_api.pack(side=tk.LEFT, padx=5, ipady=3)
        self.entry_api.insert(0, doc_api_key_da_luu()) 
        
        self.btn_pin = tk.Button(top_bar, text="📌 Ghim app", font=("Segoe UI", 9, "bold"), bg="#1f2833", fg="#ffffff", bd=1, relief="solid", padx=10, pady=4, cursor="hand2", command=self.toggle_pin_window)
        self.btn_pin.pack(side=tk.LEFT, padx=10)

        self.main_layout = tk.Frame(self.root, bg="#0b0c10")
        self.main_layout.pack(fill=tk.BOTH, expand=True)

        self.sidebar = tk.Frame(self.main_layout, bg="#151b24", width=220, bd=0, highlightthickness=1, highlightbackground="#2f3e46")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        btn_new_chat = tk.Button(self.sidebar, text="➕ Mở phiên mới", font=("Segoe UI", 10, "bold"), bg="#2f3e46", fg="#66fcf1", bd=0, pady=8, cursor="hand2", command=self.tao_phien_tro_chuyen_moi)
        btn_new_chat.pack(fill=tk.X, padx=10, pady=10)

        self.listbox_phien = tk.Listbox(self.sidebar, bg="#0b0c10", fg="#ffffff", selectbackground="#45f3ff", selectforeground="#0b0c10", font=("Segoe UI", 10), bd=0, highlightthickness=0)
        self.listbox_phien.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox_phien.bind("<<ListboxSelect>>", self.chuyen_doi_phien_chat)
        self.cap_nhat_danh_sach_listbox()

        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background="#0b0c10", borderwidth=0)
        style.configure('TNotebook.Tab', background="#1f2833", foreground="#ffffff", padding=[15, 5], font=("Segoe UI", 10, "bold"))
        style.map('TNotebook.Tab', background=[('selected', '#45f3ff')], foreground=[('selected', '#0b0c10')])

        self.notebook = ttk.Notebook(self.main_layout)
        self.notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=10)

        # TAB 1: CHAT
        self.tab_chat = tk.Frame(self.notebook, bg="#0b0c10")
        self.notebook.add(self.tab_chat, text="💬 Trợ lý Giao Tiếp")
        self.setup_tab_chat()

        # TAB 2: LUYỆN VIẾT CÂU
        self.tab_writing = tk.Frame(self.notebook, bg="#0b0c10")
        self.notebook.add(self.tab_writing, text="✍️ Luyện Viết (Writing)")
        self.setup_tab_writing()

        # TAB 3: TỪ VỰNG CHUYÊN NGÀNH
        self.tab_vocab = tk.Frame(self.notebook, bg="#151b24")
        self.notebook.add(self.tab_vocab, text="📚 Từ Vựng Chuyên Ngành")
        self.setup_tab_vocab()

    def setup_tab_chat(self):
        bottom_panel = tk.Frame(self.tab_chat, bg="#0b0c10")
        bottom_panel.pack(side=tk.BOTTOM, fill=tk.X)

        voice_panel = tk.Frame(bottom_panel, bg="#0b0c10")
        voice_panel.pack(fill=tk.X, pady=2)
        btn_speak = tk.Button(voice_panel, text="🔊 PHÁT LOA CÂU TRẢ LỜI", font=("Segoe UI", 9, "bold"), bg="#f5b041", fg="#0b0c10", bd=0, padx=15, pady=5, cursor="hand2", command=self.phat_giong_noi_gtts)
        btn_speak.pack(side=tk.LEFT, fill=tk.X, expand=True)

        control_panel = tk.Frame(bottom_panel, bg="#151b24", highlightthickness=1, highlightbackground="#45f3ff")
        control_panel.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        button_row = tk.Frame(control_panel, bg="#151b24")
        button_row.pack(fill=tk.X, padx=15, pady=(10, 5))

        self.btn_img = tk.Button(button_row, text="📷 Đính kèm hình ảnh", font=("Segoe UI", 9, "bold"), bg="#1f2833", fg="#66fcf1", bd=0, padx=15, pady=6, cursor="hand2", command=self.pick_image)
        self.btn_img.pack(side=tk.LEFT, padx=5)

        self.btn_file = tk.Button(button_row, text="📁 Thêm tệp tin", font=("Segoe UI", 9, "bold"), bg="#1f2833", fg="#45f3ff", bd=0, padx=15, pady=6, cursor="hand2", command=self.pick_document_file)
        self.btn_file.pack(side=tk.LEFT, padx=5)
        
        btn_clear_chat = tk.Button(button_row, text="❌ Xóa màn hình", font=("Segoe UI", 9, "bold"), bg="#ff4d4d", fg="#ffffff", bd=0, padx=15, pady=6, cursor="hand2", command=self.clear_toan_bo_cuoc_tro_chuyen)
        btn_clear_chat.pack(side=tk.RIGHT, padx=5)

        input_row = tk.Frame(control_panel, bg="#151b24")
        input_row.pack(fill=tk.X, padx=15, pady=(2, 10))

        self.entry = tk.Entry(input_row, bg="#0b0c10", fg="#ffffff", font=("Segoe UI", 11), bd=0, insertbackground="#ffffff")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=12)
        self.entry.bind("<Return>", lambda e: self.send_message())

        self.btn_send = tk.Button(input_row, text="🚀 GỬI ĐI", font=("Segoe UI", 10, "bold"), bg="#66fcf1", fg="#0b0c10", bd=0, padx=25, pady=10, cursor="hand2", command=self.send_message)
        self.btn_send.pack(side=tk.RIGHT, padx=5)

        self.status_img = tk.Label(bottom_panel, text="📎 Không có tệp đính kèm nào.", bg="#0b0c10", fg="#c5c6c7", font=("Segoe UI", 9, "italic"), anchor="w")
        self.status_img.pack(side=tk.BOTTOM, fill=tk.X, pady=2)

        self.txt_area = scrolledtext.ScrolledText(self.tab_chat, bg="#151b24", fg="#ffffff", font=("Segoe UI", 11), padx=15, pady=15, bd=0, highlightthickness=1, highlightbackground="#2f3e46")
        self.txt_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.txt_area.config(state=tk.DISABLED)

    def setup_tab_writing(self):
        self.card_frame = tk.Frame(self.tab_writing, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        self.card_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.lbl_task_type = tk.Label(self.card_frame, text="DỊCH SANG TIẾNG ANH:", font=("Segoe UI", 11, "bold"), fg="#7a7a7a", bg="#ffffff", anchor="w")
        self.lbl_task_type.pack(fill=tk.X, padx=25, pady=(25, 5))

        vi_row = tk.Frame(self.card_frame, bg="#ffffff")
        vi_row.pack(fill=tk.X, padx=25, pady=(0, 10))

        self.lbl_vi_sentence = tk.Label(vi_row, text="Đang tải câu hỏi...", font=("Segoe UI", 15, "bold"), fg="#2c3e50", bg="#ffffff", anchor="w", justify=tk.LEFT, wraplength=750)
        self.lbl_vi_sentence.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_next_random = tk.Button(vi_row, text="🔄 Đổi thử thách câu khác", font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#4f5d75", bd=1, relief="solid", padx=12, pady=5, cursor="hand2", command=self.yeu_cau_ai_sinh_cau_moi_ngau_nhien)
        self.btn_next_random.pack(side=tk.RIGHT, padx=5)

        self.lbl_hint_title = tk.Label(self.card_frame, text="Câu mẫu tiếng Anh (Bấm trực tiếp vào từng ô bất kỳ để xem gợi ý từ khó):", font=("Segoe UI", 9, "italic"), fg="#888888", bg="#ffffff", anchor="w")
        self.lbl_hint_title.pack(fill=tk.X, padx=25, pady=(5, 5))

        self.frame_masked_words = tk.Frame(self.card_frame, bg="#ffffff")
        self.frame_masked_words.pack(fill=tk.X, padx=25, pady=5)

        self.entry_translation = tk.Entry(self.card_frame, bg="#ffffff", fg="#2c3e50", font=("Segoe UI", 13), bd=1, relief="solid", insertbackground="#000000", highlightthickness=1, highlightcolor="#bda5ec")
        self.entry_translation.pack(fill=tk.X, padx=25, pady=10, ipady=15)
        
        self.entry_translation.insert(0, "Nhập bản dịch tiếng Anh...")
        self.entry_translation.bind("<FocusIn>", lambda e: self.clear_placeholder())
        self.entry_translation.bind("<FocusOut>", lambda e: self.set_placeholder())

        self.entry_translation.bind("<Return>", lambda e: self.kiem_tra_dap_an_thuong())
        self.entry_translation.bind("<Control-Return>", lambda e: self.cham_diem_cau_voi_ai())
        self.entry_translation.bind("<Control-space>", lambda e: self.hien_goi_y_tu_ke_tiep_shortcut())

        btn_row_frame = tk.Frame(self.card_frame, bg="#ffffff")
        btn_row_frame.pack(fill=tk.X, padx=25, pady=15)

        self.btn_submit_normal = tk.Button(btn_row_frame, text="Nộp (Enter)", font=("Segoe UI", 11, "bold"), bg="#bda5ec", fg="#ffffff", activebackground="#a88cd8", activeforeground="#ffffff", bd=0, cursor="hand2", width=22, pady=12, command=self.kiem_tra_dap_an_thuong)
        self.btn_submit_normal.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.btn_submit_ai = tk.Button(btn_row_frame, text="AI chấm (Ctrl + Enter)", font=("Segoe UI", 11, "bold"), bg="#7fc7eb", fg="#ffffff", activebackground="#65b2d6", activeforeground="#ffffff", bd=0, cursor="hand2", width=22, pady=12, command=self.cham_diem_cau_voi_ai)
        self.btn_submit_ai.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        shortcut_bar = tk.Frame(self.card_frame, bg="#f8f9fa", height=35)
        shortcut_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)

        lbl_shortcuts = tk.Label(shortcut_bar, text="Mẹo: Click chuột vào ô chữ bất kỳ để lật mở từ khó   |   Enter: Nộp bài   |   Ctrl + Enter: AI phân tích ngữ pháp", font=("Segoe UI", 9), fg="#6c757d", bg="#f8f9fa")
        lbl_shortcuts.pack(pady=5)

        self.frame_ai_feedback = tk.LabelFrame(self.card_frame, text="✨ Báo cáo phân tích câu từ AI Groq:", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#f5b041", bd=1, relief="solid")
        self.frame_ai_feedback.pack(fill=tk.BOTH, expand=True, padx=25, pady=(5, 15))

        self.txt_writing_feedback = scrolledtext.ScrolledText(self.frame_ai_feedback, bg="#fdfefe", fg="#2c3e50", font=("Segoe UI", 10), bd=0, height=5)
        self.txt_writing_feedback.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.txt_writing_feedback.insert(tk.END, "Kết quả chấm chi tiết hoặc các cách viết đồng nghĩa từ AI sẽ xuất hiện tại đây sau khi bạn nhấn 'AI chấm'...")
        self.txt_writing_feedback.config(state=tk.DISABLED)

    def setup_tab_vocab(self):
        top_frame = tk.Frame(self.tab_vocab, bg="#151b24")
        top_frame.pack(fill=tk.X, padx=15, pady=10)

        lbl_field = tk.Label(top_frame, text="Chọn hoặc gõ Chuyên ngành bạn muốn học từ vựng:", bg="#151b24", fg="#45f3ff", font=("Segoe UI", 11, "bold"))
        lbl_field.pack(anchor="w", pady=(0, 5))

        self.combo_field = ttk.Combobox(top_frame, font=("Segoe UI", 11), values=[
            "Công nghệ thông tin (Information Technology)",
            "Y học & Dược phẩm (Medicine & Pharmacy)",
            "Kinh tế, Quản trị kinh doanh & Tài chính (Business & Finance)",
            "Kỹ thuật Ô tô & Cơ khí (Automotive Engineering)",
            "Du lịch, Nhà hàng & Khách sạn (Hospitality & Tourism)",
            "Luật pháp & Pháp lý (Law & Legal)",
            "Logistics & Quản lý chuỗi cung ứng (Logistics & Supply Chain Management)"
        ])
        self.combo_field.pack(fill=tk.X, pady=5, ipady=4)
        self.combo_field.set("Logistics & Quản lý chuỗi cung ứng (Logistics & Supply Chain Management)")

        btn_gen_vocab = tk.Button(top_frame, text="📚 TẠO BÀI HỌC TỪ VỰNG CHUYÊN NGÀNH", font=("Segoe UI", 11, "bold"), bg="#66fcf1", fg="#0b0c10", bd=0, pady=12, cursor="hand2", command=self.tao_bai_hoc_tu_vung)
        btn_gen_vocab.pack(fill=tk.X, pady=10)

        mid_frame = tk.Frame(self.tab_vocab, bg="#151b24")
        mid_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        lbl_vocab_result = tk.Label(mid_frame, text="Nội dung bài học chuyên ngành từ AI:", bg="#151b24", fg="#f5b041", font=("Segoe UI", 11, "bold"))
        lbl_vocab_result.pack(anchor="w")

        self.txt_vocab_result = scrolledtext.ScrolledText(mid_frame, bg="#0b0c10", fg="#ffffff", font=("Segoe UI", 11), bd=1, relief="solid", padx=10, pady=10)
        self.txt_vocab_result.pack(fill=tk.BOTH, expand=True, pady=5)
        self.txt_vocab_result.config(state=tk.DISABLED)

    # =====================================================================
    # LOGIC CHO PHẦN LUYỆN VIẾT CÂU
    # =====================================================================
    def clear_placeholder(self):
        if self.entry_translation.get() == "Nhập bản dịch tiếng Anh...":
            self.entry_translation.delete(0, tk.END)

    def set_placeholder(self):
        if not self.entry_translation.get().strip():
            self.entry_translation.insert(0, "Nhập bản dịch tiếng Anh...")

    def tai_cau_luyen_tap(self, data_dict):
        self.cau_vi_hien_tai = data_dict["vi"]
        self.cau_en_hien_tai = data_dict["en"]
        
        self.cac_tu_en = self.cau_en_hien_tai.split()
        self.trang_thai_lat_mo_tu = [False] * len(self.cac_tu_en)

        self.lbl_vi_sentence.config(text=self.cau_vi_hien_tai)

        for child in self.frame_masked_words.winfo_children():
            child.destroy()

        for idx, word in enumerate(self.cac_tu_en):
            clean_word = re.sub(r'[.,?!:;]', '', word)
            mask_text = "👁️ " + "*" * len(clean_word)
            
            duoi_dau_cau = word[len(clean_word):]
            hien_thi_ban_dau = mask_text + duoi_dau_cau

            lbl_word = tk.Label(
                self.frame_masked_words, 
                text=hien_thi_ban_dau, 
                font=("Consolas", 11, "bold"), 
                bg="#f1f3f5", 
                fg="#495057", 
                bd=1, 
                relief="solid", 
                padx=8, 
                pady=6,
                cursor="hand2"
            )
            lbl_word.pack(side=tk.LEFT, padx=4, pady=5)
            lbl_word.bind("<Button-1>", lambda event, i=idx, w=lbl_word: self.hanh_dong_lat_mo_o_chu_vua_bam(i, w))

    def hanh_dong_lat_mo_o_chu_vua_bam(self, index, widget):
        if not self.trang_thai_lat_mo_tu[index]:
            self.trang_thai_lat_mo_tu[index] = True
            tu_goc = self.cac_tu_en[index]
            widget.config(text=tu_goc, fg="#8e44ad", bg="#f3e5f5", relief="groove")

    def hien_goi_y_tu_ke_tiep_shortcut(self):
        for idx, da_mo in enumerate(self.trang_thai_lat_mo_tu):
            if not da_mo:
                children = self.frame_masked_words.winfo_children()
                if idx < len(children):
                    self.hanh_dong_lat_mo_o_chu_vua_bam(idx, children[idx])
                break
        return "break"

    def yeu_cau_ai_sinh_cau_moi_ngau_nhien(self):
        self.lbl_vi_sentence.config(text="⏳ AI Groq đang suy nghĩ biên soạn một câu ngẫu nhiên mới... Chờ xíu nhé...")
        self.entry_translation.delete(0, tk.END)
        self.set_placeholder()
        threading.Thread(target=self.xu_ly_ai_sinh_cau_ngau_nhien_bg, daemon=True).start()

    def xu_ly_ai_sinh_cau_ngau_nhien_bg(self):
        api_key = self.entry_api.get().strip()
        
        if not api_key or not api_key.startswith("gsk_"):
            cau_ngau_nhien = random.choice(KHO_CAU_DU_PHONG)
            while cau_ngau_nhien["vi"] == self.cau_vi_hien_tai:
                cau_ngau_nhien = random.choice(KHO_CAU_DU_PHONG)
            self.root.after(0, lambda: self.tai_cau_luyen_tap(cau_ngau_nhien))
            return

        try:
            client = Groq(api_key=api_key)
            system_prompt = (
                "You are a random English-Vietnamese sentence generator for translation practice. "
                "Your goal is to output exactly ONE random English sentence (A2, B1, or B2 level) and its Vietnamese translation.\n"
                "You MUST return the response strictly in JSON format with two keys 'vi' and 'en'. Do not include any explanation outside the JSON.\n"
                "Example format:\n"
                "{\"vi\": \"Vui lòng gửi cho tôi tệp tin đính kèm.\", \"en\": \"Please send me the attached file.\"}"
            )

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Generate 1 random new sentence pair."}
                ],
                temperature=1.0
            )

            raw_content = completion.choices[0].message.content.strip()
            
            if "{" in raw_content and "}" in raw_content:
                start_idx = raw_content.find("{")
                end_idx = raw_content.rfind("}") + 1
                json_cleaned = raw_content[start_idx:end_idx]
                data = json.loads(json_cleaned)
                
                if "vi" in data and "en" in data:
                    self.root.after(0, lambda: self.tai_cau_luyen_tap(data))
                    return

            raise ValueError("Phản hồi trả về không đúng định dạng cấu trúc cặp câu.")

        except Exception as e:
            print(f"[CẢNH BÁO AI] Lỗi sinh câu hỏi, quay về dùng kho câu mặc định: {e}")
            cau_ngau_nhien = random.choice(KHO_CAU_DU_PHONG)
            self.root.after(0, lambda: self.tai_cau_luyen_tap(cau_ngau_nhien))

    def kiem_tra_dap_an_thuong(self):
        user_ans = self.entry_translation.get().strip().lower().replace(".", "").replace(",", "").replace("?", "")
        target_ans = self.cau_en_hien_tai.strip().lower().replace(".", "").replace(",", "").replace("?", "")

        if user_ans == "nhập bản dịch tiếng anh..." or not user_ans:
            messagebox.showwarning("Thông báo", "Bạn chưa nhập câu trả lời dịch!")
            return

        if user_ans == target_ans:
            children = self.frame_masked_words.winfo_children()
            for idx, word in enumerate(self.cac_tu_en):
                if idx < len(children):
                    self.trang_thai_lat_mo_tu[idx] = True
                    children[idx].config(text=word, fg="#27ae60", bg="#e8f8f5")
            messagebox.showinfo("Chính xác! 🎉", "Tuyệt vời! Câu dịch của bạn trùng khớp hoàn toàn với đáp án gốc.")
        else:
            messagebox.showwarning("Chưa khớp ❌", "Câu dịch của bạn chưa trùng khớp hoàn toàn với mẫu.\nMẹo: Hãy bấm chuột trực tiếp vào các ô chữ phía trên để xem từ gợi ý khó nhé!")

    def cham_diem_cau_voi_ai(self):
        user_ans = self.entry_translation.get().strip()
        if user_ans == "nhập bản dịch tiếng anh..." or not user_ans:
            messagebox.showwarning("Thông báo", "Vui lòng gõ nội dung câu dịch của bạn trước khi gọi AI đánh giá!")
            return

        self.txt_writing_feedback.config(state=tk.NORMAL)
        self.txt_writing_feedback.delete("1.0", tk.END)
        self.txt_writing_feedback.insert(tk.END, "⏳ Đang kết nối bộ não AI Groq để phân tích ngữ pháp câu viết... Vui lòng chờ...")
        self.txt_writing_feedback.config(state=tk.DISABLED)

        threading.Thread(target=self.xu_ly_cham_cau_ai_bg, args=(user_ans,), daemon=True).start()
        return "break"

    def xu_ly_cham_cau_ai_bg(self, user_text):
        api_key = self.entry_api.get().strip()
        if not api_key or not api_key.startswith("gsk_"):
            self.hien_thi_ket_qua_feedback_cau("❌ Thất bại: Cần nhập mã Groq API Key hợp lệ ở thanh trên cùng để sử dụng tính năng này.")
            return

        try:
            client = Groq(api_key=api_key)
            system_prompt = (
                "You are an elite bilingual English-Vietnamese Grammar Coach. "
                "The user is translating a sentence from Vietnamese to English.\n"
                f"Original Vietnamese sentence: {self.cau_vi_hien_tai}\n"
                f"Standard Template English answer: {self.cau_en_hien_tai}\n\n"
                "Evaluate the user's translation and provide direct feedback in Vietnamese: "
                "1. Check if it is grammatically correct and natural. Point out minor mistakes if any.\n"
                "2. Provide 2 alternative smart ways to write this sentence to expand their active vocabulary."
            )

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User's Translation: '{user_text}'"}
                ],
                temperature=0.3
            )

            feedback_content = completion.choices[0].message.content.strip()
            self.hien_thi_ket_qua_feedback_cau(feedback_content)

        except Exception as e:
            self.hien_thi_ket_qua_feedback_cau(f"❌ Gặp lỗi kết nối máy chủ dịch vụ Groq: {str(e)}")

    def hien_thi_ket_qua_feedback_cau(self, text):
        self.txt_writing_feedback.config(state=tk.NORMAL)
        self.txt_writing_feedback.delete("1.0", tk.END)
        self.txt_writing_feedback.insert(tk.END, text)
        self.txt_writing_feedback.config(state=tk.DISABLED)

    # =====================================================================
    # LOGIC CHO PHÂN HỆ CHAT VÀ TỪ VỰNG CHUYÊN NGÀNH
    # =====================================================================
    def send_message(self):
        """Hàm xử lý logic gửi tin nhắn ở Tab Giao tiếp chính (Dòng 651 cũ bị lỗi)"""
        prompt_text = self.entry.get().strip()
        if not prompt_text and not self.noi_dung_tep_tin_tai_len:
            return

        api_key = self.entry_api.get().strip()
        if not api_key or not api_key.startswith("gsk_"):
            messagebox.showwarning("Cấu hình thiếu", "Vui lòng điền mã Groq API Key ở thanh công cụ phía trên trước!")
            return

        luu_api_key_vao_file(api_key)

        # Xây dựng prompt hoàn chỉnh dựa trên file đính kèm
        if self.noi_dung_tep_tin_tai_len:
            full_prompt = f"Nội dung tài liệu đính kèm:\n{self.noi_dung_tep_tin_tai_len}\n\nYêu cầu cụ thể: {prompt_text}"
        else:
            full_prompt = prompt_text

        # Hiển thị tin nhắn của User lên khung chat
        self.txt_area.config(state=tk.NORMAL)
        self.txt_area.insert(tk.END, f"👤 BẠN: {prompt_text}\n\n")
        self.txt_area.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)

        # Chạy luồng nền xử lý gọi API tránh đơ giao diện UI
        threading.Thread(target=self.xu_ly_chat_ai_bg, args=(api_key, full_prompt), daemon=True).start()

    def xu_ly_chat_ai_bg(self, api_key, full_prompt):
        try:
            client = Groq(api_key=api_key)
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful, professional English tutor assisting a Vietnamese student."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7
            )
            response_text = completion.choices[0].message.content.strip()
            self.cau_tra_loi_cuoi_cung = response_text
            
            self.root.after(0, lambda: self.hien_thi_tin_nhan_ai(response_text))
        except Exception as e:
            self.root.after(0, lambda: self.hien_thi_tin_nhan_ai(f"❌ Lỗi xử lý AI: {str(e)}"))

    def hien_thi_tin_nhan_ai(self, text):
        self.txt_area.config(state=tk.NORMAL)
        self.txt_area.insert(tk.END, f"🤖 AI: {text}\n\n" + "-"*50 + "\n\n")
        self.bo_nho_lich_su_chat[self.phien_chat_hien_tai] = self.txt_area.get("1.0", tk.END)
        self.txt_area.config(state=tk.DISABLED)
        self.txt_area.yview(tk.END)

    def phat_giong_noi_gtts(self):
        if not self.cau_tra_loi_cuoi_cung:
            messagebox.showinfo("Thông báo", "Chưa có phản hồi nào từ AI để phát âm thanh!")
            return
        
        def run_tts():
            try:
                # Lọc lấy các đoạn tiếng Anh để phát âm chuẩn hơn
                clean_eng = re.sub(r'[^\x00-\x7F]+', '', self.cau_tra_loi_cuoi_cung)
                if len(clean_eng.strip()) < 5:
                    clean_eng = self.cau_tra_loi_cuoi_cung
                
                tts = gTTS(text=clean_eng[:300], lang='en', tld='com')
                tts.save("speech_preview.mp3")
                os.system("start speech_preview.mp3" if os.name == "nt" else "open speech_preview.mp3")
            except Exception as e:
                print(f"Lỗi phát âm: {e}")

        threading.Thread(target=run_tts, daemon=True).start()

    def tao_bai_hoc_tu_vung(self):
        chuyen_nganh = self.combo_field.get().strip()
        if not chuyen_nganh:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập hoặc chọn một ngành nghề chuyên biệt!")
            return

        self.txt_vocab_result.config(state=tk.NORMAL)
        self.txt_vocab_result.delete("1.0", tk.END)
        self.txt_vocab_result.insert(tk.END, f"⏳ Hệ thống AI đang biên soạn giáo án từ vựng thuật ngữ riêng cho ngành [{chuyen_nganh}]... Vui lòng chờ...")
        self.txt_vocab_result.config(state=tk.DISABLED)

        threading.Thread(target=self.xu_ly_tu_vung_ai, args=(chuyen_nganh,), daemon=True).start()

    def xu_ly_tu_vung_ai(self, nganh_hoc):
        api_key = self.entry_api.get().strip()
        if not api_key or not api_key.startswith("gsk_"):
            self.hien_thi_ket_qua_vocab("❌ Lỗi cấu hình: Cần cung cấp Groq API Key hợp lệ ở thanh công cụ phía trên.")
            return

        luu_api_key_vao_file(api_key)

        try:
            client = Groq(api_key=api_key)
            system_prompt = (
                "You are an expert English Lexicographer and technical vocabulary trainer. "
                "The user will give you a specific professional field/industry. "
                "Your task is to generate a premium and highly effective vocabulary lesson for that specific field in Vietnamese. "
                "Provide exactly 5 essential high-level jargon words or idioms. "
                "For each word, strictly follow this layout:\n"
                "🔹 [Từ vựng/Thuật ngữ] (Từ loại) - /Cách phát âm IPA/\n"
                "   + Nghĩa tiếng Việt: ...\n"
                "   + Định nghĩa tiếng Anh: ...\n"
                "   + Câu ví dụ thực tế trong công việc: (Kèm dịch tiếng Việt)\n\n"
                "At the end of the lesson, write a small paragraph (3-4 sentences) using those terms together to show how they work in context."
            )

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Chuyên ngành yêu cầu: {nganh_hoc}"}
                ],
                temperature=0.6
            )

            bai_hoc = completion.choices[0].message.content.strip()
            self.hien_thi_ket_qua_vocab(bai_hoc)

        except Exception as e:
            self.hien_thi_ket_qua_vocab(f"❌ Đã xảy ra sự cố kết nối máy chủ dữ liệu AI: {str(e)}")

    def hien_thi_ket_qua_vocab(self, text):
        self.txt_vocab_result.config(state=tk.NORMAL)
        self.txt_vocab_result.delete("1.0", tk.END)
        self.txt_vocab_result.insert(tk.END, text)
        self.txt_vocab_result.config(state=tk.DISABLED)

    # =====================================================================
    # CÁC PHƯƠNG THỨC GIAO DIỆN PHỤ TRỢ KHÁC
    # =====================================================================
    def refresh_khung_chat_tu_bo_nho(self):
        self.txt_area.config(state=tk.NORMAL)
        self.txt_area.delete("1.0", tk.END)
        self.txt_area.insert(tk.END, self.bo_nho_lich_su_chat[self.phien_chat_hien_tai])
        self.txt_area.config(state=tk.DISABLED)
        self.txt_area.yview(tk.END)

    def toggle_pin_window(self):
        self.is_pinned = not self.is_pinned
        self.root.attributes("-topmost", self.is_pinned)
        if self.is_pinned:
            self.btn_pin.config(text="📌 Đang ghim", bg="#45f3ff", fg="#0b0c10")
        else:
            self.btn_pin.config(text="📌 Ghim app", bg="#1f2833", fg="#ffffff")

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.btn_toggle_sidebar.config(text="☲ Hiện Lịch sử")
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
            self.notebook.pack_forget()
            self.notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=10)
            self.btn_toggle_sidebar.config(text="☲ Ẩn Lịch sử")
        self.sidebar_visible = not self.sidebar_visible

    def tao_phien_tro_chuyen_moi(self):
        thoi_gian = datetime.datetime.now().strftime("%H:%M:%S")
        ten_phien_moi = f"Phiên học lúc {thoi_gian}"
        self.bo_nho_lich_su_chat[ten_phien_moi] = f"🤖 AI: Hệ thống đã mở không gian học tập mới lúc {thoi_gian}.\n\n"
        self.phien_chat_hien_tai = ten_phien_moi
        self.cap_nhat_danh_sach_listbox()
        self.refresh_khung_chat_tu_bo_nho()

    def chuyen_doi_phien_chat(self, event):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            self.phien_chat_hien_tai = widget.get(index)
            self.refresh_khung_chat_tu_bo_nho()

    def cap_nhat_danh_sach_listbox(self):
        self.listbox_phien.delete(0, tk.END)
        for phien in self.bo_nho_lich_su_chat.keys():
            self.listbox_phien.insert(tk.END, phien)
        try:
            idx = list(self.bo_nho_lich_su_chat.keys()).index(self.phien_chat_hien_tai)
            self.listbox_phien.selection_set(idx)
        except: 
            pass

    def clear_toan_bo_cuoc_tro_chuyen(self):
        self.bo_nho_lich_su_chat[self.phien_chat_hien_tai] = f"🤖 AI: Màn hình đã được dọn sạch.\n\n"
        self.refresh_khung_chat_tu_bo_nho()

    def pick_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp")])
        if file_path:
            self.duong_dan_anh_cho = file_path
            self.status_img.config(text=f"📎 Đã đính kèm ảnh: {os.path.basename(file_path)}")

    def pick_document_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Documents", "*.txt;*.docx;*.pdf")])
        if file_path:
            try:
                if file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.noi_dung_tep_tin_tai_len = f.read()
                elif file_path.endswith('.docx'):
                    doc = docx.Document(file_path)
                    self.noi_dung_tep_tin_tai_len = "\n".join([p.text for p in doc.paragraphs])
                elif file_path.endswith('.pdf'):
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        van_ban = ""
                        for trang in reader.pages:
                            van_ban += trang.extract_text() or ""
                        self.noi_dung_tep_tin_tai_len = van_ban
                
                self.status_img.config(text=f"📎 Đã đọc tài liệu: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Lỗi đọc file", f"Không thể đọc tệp tin: {str(e)}")

# =====================================================================
# KHỞI CHẠY ỨNG DỤNG HỆ THỐNG
# =====================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AppHocTiengAnhCungAI(root)
    root.mainloop()
