---
title: "Nhật ký tuần 1"
date: 2024-01-01
weight: 1
chapter: false
pre: " <b> 1.1. </b> "
---

# Tuần 1 - Phân tích project và kiến trúc cơ sở

## Mục tiêu

Trong nhóm 5 thành viên, mục tiêu cá nhân của tôi trong tuần đầu là tìm hiểu các phần mã nguồn liên quan đến triển khai, xác định ranh giới và phụ thuộc giữa các service, đồng thời lập tài liệu kiến trúc cơ sở cho công việc Cloud/DevOps ở các tuần sau.

## Phần việc cá nhân

| Trạng thái | Phần việc được phân công | Cơ sở minh chứng |
|---|---|---|
| Hoàn thành | Khảo sát cấu trúc monorepo và xác định các service chạy chính. | Cây mã nguồn, `README.md`, `docker-compose.yml` và commit `4e939cf`. |
| Hoàn thành | Lập bản đồ phụ thuộc giữa frontend, FastAPI backend, chat service, AI service, PostgreSQL, Redis và DynamoDB. | Các thư mục service, Compose và cấu hình hệ thống. |
| Hoàn thành | Review luồng request ban đầu giữa browser, API, chat và các lớp lưu trữ. | API client, backend router, Socket.IO server và storage service. |
| Hoàn thành | Kiểm tra mô hình khởi chạy local và tài liệu hóa cách chạy riêng từng service. | Commit `d3c1168` và `e43cc04`. |

## Triển khai kỹ thuật

Kho mã nguồn là một monorepo, trong đó mỗi dịch vụ đảm nhiệm một trách nhiệm riêng:

- `frontend/`: ứng dụng React và Vite dành cho ứng viên và nhân sự.
- `backend/`: API FastAPI, mô hình SQLAlchemy, migration Alembic, xác thực, công việc, hồ sơ ứng tuyển, tài liệu và các tuyến điều phối AI.
- `chat-service/`: Node.js, Express, Socket.IO, bộ điều hợp Redis và cơ chế lưu hội thoại trên DynamoDB.
- `ai_service/`: phân tích AI, chuẩn hóa CV/công việc, xếp hạng lại và mã bộ điều hợp SageMaker được bổ sung sau đó.
- `docker-compose.yml`: các thành phần phụ thuộc cục bộ và quy trình khởi chạy nhiều dịch vụ.

Kiến trúc cơ sở ban đầu:

{{< mermaid >}}
graph LR
  User["Candidate / HR browser"] --> Frontend["React / Vite frontend"]
  Frontend --> Backend["FastAPI backend"]
  Frontend --> Chat["Node.js Socket.IO chat service"]
  Backend --> Postgres["PostgreSQL"]
  Backend --> Storage["S3-compatible document storage"]
  Backend --> AI["AI service"]
  Chat --> Redis["Redis pub/sub"]
  Chat --> DynamoDB["DynamoDB chat tables"]
{{< /mermaid >}}

Kiến trúc cơ sở cũng xác định hướng chuyển đổi lên đám mây ban đầu: đóng gói backend và dịch vụ chat chạy dài hạn trong container, chuyển dữ liệu quan hệ bền vững sang PostgreSQL/RDS, dùng DynamoDB cho bản ghi hội thoại, dùng Redis để phân phối sự kiện thời gian thực, đồng thời chuẩn bị ứng dụng cho container và CI/CD.

## Vấn đề và giải pháp

| Vấn đề | Nguyên nhân gốc | Giải pháp | Trạng thái |
|---|---|---|---|
| Ảnh chụp mã nguồn đầu tiên chứa phạm vi mã ứng dụng và thành phần phụ thuộc được sinh tự động quá rộng. | Commit ban đầu đưa toàn bộ nền tảng vào một commit lớn. | Các công việc sau đó tách tài liệu, tập lệnh và trách nhiệm thời gian chạy thành các đường dẫn rõ ràng hơn. | Hoàn thành |
| Dự án ban đầu còn thành phần cơ sở dữ liệu Node liên quan đến Prisma trong khi backend dùng SQLAlchemy/PostgreSQL. | Chiến lược cơ sở dữ liệu chuyển sang FastAPI, SQLAlchemy, Alembic và PostgreSQL. | Commit `ab60f7d` loại bỏ thành phần Prisma và ghi lại hướng triển khai EC2/RDS. | Hoàn thành |
| Cách khởi chạy cục bộ cần hỗ trợ nhiều quy trình phát triển. | Một lệnh duy nhất thuận tiện khi trình diễn, còn các lệnh terminal riêng dễ gỡ lỗi hơn. | Các commit `d3c1168` và `e43cc04` ghi lại cả hai cách khởi chạy. | Hoàn thành |

## Kết quả kiểm thử, build và triển khai

| Hạng mục | Kết quả | Minh chứng |
|---|---|---|
| Rà soát mã nguồn | Hoàn thành | `git show --stat 4e939cf` cho thấy backend, frontend, Docker, migration, kiểm thử và tài liệu được thêm trong commit đầu tiên. |
| Khởi chạy cục bộ | Hoàn thành một phần | Lịch sử có tập lệnh khởi chạy và hướng dẫn README nhưng không tìm thấy nhật ký terminal đã lưu. |
| Kiểm thử | Hoàn thành một phần | Có các tệp kiểm thử trong `backend/tests`; chưa tìm thấy kết quả kiểm thử của tuần 1. |
| Build | Hoàn thành một phần | Có Dockerfile và các tệp dự án Vite; chưa tìm thấy nhật ký build của tuần 1. |
| Triển khai | Đã lập kế hoạch | Tuần 1 chỉ xác định hướng triển khai, chưa đặt mục tiêu triển khai AWS. |

## Minh chứng

### Commit và yêu cầu kéo mã

| Commit | Mô tả | Minh chứng | Yêu cầu kéo mã |
|---|---|---|---|
| `4e939cf` | Tạo nền tảng ứng dụng ban đầu gồm backend, frontend, Docker Compose, migration và kiểm thử. | [Xem commit](https://github.com/Temp-orgo/AWS-Internship/commit/4e939cf0313e73fd915380987cce1a5a7c9728a0) | Minh chứng đang chờ |
| `5ab2924` | Bổ sung đối sánh CV bằng AI và cấu hình AWS RDS. | [Xem commit](https://github.com/Temp-orgo/AWS-Internship/commit/5ab2924ca69ed90f7ef5fe5a454578bfa888e9dc) | Minh chứng đang chờ |
| `ab60f7d` | Loại bỏ thành phần Prisma và ghi lại hướng triển khai EC2/RDS. | [Xem commit](https://github.com/Temp-orgo/AWS-Internship/commit/ab60f7d02c6c8fc73384198117625dea5973e24f) | Minh chứng đang chờ |
| `d3c1168` | Bổ sung cách khởi chạy toàn bộ hệ thống bằng một lệnh. | [Xem commit](https://github.com/Temp-orgo/AWS-Internship/commit/d3c1168cea4521823febf32e1fd9714e928d0ddc) | Minh chứng đang chờ |
| `e43cc04` | Ghi lại các lệnh khởi chạy riêng cho từng dịch vụ. | [Xem commit](https://github.com/Temp-orgo/AWS-Internship/commit/e43cc042d868b1ca5c18524d4735dca178f25043) | Minh chứng đang chờ |

### Nhật ký kiểm thử

Minh chứng đang chờ: không tìm thấy nhật ký kiểm thử cục bộ hoặc CI của tuần 1 trong kho mã nguồn.

### Nhật ký build

Minh chứng đang chờ: không tìm thấy nhật ký build Docker hoặc frontend của tuần 1 trong kho mã nguồn.

### Nhật ký triển khai

Không áp dụng cho tuần 1. Giai đoạn này bắt đầu lập kế hoạch triển khai; việc triển khai lên đám mây được dành cho các tuần sau.

## Kết quả trong tuần

Cuối tuần 1, tôi đã hoàn thành bản đồ service/phụ thuộc phục vụ phạm vi triển khai và xác định hướng container hóa, triển khai AWS ban đầu. Mã nguồn ứng dụng và các chức năng nền tảng là kết quả chung của nhóm 5 thành viên.

## Bài học rút ra

Bài học chính là kế hoạch triển khai phụ thuộc vào ranh giới thời gian chạy rõ ràng. Việc sớm tách API, chat, AI, dữ liệu quan hệ, cơ chế phát/nhận thời gian thực và lưu trữ tài liệu giúp công việc Docker, Kubernetes và AWS ở các tuần sau dễ phân tích hơn.

## Kế hoạch tuần tiếp theo

Tuần tiếp theo tập trung vào tính toàn vẹn dữ liệu và xử lý đồng thời: ràng buộc cơ sở dữ liệu, xử lý yêu cầu trùng, khóa chống lặp, lệnh quy trình có phiên bản và các kiểm thử chứng minh thao tác ghi đồng thời trả về xung đột có kiểm soát thay vì dữ liệu không nhất quán.
