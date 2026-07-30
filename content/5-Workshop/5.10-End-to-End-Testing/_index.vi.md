---
title: "Kiểm thử đầu - cuối (E2E Testing)"
date: 2024-01-01
weight: 10
chapter: false
pre: " <b> 5.10. </b> "
---

## Mục tiêu

Xây dựng và định nghĩa trọn bộ danh sách ca kiểm thử nghiệm thu (acceptance test set) cho hệ thống Internship Application Tracker đã triển khai thực tiễn, đồng thời tường minh ghi nhận các kết quả đã được rà kiểm chứng, các tính năng đã cài đặt nhưng còn chờ minh chứng lúc chạy (runtime evidence), các hạng mục được đề xuất hay những thành phần chưa hoàn thiện.

## Bối cảnh kiến trúc

Các kịch bản kiểm thử E2E buộc phải bao quát trọn mạch truy cập công cộng toàn trình:

```text
Trình duyệt (Browser) -> CloudFront -> S3 hoặc ALB -> Các workload EKS -> Các dịch vụ AWS được quản lý
```

Song song, các luồng kiểm định phải thâu trượt qua dải tác vụ xử lý bất đồng bộ:

```text
Backend -> Bảng PostgreSQL outbox -> Tiến trình dispatcher -> SQS -> Lambda -> Bảng DynamoDB khử lặp dedupe -> Kho lưu trữ S3 archive -> Dịch vụ mail SES
```

## Định nghĩa các trạng thái kiểm thử

| Trạng thái | Ý nghĩa |
|---|---|
| Đã kiểm chứng (Verified) | Bằng chứng lúc chạy (runtime evidence) trong hồ sơ Tuần 8 hoặc chuỗi tài liệu trích cẩu từ mạn production chứng minh thuyết phục thành quả thực thi |
| Đã triển khai, cần xác minh (Implemented, verification required) | Hồ sơ mã nguồn hoặc hệ manifests đã gài đặt chức năng, nhưng tài liệu minh chứng khi chạy thực tại cõi production vẫn còn vắng hụt |
| Đề xuất (Proposed) | Các kịch bản kiểm thử hoặc giải pháp rào cản mang tính tiến cử, chưa có minh chứng áp dụng rõ ràng |
| Chưa hoàn thành (Not completed) | Tính năng chưa được dệt tạo hoặc chưa đạt độ hoàn vãn trong bộ bằng chứng lưu chiểu hiện có |

## Bảng kiểm thử nghiệm thu (Acceptance test table)

| ID | Ca kiểm thử (Test case) | Đầu vào hoặc lệnh kiểm thử | Kết quả mong đợi | Trạng thái bằng chứng |
|---|---|---|---|---|
| TC01 | Kiểm định frontend từ CloudFront | `curl -I https://dhm2rz5nmsibj.cloudfront.net/` | CloudFront trả về dữ liệu phản hồi tiêu đề của frontend | Đã triển khai, cần xác minh |
| TC02 | Điểm tra sức khỏe backend qua CloudFront | `curl -fsS https://dhm2rz5nmsibj.cloudfront.net/api/health/ready` | Trả về JSON sức khỏe backend, xác nhận cọc phụ thuộc PostgreSQL đạt true | Đã triển khai, cần xác minh |
| TC03 | Điểm tra sức khỏe chat qua CloudFront | `curl -fsS https://dhm2rz5nmsibj.cloudfront.net/chat/health/ready` | Trả về JSON sức khỏe dịch vụ chat, xác nhận hai trụ Redis và DynamoDB đạt true | Đã triển khai, cần xác minh |
| TC04 | Bước gạt liên lạc Socket.IO (handshake) | Trình duyệt hoặc máy khách Socket.IO gõ kết nối vào đường rẽ `/socket.io` | Kết nối socket cất lập thuận buồm băng qua ranh rào CloudFront lẫn cổng ALB | Đã triển khai, cần xác minh |
| TC05 | Đăng ký tài khoản | Nặn mới một thông tin người ứng tuyển (candidate) hoặc quản lý HR | Tài khoản thọ sinh thành tài, hoặc bị từ chối trả về mã HTTP 409 nếu địa chỉ mail dính trùng | Đã triển khai, cần xác minh |
| TC06 | Đăng nhập hệ thống | Dùng chuỗi thông tin đăng ký xác thực | Gặt về thẻ phiên làm việc JWT và điều hướng lọt trúng ranh trang tương ứng quyền hạn | Đã triển khai, cần xác minh |
| TC07 | Khởi tạo công việc tuyển dụng | HR ra tay ban bố vị trí việc làm mới | Hồ sơ tin được lưu trọ kiên trung trong PostgreSQL đi kèm số phiên bản | Đã triển khai, cần xác minh |
| TC08 | Nộp hồ sơ ứng tuyển (Application submission) | Ứng viên gửi đơn xin việc cho một tin tuyển dụng đang mở | Toàn bộ dữ liệu đơn, tệp văn kiện, lịch sử quy trình, sự kiện outbox và tác vụ xử lý hàng đợi (processing job) thảy đều chốt vãn trọn trong 1 lượt transaction | Đã triển khai, cần xác minh |
| TC09 | Kiểm soát chống nộp đơn trùng lặp | Thọ nộp đúp 2 lần cùng một vị trí với 1 tài khoản | Bị từ chối gay gắt qua mã `409` cho án nộp đơn trùng, hoặc được hệ thống xử lý bất biến mĩ mãn | Đã triển khai, cần xác minh |
| TC10 | Tải lên tài liệu CV | Gửi đơn kèm đệm theo file văn kiện/CV | Tệp nhở cẩu an cư vào lòng S3 (hay kho dịch vụ lưu trữ trỏ cấu hình), còn chuỗi thông số metadata trú vào lòng PostgreSQL | Đã triển khai, cần xác minh |
| TC11 | Tác tạo hàng đợi công việc xử lý | Kích nổ yêu cầu đọc hiểu CV/job | Nặn ra một dòng thông số mới cất tại bảng `async_processing_jobs` và trân lộ trạng thái rành mạch | Đã triển khai, cần xác minh |
| TC12 | Xử lý AI hoàn tất | Worker gửi còi gọi tới pod `ai-service` và trạm cất suy đoán SageMaker endpoint | Dữ liệu CV/job đã giải mác hoặc kết quả tính điểm độ khớp hoan khải được ghim bão thọ thêu bền bỉ | Đã triển khai, cần xác minh |
| TC13 | Hội thoại chat giữa 2 phía khách | Buông lời tin nhắn riêng tư hoặc xướng vào cả nhóm đàm | Phía xướng gặt trả lại chứng chỉ phát đi ACK; bên phía nhở thâu lọt tin lập tức trong thì hiện thực (realtime) | Đã triển khai, cần xác minh |
| TC14 | Bền lâu cất dữ liệu hội thoại (Chat persistence) | Re-load nạp lại luôn mạch lịch sử đàm thoại | Cỗ dữ liệu DynamoDB ung dung trao trả nội sung các tin nhắn đã ghi trước đó | Đã triển khai, cần xác minh |
| TC15 | Rà tải nặn lại pod chat và thọ tái kết nối | Cho khởi búng gục restart một pod chat giữa chừng khi phiên kết nối đang mở | Socket khôn ngoan tự tái nối tiếp và cự tuyệt hoàn toàn việc bồi chốt tạo lặp lại tin nhắn trong cơ quan retry | Đã triển khai, cần xác minh |
| TC16 | Kiểm nghiệm mạch thông cõi PostgreSQL | Điểm gọi của backend `/health/ready` | Gặt về chuỗi `postgres: true` | Đã triển khai, cần xác minh |
| TC17 | Sức khỏe cõi Redis | Điểm rà của chat `/health/ready` | Gặt về cọc `redis: true` | Trạng thái cất vãn của Redis thực thế thọ chứng qua minh chứng Tuần 8; trích chuỗi rà từ điểm endpoint tiếp vãng trọ vai hữu hảo |
| TC18 | Tình thế vận hanh các bảng DynamoDB | Dùng lệnh `describe-table` soi rà chuỗi bảng chat | Hiển tuệ mác `ACTIVE` đồng loạt cho 3 ranh `ChatUsers`, `ChatGroups`, `ChatMessages` | Đã xác minh trọn từ hồ sơ minh chứng DynamoDB trong Tuần 8 |
| TC19 | Bộ chuyển tin sự kiện Outbox dispatcher | Thám xét cọc triển khai dispatcher và đọc kỹ nhật ký log | Trình dispatcher tựu chung thọ chiết rỗng bãi tin trong PostgreSQL rồi trút bạt lọt cống qua SQS | Workload vãn gác chứng nhận an cư qua hồ sơ EKS Tuần 8; riêng khâu gửi tin sự kiện khẩn hoan chờ còi xác minh |
| TC20 | Hàng đợi sự kiện SQS | Trích kiểm cộc hàng đợi `internship-prod-outbox` | Thông điệp vào bãi gạt khóa bảo mật SSE, bấu mốc thời hạn ẩn visibility timeout cùng quy chuẩn lưu lâu dài retention | Hàng đợi chủ lực cùng bàn lỗi DLQ thọ vãnh chứng từ hồ sơ SQS Tuần 8 |
| TC21 | Xử lý trên Lambda | Thả cẩu test thử tin `lambda-smoke-fixed-1785220478` | Lambda gặt thông điệp, thiếp múa mĩ mãn và gặt xướng kết quả `EMAIL_SENT` | Hàm thi hành và log group thọ chốt xác tín 1 phần; bằng chứng ra lệnh thi cẩu thực thọ hoàn thiện vẫn còn trong mạn ráo đón |
| TC22 | Tác vụ báo thư tín qua SES | Sử dụng lại cọc tin khói thử ở kịch bản trước | Thư bồi cảnh báo đắc thắng mang nhãn chốt `EMAIL_SENT` | Cần xác minh thêm; minh chứng của Tuần 8 chả ráo phô vãi chớp bằng việc thư cẩu đi tót lọt qua SES |
| TC23 | Bãi chôn văn thư sự kiện S3 archive | Tra kiếm cộc định danh archive key | Bồi xác minh sự thọ mang của tệp `outbox-archive/2026/07/28/lambda-smoke-fixed-1785220478.json` | Cần xác minh; cọc bằng chứng Tuần 8 không ghi mác hiển phơi việc sinh ra tệp lưu vào bãi archive này |
| TC24 | Tính bất biến (idempotency) của DynamoDB | Kích cho chạy rà một mã event ID bị cẩu giục đúp đè | Tin nhắn trùng lập tức bị cỗ rào cản bảng dedupe gạt xô đi nhã nhặn | Đã triển khai, cần xác minh |
| TC25 | Nhận thông tin bồi đè trên Lambda | Ấn gửi cẩu tiếp tục trùng một con số event ID | Khảng từ khước tiệm tiến nặn bục ra tác vụ phụ thứ hai | Đã triển khai, cần xác minh |
| TC26 | Xử trí bãi thi cõi DLQ | Tạo giả lập một ca xử lý lỗi consumer bồi tụ trong không gian kiểm nghiệm an nộ | Thông điệp sau thời kỳ nỗ lực thu hồi (max receive count) khôn ngoan bẻ cẩu lao xuống bãi lỗi `internship-prod-outbox-dlq` | Đề xuất |
| TC27 | Minh bạch luân điều rẽ trên CloudFront | Thao soát bảng cấu hình cọc distribution behaviors | Rãnh mặc định hướng trúng S3; dải `api`, `/chat`, và `/socket.io` rẽ hướng trúng mạn ALB | Xác tín bán phần dựa vào quan sát bấu theo CloudFront metrics; hồ sơ tải cấu hình behavior hoặc cẩu múa trực quan trình duyệt vẫn khẩn khoản rước đợi |
| TC28 | Frontend bóc xóa hoàn tàn ranh khỏi EKS | Tra `kubectl get deployment frontend -n internship` | Hưởng mác Không tìm thấy tài nguyên (Not found) | Bán phần chốt duyệt qua quy hoạch kiến trúc và minh chứng EKS workload; lệnh cẩu kiểm trần ra chữ minh văn vẫn luôn sắm vị trí trọng kính |

## Tập lệnh rà soát thủ công

Lệnh gọi kiểm tra dưới đây đòi hỏi khắt khe tài khoản thực thi phải quy thọ ủy quyền hợp pháp bên trong ranh giới cõi production:

```bash
aws eks update-kubeconfig --name internship-prod --region ap-southeast-1
kubectl get deployments,pods,svc,endpoints,hpa,pdb -n internship -o wide
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/api/health/ready
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/chat/health/ready
```

Thao tác kiểm tra cọc dịch vụ mạng bên chiến tuyến AWS:

```bash
aws dynamodb describe-table --table-name ChatUsers --region ap-southeast-1
aws dynamodb describe-table --table-name ChatGroups --region ap-southeast-1
aws dynamodb describe-table --table-name ChatMessages --region ap-southeast-1
aws elasticache describe-replication-groups --replication-group-id internship-prod-redis --region ap-southeast-1
aws sqs get-queue-url --queue-name internship-prod-outbox --region ap-southeast-1
aws lambda get-function --function-name internship-outbox-handler --region ap-southeast-1
aws sagemaker describe-endpoint --endpoint-name internship-qwen3-4b --region ap-southeast-1
```

## Một số mẫu lệnh kiểm thử nhanh

Điểm gọi rà sức khỏe mạn backend:

```bash
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/api/health/ready
```

Điểm gọi rà sức khỏe mạn dịch vụ chat:

```bash
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/chat/health/ready
```

Rà soát tình trạng sẵn gặt của dịch vụ AI thông qua cầu cống chuyển tiếp (port-forward):

```bash
kubectl port-forward service/ai-service 18082:8010 -n internship
curl -fsS http://127.0.0.1:18082/health/ready
```

## Tra soát kết quả trên cơ sở dữ liệu

Nghệ múa quy ước cản bãi cấm bục vãi mọi mật mã tài khoản cõi CSDL hay trường tin mang dữ liệu riêng tư của cá nhân ra không gian chung. Ưu việt áp dụng các cánh cổng API nghiệp vụ, nhật ký migration hay bảng số liệu trích tổng quát để thao khảo muôn kịch bản rà tra.

Một bộ chuỗi lệnh tra cứu thọ chuẩn an nộ khi thao diễn thẳng trên cọc production:

```bash
kubectl logs job/backend-migrate -n internship --tail=100
kubectl logs deployment/backend-processing-worker -n internship --tail=100
kubectl logs deployment/backend-outbox-dispatcher -n internship --tail=100
```

## Tra soát kết quả lưu trữ

Kho hòm lưu trữ của frontend:

```bash
aws s3 ls s3://internship-prod-frontend-<AWS_ACCOUNT_ID>/ --region ap-southeast-1
```

Bãi an ngụ văn thư sự kiện lâu năm:

```bash
aws s3 ls s3://internship-prod-uploads-<AWS_ACCOUNT_ID>/outbox-archive/2026/07/28/ --region ap-southeast-1
```

## Tra soát nhật ký CloudWatch Logs

Nhật ký của hàm Lambda:

```bash
aws logs tail /aws/lambda/internship-outbox-handler --since 1h --region ap-southeast-1
```

Chuỗi danh sách định danh cọc CloudWatch log groups gắn đệm cùng các workload trên EKS khẩn nài minh chứng từ kịch bản thi gom nhật ký (log shipping configuration) trước khi hoan khải liệt rãnh là đã vinh vãng cài đặt.

## Kết quả mong đợi

Toàn bãi nền tảng ứng dụng nghiêng còi ăn trát qua khâu nghiệm thu múa diễn (demonstration) ngay thềm khi muôn cọc khảo sát sức khỏe công cộng trọng yếu bão khải thông, khối workload bên cõi EKS hô hào trạng thái Ready, dàn tài nguyên hạ tầng DynamoDB/Redis/SQS/Lambda/SageMaker rạng ngời available, đi kèm dải minh chứng trút ra thực thụ cho kịch bản khói Lambda bao vây trọn khâu tiếp xử sự kiện, nén tệp archive và mác cất thành bại gửi mail.

## Các lỗi thường gặp

| Triệu chứng | Nguyên nhân khả nghi | Hướng khắc phục |
|---|---|---|
| Rà sức khỏe bổng mượt thông qua cống ALB nhưng lại chọc rách hỏng lật qua CDN CloudFront | Cấu hỏng trật quy bạo trong behavior của CloudFront hoặc khai nhầm origin | Vào tra kỹ lưỡng danh sách cọc cấu hình behavior thuộc mạn distribution của CloudFront |
| Kịch bản kiểm rà chat giãy khóc sau kì thao diễn bồi thêm số pod (scaling) | Trục chao rãnh Redis adapter hay rào bảo băm stickiness bên target group của ALB trượt cọc | Xác tín thọ sinh vững chắc của Redis cũng như nút gạt stickiness tại target group |
| Ứng viên nộp 1 đơn xin việc vỗ trát đẻ liền 2 bản ghi | Thiếu hụt trường unique constraint tại cơ quan CSDL hoặc lọt bug ở thuật toán tính bất biến | Cho thiển trọ chạy hệ bài test bất biến mạn backend và rà xem kỹ lưỡng các ràng buộc cọc CSDL |
| Tác vụ nằm trong hàng đợi processing gầm lì bế kẹt cõi queued | Cụm worker gục khóa tịt (disabled) hay trạm cất SageMaker chẳng mỉm cười sẵn sàng | Tra thông số cờ biến `PROCESSING_WORKER_ENABLED`, trạng thái cất pod `ai-service` cùng cõi thọ của endpoint |
| Bài kiểm test khói cho Lambda chửi rủa do vô tình phạm chuỗi từ khóa bị cấm (reserved word) của DynamoDB | Dùng cộc lốc chuỗi thẳng chữ `result` khi nặn hàm UpdateExpression | Tự trọng ứng chiêu trỏ `#result` phối hở rẽ qua bản quy quy cho trường `ExpressionAttributeNames` |

## Kết luận

Kế hoạch rà nghiệm thu E2E tuân thủ chánh đạo trọng thị minh chứng thực thọ. Khung bạt này ráo riết từ bẻ nhĩ ngọ thuyên mác "đã pass" cho những ca kiểm nghiệm chỉ đơn giản vì nhìn cẩu thấy đoạn mã tồn tại, mà nghiêm trung chốt hạ rõ ranh những nhịp kiểm tra khi chạy nào đang bốc hờ đợi cẩu rào bằng chứng thọ xuất thực bãi.
