"""
init_db.py - Script khởi tạo Cơ sở dữ liệu SQLite và nạp dữ liệu mẫu (Phân hệ Thành viên 2)
Đề tài: NLCNPM23CS-38 - Xây dựng ứng dụng hỗ trợ định hướng kỹ năng nghề nghiệp cho sinh viên CNTT dựa trên tin tuyển dụng

Cách chạy:
    python init_db.py
"""

from models import init_db, DB_PATH
from seed_data import seed_database
from tao_csdl_tieng_viet import build_vietnamese_database, DB_VN_PATH


def main():
    print("=" * 65)
    print("  KHOI TAO CO SO DU LIEU SQLITE (init_db.py)")
    print("=" * 65)
    init_db()
    seed_database()
    build_vietnamese_database()
    print(f"  [OK] Co so du lieu chinh: {DB_PATH}")
    print(f"  [OK] Co so du lieu 11 bang tieng Viet: {DB_VN_PATH}")
    print("=" * 65)


if __name__ == "__main__":
    main()
