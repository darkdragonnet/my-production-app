import os
import logging
import time
import requests
from datetime import datetime

# Cấu hình logging để xem trên Docker
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Khởi tạo biến toàn cục cho Admin ID
ADMIN_ZALO_ID = None
FLASK_API_URL = os.getenv("FLASK_API_URL", "http://zalo-flask-api:5001")

def get_admin_id_on_startup():
    """Hàm chạy khi khởi động để lấy ID của Admin từ biến môi trường"""
    global ADMIN_ZALO_ID
    
    # Quét biến môi trường để lấy ID
    ADMIN_ZALO_ID = os.getenv("ADMIN_ZALO_ID")
    
    if ADMIN_ZALO_ID:
        logger.info(f"✅ [STARTUP] Đã nhận diện thành công Admin ID: {ADMIN_ZALO_ID}")
        # Gửi thông báo cho Admin rằng hệ thống đã khởi động
        notify_admin_system_online(ADMIN_ZALO_ID)
    else:
        logger.warning("⚠️ [STARTUP] Chưa tìm thấy ADMIN_ZALO_ID trong cấu hình. Các tính năng thông báo cho Admin sẽ bị vô hiệu hóa.")

def notify_admin_system_online(admin_id):
    """Gửi tin nhắn thông báo cho Admin rằng hệ thống đã khởi động"""
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        message = f"🤖 Bot đã khởi động thành công lúc {current_time}. Hệ thống sẵn sàng phục vụ!"
        
        logger.info(f"📨 Đang gửi tin nhắn báo thức dậy cho Admin {admin_id}...")
        
        # Gọi API Flask để gửi tin nhắn (bạn cần thêm endpoint này vào app.py)
        response = requests.post(
            f"{FLASK_API_URL}/send-message",
            json={
                "recipient_id": admin_id,
                "message": message
            },
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Tin nhắn đã gửi thành công cho Admin {admin_id}")
        else:
            logger.warning(f"⚠️ Gửi tin nhắn thất bại. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Lỗi khi gửi tin nhắn cho Admin: {e}")

def monitor_system_health():
    """Hàm giám sát sức khỏe hệ thống và gửi cảnh báo nếu có lỗi"""
    try:
        response = requests.get(f"{FLASK_API_URL}/status", timeout=5)
        if response.status_code != 200:
            logger.error(f"❌ API gặp lỗi! Status: {response.status_code}")
            if ADMIN_ZALO_ID:
                # Gửi cảnh báo cho Admin
                requests.post(
                    f"{FLASK_API_URL}/send-message",
                    json={
                        "recipient_id": ADMIN_ZALO_ID,
                        "message": "⚠️ CẢNH BÁO: API gặp lỗi và không phản hồi!"
                    },
                    timeout=5
                )
    except Exception as e:
        logger.error(f"❌ Lỗi khi kiểm tra sức khỏe hệ thống: {e}")

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("🚀 Bot Service đang khởi động...")
    logger.info("=" * 50)
    
    # 1. Gọi hàm kiểm tra admin đầu tiên khi chạy file
    get_admin_id_on_startup()
    
    # 2. Chạy logic chính của Bot (vòng lặp duy trì kết nối)
    logger.info("Bot Service đang hoạt động...")
    logger.info("=" * 50)
    
    counter = 0
    while True:
        try:
            counter += 1
            
            # Mỗi 5 phút (300 giây) kiểm tra một lần sức khỏe hệ thống
            if counter % 5 == 0:
                monitor_system_health()
            
            # Xử lý các task ngầm ở đây
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Bot Service đã dừng.")
            break
        except Exception as e:
            logger.error(f"Lỗi trong vòng lặp chính: {e}")
            time.sleep(60)
