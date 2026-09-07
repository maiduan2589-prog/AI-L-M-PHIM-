# AI TỰ VIẾT KỊCH BẢN VÀ TỰ LÀM PHIM

AI Film Factory — hệ thống AI tự động lập kế hoạch, sản xuất, kiểm tra, sửa và dựng phim từ một ý tưởng ban đầu.

## Mục tiêu

Xây dựng một xưởng sản xuất phim AI có khả năng:

**Ý tưởng → Kịch bản → Phân cảnh → Tài sản → Video/Audio → Dựng → QA/Continuity → Sửa → Xuất phim**

Website phát hành là một phần riêng, được giữ đơn giản:

- Chỉ chủ hệ thống đăng phim.
- Người xem không cần tạo kênh hay đăng phim.
- Website tập trung vào xem, khám phá và tìm phim.
- Quảng cáo đặt trên các trang phù hợp, không chèn quảng cáo vào nội dung phim.

## Nguyên tắc kiến trúc

1. AI Film Factory là phần cốt lõi.
2. Pipeline phải có khả năng **plan → execute → evaluate → revise → continue**.
3. Các nhà cung cấp AI được thiết kế theo adapter để có thể thay thế.
4. Dữ liệu sản xuất phải có cấu trúc và có thể tiếp tục/resume.
5. Website công khai tối giản, ưu tiên tốc độ và trải nghiệm xem phim.
6. Không xây các tính năng mạng xã hội/creator upload trong phiên bản đầu.

## Các giai đoạn chính

- [ ] Nền tảng dữ liệu và cấu trúc project
- [ ] Orchestrator / Production Engine
- [ ] Story & Script Engine
- [ ] Scene/Shot Planner
- [ ] Asset & Continuity Manager
- [ ] AI provider adapters
- [ ] Video/Audio production pipeline
- [ ] QA & automatic revision loop
- [ ] Rendering/Export
- [ ] Public Film Website
- [ ] Admin publishing
- [ ] Analytics & advertising integration

## Trạng thái

Đây là repository chính thức của dự án AI Film Factory. Phiên bản đầu tiên sẽ ưu tiên xây **production engine** trước, sau đó kết nối website phát hành.
