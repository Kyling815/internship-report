---
title: "Sự kiện 1: Ngày hội cộng đồng FCAJ – tháng 6 năm 2026"
date: 2024-01-01
weight: 1
chapter: false
pre: " <b> 4.1. </b> "
---


## Tên sự kiện

FCAJ Community Day – June 2026: Data Driven, AI Risen

Đây là sự kiện cộng đồng về AWS Cloud và AI, bao gồm các phần chia sẻ liên quan đến nghề nghiệp Cloud, AI Agent, Voice AI, DevOps Automation, Amazon Q và bảo mật kết nối MCP.

## Thời gian

09:00, Thứ Bảy, ngày 27/06/2026.

## Địa điểm

Tầng 26 và tầng 36, Bitexco Financial Tower, số 02 Hải Triều, Thành phố Hồ Chí Minh.

Trong phạm vi báo cáo này, mình tham gia sự kiện theo hình thức trực tuyến thông qua livestream của AWS Study Group trên nền tảng Youtube.

## Vai trò

Người tham dự trực tuyến.

Mình theo dõi các phần trình bày, ghi chép nội dung kỹ thuật và phân tích khả năng áp dụng những giải pháp được giới thiệu vào các project Cloud và AI.

## Nội dung chính

Sự kiện bao gồm nhiều chủ đề liên quan đến việc đưa AI và Cloud vào môi trường doanh nghiệp.

### Sự thay đổi của nghề nghiệp Cloud trong thời đại AI

Phần chia sẻ đầu tiên đề cập đến tác động của AI đối với công việc của Cloud Engineer và Solution Architect.

AI có thể hỗ trợ viết code, phân tích log và tự động hóa nhiều tác vụ vận hành. Tuy nhiên, sự phát triển này cũng yêu cầu kỹ sư phải hiểu sâu hơn về kiến trúc hệ thống, bảo mật, chi phí và phương pháp xử lý sự cố.

AI có thể hỗ trợ tăng năng suất, nhưng kỹ sư vẫn phải chịu trách nhiệm kiểm tra kết quả và đưa ra quyết định kỹ thuật phù hợp.

### Xây dựng Voice AI Agent cho thị trường Việt Nam

Các diễn giả giới thiệu quy trình xây dựng Voice AI Agent theo luồng:

Speech-to-Text -> Large Language Model -> Text-to-Speech

Những thách thức quan trọng bao gồm:

- Giảm độ trễ của hệ thống.
- Nhận diện chính xác tiếng Việt.
- Xử lý sự khác biệt về vùng miền và cách phát âm.
- Nhận biết khi người dùng ngắt lời.
- Duy trì ngữ cảnh trong quá trình hội thoại.
- Kiểm soát chi phí và đảm bảo độ ổn định.

Voice AI Agent cũng có thể được kết nối với các công cụ nghiệp vụ để thực hiện tác vụ thực tế, thay vì chỉ trả lời câu hỏi.

### Tự động hóa xử lý sự cố bằng AWS DevOps Agent

AWS DevOps Agent được giới thiệu như một công cụ hỗ trợ thu thập log, phân tích cảnh báo, xác định nguyên nhân gốc và đề xuất các bước khắc phục.

Giải pháp này có thể giúp giảm thời gian xử lý sự cố so với việc kỹ sư phải kiểm tra thủ công nhiều nguồn dữ liệu khác nhau. Tuy nhiên, người vận hành vẫn cần xác minh nguyên nhân và đánh giá mức độ an toàn của phương án do AI đề xuất.

### Ứng dụng Amazon Q trong hoạt động tuyển dụng

Một tình huống được trình bày là sử dụng Amazon Q để đọc nhiều CV, đối chiếu kỹ năng của ứng viên với mô tả công việc và tạo báo cáo đánh giá.

Giải pháp này có thể giảm thời gian sàng lọc hồ sơ. Đồng thời, nội dung trình bày cũng cho thấy AI doanh nghiệp cần được triển khai trong môi trường có kiểm soát nhằm bảo vệ dữ liệu cá nhân và dữ liệu ứng viên.

### Bảo mật kết nối MCP

Phần cuối trình bày các rủi ro khi MCP Server được công khai trực tiếp trên Internet. Những rủi ro có thể bao gồm truy cập trái phép, tấn công từ chối dịch vụ hoặc đánh cắp dữ liệu trong quá trình truyền.

Giải pháp được đề xuất là đặt MCP Server trong mạng riêng, kết hợp VPC, private subnet, private endpoint và cơ chế phân giải tên miền nội bộ.

Cách tiếp cận này giúp dữ liệu trao đổi giữa AI Assistant và các công cụ doanh nghiệp không phải đi qua Internet công cộng, từ đó giảm bề mặt tấn công và cải thiện khả năng kiểm soát truy cập.

## Hình ảnh hoặc video chứng minh tham gia

Minh chứng tham gia cá nhân:

![Minh chứng tham gia sự kiện 1](/images/3-Events/Evidence_Events%201.jpg)

## Bài học rút ra

Sau sự kiện, mình nhận thấy AI chỉ thực sự tạo ra giá trị khi được tích hợp với dữ liệu và quy trình nghiệp vụ.

Một chatbot đơn thuần có thể trả lời câu hỏi, nhưng một hệ thống AI doanh nghiệp cần có khả năng truy xuất dữ liệu đáng tin cậy, sử dụng công cụ, kiểm soát quyền truy cập và ghi lại các hoạt động đã thực hiện.

Phần Voice AI giúp mình hiểu rằng việc kết hợp STT, LLM và TTS có thể được thực hiện tương đối nhanh ở mức thử nghiệm. Tuy nhiên, để triển khai trong môi trường production, nhóm phát triển phải giải quyết nhiều vấn đề liên quan đến độ trễ, khả năng ngắt lời, giọng vùng miền, chi phí và độ ổn định.

Phần AWS DevOps Agent cho thấy AI có thể hỗ trợ đáng kể trong việc phân tích log và xử lý sự cố. Tuy nhiên, kỹ sư vẫn phải hiểu kiến trúc hệ thống để kiểm tra tính hợp lý của nguyên nhân và phương án khắc phục do AI đề xuất.

Bài học quan trọng nhất đối với mình là bảo mật phải được xem xét ngay từ giai đoạn thiết kế. Khi AI được kết nối với email, cơ sở dữ liệu, hệ thống quản lý công việc hoặc các công cụ nội bộ, một lỗi cấu hình có thể dẫn đến rò rỉ dữ liệu quan trọng.

Vì vậy, hệ thống cần áp dụng nguyên tắc quyền tối thiểu, sử dụng mạng riêng khi phù hợp và kiểm soát đầy đủ các hành động của AI Agent.

## Đóng góp cá nhân

Đóng góp cá nhân của mình là ghi chép và phân loại các nội dung của sự kiện theo ba nhóm chính:

- AI và các ứng dụng Agent.
- Vận hành hệ thống Cloud.
- Bảo mật hệ thống và kết nối.

Mình cũng liên hệ những kiến thức này với project thực tập, đặc biệt là khả năng sử dụng AI để phân tích CV, đánh giá mức độ phù hợp giữa ứng viên và công việc, đồng thời bảo vệ dữ liệu cá nhân được lưu trữ trên hệ thống.

Thông qua quá trình tổng hợp, mình xác định được một số yêu cầu cần quan tâm khi phát triển tính năng AI, bao gồm quyền truy cập dữ liệu, khả năng theo dõi hoạt động, cơ chế xác nhận của người dùng và bảo vệ thông tin nhạy cảm.
