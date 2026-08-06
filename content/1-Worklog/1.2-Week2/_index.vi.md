---
title: "Nhật ký tuần 2"
date: 2024-01-01
weight: 2
chapter: false
pre: " <b> 1.2. </b> "
---

# Tuần 2 - Kiểm soát concurrency và data integrity

## Mục tiêu

Trong nhóm 5 thành viên, mục tiêu tuần 2 của tôi là review các yêu cầu concurrency và data integrity ảnh hưởng đến môi trường nhiều replica. Tôi hỗ trợ thành viên backend và chat kiểm tra idempotency, version check và database constraint trước khi đưa hệ thống lên Kubernetes.

## Phần việc cá nhân

| Trạng thái | Phần việc được phân công | Cơ sở minh chứng |
|---|---|---|
| Hoàn thành | Phân tích concurrent write khi nhiều backend pod xử lý đồng thời. | `docs/architecture/concurrency-policy.md`. |
| Hoàn thành | Đóng góp góc nhìn triển khai vào chính sách optimistic/pessimistic UI. | `docs/architecture/concurrency-policy.md` và `docs/frontend/COMMAND_MUTATION_POLICY.md`. |
| Hoàn thành | Review cơ chế idempotency do thành viên backend triển khai cho thao tác ứng tuyển. | Service, router và migration `0004_idempotency_records.py`. |
| Hoàn thành | Review workflow command dùng `expectedVersion` trong môi trường nhiều pod. | Optimistic concurrency service, workflow command và các router liên quan. |
| Hoàn thành | Phối hợp với thành viên chat kiểm tra hành vi retry và chống ghi trùng. | Chat repository và concurrency test. |

## Triển khai kỹ thuật

Kiểm soát đồng thời được triển khai ở tầng cơ sở dữ liệu và hợp đồng API:

- Các ràng buộc duy nhất của PostgreSQL ngăn bản ghi người dùng, công ty, hồ sơ ứng tuyển và chống lặp bị trùng.
- `Idempotency-Key` được chấp nhận khi ứng viên nộp hồ sơ và khi gọi một số lệnh quy trình.
- Dùng lại cùng khóa chống lặp với cùng dữ liệu đầu vào sẽ phát lại phản hồi đã lưu.
- Dùng lại cùng khóa với dữ liệu đầu vào khác sẽ trả về mã `409` và lỗi `idempotency_key_reused`.
- Các lệnh sửa công việc và hồ sơ ứng tuyển của nhân sự yêu cầu `expectedVersion`.
- Cập nhật dựa trên phiên bản cũ trả về phản hồi `409 Conflict` có kiểm soát.
- Khi thử gửi lại tin nhắn, dịch vụ chat dùng mã tin nhắn phía máy khách có tính xác định và phép ghi có điều kiện của DynamoDB để tránh trùng tin nhắn logic.

Luồng xử lý xung đột:

{{< mermaid >}}
sequenceDiagram
  participant C as Client
  participant API as FastAPI backend pod
  participant DB as PostgreSQL
  C->>API: POST /jobs/{id}/apply + Idempotency-Key
  API->>DB: reserve scoped idempotency record
  alt new request
    API->>DB: insert application, documents, history
    API->>DB: complete idempotency record
    API-->>C: 200/201 application response
  else exact replay
    DB-->>API: completed stored response
    API-->>C: stored response + Idempotency-Replayed
  else payload mismatch or duplicate business conflict
    API-->>C: 409 Conflict
  end
{{< /mermaid >}}

## Vấn đề và giải pháp

| Vấn đề | Nguyên nhân gốc | Giải pháp | Trạng thái |
|---|---|---|---|
| Đăng ký hoặc tạo công ty trùng có thể làm lộ lỗi cơ sở dữ liệu chưa kiểm soát. | Đã có hoặc cần bổ sung ràng buộc duy nhất, đồng thời phải ánh xạ lỗi tường minh. | Lỗi toàn vẹn được hoàn tác và chuyển thành `409 Conflict`. | Hoàn thành |
| Trình duyệt hoặc mạng có thể khiến yêu cầu ứng tuyển được gửi lại. | Yêu cầu thứ hai có thể đến pod backend khác trước khi phản hồi đầu tiên quay về. | Bản ghi chống lặp theo phạm vi lưu hàm băm yêu cầu và dữ liệu phản hồi. | Hoàn thành |
| Cập nhật quy trình nhân sự có thể dùng dữ liệu cũ khi hai người cùng thao tác. | Cập nhật thông thường không biết máy khách đã nhìn thấy phiên bản mới nhất hay chưa. | Lệnh yêu cầu `expectedVersion` và dùng cập nhật có điều kiện. | Hoàn thành |
| Thử gửi lại có thể làm trùng tin nhắn thời gian thực. | Cơ chế thử lại qua Socket và REST có thể gửi lại cùng một tin nhắn logic. | Kho chat dùng định danh tin nhắn có tính xác định và bỏ qua phát lại khi nhận bản trùng. | Hoàn thành |

## Kết quả kiểm thử, build và triển khai

| Hạng mục | Kết quả | Minh chứng |
|---|---|---|
| Kiểm thử đồng thời của backend | Hoàn thành một phần | Có các tệp kiểm thử: `backend/tests/test_apply_idempotency.py`, `backend/tests/test_apply_idempotency_postgres.py`, `backend/tests/test_optimistic_concurrency.py` và `backend/tests/test_optimistic_concurrency_postgres.py`. Kết quả chạy hiện tại đang chờ. |
| Kiểm thử đồng thời của chat | Hoàn thành một phần | Có tệp `chat-service/tests/chatRepository.concurrency.test.js`. Kết quả chạy hiện tại đang chờ. |
| Hành vi xung đột của API | Đã triển khai | Mã nguồn xử lý tường minh mã `409` cho phiên bản cũ, ứng tuyển trùng và dùng lại khóa chống lặp. |
| Triển khai | Đã lập kế hoạch | Tuần này tập trung bảo đảm tính đúng đắn trước khi triển khai. |

## Minh chứng

### Commit và yêu cầu kéo mã

| Commit | Mô tả | Minh chứng | Yêu cầu kéo mã |
|---|---|---|---|
| `0f9e7f2` | Bổ sung outbox quy trình backend, bản ghi chống lặp, công cụ đồng thời lạc quan, nền tảng xử lý bất đồng bộ và kiểm thử. | [Xem commit](https://github.com/Temp-orgo/AWS-Internship/commit/0f9e7f2aed730153e905df0700fc3401f8957b21) | Minh chứng đang chờ |
| `5326cb0` | Củng cố xử lý đồng thời của kho chat và bổ sung kiểm thử. | [Xem commit](https://github.com/Temp-orgo/AWS-Internship/commit/5326cb0ad12bf5e311236469e5c2b90c7fe20b6e) | Minh chứng đang chờ |
| `77faab4` | Tích hợp hợp đồng quy trình và xử lý vào công cụ API cùng luồng giao diện frontend. | [Xem commit](https://github.com/Temp-orgo/AWS-Internship/commit/77faab4a919405beef1865fc06a106b0289a3310) | Minh chứng đang chờ |
| `5041f84` | Sửa các khẳng định bị lỗi trong kiểm thử đồng thời lạc quan. | [Xem commit](https://github.com/Temp-orgo/AWS-Internship/commit/5041f84600390724c4760c51da499592b1cf6104) | Minh chứng đang chờ |

### Nhật ký kiểm thử

Minh chứng đang chờ: đính kèm kết quả thực tế từ các lệnh như:

```bash
cd backend
python -m pytest tests/test_apply_idempotency.py tests/test_optimistic_concurrency.py
python -m pytest -m postgres tests/test_apply_idempotency_postgres.py tests/test_optimistic_concurrency_postgres.py
```

### Nhật ký build

Không áp dụng cho nhiệm vụ chính của tuần 2. Không tìm thấy sản phẩm build riêng cho giai đoạn này.

### Nhật ký triển khai

Không áp dụng cho tuần 2. Tính năng được thiết kế an toàn trước khi mở rộng backend trên Kubernetes.

## Kết quả trong tuần

Kết quả cá nhân tuần 2 là bản review theo góc nhìn triển khai đối với chính sách concurrency của nhóm và hành vi khi chạy nhiều replica. Phần triển khai backend và chat thuộc trách nhiệm của các thành viên phụ trách hai component này.

## Bài học rút ra

Cân bằng tải dịch vụ không tuần tự hóa thao tác ghi. Tính đúng đắn phải được bảo đảm tại ranh giới lưu trữ và giao dịch, sau đó thể hiện rõ qua mã phản hồi API và hành vi giao diện.

## Kế hoạch tuần tiếp theo

Xây dựng outbox giao dịch và các tầng xử lý bất đồng bộ để thay đổi nghiệp vụ đã commit có thể kích hoạt công việc phía sau một cách tin cậy mà không giữ yêu cầu API chính chờ lâu.
