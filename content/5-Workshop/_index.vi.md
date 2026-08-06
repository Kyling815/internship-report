---
title: "Hội thảo thực hành"
date: 2024-01-01
weight: 5
chapter: false
pre: " <b> 5. </b> "
includeContainerContentInReport: true
---

## Tổng quan

Workshop này trình bày toàn bộ quy trình triển khai ứng dụng Internship Application Tracker trên nền tảng AWS.

Nội dung workshop bao gồm chuẩn bị mã nguồn, khởi tạo hạ tầng cloud, triển khai cơ sở dữ liệu, triển khai ứng dụng, xử lý AI, gửi thông báo theo sự kiện, giám sát, kiểm thử, xử lý sự cố và dọn dẹp tài nguyên.

Kiến trúc chính thức sử dụng:

- Amazon CloudFront và Amazon S3 để phân phối frontend.
- Application Load Balancer để tiếp nhận lưu lượng public API và thời gian thực (realtime).
- Amazon EKS cho các workload backend, chat, worker và AI adapter.
- Amazon RDS PostgreSQL để lưu trữ dữ liệu giao dịch nghiệp vụ.
- Amazon ElastiCache Redis phục vụ kênh pub/sub thời gian thực cho Socket.IO.
- Amazon DynamoDB để lưu trữ bền vững dữ liệu chat và khử lặp (deduplication) sự kiện cho Lambda.
- Amazon SQS để truyền tải sự kiện bất đồng bộ.
- AWS Lambda và Amazon SES để gửi thông báo.
- Amazon SageMaker để phục vụ suy đoán AI (AI inference).
- GitHub Actions và AWS OIDC cho luồng triển khai tự động liên tục.

## Mục tiêu học tập

Sau khi hoàn thành workshop này, người đọc có thể:

1. Chuẩn bị một ứng dụng kiến trúc đa dịch vụ (multi-service) sẵn sàng để triển khai lên AWS.
2. Triển khai các dịch vụ container lên Amazon EKS.
3. Triển khai frontend tĩnh React thông qua Amazon S3 và CloudFront.
4. Kết nối các workload trên EKS với RDS, Redis, DynamoDB, SQS và SageMaker.
5. Thực hiện xử lý bất đồng bộ bằng các worker và mô hình transactional outbox.
6. Xử lý các sự kiện SQS bằng AWS Lambda.
7. Triển khai cơ chế xử lý tính bất biến (idempotent) cho Lambda bằng cách sử dụng DynamoDB.
8. Cấu hình luồng CI/CD sử dụng GitHub Actions và AWS OIDC.
9. Kiểm chứng toàn bộ hệ thống thông qua kiểm thử đầu cuối (end-to-end testing).
10. Chẩn đoán các lỗi mạng, IAM và triển khai phổ biến.

## Đối tượng hướng đến

Workshop này phù hợp dành cho:

- Thực tập sinh kỹ thuật Cloud (Cloud engineering interns).
- Sinh viên theo học hướng Backend và DevOps.
- Lập trình viên đang tìm hiểu và thực hành với Amazon EKS.
- Lập trình viên muốn xây dựng kiến trúc hướng sự kiện (event-driven architectures) trên AWS.
- Sinh viên đang thực hiện báo cáo thực tập hoặc đồ án tốt nghiệp về hệ thống AWS.

## Tóm tắt kiến trúc

![Kiến trúc hạ tầng Internship Application Tracker trên AWS](/images/5-Workshop/infra.png)

Trình duyệt người dùng kết nối an toàn tới Amazon CloudFront thông qua giao thức HTTPS.

CloudFront định tuyến:

- các request tải trang tĩnh của frontend đến Amazon S3
- các request `/api/*` đến dịch vụ backend thông qua Application Load Balancer
- các request `/chat/*` đến dịch vụ chat
- các request `/socket.io/*` đến dịch vụ liên lạc thời gian thực Socket.IO

Backend, dịch vụ chat, processing worker, dịch vụ AI và outbox dispatcher vận hành bên trong Amazon EKS.

PostgreSQL lưu trữ dữ liệu giao dịch nghiệp vụ và các tác vụ processing jobs. DynamoDB lưu trữ dữ liệu tin nhắn chat. Redis cung cấp cơ chế pub/sub điều phối tin nhắn giữa các pod chat.

Processing worker gọi đến dịch vụ AI (AI service), và dịch vụ AI sẽ trực tiếp gửi lời gọi đến máy chủ SageMaker endpoint.

Outbox dispatcher tiến hành phát hành các sự kiện nghiệp vụ sang Amazon SQS. AWS Lambda tiếp nhận các sự kiện này, thực thi logic khử lặp trong DynamoDB, lưu giữ (archive) nội dung sự kiện vào Amazon S3 và phát tán email thông báo thông qua Amazon SES.

## Danh sách các chương

| Chương | Tiêu đề | Mô tả | Trạng thái |
|---|---|---|---|
| 5.1 | Tổng quan | Mục tiêu, phạm vi và kiến trúc hoàn chỉnh của workshop | Hoàn thành |
| 5.2 | Kiến trúc | Chi tiết kiến trúc AWS và luồng di chuyển của các request | Hoàn thành |
| 5.3 | Điều kiện tiên quyết | Yêu cầu về tài khoản, công cụ kỹ thuật và cấu trúc máy địa phương | Hoàn thành |
| 5.4 | Chuẩn bị mã nguồn | Cấu trúc repository, biến môi trường và quy tắc kiểm định | Hoàn thành |
| 5.5 | Hạ tầng AWS | Mạng kết nối, IAM, EKS, ECR, ALB và CloudFront | Hoàn thành |
| 5.6 | Triển khai cơ sở dữ liệu | Triển khai PostgreSQL, Redis và DynamoDB | Hoàn thành |
| 5.7 | Triển khai backend | Triển khai backend, chat, dispatcher, dịch vụ AI và worker | Hoàn thành |
| 5.8 | Triển khai frontend | Build mã React, tải tệp lên S3 và thiết lập CDN CloudFront | Hoàn thành |
| 5.9 | Giám sát và nhật ký | Nhật ký, điểm kiểm tra sức khỏe, thông số metrics và cảnh báo | Hoàn thành |
| 5.10 | Kiểm thử đầu cuối | Nghiệm thu tổng thể ứng dụng, chat, dịch vụ AI và Lambda | Hoàn thành |
| 5.11 | Bảo mật và chi phí | IAM, mã hóa dữ liệu, OIDC và các giả định về cước phí | Hoàn thành |
| 5.12 | Xử lý sự cố | Phân tích và tháo gỡ các lỗi triển khai cũng như lỗi vận hành thực tế | Hoàn thành |
| 5.13 | Dọn dẹp tài nguyên |Quy trình từng bước hủy bỏ an toàn các tài nguyên mồi gánh chi phí | Hoàn thành |

## Kết quả đầu ra

Tại điểm kết thúc workshop, ứng dụng Internship Application Tracker sẵn sàng đón nhận kết nối qua mạng CloudFront và đảm bảo trọn vẹn các năng lực:

- phân phối trang tĩnh cho frontend
- hệ thống API từ backend
- liên lạc chat thời gian thực
- lưu trữ dữ liệu an toàn và lâu dài
- tác nghiệp suy đoán AI bất đồng bộ
- khâu phát tin nhắn theo mô hình transactional outbox
- gửi thông tin cảnh báo thông qua AWS Lambda
- luồng triển khai tự động hóa mượt mà nhờ GitHub Actions
