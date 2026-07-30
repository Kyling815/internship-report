---
title: "Triển khai cơ sở dữ liệu"
date: 2024-01-01
weight: 6
chapter: false
pre: " <b> 5.6. </b> "
---

## Mục tiêu

Triển khai và kiểm chứng lớp dữ liệu (data layer) phục vụ ứng dụng Internship Application Tracker bao gồm: RDS PostgreSQL, ElastiCache Redis, các bảng DynamoDB cho dữ liệu chat, và bảng DynamoDB khử lặp sự kiện cho Lambda (idempotency table).

## Bối cảnh kiến trúc

Hệ thống tận dụng các kho dữ liệu khác nhau để giải quyết cho từng mô hình truy xuất chuyên biệt:

| Kho lưu trữ (Store) | Mục đích |
|---|---|
| RDS PostgreSQL | Lưu trữ người dùng, công ty, tin tuyển dụng, đơn xin việc, lịch sử thay đổi trạng thái quy trình, bản ghi tính bất biến, hàng đợi xử lý bất đồng bộ và bảng sự kiện outbox |
| ElastiCache Redis | Phục vụ kênh phát tán liên lạc pub/sub theo chuẩn Socket.IO giữa các pod trong cụm dịch vụ chat |
| Các bảng DynamoDB cho chat | Lưu trữ lâu dài thông tin người dùng tham gia chat, các nhóm hội thoại và nội dung tin nhắn |
| Bảng DynamoDB khử lặp (dedupe table) | Bịt rào bảo lưu tính bất biến cho Lambda consumer trong quá trình thụ thụ tin sự kiện SQS |
| S3 | Nơi quy giữ tệp file đính kèm cùng văn thư sự kiện lâu năm (được đề cập riêng trong các chương hạ tầng và frontend) |

## Triển khai PostgreSQL

Máy chủ cơ sở dữ liệu RDS trên production sở hữu danh xưng định danh `internship-prod-postgres`. PostgreSQL chịu trách nhiệm chốt giữ toàn bộ dữ liệu giao dịch cốt lõi và các hàng đợi công việc của worker cần bấu rào cống cơ sở dữ liệu.

Cần bằng chứng:

- thông số phân loại máy chủ DB instance class
- dung lượng đĩa được ban cấp
- tình trạng bật mã hóa lưu trữ
- thời gian bảo lưu sao lưu tự động (backup retention)
- thiết lập dự phòng qua Multi-AZ
- tên định nghĩa subnet group
- danh mục các ID thuộc về security group
- tình trạng khóa bảo vệ khỏi thao tác xóa (deletion protection setting)

Kiểm chứng:

```bash
aws rds describe-db-instances \
  --db-instance-identifier internship-prod-postgres \
  --region ap-southeast-1
```

Tra cứu cấu hình subnet groups:

```bash
aws rds describe-db-subnet-groups --region ap-southeast-1
```

## Bộ di cư Alembic (Alembic migrations)

Backend điều khiển tiến hóa cơ sở dữ liệu nhờ chuỗi tệp kịch bản Alembic nằm bên trong thư mục `backend/alembic/versions/`. Các mốc di cư quan trọng bao gồm:

| Migration | Mục đích |
|---|---|
| `0004_idempotency_records.py` | Tạo bảng chốt lưu bản ghi tính bất biến |
| `0005_idempotency_status_check.py` | Áp quy chuẩn kiểm tra giới hạn cho các rào trạng thái bất biến |
| `0006_job_application_versions.py` | Thêm trường quản lý phiên bản phục vụ khóa lạc quan (optimistic currency) |
| `0007_outbox_events.py` | Kiến thiết hạ tầng bảng transactional outbox |
| `0008_async_processing_jobs.py` | Tạo hàng đợi tác nghiệp bất đồng bộ |
| `1065bcf66cb9_0007_add_rerank_run_tables.py` | Khai sinh bộ bảng vận hành tính điểm xếp hạng lại (Rerank run tables) |

Tiến trình triển khai EKS ban khải ra một Kubernetes Job với mã định danh `backend-migrate` thi thố dòng lệnh:

```bash
alembic upgrade head
```

Thao tác kiểm nghiệm thủ công cẩu trực tiếp ngay tại gốc thư mục repo mã nguồn:

```bash
cd backend
alembic current
alembic heads
alembic history --verbose
```

Nghiêm răn: Tuyệt đối cấm thao diễn tự ý gõ chạy migration thẳng vào mạn cọc production trừ phi mốc khung giờ triển khai đi kèm kịch bản tháo rỡ sa lui (rollback plan) đã vỗ tay nhận được cái gật đầu phê duyệt.

## Cấu hình kết nối PostgreSQL

Tiến trình ban bố production nạp chuỗi thông số biến cấu hình `DATABASE_URL` tới qua cơ quan rào bảo mật Kubernetes Secret `internship-secrets`. Nội sung thực chuỗi kết nối lưu mang mật mã truy cập cẩn khôn, bởi thế tôi chối cự từ việc phơi văn xuất chuỗi ra khỏi bản báo cáo tài liệu này.

Kiểm chứng tình hình an bấu trên Kubernetes mà không đả thương tới giá trị bí ẩn:

```bash
kubectl get secret internship-secrets -n internship
kubectl describe secret internship-secrets -n internship
```

Luồng kiểm định sức khỏe readiness từ phía backend tiến hành thẩm ra tình hình an nộ của PostgreSQL thông qua lệnh tra khảo `SELECT 1`:

```bash
kubectl port-forward service/backend 18080:8000 -n internship
curl -fsS http://127.0.0.1:18080/health/ready
```

Kết quả trả về mong đợi:

```json
{"status":"ready","service":"internship-api","dependencies":{"postgres":true}}
```

## ElastiCache Redis

Cụm máy nhân bản Redis trên production giữ thẻ tên `internship-prod-redis`, đồng thời được tôi tra rà chứng nghiệm thọ trạng thái `available` trọn bãi trong bằng chứng Tuần 8. Cụm Redis đứng đằng sau bảo kê cho bộ giao diện Socket.IO adapter nhằm giúp luồng sự kiện đàm thoại thả ga reo vui lan tỏa giữa các pod phục vụ chat chạy song hành.

Kiểm chứng:

```bash
aws elasticache describe-replication-groups \
  --replication-group-id internship-prod-redis \
  --region ap-southeast-1
```

Dịch vụ chat tiếp thu thông ký biến `REDIS_URL` tự trong hòm bí mật `internship-secrets`. Tại production, Redis đương nhiên bắt buộc nằm gọn trong cự ly bắt sóng từ các pod chat và khẩn kiêng mọi khe nứt rò hở tuột cọc hướng ra không gian public ngoài kia.

## Các bảng DynamoDB cho chat

Dịch vụ chat phụ trách quán cọc 3 bàn lưu trữ cơ sở trên DynamoDB:

- `ChatUsers`
- `ChatGroups`
- `ChatMessages`

Tôi đã tự hào thẩm định toàn bộ 3 bàn chứa này ngạo ngễ rạng trạng thái `ACTIVE` kiên cố trong bộ tài liệu chứng cứ Tuần 8. Điểm gọi trích soát sức khỏe readiness của dịch vụ chat gắn kiếp ràng buộc vào sự hưng thịnh đồng loạt từ phía cả DynamoDB lẫn Redis:

```bash
kubectl port-forward service/chat-service 18081:3000 -n internship
curl -fsS http://127.0.0.1:18081/health/ready
```

Chuỗi tin đáp trả như mong đợi ngay thời khắc muôn rào phụ thuộc đều xanh mướt:

```json
{"status":"ready","dependencies":{"redis":true,"dynamodb":true}}
```

Kiểm chứng DynamoDB:

```bash
aws dynamodb describe-table --table-name ChatUsers --region ap-southeast-1
aws dynamodb describe-table --table-name ChatGroups --region ap-southeast-1
aws dynamodb describe-table --table-name ChatMessages --region ap-southeast-1
```

## Bảng DynamoDB khử lặp cho Lambda

Tiến trình Lambda chuyên tiêu đè tin từ SQS gặm sử dụng bàn lưu `InternshipLambdaEventDedupe` để nạp chốt trữ vĩnh cửu những khóa `eventId` vừa múa việc xong trôi flowing over. Trục cơ quan này dựng thành hào cống chở che trọn bên sườn Lambda trước cảnh bẽ hão tin lặp vô ý trồi sa sang theo tự tính từ hạ tầng SQS.

Kiểm chứng:

```bash
aws dynamodb describe-table \
  --table-name InternshipLambdaEventDedupe \
  --region ap-southeast-1
```

Đối chiếu dấu tích từ lời gõ khói (smoke test) thành quả thu được:

```bash
aws dynamodb get-item \
  --table-name InternshipLambdaEventDedupe \
  --key '{"eventId":{"S":"lambda-smoke-fixed-1785220478"}}' \
  --region ap-southeast-1
```

Tài liệu báo cáo cấm được cho phép bô lô phô vãng lời tự xưng ra lệnh thi thố cú rẽ trên, trừ phi trích đoạn chuỗi tệp đầu lời giải được xuất kho bọc bồi vào kho tàng bằng chứng.

## Thiết kế đảm bảo tính nhất quán dữ liệu

| Vấn đề (Concern) | Cơ chế xử lý |
|---|---|
| Trùng lặp lượt đăng ký tài khoản | Vận dụng ràng buộc unique trên PostgreSQL đi đôi thuật khéo trả mã lỗi HTTP 409 |
| Nộp trượt nấc 2 đơn trùng ứng tuyển cùng lúc | Cọc ràng buộc độc nhất `(job_posting_id, candidate_user_id)` quy theo tiêu chuẩn `Idempotency-Key` |
| Bồi đè dữ liệu cũ kỹ lạc hậu lúc HR thao tác cập nhật | Khóa `expectedVersion` kết hợp chiêu update cõng theo điều kiện ràng rẽ |
| Tiến trình tác nghiệp AI hao kéo dài gian phi | Cất bảng lưu bão bốc `async_processing_jobs` mang kề các quy ước thuê tác quyền (leases) và giới rèn lượt tự phục hồi retry |
| Trượt rách sẩy tháo thất ngạc lời kêu gửi sự kiện outbox | Trữ vào bàn `outbox_events` trói chung một cơ quan giao dịch transaction trúng nhịp với biến múa dữ liệu nghiệp vụ |
| Nhận thông điệp bồi trùng lặp từ kênh hàng đợi SQS | Lệnh ghi theo điều kiện trên DynamoDB của Lambda giục vây cọc theo trường trường dữ liệu `eventId` |
| Sẩy lặp trát mồi tin nhắn đàm thoại sau cọc retry từ phía người đàm | Chiêu khởi nặn dòng mới có điều kiện trên DynamoDB ôm sát chuỗi định danh con cọc `clientMessageId` |

## Các lệnh kiểm chứng

Tra soát tình thế cấu trúc tập thông tin cấu hình phục vụ luồng cất dữ liệu bên trong cụm Kubernetes:

```bash
kubectl get configmap internship-config -n internship -o yaml
kubectl get secret internship-secrets -n internship
kubectl get job backend-migrate chat-init -n internship
kubectl logs job/backend-migrate -n internship
kubectl logs job/chat-init -n internship
```

Tra cứu hiện trạng bàn bảng cơ sở thông qua điểm rà sức khỏe:

```bash
kubectl rollout status deployment/backend -n internship --timeout=300s
kubectl rollout status deployment/chat-service -n internship --timeout=300s
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/api/health/ready
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/chat/health/ready
```

## Kết quả mong đợi

- Tác vụ `backend-migrate` cắm phơi nhãn hoàn trọn thành công rực rỡ.
- Trạm khảo sát sức khỏe sẵn lòng của backend xướng trả cọc phụ thuộc PostgreSQL bằng giá trị `true`.
- Điểm tra soát sức khỏe của dịch vụ chat reo vui trả giá trị cọc Redis cùng DynamoDB là `true`.
- Toàn thể các bàn chứa chat trên DynamoDB tự tại trụ ở trạng thái `ACTIVE`.
- Nhóm nhân bản thuộc dịch vụ Redis duy dãn khang trang ngả theo cọc `available`.
- Bàn khử lặp Lambda nghiêng giỗ thọ hình an tọa, sẵn lòng trợ thủ trót lọt các lượt thi triển ghi có điều kiện.

## Các lỗi thường gặp

| Triệu chứng | Nguyên nhân gốc rễ | Hướng khắc phục |
|---|---|---|
| Thẩm rà sức khỏe từ backend gào khóc thất bại | Biến `DATABASE_URL` cài sai thảm lật, lỗi nghẽn kẹt tường rào security group hoặc tiến trình migration lâm nạn | Vào sâu thanh rà tệp log của backend và chuỗi cấu hình security groups bên tài nguyên RDS |
| Trình Alembic chao chát phi cớ không rã dịch ra URL | Vướng trật trượt trong phép nhồi biến interpolation thuộc shell hoặc file secret ngự trúng định dạng gieo hãm sai lệch | Đem khóa URL an trú cẩn mẫn vào trong một tệp secret an ninh và cấm tha buông cống gõ in chuỗi trần ra |
| Điểm gọi sức khỏe dịch vụ chat gầm rầm cọc mác `not_ready` | Trục bộ Redis adapter hoặc kịch bản khai quan khởi tạc DynamoDB trượt dốc | Rà kỹ nhật ký tệp log thuộc pod `chat-service` đi cùng tiến trình thợ job `chat-init` |
| Tác vụ Lambda dính lặp sự kiện thi thố gửi đi mail cảnh báo 2 lần | Bỏ sẩy quên béng việc chốt ghi vào bàn khử lặp hoặc khi ghi khuyết trống tham số rào điều kiện | Sửa lệnh cho tuân lệnh nghiêm cấm ghi theo cơ quan có điều kiện DynamoDB trói sát trường biến `eventId` |
| Các hàng tin nằm trong outbox trơ lỳ gan chây bám ngục trạng thái pending | Tiến trình dispatcher khốn quẫn bất lực chẳng vãng được cống gửi qua hàng đợi SQS | Đối soát đường URL biến `OUTBOX_QUEUE_URL`, dải quyền hạn bấu theo IAM IRSA SQS, cùng nhật ký log từ dispatcher |

## Xử lý sự cố (Troubleshooting)

Kịp thời ứng trói cụm lệnh bọc lót bên dưới mỗi lúc giáp mặt sự cố:

```bash
kubectl logs deployment/backend -n internship --tail=200
kubectl logs deployment/chat-service -n internship --tail=200
kubectl logs deployment/backend-outbox-dispatcher -n internship --tail=200
kubectl logs deployment/backend-processing-worker -n internship --tail=200
aws rds describe-db-instances --db-instance-identifier internship-prod-postgres --region ap-southeast-1
aws elasticache describe-replication-groups --replication-group-id internship-prod-redis --region ap-southeast-1
aws dynamodb describe-table --table-name ChatMessages --region ap-southeast-1
```

## Kết luận

Toàn cảnh móng rào cho cơ sở dữ liệu nghiêng còi ăn chốt thông quan ngay thời khắc các luồng di cư cơ quan PostgreSQL thành tài hoàn tất, cụm nhớ Redis nghênh tay cất sóng vui cười với đoàn pod chat, các bàn dữ liệu DynamoDB ngạo bạt trạng thái active, bàn khử lặp Lambda cấu định minh chánh và cọc kiểm định sức khỏe toàn dải ứng dụng hoan thả tin mừng êm xuôi băng rẽ qua khắp các cung đường định hướng triển khai.
