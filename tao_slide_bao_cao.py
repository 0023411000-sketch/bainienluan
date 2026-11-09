# -*- coding: utf-8 -*-
"""
Script tạo file PowerPoint (.pptx) Báo cáo tiến độ Niên luận ngành CNTT
Mã đề tài: NLCNPM23CS-38
Sử dụng thư viện python-pptx để thiết kế bộ 12 Slide chuẩn Widescreen (16:9).
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_FILE = Path(r"G:\bainienluana\Bao_Cao_Tien_Do_Nien_Luan_NLCNPM23CS-38.pptx")

# Bảng màu chủ đạo (Modern Tech Blue)
C_NAVY_DARK = RGBColor(15, 23, 42)     # #0F172A
C_BLUE_MAIN = RGBColor(30, 58, 138)    # #1E3A8A
C_BLUE_ACCENT = RGBColor(37, 99, 235)  # #2563EB
C_BLUE_LIGHT = RGBColor(219, 234, 254) # #DBEAFE
C_TEAL = RGBColor(15, 118, 110)        # #0F766E
C_GREEN = RGBColor(4, 120, 87)         # #047857
C_AMBER = RGBColor(180, 83, 9)         # #B45309
C_PURPLE = RGBColor(109, 40, 217)      # #6D28D9
C_BG_LIGHT = RGBColor(248, 250, 252)   # #F8FAFC
C_WHITE = RGBColor(255, 255, 255)
C_TEXT_DARK = RGBColor(30, 41, 59)     # #1E293B
C_TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
C_BORDER = RGBColor(203, 213, 225)     # #CBD5E1


def set_slide_bg(slide, color):
    bg = slide.Shapes.AddShape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5)) if hasattr(slide, "Shapes") else None
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    rect.fill.solid()
    rect.fill.fore_color.rgb = color
    rect.line.fill.background()
    return rect


def add_header_and_footer(slide, section_label, slide_title, slide_num, total_slides=12):
    set_slide_bg(slide, C_BG_LIGHT)

    # Header bar
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.25))
    header.fill.solid()
    header.fill.fore_color.rgb = C_BLUE_MAIN
    header.line.fill.background()

    # Accent stripe
    stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.20), Inches(13.333), Inches(0.06))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = C_BLUE_ACCENT
    stripe.line.fill.background()

    # Section text
    tb_sec = slide.shapes.add_textbox(Inches(0.6), Inches(0.12), Inches(11.5), Inches(0.35))
    tf_sec = tb_sec.text_frame
    tf_sec.word_wrap = True
    p_sec = tf_sec.paragraphs[0]
    p_sec.text = section_label.upper()
    p_sec.font.name = "Arial"
    p_sec.font.size = Pt(11)
    p_sec.font.bold = True
    p_sec.font.color.rgb = RGBColor(147, 197, 253)

    # Main slide title
    tb_title = slide.shapes.add_textbox(Inches(0.6), Inches(0.42), Inches(12.0), Inches(0.65))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = slide_title
    p_title.font.name = "Arial"
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE

    # Footer bar
    footer = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(7.05), Inches(13.333), Inches(0.45))
    footer.fill.solid()
    footer.fill.fore_color.rgb = RGBColor(226, 232, 240)
    footer.line.fill.background()

    tb_ft = slide.shapes.add_textbox(Inches(0.6), Inches(7.10), Inches(10.0), Inches(0.35))
    p_ft = tb_ft.text_frame.paragraphs[0]
    p_ft.text = "Báo cáo tiến độ Niên luận ngành CNTT  |  Mã đề tài: NLCNPM23CS-38  |  Hệ thống IT Career Compass"
    p_ft.font.name = "Arial"
    p_ft.font.size = Pt(10.5)
    p_ft.font.color.rgb = C_TEXT_MUTED

    tb_pg = slide.shapes.add_textbox(Inches(11.5), Inches(7.10), Inches(1.2), Inches(0.35))
    p_pg = tb_pg.text_frame.paragraphs[0]
    p_pg.alignment = PP_ALIGN.RIGHT
    p_pg.text = f"Trang {slide_num}/{total_slides}"
    p_pg.font.name = "Arial"
    p_pg.font.size = Pt(10.5)
    p_pg.font.bold = True
    p_pg.font.color.rgb = C_BLUE_MAIN


def add_card(slide, left, top, width, height, header_text, items, header_color=C_BLUE_ACCENT, font_size=13.5):
    # Card body
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.adjustments[0] = 0.02
    card.fill.solid()
    card.fill.fore_color.rgb = C_WHITE
    card.line.color.rgb = C_BORDER
    card.line.width = Pt(1.2)

    # Card header
    hdr_h = Inches(0.58)
    hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, hdr_h)
    hdr.adjustments[0] = 0.02
    hdr.fill.solid()
    hdr.fill.fore_color.rgb = header_color
    hdr.line.fill.background()

    tf_h = hdr.text_frame
    tf_h.word_wrap = True
    tf_h.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_h = tf_h.paragraphs[0]
    p_h.alignment = PP_ALIGN.CENTER
    p_h.text = header_text
    p_h.font.name = "Arial"
    p_h.font.size = Pt(14)
    p_h.font.bold = True
    p_h.font.color.rgb = C_WHITE

    # Card content textbox
    tb = slide.shapes.add_textbox(left + Inches(0.18), top + hdr_h + Inches(0.12),
                                  width - Inches(0.36), height - hdr_h - Inches(0.24))
    tf = tb.text_frame
    tf.word_wrap = True

    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = f"•  {item}"
        p.font.name = "Arial"
        p.font.size = Pt(font_size)
        p.font.color.rgb = C_TEXT_DARK
        p.space_before = Pt(4)
        p.space_after = Pt(6)


def generate_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TRANG BÌA (TITLE SLIDE)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, C_NAVY_DARK)

    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.18))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_BLUE_ACCENT
    top_bar.line.fill.background()

    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.1), Inches(6.8), Inches(0.55))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(30, 41, 59)
    badge.line.color.rgb = C_BLUE_ACCENT
    p_b = badge.text_frame.paragraphs[0]
    p_b.text = "BÁO CÁO TIẾN ĐỘ NIÊN LUẬN NGÀNH CÔNG NGHỆ THÔNG TIN"
    p_b.font.name = "Arial"
    p_b.font.size = Pt(13)
    p_b.font.bold = True
    p_b.font.color.rgb = RGBColor(96, 165, 250)

    tb_main = s1.shapes.add_textbox(Inches(0.9), Inches(1.95), Inches(11.5), Inches(2.3))
    tf_main = tb_main.text_frame
    tf_main.word_wrap = True
    p_m = tf_main.paragraphs[0]
    p_m.text = "XÂY DỰNG ỨNG DỤNG HỖ TRỢ ĐỊNH HƯỚNG KỸ NĂNG NGHỀ NGHIỆP CHO SINH VIÊN CNTT DỰA TRÊN TIN TUYỂN DỤNG"
    p_m.font.name = "Arial"
    p_m.font.size = Pt(30)
    p_m.font.bold = True
    p_m.font.color.rgb = C_WHITE

    info_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(4.55), Inches(11.5), Inches(2.0))
    info_box.adjustments[0] = 0.03
    info_box.fill.solid()
    info_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
    info_box.line.color.rgb = RGBColor(71, 85, 105)
    tf_info = info_box.text_frame
    tf_info.word_wrap = True
    info_lines = [
        ("Mã đề tài: ", "NLCNPM23CS-38  |  Tên hệ thống: IT Career Compass"),
        ("Quy mô thực hiện: ", "02 Thành viên (Phân hệ Thành viên 1 & Thành viên 2)"),
        ("Công nghệ triển khai: ", "Python Flask, SQLite (11 bảng), Bootstrap 5, Chart.js"),
        ("Kho mã nguồn GitHub: ", "https://github.com/0023411000-sketch/bainienluan (Nhánh develop & main)")
    ]
    for idx, (lbl, val) in enumerate(info_lines):
        p = tf_info.paragraphs[0] if idx == 0 else tf_info.add_paragraph()
        p.text = f"•  {lbl}{val}"
        p.font.name = "Arial"
        p.font.size = Pt(15)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_before = Pt(4)
        p.space_after = Pt(4)

    # =========================================================================
    # SLIDE 2: NỘI DUNG BÁO CÁO (AGENDA)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header_and_footer(s2, "Tổng quan báo cáo", "Nội Dung Báo Cáo Tiến Độ Thực Hiện", 2)
    add_card(
        s2, Inches(0.6), Inches(1.55), Inches(5.9), Inches(5.15),
        "PHẦN I: BÀI TOÁN, MỤC TIÊU, PHẠM VI & KHẢO SÁT",
        [
            "1. Đặt vấn đề & Bối cảnh thực tế của sinh viên ngành CNTT.",
            "2. Phát biểu bài toán tổng thể theo mô hình Input – Process – Output.",
            "3. Mục tiêu chung & Mục tiêu cụ thể (Nghiệp vụ & Kỹ thuật).",
            "4. Phạm vi đề tài (6 nhóm chức năng, 8 vị trí CNTT & Giới hạn).",
            "5. Khảo sát các hệ thống hiện có (TopCV, ITviec, LinkedIn, Đào tạo ĐH) và Điểm khác biệt của đề tài."
        ],
        header_color=C_BLUE_ACCENT, font_size=14.5
    )
    add_card(
        s2, Inches(6.8), Inches(1.55), Inches(5.9), Inches(5.15),
        "PHẦN II: KẾ HOẠCH THỰC HIỆN & BÁO CÁO TIẾN ĐỘ",
        [
            "6. Kiến trúc hệ thống & Thiết kế CSDL quan hệ (11 bảng SQLite).",
            "7. Quy trình quản lý mã nguồn Git Flow (main, develop, 2 nhánh TV).",
            "8. Bảng phân công nhiệm vụ chi tiết cho 02 thành viên (50% - 50%).",
            "9. Lộ trình thực hiện 6 tuần & Kết quả đạt được thực tế (100% tính năng).",
            "10. Kết quả kiểm thử tự động, Demo trực tiếp & Hướng phát triển."
        ],
        header_color=C_TEAL, font_size=14.5
    )

    # =========================================================================
    # SLIDE 3: 1. ĐẶT VẤN ĐỀ & BỐI CẢNH THỰC TẾ
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header_and_footer(s3, "1. Bài toán nghiên cứu", "1.1. Đặt Vấn Đề & Bối Cảnh Thực Tế", 3)
    add_card(
        s3, Inches(0.6), Inches(1.55), Inches(5.9), Inches(5.15),
        "THỰC TRẠNG & KHOẢNG CÁCH KỸ NĂNG (SKILL GAP)",
        [
            "Thị trường lao động CNTT biến động rất nhanh với sự ra đời liên tục của các ngôn ngữ, framework, công nghệ Cloud/DevOps và chứng chỉ quốc tế mới.",
            "Tồn tại khoảng cách lớn giữa kiến thức tích lũy trong chương trình đại học (học phần, tín chỉ) và yêu cầu thực tế từ doanh nghiệp tuyển dụng.",
            "Sinh viên khi chuẩn bị thực tập hoặc tốt nghiệp thường lúng túng không biết hồ sơ hiện tại của mình phù hợp với vị trí nghề nghiệp nào nhất."
        ],
        header_color=C_AMBER, font_size=14.5
    )
    add_card(
        s3, Inches(6.8), Inches(1.55), Inches(5.9), Inches(5.15),
        "3 KHÓ KHĂN LỚN CỦA SINH VIÊN CNTT",
        [
            "Chưa định lượng được mức độ phù hợp: Không biết hồ sơ bản thân đáp ứng được bao nhiêu phần trăm (%) so với vị trí mong muốn (Backend, Frontend, Data, AI...).",
            "Khó tổng hợp nhu cầu thị trường: Khó thống kê đâu là kỹ năng cốt lõi, công nghệ phổ biến và chứng chỉ được nhà tuyển dụng yêu cầu nhiều nhất.",
            "Thiếu lộ trình bù đắp tự động: Chưa có công cụ chỉ rõ kỹ năng còn thiếu và tự động gợi ý các môn học đại học CNTT / khóa học cần bổ sung."
        ],
        header_color=C_BLUE_ACCENT, font_size=14.5
    )

    # =========================================================================
    # SLIDE 4: 1. PHÁT BIỂU BÀI TOÁN (INPUT - PROCESS - OUTPUT)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header_and_footer(s4, "1. Bài toán nghiên cứu", "1.2. Phát Biểu Bài Toán (Mô Hình Input – Process – Output)", 4)
    add_card(
        s4, Inches(0.6), Inches(1.55), Inches(3.85), Inches(5.15),
        "ĐẦU VÀO (INPUT)",
        [
            "Hồ sơ cá nhân sinh viên: Họ tên, MSSV, trường, chuyên ngành, GPA, vị trí mục tiêu.",
            "4 danh mục năng lực: Học phần đã học (mã môn, tín chỉ, điểm), Kỹ năng (mức 1-5), Chứng chỉ, Kinh nghiệm & Dự án.",
            "Dữ liệu tuyển dụng: 8 vị trí nghề nghiệp CNTT & kho tin tuyển dụng thực tế (nhập trực tiếp hoặc từ CSV)."
        ],
        header_color=C_BLUE_MAIN, font_size=13.5
    )
    add_card(
        s4, Inches(4.74), Inches(1.55), Inches(3.85), Inches(5.15),
        "XỬ LÝ (PROCESS)",
        [
            "Thống kê tần suất xuất hiện của từng kỹ năng, công nghệ, chứng chỉ, kinh nghiệm theo vị trí.",
            "Đối sánh đa chiều (Kỹ năng + Học phần đã học + Chứng chỉ + Kinh nghiệm) để tính điểm phù hợp (%).",
            "Tự động lọc & gợi ý các môn học đại học CNTT (17 học phần chuẩn) bù đắp trực tiếp kỹ năng còn thiếu."
        ],
        header_color=C_TEAL, font_size=13.5
    )
    add_card(
        s4, Inches(8.88), Inches(1.55), Inches(3.85), Inches(5.15),
        "ĐẦU RA (OUTPUT)",
        [
            "Biểu đồ thống kê trực quan nhu cầu kỹ năng & công nghệ của thị trường theo từng vị trí.",
            "Báo cáo độ phù hợp (%), danh sách Kỹ năng đã có (Badge xanh) – Kỹ năng còn thiếu (Badge đỏ).",
            "Danh sách học phần đại học khuyến nghị & Lộ trình học tập cá nhân (Todo / Doing / Done) trên Dashboard."
        ],
        header_color=C_GREEN, font_size=13.5
    )

    # =========================================================================
    # SLIDE 5: 2. MỤC TIÊU CỦA ĐỀ TÀI
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header_and_footer(s5, "2. Mục tiêu của đề tài", "Mục Tiêu Chung & Mục Tiêu Cụ Thể", 5)
    add_card(
        s5, Inches(0.6), Inches(1.55), Inches(5.9), Inches(5.15),
        "MỤC TIÊU VỀ NGHIỆP VỤ & CHỨC NĂNG",
        [
            "Mục tiêu chung: Giúp sinh viên CNTT tự đánh giá năng lực so với nhu cầu doanh nghiệp, xác định khoảng trống kỹ năng và lập kế hoạch học tập chủ động.",
            "Quản lý tập trung hồ sơ sinh viên theo 4 nhóm: Học phần, Kỹ năng, Chứng chỉ, Kinh nghiệm dự án.",
            "Quản lý danh mục vị trí nghề nghiệp & tin tuyển dụng (hỗ trợ tìm kiếm, lọc và nhập CSV hàng loạt).",
            "Thống kê tự động & trực quan hóa yêu cầu tuyển dụng bằng biểu đồ.",
            "Tự động chấm điểm phù hợp (%) và gợi ý môn học đại học CNTT tương ứng ngay khi cập nhật hồ sơ."
        ],
        header_color=C_BLUE_ACCENT, font_size=13.5
    )
    add_card(
        s5, Inches(6.8), Inches(1.55), Inches(5.9), Inches(5.15),
        "MỤC TIÊU VỀ KỸ THUẬT & CÔNG NGHỆ",
        [
            "Xây dựng Backend chuẩn RESTful API với Python Flask, kiến trúc rõ ràng, dễ bảo trì và mở rộng.",
            "Thiết kế Cơ sở dữ liệu quan hệ SQLite gồm 11 bảng chuẩn hóa (kèm script tương thích SQL Server).",
            "Xây dựng giao diện Web hiện đại, responsive bằng HTML5/CSS3/JS (Bootstrap 5 + Chart.js).",
            "Đảm bảo an toàn & bảo mật: Mã hóa mật khẩu (Werkzeug Security), quản lý phiên Session, chống XSS.",
            "Phân quyền người dùng chặt chẽ theo vai trò (RBAC: Quản trị viên Admin & Sinh viên Student)."
        ],
        header_color=C_PURPLE, font_size=13.5
    )

    # =========================================================================
    # SLIDE 6: 3. PHẠM VI CỦA ĐỀ TÀI
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header_and_footer(s6, "3. Phạm vi của đề tài", "Phạm Vi Chức Năng, Dữ Liệu & Giới Hạn Hệ Thống", 6)
    add_card(
        s6, Inches(0.6), Inches(1.55), Inches(6.3), Inches(5.15),
        "PHẠM VI 6 NHÓM CHỨC NĂNG CỐT LÕI",
        [
            "1. Quản lý Tài khoản, Phân quyền RBAC & Hồ sơ năng lực 4 danh mục (Học phần, Kỹ năng, Chứng chỉ, Kinh nghiệm).",
            "2. Quản lý Vị trí nghề nghiệp & Tin tuyển dụng (CRUD, tìm kiếm, lọc, nhập CSV).",
            "3. Thống kê & Tổng hợp yêu cầu theo vị trí (Biểu đồ cột ngang Top kỹ năng & Biểu đồ tròn Công nghệ).",
            "4. Đối sánh hồ sơ đa chiều & Tự động gợi ý môn học đại học CNTT ngay trên trang Hồ sơ.",
            "5. Quản lý Kế hoạch phát triển năng lực cá nhân (Chưa bắt đầu / Đang học / Hoàn thành).",
            "6. Dashboard tổng quan 4 chỉ số & Biểu đồ so sánh điểm phù hợp giữa các vị trí."
        ],
        header_color=C_BLUE_MAIN, font_size=13.2
    )
    add_card(
        s6, Inches(7.15), Inches(1.55), Inches(5.55), Inches(5.15),
        "PHẠM VI DỮ LIỆU & GIỚI HẠN ĐỀ TÀI",
        [
            "Đối tượng sử dụng: Sinh viên ngành CNTT, KHMT, KTPM và Quản trị viên hệ thống.",
            "8 vị trí nghề nghiệp CNTT trọng điểm: Backend, Frontend, Fullstack, Data Analyst, DevOps, QA/QC Tester, Mobile App, AI/ML Engineer.",
            "Tích hợp chương trình 17 học phần đại học CNTT chuẩn ánh xạ trực tiếp với kỹ năng doanh nghiệp.",
            "Giới hạn đề tài: Thu thập dữ liệu tin tuyển dụng qua chức năng quản trị & nhập file CSV chuẩn hóa (không thực hiện crawl tự động trái phép)."
        ],
        header_color=C_TEAL, font_size=13.5
    )

    # =========================================================================
    # SLIDE 7: 4. KHẢO SÁT HIỆN TRẠNG & ĐIỂM KHÁC BIỆT
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header_and_footer(s7, "4. Khảo sát hiện trạng", "Khảo Sát Các Hệ Thống Hiện Có & Điểm Khác Biệt Của Đề Tài", 7)
    add_card(
        s7, Inches(0.6), Inches(1.55), Inches(3.85), Inches(5.15),
        "CỔNG TUYỂN DỤNG (TOPCV, ITVIEC, LINKEDIN)",
        [
            "Ưu điểm: Kho tin tuyển dụng phong phú, hỗ trợ tạo CV và kết nối doanh nghiệp.",
            "Hạn chế với sinh viên: Hướng tới người đã đi làm tìm việc ngay.",
            "Không quản lý bảng điểm học phần đại học, không thống kê tỷ lệ kỹ năng theo vị trí và không có công cụ lập kế hoạch học tập dài hạn."
        ],
        header_color=RGBColor(71, 85, 105), font_size=13.5
    )
    add_card(
        s7, Inches(4.74), Inches(1.55), Inches(3.85), Inches(5.15),
        "HỆ THỐNG QUẢN LÝ ĐÀO TẠO ĐẠI HỌC",
        [
            "Ưu điểm: Lưu trữ chính xác mã học phần, số tín chỉ tích lũy, điểm chữ và GPA của sinh viên.",
            "Hạn chế: Chỉ quản lý kết quả học tập nội bộ trong nhà trường.",
            "Hoàn toàn tách biệt với dữ liệu thị trường tuyển dụng; sinh viên không biết các môn đã học đáp ứng được bao nhiêu % yêu cầu doanh nghiệp."
        ],
        header_color=RGBColor(71, 85, 105), font_size=13.5
    )
    add_card(
        s7, Inches(8.88), Inches(1.55), Inches(3.85), Inches(5.15),
        "ĐIỂM KHÁC BIỆT CỦA IT CAREER COMPASS",
        [
            "Đóng vai trò cầu nối trực tiếp giữa Nhà trường (Học phần/Tín chỉ) và Doanh nghiệp (Tin tuyển dụng).",
            "Tự động cộng hưởng kỹ năng từ các học phần đã hoàn thành vào điểm phù hợp nghề nghiệp.",
            "Gợi ý chính xác môn học đại học CNTT cần đăng ký tiếp theo và chuyển hóa kỹ năng thiếu thành Kế hoạch học tập cá nhân."
        ],
        header_color=C_BLUE_ACCENT, font_size=13.5
    )

    # =========================================================================
    # SLIDE 8: 5. KIẾN TRÚC HỆ THỐNG & CSDL 11 BẢNG
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header_and_footer(s8, "5. Thiết kế hệ thống", "Kiến Trúc Kỹ Thuật & Thiết Kế Cơ Sở Dữ Liệu (11 Bảng)", 8)
    add_card(
        s8, Inches(0.6), Inches(1.55), Inches(5.6), Inches(5.15),
        "KIẾN TRÚC CÔNG NGHỆ (TECH STACK)",
        [
            "Tầng Giao diện (Frontend): HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons & thư viện biểu đồ Chart.js.",
            "Tầng Giao tiếp API: Kiến trúc tập trung qua static/js/api.js (Fetch RESTful JSON).",
            "Tầng Xử lý (Backend): Python 3 + Flask Framework với hơn 25 API endpoints xử lý xác thực, thống kê, đối sánh đa chiều.",
            "Quản lý mã nguồn: Git & GitHub theo mô hình Git Flow 4 nhánh (main, develop, thanh-vien-1, thanh-vien-2)."
        ],
        header_color=C_BLUE_MAIN, font_size=13.5
    )
    add_card(
        s8, Inches(6.45), Inches(1.55), Inches(6.25), Inches(5.15),
        "CƠ SỞ DỮ LIỆU QUAN HỆ SQLITE (11 BẢNG CHUẨN HÓA)",
        [
            "1. users: Quản lý tài khoản đăng nhập & phân quyền (student / admin).",
            "2. student_profiles: Hồ sơ học thuật & vị trí nghề nghiệp mục tiêu.",
            "3-6. courses (Học phần), skills (Kỹ năng), certificates (Chứng chỉ), experiences (Kinh nghiệm thực tế).",
            "7-8. positions (8 Vị trí nghề nghiệp CNTT) & jobs (Kho tin tuyển dụng thực tế).",
            "9. learning_plans: Mục tiêu & tiến độ kế hoạch học tập cá nhân.",
            "10-11. course_recommendations (Kho gợi ý khóa học) & comparison_history (Lịch sử đối sánh hồ sơ)."
        ],
        header_color=C_TEAL, font_size=13.2
    )

    # =========================================================================
    # SLIDE 9: 6. KẾ HOẠCH & PHÂN CÔNG NHIỆM VỤ 2 THÀNH VIÊN
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header_and_footer(s9, "6. Kế hoạch thực hiện", "Phân Công Nhiệm Vụ Chi Tiết Cho 02 Thành Viên (50% – 50%)", 9)
    add_card(
        s9, Inches(0.6), Inches(1.55), Inches(5.9), Inches(5.15),
        "THÀNH VIÊN 1 (Nhánh: thanh-vien-1) - CORE DATA & CRUD",
        [
            "Vai trò: Phụ trách Phân hệ Người dùng, Hồ sơ sinh viên, Vị trí nghề nghiệp & Tin tuyển dụng.",
            "1. Thiết kế CSDL nền tảng: Bảng users, student_profiles, courses, skills, certificates, experiences, positions, jobs & dữ liệu mẫu.",
            "2. Xác thực & Phân quyền: API Đăng ký, Đăng nhập, Đăng xuất, Quản trị tài khoản Admin (/admin/users).",
            "3. Quản lý Hồ sơ sinh viên: Cập nhật thông tin cá nhân & CRUD đầy đủ 4 danh mục năng lực.",
            "4. Quản lý Vị trí & Tin tuyển dụng: CRUD vị trí, CRUD tin tuyển dụng, tìm kiếm, lọc & nhập CSV hàng loạt."
        ],
        header_color=C_BLUE_ACCENT, font_size=13.2
    )
    add_card(
        s9, Inches(6.8), Inches(1.55), Inches(5.9), Inches(5.15),
        "THÀNH VIÊN 2 (Nhánh: thanh-vien-2) - ANALYTICS & PLAN",
        [
            "Vai trò: Phụ trách Phân hệ Thống kê, Đối sánh, Gợi ý môn học & Kế hoạch học tập.",
            "1. Thiết kế CSDL Phân tích: Bảng learning_plans, course_recommendations, comparison_history.",
            "2. Thống kê thị trường: Thuật toán tổng hợp tần suất kỹ năng, công nghệ, chứng chỉ & vẽ biểu đồ Chart.js (/statistics).",
            "3. Đối sánh & Gợi ý tự động: Thuật toán tính điểm phù hợp đa chiều (%) & tự động gợi ý 17 học phần đại học CNTT (/profile, /compare).",
            "4. Quản lý Kế hoạch phát triển năng lực (/plan) & Dashboard tổng quan (/dashboard)."
        ],
        header_color=C_TEAL, font_size=13.2
    )

    # =========================================================================
    # SLIDE 10: 6. LỘ TRÌNH THỰC HIỆN 6 TUẦN (TIMELINE)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header_and_footer(s10, "6. Kế hoạch thực hiện", "Lộ Trình Thực Hiện 6 Tuần & Trạng Thái Hoàn Thành", 10)
    add_card(
        s10, Inches(0.6), Inches(1.55), Inches(5.9), Inches(5.15),
        "GIAI ĐOẠN 1: TUẦN 1 – TUẦN 3 (KHỞI TẠO & NỀN TẢNG)",
        [
            "Tuần 1 [Hoàn thành 100%]: Khảo sát bài toán, chốt đề cương kehoach.md, thiết kế sơ đồ ERD 11 bảng và khởi tạo kho GitHub với 4 nhánh Git Flow.",
            "Tuần 2 [Hoàn thành 100%]: Xây dựng hoàn chỉnh bộ giao diện Frontend (HTML5/CSS3/JS, Bootstrap 5, Chart.js) cho toàn bộ các trang của 2 thành viên.",
            "Tuần 3 [Hoàn thành 100%]: Phát triển Backend API giai đoạn 1 – Khởi tạo database.db, API Xác thực, API Hồ sơ 4 danh mục & API Thống kê kỹ năng."
        ],
        header_color=C_BLUE_MAIN, font_size=14
    )
    add_card(
        s10, Inches(6.8), Inches(1.55), Inches(5.9), Inches(5.15),
        "GIAI ĐOẠN 2: TUẦN 4 – TUẦN 6 (TÍCH HỢP & HOÀN THIỆN)",
        [
            "Tuần 4 [Hoàn thành 100%]: Phát triển Backend API giai đoạn 2 – API Vị trí, Tin tuyển dụng, Import CSV, Đối sánh, Kế hoạch học tập & Dashboard.",
            "Tuần 5 [Hoàn thành 100%]: Tích hợp Frontend - Backend thật, nâng cấp tự động gợi ý môn học CNTT ngay trên Profile, Phân quyền RBAC & Kiểm thử tự động.",
            "Tuần 6 [Đang hoàn tất]: Hoàn thiện quyển báo cáo Niên luận, slide thuyết trình báo cáo tiến độ và chuẩn bị bảo vệ trước Hội đồng."
        ],
        header_color=C_GREEN, font_size=14
    )

    # =========================================================================
    # SLIDE 11: 7. BÁO CÁO TIẾN ĐỘ & KẾT QUẢ ĐẠT ĐƯỢC
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header_and_footer(s11, "7. Báo cáo tiến độ thực tế", "Kết Quả Đạt Được Hiện Tại (Hoàn Thành 100% Chức Năng)", 11)
    add_card(
        s11, Inches(0.6), Inches(1.55), Inches(3.85), Inches(5.15),
        "CƠ SỞ DỮ LIỆU & BACKEND (100%)",
        [
            "Hoàn thành 11/11 bảng SQLite (database.db) cùng tập dữ liệu mẫu phong phú cho 8 vị trí CNTT.",
            "Hoàn thành hơn 25 RESTful API endpoints chạy ổn định.",
            "Tích hợp danh mục 17 học phần đại học CNTT chuẩn (ACADEMIC_CURRICULUM) để ánh xạ kỹ năng và gợi ý tự động."
        ],
        header_color=C_GREEN, font_size=13.5
    )
    add_card(
        s11, Inches(4.74), Inches(1.55), Inches(3.85), Inches(5.15),
        "GIAO DIỆN & TÍNH NĂNG (100%)",
        [
            "Hoàn thành 12/12 trang giao diện Web trực quan, biểu đồ Chart.js sinh động.",
            "Tự động chấm điểm phù hợp (%) & gợi ý môn học ngay khi sinh viên cập nhật bất kỳ mục nào trong hồ sơ.",
            "Bổ sung trang Quản trị & Phân quyền (/admin/users) và trang Xem CSDL trực tiếp (/db-viewer)."
        ],
        header_color=C_BLUE_ACCENT, font_size=13.5
    )
    add_card(
        s11, Inches(8.88), Inches(1.55), Inches(3.85), Inches(5.15),
        "KIỂM THỬ & GIT FLOW (100%)",
        [
            "Xây dựng kịch bản kiểm thử tự động (test_profile_evaluation.py) đạt 100% Pass.",
            "Rà soát toàn bộ 213 DOM ID, 46 lệnh API.* và 12 route giao diện không có lỗi.",
            "Mã nguồn đã được tích hợp sạch sẽ và đẩy lên nhánh develop & main trên GitHub."
        ],
        header_color=C_PURPLE, font_size=13.5
    )

    # =========================================================================
    # SLIDE 12: TỔNG KẾT & HƯỚNG PHÁT TRIỂN
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header_and_footer(s12, "8. Tổng kết & Định hướng", "Tổng Kết Đề Tài & Hướng Phát Triển Tiếp Theo", 12)
    add_card(
        s12, Inches(0.6), Inches(1.55), Inches(5.9), Inches(5.15),
        "TỔNG KẾT KẾT QUẢ ĐẠT ĐƯỢC",
        [
            "Ứng dụng IT Career Compass (Mã đề tài: NLCNPM23CS-38) đã hoàn thành 100% các mục tiêu và phạm vi đề ra.",
            "Giải quyết trọn vẹn bài toán định lượng mức độ phù hợp nghề nghiệp (%) dựa trên sự kết hợp giữa Học phần đại học, Kỹ năng, Chứng chỉ và Kinh nghiệm.",
            "Hỗ trợ thiết thực cho sinh viên CNTT nhận diện khoảng trống kỹ năng và đăng ký học phần / khóa học bổ sung kịp thời."
        ],
        header_color=C_BLUE_MAIN, font_size=14
    )
    add_card(
        s12, Inches(6.8), Inches(1.55), Inches(5.9), Inches(5.15),
        "HƯỚNG PHÁT TRIỂN MỞ RỘNG",
        [
            "Tích hợp tính năng tải lên CV định dạng PDF/DOCX và tự động bóc tách kỹ năng, học phần vào hồ sơ sinh viên.",
            "Ứng dụng mô hình xử lý ngôn ngữ tự nhiên (NLP / Semantic Embedding) để so khớp sâu hơn các yêu cầu công việc phức tạp.",
            "Phát triển thêm phân hệ dành cho Doanh nghiệp đăng tin trực tiếp và tìm kiếm ứng viên sinh viên phù hợp.",
            "Trân trọng cảm ơn Giảng viên hướng dẫn & Hội đồng đã lắng nghe!"
        ],
        header_color=C_TEAL, font_size=14
    )

    prs.save(str(OUTPUT_FILE))
    print(f"Đã xuất thành công file PowerPoint (12 slides) tại: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_presentation()
