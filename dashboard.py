import streamlit as st
import requests
import os
import pandas as pd
import time

st.set_page_config(page_title="Zalo Bot Dashboard", layout="wide")
FLASK_API_URL = os.getenv("FLASK_API_URL", "http://zalo-flask-api:5001").strip()

st.title("📊 Zalo Bot Admin Dashboard")
st.header("🤖 Thông tin Zalo Bot")

# 🔑 FIX LOGIC: Chỉ cần "ok": true trong cục JSON là đủ, mặc kệ status_code HTTP
try:
    with st.spinner("Đang tải thông tin từ Zalo..."):
        res = requests.get(f"{FLASK_API_URL}/bot-info", timeout=15)
        data = res.json()
        
        if data.get("ok"):
            bot_info = data["result"]
            col1, col2, col3 = st.columns(3)
            col1.metric("Tên Bot", bot_info.get("display_name", "N/A"))
            col2.metric("Bot ID", bot_info.get("id", "N/A"))
            col3.metric("Loại tài khoản", bot_info.get("account_type", "N/A"))
        else:
            st.warning("⚠️ Chưa cấu hình ZALO_BOT_TOKEN hoặc token không hợp lệ.")
except Exception as e: st.error(f"❌ Không thể kết nối đến Flask API: {e}")

st.divider()
tab1, tab2 = st.tabs(["📨 Lịch sử Tin nhắn & Webhook", "👥 Quản lý Người dùng & Gửi tin"])

with tab1:
    col_btn, _ = st.columns([1, 4])
    # 🔑 FIX: Thay use_container_width=True thành width="stretch" theo lời khuyên của Streamlit
    if col_btn.button("🔄 Làm mới tin nhắn", width="stretch"): st.rerun()
    try:
        res = requests.get(f"{FLASK_API_URL}/get-messages", timeout=5)
        if res.status_code == 200:
            messages = res.json().get("messages", [])
            if messages:
                df = pd.DataFrame(messages)
                if not df.empty and 'timestamp' in df.columns:
                    display_df = df[['timestamp', 'event_name', 'sender_id', 'message_text']]
                    display_df.columns = ['Thời gian', 'Sự kiện', 'Zalo ID', 'Nội dung tin nhắn']
                    st.dataframe(display_df, hide_index=True)
                with st.expander("🔍 Xem dữ liệu JSON thô"): st.json(messages)
            else: st.info("📭 Chưa có tin nhắn nào.")
    except Exception as e: st.error(f"❌ Lỗi tải tin nhắn: {e}")

with tab2:
    col_btn2, _ = st.columns([1, 4])
    if col_btn2.button("🔄 Làm mới danh sách", width="stretch"): st.rerun()
    
    followers = []
    try:
        res_users = requests.get(f"{FLASK_API_URL}/followers", timeout=5)
        if res_users.status_code == 200:
            data = res_users.json()
            followers = data.get("followers", [])
            st.metric(label="🌟 Tổng số người dùng đã tương tác", value=f"{data.get('total_followers', 0)} người")
            if followers:
                df_users = pd.DataFrame(followers)[['avatar', 'name', 'sender_id', 'last_active', 'interaction_count']]
                st.dataframe(df_users, column_config={
                    "avatar": st.column_config.ImageColumn("Ảnh đại diện", width="small"),
                    "name": "Tên Zalo", "sender_id": "Zalo UID", "last_active": "Lần hoạt động cuối",
                    "interaction_count": st.column_config.NumberColumn("Số lần tương tác", format="%d")
                }, hide_index=True)
            else: st.info("Chưa có người dùng nào tương tác với Bot.")
    except Exception as e: st.error(f"❌ Lỗi tải danh sách người dùng: {e}")

    if followers:
        st.divider()
        st.subheader("💬 Trạm Phát Sóng Tin Nhắn")
        user_dict = {"🌟 --- GỬI HÀNG LOẠT CHO TẤT CẢ ---": "ALL"}
        for u in followers: user_dict[f"👤 {u['name']} (ID: {u['sender_id']})"] = u['sender_id']
            
        selected_user = st.selectbox("🎯 Chọn người nhận:", options=list(user_dict.keys()))
        target_chat_id = user_dict[selected_user]
        msg_type = st.radio("Loại tin nhắn:", ["Văn bản (Text)", "Hình ảnh (Photo)", "Nhãn dán (Sticker)"], horizontal=True)

        with st.form("send_msg_form"):
            text_val, photo_val, caption_val, sticker_val = "", "", "", ""
            if "Văn bản" in msg_type: text_val = st.text_area("Nội dung tin nhắn:")
            elif "Hình ảnh" in msg_type:
                photo_val = st.text_input("Đường dẫn hình ảnh (URL):")
                caption_val = st.text_input("Chú thích (Caption - Tùy chọn):")
            elif "Nhãn dán" in msg_type: sticker_val = st.text_input("Mã Sticker ID:")

            if st.form_submit_button("🚀 Gửi Tin Nhắn", width="stretch"):
                base_payload = {}
                if "Văn bản" in msg_type: base_payload.update({"type": "text", "text": text_val})
                elif "Hình ảnh" in msg_type: base_payload.update({"type": "photo", "photo_url": photo_val, "caption": caption_val})
                elif "Nhãn dán" in msg_type: base_payload.update({"type": "sticker", "sticker_id": sticker_val})

                if target_chat_id != "ALL":
                    payload = base_payload.copy()
                    payload["chat_id"] = target_chat_id
                    with st.spinner(f"Đang gửi tới {selected_user}..."):
                        try:
                            resp = requests.post(f"{FLASK_API_URL}/send-message", json=payload)
                            if resp.status_code == 200: st.success(f"✅ Đã gửi thành công!")
                            else: st.error(f"❌ Lỗi: {resp.json().get('error')}")
                        except Exception as e: st.error(f"❌ Lỗi hệ thống: {e}")
                else:
                    total_sent, progress_bar, status_text = 0, st.progress(0), st.empty()
                    for index, user in enumerate(followers):
                        status_text.text(f"Đang gửi cho: {user['name']}...")
                        payload = base_payload.copy()
                        payload["chat_id"] = user['sender_id']
                        try:
                            if requests.post(f"{FLASK_API_URL}/send-message", json=payload).status_code == 200: total_sent += 1
                        except: pass
                        progress_bar.progress((index + 1) / len(followers))
                        time.sleep(0.5)
                    st.success(f"🎉 Hoàn thành! Đã gửi thành công tới {total_sent}/{len(followers)} khách hàng.")
