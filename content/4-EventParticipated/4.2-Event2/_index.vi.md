---
title: "Sự kiện 2: Kiến trúc Cloud doanh nghiệp và ứng dụng trong thực tế"
date: 2024-01-01
weight: 2
chapter: false
pre: " <b> 4.2. </b> "
---

## Tên sự kiện

AWS Study Tour: Enterprise Cloud Architectures and Industry Applications featuring Cloud Kinetics and Renova Cloud

Đây là chương trình tham quan và học tập thực tế tại AWS, với các phần chia sẻ chuyên môn đến từ đại diện AWS, Cloud Kinetics và Renova Cloud.

## Thời gian

Ngày 23/05/2026.

## Địa điểm

Văn phòng Amazon Web Services Việt Nam, Bitexco Financial Tower, Thành phố Hồ Chí Minh.

Nội dung sự kiện cũng được phát trực tuyến và lưu lại trên kênh YouTube của AWS Study Group để người tham dự có thể theo dõi từ xa hoặc xem lại sau chương trình.

## Vai trò

Người tham dự trực tuyến.

Mình tham gia với vai trò người học, theo dõi các phần chia sẻ của chuyên gia và tìm hiểu cách kiến trúc Cloud được thiết kế, triển khai và vận hành trong môi trường doanh nghiệp.

## Nội dung chính

Sự kiện giới thiệu các kiến thức liên quan đến kiến trúc Cloud cấp doanh nghiệp và cách AWS được ứng dụng để giải quyết các bài toán thực tế.

Một nội dung quan trọng là sự khác biệt giữa một hệ thống Cloud đơn giản và một hệ thống đáp ứng các yêu cầu của doanh nghiệp. Một kiến trúc doanh nghiệp không chỉ cần hoạt động được mà còn phải đáp ứng các tiêu chí như:

- Khả năng mở rộng khi số lượng người dùng hoặc khối lượng dữ liệu tăng.
- Tính sẵn sàng cao và khả năng hạn chế thời gian gián đoạn.
- Bảo mật dữ liệu và quản lý quyền truy cập.
- Khả năng sao lưu và phục hồi khi xảy ra sự cố.
- Theo dõi hiệu năng, nhật ký hoạt động và chi phí sử dụng tài nguyên.
- Tuân thủ các yêu cầu nội bộ và quy định của từng lĩnh vực.

Các diễn giả cũng trình bày vai trò của Solution Architect trong quá trình chuyển đổi yêu cầu kinh doanh thành kiến trúc kỹ thuật. Solution Architect cần tìm hiểu nhu cầu của khách hàng, xác định yêu cầu chức năng và phi chức năng, sau đó lựa chọn các dịch vụ AWS phù hợp.

Một nội dung đáng chú ý khác là quá trình đưa ứng dụng từ môi trường development lên production. Một hệ thống production cần có quy trình triển khai tự động, cơ chế giám sát và cảnh báo, phương pháp kiểm soát thay đổi và kế hoạch khôi phục khi phiên bản mới gặp lỗi.

Các phần chia sẻ từ Cloud Kinetics và Renova Cloud giúp mình hiểu rõ hơn cách doanh nghiệp ứng dụng Cloud để hiện đại hóa hệ thống, cải thiện khả năng mở rộng và hỗ trợ quá trình chuyển đổi số. Sự kiện cũng tạo cơ hội để sinh viên tiếp cận kinh nghiệm thực tế từ các Solution Architect đang làm việc trong lĩnh vực Cloud.

## Hình ảnh hoặc video chứng minh tham gia

Minh chứng tham gia cá nhân:

![Minh chứng tham gia sự kiện 2](/images/3-Events/Evidence_Events%202.jpg)

## Bài học rút ra

Bài học đầu tiên mình rút ra là khi thiết kế một hệ thống Cloud, không nên chỉ tập trung vào việc làm cho ứng dụng có thể chạy. Người phát triển còn phải quan tâm đến bảo mật, hiệu năng, khả năng mở rộng, giám sát, phục hồi sự cố và chi phí vận hành.

Bài học thứ hai là mỗi dịch vụ AWS chỉ nên được sử dụng khi phù hợp với yêu cầu của hệ thống. Việc sử dụng nhiều dịch vụ không đồng nghĩa với một kiến trúc tốt hơn. Một kiến trúc phù hợp cần đơn giản, có thể quản lý, dễ mở rộng và giải quyết đúng nhu cầu.

Bài học thứ ba là môi trường production cần được chuẩn bị và vận hành khác với môi trường development. Thông tin nhạy cảm không nên được lưu trực tiếp trong source code; dữ liệu cần có cơ chế sao lưu; hệ thống cần có log, metric, alarm và quy trình xử lý sự cố.

## Đóng góp cá nhân

Đối với project thực tập, kiến thức từ sự kiện giúp mình hiểu rõ hơn vai trò của các thành phần như API Gateway, máy chủ backend, cơ sở dữ liệu, hệ thống lưu trữ và dịch vụ giám sát.

Mình đã tổng hợp các nguyên tắc thiết kế kiến trúc doanh nghiệp và đối chiếu với kiến trúc của project đang triển khai. Qua đó, mình xác định được một số nội dung cần tiếp tục cải thiện, bao gồm monitoring, backup, quản lý secret, khả năng mở rộng và kiểm soát chi phí.

Mình cũng áp dụng tư duy phân lớp hệ thống, giới hạn quyền truy cập và giám sát tài nguyên khi đánh giá mức độ an toàn và khả năng vận hành của project.
