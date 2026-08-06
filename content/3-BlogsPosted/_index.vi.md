---
title: "Các bài viết đã đăng"
date: 2024-01-01
weight: 3
chapter: false
pre: " <b> 3. </b> "
---

Phần này liệt kê và giới thiệu các bài blog mình đã đăng hoặc đang chuẩn bị đăng trong nhóm [AWS Study Group](https://www.facebook.com/groups/awsstudygroupfcj). Các bài blog được chia thành ba mục nhỏ, giữ cùng format với trang workshop mẫu.

### [Blog 1 - TẮT EC2 RỒI NHƯNG AWS VẪN TÍNH PHÍ?](3.1-Blog1/)

Bài blog này giải thích lý do AWS vẫn có thể phát sinh chi phí dù EC2 instance đã được tắt, tập trung vào các tài nguyên liên quan vẫn có thể tiếp tục được tính phí ngoài bản thân instance đang chạy.

**Ngày đăng:** 22/07/2026\
**Nền tảng:** AWS Study Groups  
**Trạng thái:** Đã duyệt\
**Liên kết công khai:** [Blog 1](https://www.facebook.com/groups/awsstudygroupfcj/permalink/2219932025438424/?rdid=SGRgenG5JS3UR6Y0#)

### [Blog 2 - XÂY DỰNG HỆ THỐNG CHAT REALTIME CÓ KHẢ NĂNG MỞ RỘNG VỚI SOCKET.IO, REDIS VÀ DYNAMODB](3.2-Blog2/)

Bài blog này giới thiệu cách thiết kế một hệ thống chat realtime có khả năng mở rộng bằng Socket.IO, Redis và DynamoDB. Nội dung tập trung vào cách giao tiếp thời gian thực, trạng thái phân tán và lưu trữ lâu dài có thể phối hợp trong một hệ thống lớn hơn.

**Ngày đăng:** 23/07/2026\
**Nền tảng:** AWS Study Groups  
**Trạng thái:** Đang chờ duyệt

### [Blog 3 - Một chút “thu hoạch” sau hành trình làm Software Engineer: từ viết code đến lúc tự tay làm hệ thống sập rồi tự cứu lại](3.3-Blog3/)

Bài viết chia sẻ hành trình trưởng thành từ một người chủ yếu tập trung vào viết code thành một Software Engineer hiểu toàn diện hơn về cách hệ thống vận hành, gặp sự cố và phục hồi. Qua quá trình làm việc với backend, frontend, Docker, Kubernetes, CI/CD, IAM, database, message queue và AWS, tác giả nhận ra rằng code chạy được ở local chưa đủ; một hệ thống ổn định còn phụ thuộc vào cấu hình, network, quyền truy cập, dữ liệu, hạ tầng và khả năng xử lý lỗi. Bài học lớn nhất là cần debug có hệ thống, kiểm tra đúng điểm gãy thay vì sửa ngẫu nhiên, đồng thời thiết kế để lỗi khó lặp lại hơn.

**Ngày đăng:** 28/07/2026\
**Nền tảng:** AWS Study Groups  
**Trạng thái:** Đang chờ duyệt\
**Liên kết công khai:** [Blog 3](https://www.facebook.com/groups/awsstudygroupfcj/permalink/2227122848052675/#)

### [Blog 4 - AWS Networking Advanced: 3 kỹ thuật nâng cấp VPC chuẩn doanh nghiệp](3.4-Blog4/)

Bài viết trình bày ba kỹ thuật giúp nâng cấp kiến trúc VPC cơ bản thành mô hình phù hợp hơn với hệ thống doanh nghiệp. Nội dung tập trung vào việc sử dụng VPC Endpoints để giảm lưu lượng qua NAT Gateway, triển khai hạ tầng Multi-AZ để tăng tính sẵn sàng và hạn chế chi phí truyền dữ liệu chéo AZ, đồng thời sử dụng AWS Transit Gateway để quản lý kết nối giữa nhiều VPC theo mô hình tập trung. Bài viết cho thấy việc tối ưu network architecture không chỉ cải thiện bảo mật và khả năng mở rộng mà còn giúp kiểm soát chi phí vận hành AWS hiệu quả hơn.

**Ngày đăng:** 29/07/2026\
**Nền tảng:** AWS Study Groups  
**Trạng thái:** Đã xuất bản\
**Liên kết công khai:** [Blog 4](https://www.facebook.com/groups/awsstudygroupfcj/permalink/2225997548165205/#)
