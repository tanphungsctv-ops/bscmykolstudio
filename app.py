import streamlit as st
import replicate
import os
import requests
import datetime
from PIL import Image
from io import BytesIO

# --- HỆ THỐNG LƯU TRỮ ---
HISTORY_DIR = "kol_studio_history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="AI KOL Studio Pro",
    page_icon="📸",
    layout="wide"
)

# --- GIAO DIỆN CSS: XANH & TRẮNG SIÊU RÕ NÉT ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #F8FAFC !important;
        color: #1A202E;
    }

    /* Tiêu đề Header */
    .main-header {
        text-align: center;
        padding: 20px;
        background: #FFFFFF;
        border-bottom: 5px solid #2563EB;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
    }

    /* Khu vực nhập API Token nổi bật ở giữa */
    .api-box {
        background-color: #EBF3FF !important;
        border: 2px solid #2563EB !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin-bottom: 30px !important;
        text-align: center;
    }

    /* Khung trắng Card */
    .st-emotion-cache-1r6slb0, .st-emotion-cache-v0683z {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 20px !important;
        padding: 20px !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.04) !important;
    }

    /* Nút bấm Xanh to rõ */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 60px;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        border: none !important;
    }

    label {
        font-weight: 700 !important;
        color: #1E40AF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. HEADER ---
st.markdown("""
    <div class="main-header">
        <h1>📸 AI KOL STUDIO PRO</h1>
        <p style="color:#3B82F6; font-weight:600;">Hệ thống tạo ảnh Blue-White Luxury</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. KHU VỰC NHẬP API TOKEN (NGAY TRÊN CÙNG - KHÔNG THỂ BỎ LỠ) ---
st.markdown("### 🔑 BƯỚC 0: KÍCH HOẠT HỆ THỐNG AI")
with st.container():
    # Kiểm tra xem đã có token trong cấu hình chưa
    default_token = st.secrets.get("REPLICATE_API_TOKEN", "")
    
    # Ô NHẬP TOKEN CHÍNH
    input_token = st.text_input(
        "Dán mã Replicate API Token của bạn vào đây để bắt đầu:", 
        value=default_token, 
        type="password", 
        placeholder="Mã bắt đầu bằng r8_..."
    )

    if input_token:
        os.environ["REPLICATE_API_TOKEN"] = input_token
        st.success("✅ HỆ THỐNG ĐÃ SẴN SÀNG! HÃY TẢI ẢNH VÀ TẠO NGAY BÊN DƯỚI.")
    else:
        st.error("❌ BẠN PHẢI NHẬP MÃ TOKEN Ở TRÊN THÌ AI MỚI CHẠY ĐƯỢC!")

st.divider()

# --- 3. NỘI DUNG CHÍNH ---
tab1, tab2 = st.tabs(["✨ TẠO ẢNH MỚI", "📚 THƯ VIỆN ẢNH"])

with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("### 🟦 1. TẢI ẢNH GỐC")
        src_file = st.file_uploader("Chọn ảnh rõ mặt nhân vật", type=["jpg", "png", "jpeg"])
        
        st.markdown("### 🟦 2. NHẬP MÔ TẢ")
        prompt = st.text_area("Bạn muốn KOL xuất hiện ở đâu?", 
                             "A professional KOL standing in a luxury modern office, wearing a premium suit, cinematic lighting, 8k", 
                             height=100)
        
        ratio = st.selectbox("Tỷ lệ khung hình:", ["3:4 (Portrait)", "1:1 (Square)", "9:16 (Story)"])
        
        # Thêm các tùy chọn nhỏ
        c1, c2 = st.columns(2)
        with c1: skin = st.checkbox("Làm mịn da", value=True)
        with c2: face = st.checkbox("Tăng nét mặt", value=True)
        
        btn_gen = st.button("🚀 BẮT ĐẦU TẠO ẢNH")

    with col_right:
        st.markdown("### 🟦 3. KẾT QUẢ")
        if btn_gen:
            if not input_token:
                st.error("❌ Bạn chưa nhập Token ở Bước 0 (Phía trên cùng)!")
            elif not src_file:
                st.warning("⚠️ Vui lòng chọn ảnh gốc!")
            else:
                with st.status("💎 AI đang xử lý...", expanded=True) as status:
                    try:
                        status.write("⏳ Đang dựng bối cảnh...")
                        r_map = {"3:4 (Portrait)": "3:4", "1:1 (Square)": "1:1", "9:16 (Story)": "9:16"}
                        base = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": r_map[ratio]})
                        
                        status.write("🎯 Đang ghép mặt Identity 98%...")
                        swap = replicate.run("lucataco/faceswap:9a429103ed57553f02f30411ad914c090336da90df113e64ca98282f1d079b50",
                                            input={"target_image": base[0], "source_image": src_file})

                        final_url = swap
                        if skin or face:
                            status.write("✨ Đang làm đẹp hậu kỳ...")
                            final_url = replicate.run("tencentarc/gfpgan:9283608cc6b7c9cc2b527d6563da08ad9510595730335f65bc50c4abc3c79119",
                                                     input={"img": swap, "upscale": 2})

                        status.update(label="✅ ĐÃ XONG!", state="complete")
                        st.image(final_url, use_container_width=True)
                        
                        res_data = requests.get(final_url).content
                        st.download_button("📥 TẢI ẢNH 4K", res_data, file_name="kol_ai.png", mime="image/png")
                        
                        # Lưu lịch sử
                        ts = datetime.datetime.now().strftime("%H%M%S")
                        with open(os.path.join(HISTORY_DIR, f"KOL_{ts}.png"), "wb") as f: f.write(res_data)

                    except Exception as e:
                        st.error(f"Lỗi: {e}")
        else:
            st.info("Ảnh sẽ hiện ở đây sau khi bạn nhập mã Token và bấm nút Tạo.")

with tab2:
    st.markdown("### 📚 THƯ VIỆN CỦA TÔI")
    files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".png")]
    files.sort(reverse=True)
    if not files: st.info("Chưa có ảnh nào.")
    else:
        grid = st.columns(4)
        for i, f in enumerate(files):
            with grid[i % 4]:
                p = os.path.join(HISTORY_DIR, f)
                st.image(p, use_container_width=True)
                with open(p, "rb") as fd: st.download_button("Tải", fd.read(), file_name=f, key=f"dl_{i}")

st.markdown("<br><hr><p style='text-align:center; color:#94A3B8;'>AI KOL Studio Pro Gold Edition</p>", unsafe_allow_html=True)
