---
title: "Giám sát và nhật ký"
date: 2024-01-01
weight: 9
chapter: false
pre: " <b> 5.9. </b> "
---

## Mục tiêu

Giám sát an nộ sức khỏe của ứng dụng, trạng thái của các tiến trình triển khai, chuỗi tập tin nhật ký (logs), hệ thông lượng đo lường metrics, danh sách các hàng đợi, luồng xử lý trên hàm Lambda, và toàn diện cụm tài nguyên dịch vụ AWS được quản lý.

## Bối cảnh kiến trúc

Kho chứa repository tích hợp sẵn các hồ sơ bản vẽ kịch bản Kubernetes mang thói quen ServiceMonitor cùng PrometheusRule dùng thi cẩu gặt hái thông tham số ứng dụng metrics. Các chỉ số metrics và báo nguy cảnh báo nằm tại cõi AWS CloudWatch buộc lòng yêu cầu thanh kiểm cẩn khôn trên tài khoản AWS của dự án trước thềm ra phán cờ ghi mác là đã thực thi trong production.

## Tra soát tài nguyên Kubernetes

Ứng dụng thọ gõ cụm lệnh cất nhanh `kubectl get` để thanh kiểm tức thời mọi nhịp sinh trồi trạng thái:

```bash
kubectl get deployments,pods,svc,endpoints,hpa,pdb,jobs -n internship -o wide
kubectl get ingress internship-public -n internship
kubectl get events -n internship --sort-by=.lastTimestamp
```

Kết quả mong đợi:

- Hai chiến tuyến `backend` và `chat-service` nghênh ngang hãy múa con số các replica mang trạng thái Ready.
- Tiến trình `backend-outbox-dispatcher` vững kiên an tọa cọc trạng thái Ready.
- Trình `backend-processing-worker` ung dung chễm trệ trạng thái Ready, hoặc kiên khôn ngả bãi xuống quy mô 0 replica đúng nhĩ kịch bản.
- Dịch vụ `ai-service` báo danh cọc Ready mỗi dịp chu trình ban bố mở cống AI vỗ còi thêu bật.
- Cụm tác vụ job thợ múa `backend-migrate` và `chat-init` hoan khải khép kín một mạch thi hành thành tài hoàn trọn.

## Trạng thái cuộn bản phát hành (Rollout status)

```bash
kubectl rollout status deployment/backend -n internship --timeout=300s
kubectl rollout status deployment/chat-service -n internship --timeout=300s
kubectl rollout status deployment/backend-outbox-dispatcher -n internship --timeout=300s
kubectl rollout status deployment/backend-processing-worker -n internship --timeout=300s
kubectl rollout status deployment/ai-service -n internship --timeout=900s
```

Chú tâm khẩn kiệt nhấp rà lệnh trát của `ai-service` duy chỉ lúc rào cấu hình cho phép triển khai pod trung gian AI service mở rộng đón cẩu.

## Nhật ký ứng dụng (Application logs)

```bash
kubectl logs deployment/backend -n internship --tail=200
kubectl logs deployment/chat-service -n internship --tail=200
kubectl logs deployment/backend-outbox-dispatcher -n internship --tail=200
kubectl logs deployment/backend-processing-worker -n internship --tail=200
kubectl logs deployment/ai-service -n internship --tail=200
```

Kiên kỵ huy động thêm tham cờ `--previous` trong hoàn cảnh con pod tuôn cọc tái khởi sinh lật cõi:

```bash
kubectl logs deployment/backend -n internship --previous --tail=200
```

## Các lệnh describe

Ưu vãng thọ gọi câu lệnh `kubectl describe` mỗi lúc tiến trình khảo sát sức khỏe readiness, phân rã vãng lịch chạy pod, bộ đo lường sức khỏe, hoặc cỗ máy canh rà đồng bộ Ingress bốc hỏng dội sập:

```bash
kubectl describe pod -n internship -l app=backend
kubectl describe pod -n internship -l app=chat-service
kubectl describe hpa backend -n internship
kubectl describe ingress internship-public -n internship
```

## Các đường dẫn kiểm thử sức khỏe

Hệ rà soát sức khỏe sẵn lòng thuộc mạn backend thi ra chiêu tra khảo kết nối cọc tới PostgreSQL:

```bash
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/api/health/ready
```

Chuỗi tin đáp trả theo kỳ vọng:

```json
{"status":"ready","service":"internship-api","dependencies":{"postgres":true}}
```

Nhịp tim đo đạc rà sức khỏe từ dịch vụ chat tiến tới thấu trát soát 2 cơ quan Redis kết bấu cùng DynamoDB:

```bash
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/chat/health/ready
```

Kết quả trả về mong đợi:

```json
{"status":"ready","dependencies":{"redis":true,"dynamodb":true}}
```

Luồng soát sức khỏe bên mạn dịch vụ AI bấu giữ xác minh tinh trát xem khóa biến `SAGEMAKER_ENDPOINT_NAME` đã sắm vãng vào đủ chăng:

```bash
kubectl port-forward service/ai-service 18082:8010 -n internship
curl -fsS http://127.0.0.1:18082/health/ready
```

## Prometheus và Grafana

Kho repository cất tạc trọn cõi định nghĩa cho các tài nguyên mang mác ServiceMonitor tương ứng cho:

- `backend`
- `chat-service`
- `backend-outbox-dispatcher`
- `backend-processing-worker`
-

Ban bố gõ lệnh ứng cài các manifest mỗi khi rèm cấu trúc bộ khung CRD thuộc về Prometheus Operator thi thố an tọa bãi:

```bash
kubectl apply -f k8s/observability/service-monitors.yaml
kubectl apply -f k8s/observability/prometheus-rules.yaml
```

Kiểm chứng:

```bash
kubectl get servicemonitor,prometheusrule -n monitoring
kubectl port-forward service/kube-prometheus-stack-prometheus 9092:9090 -n monitoring
curl -fsS "http://127.0.0.1:9092/api/v1/targets?state=active"
```

Các đích đến (targets) giám sát mong đợi xuất ngụ ra cho ứng dụng:

- `backend`
- `chat-service`
- `backend-outbox-dispatcher`
- `backend-processing-worker`

## Cảnh báo được định nghĩa trong repository

Thư viện kịch bản tại gốc repository sở hữu trọn tập quy nạp cho dải báo nguy Prometheus alerts chuyên phục vụ:

| Cảnh báo | Mục đích |
|---|---|
| `InternshipBackendDown` | Mục tiêu (target) giám sát metrics cho backend bặt tàn vắng dạng |
| `InternshipChatDown` | Mục tiêu giám sát metrics thuộc về chat cự cõi tuột giốc |
| `InternshipChatDependencyDown` | Trụ cọc tài nguyên phụ thuộc (Redis hay DynamoDB) của chat sa cọc nghẹt |
| `InternshipOutboxDispatcherDown` | Mục tiêu giám sát metrics của dispatcher rơi tõm kiệt dạng |
| `InternshipProcessingWorkerDown` | Mục tiêu giám sát metrics cho processing worker gào ngã kiếp im lì |
| `InternshipBackend5xxHigh` | Tỷ lệ lỗi 5xx vọt bổng leo dốc cao chót vót cõi backend |
| `InternshipBackendP95LatencyHigh` | Chỉ số trễ mác p95 tại backend trỗi nhịp phình bạo rực rỡ |
| `InternshipChatMessageFailureRatioHigh` | Tỷ lệ thư tín đàm thoại dính thảm bại thuyên trượt qua ngưỡng an toàn |
| `InternshipPodCrashLooping` | Các pod bấu tuội mắc kẹt trong bẫy vòng lặp tử thần CrashLoopBackOff |
| `InternshipOutboxDeadEventsPresent` | Tác nghiệp sự kiện cõi outbox trườn ốm chết đe lị, giục gọi tay con người thiền can thiệp |
| `InternshipOutboxPendingTooOld` | Nhĩ sự kiện chây gan ngọ ngập ngạc mác pending trượt tuổi hạn xa hoa |
| `InternshipOutboxTransportErrors` | Lỗi vãng đò vận trút trên cõi vận tải SQS |
| `InternshipProcessingQueueOld` | Tuổi hàng đợi xử lý processing queue sa chao quá nấc giới hạn thọ |
| `InternshipProcessingJobsFailing` | Các processing jobs trồi sa đâm sấp thảm bại liên hoàn |
| `InternshipAIProviderFailures` | Trùng trùng lỗi chát dội sang từ nguồn cất trát dịch vụ AI |

Trang thái: đã triển khai trong các manifest của repository. Cần bằng chứng để minh chứng các cảnh báo này đã được áp dụng trong production.

## Nhật ký CloudWatch (CloudWatch Logs)

Kiểm tra nhật ký log của Lambda:

```bash
aws logs describe-log-groups \
  --log-group-name-prefix /aws/lambda/internship-outbox-handler \
  --region ap-southeast-1

aws logs tail /aws/lambda/internship-outbox-handler \
  --since 1h \
  --region ap-southeast-1
```

Kiêm tra soát các tệp log phát nạp từ mạn EKS duy nhất chỉ những chuỗi thời khắc cọc điều hướng thu tệp container log shipping gieo rắc kích múa thành công. Cần bằng chứng: tên các log group trên CloudWatch dành cho backend, chat, worker, dispatcher, và AI service.

## Chỉ số giám sát của các dịch vụ AWS được quản lý

| Dịch vụ | Các chỉ số hữu ích |
|---|---|
| ALB | `HTTPCode_Target_5XX_Count`, `TargetResponseTime`, tổng lượng target khỏe múa (healthy hosts), và mức hao tổn đơn vị LCU |
| CloudFront | tổng số lượt request, tỉ lệ cõng lỗi 4xx/5xx, chỉ số trễorigin latency, cùng trữ lượng byte tài liệu tải ra (bytes downloaded) |
| RDS | dung tổn CPU, quy mô bộ nhớ trống (free storage), trữ lượng kết nối (connections), thông lượng IOPS thao tác đọc/ghi, và nhịp trễ nhân bản cọc replica lag (nếu dùng) |
| ElastiCache Redis | tiêu chi CPU, lượng tài nguyên RAM memory, lượt dồn bạt evictions, đi kèm tổng con số kết nối trực tiệp hiện hữu (current connections) |
| DynamoDB | quy bạo request dính án chặn throttled requests, lượng đơn vị đọc/ghi tiếp thoạt consumed read/write capacity, và hệ thông lỗi cọc system errors |
| SQS | số tin nhắn nhìn rãnh approximate visible messages, mác chu kỳ tuổi của con tin lâu đời nhất (age of oldest message), cùng số lượng tin ứ tắc thọ ngụ cõi DLQ visible messages |
| Lambda | lượng mã lỗi errors, độ dài thời cẩu duration, thông ký bạt hãm throttles, mác chu kỳ iterator age, đi kèm cọc lượt khởi thi hành song song concurrent executions |
| SageMaker | thông lượng lỗi gõ lời gọi endpoint invocation errors, chu kỳ trễ cống model latency, chỉ số trễ mạn overhead latency, cùng mức gặm kiệt tải con máy instance utilization |

## Đề xuất các cảnh báo CloudWatch (Proposed CloudWatch alarms)

Các mô hình cảnh báo dưới đây mang dáng hình lời khuyến nghị. Cần bằng chứng trước khi chốt quyền xướng danh cúng trát là đã vinh quy múa việc tại cõi triển khai production:

| Cảnh báo | Điều kiện đề xuất |
|---|---|
| Tin nhắn lộ vãng cõi DLQ | Ghi nhận cọc tham số `ApproximateNumberOfMessagesVisible > 0` cọ rẽ trên hàng đợi `internship-prod-outbox-dlq` |
| Tuổi của hàng đợi chủ lực vọt mác | Chu kỳ thời chao tàn già của con tin nhắn SQS vọt thêu trèo bạt sang qua rào cản vận hành quy đúc |
| Hàm Lambda lâm bãi rách hỏng | Ghi nhận chỉ số `Errors > 0` ngã trúng đầu hàm `internship-outbox-handler` |
| Lambda sa án nghẹt trần phanh (throttles) | Thông ký cọc `Throttles > 0` xuất cõi |
| Tỷ lệ lỗi 5xx trên target ALB phình bạo | Con số lỗi hoặc tỷ lệ 5xx do đích đến target group dội trả ngớp ngoái vượt trần cho phép |
| Tổn hao cọc CPU trên RDS réo kỉnh | Nhịp chiêu tiêu CPU bám cọc duy trì đỉnh cao miên man rả rích xô nấc giới hạn |
| Trữ lượng trống trên RDS sụt giảm (free storage low) | Phần dung lượng đĩa trống an toàn sụt lún chao tụt rớt xa rào bảo vệ |
| Memory của Redis cao vãng trần | Mức tiêu dùng bộ nhớ hoặc lượng bạt tàn evictions phi dốc vọt qua rào nấc định quy |
| SageMaker thông cáo thảm lỗi | Số lần gõ bạt cất rách suy luận hoặc lỗi cỗ model tựa cọc thuyên quá trần cản rào |
| Lỗi 5xx cõi CDN CloudFront phi mã | Tỉ lệ request sa nhầm trúng cọc 5xx băng bổng kiếp vọt nấc rào cản cảnh giác |

## Kết quả mong đợi

- Các cụm Deployment trong lòng Kubernetes reo ca tinh thần Ready trơn chu.
- Bộ trạm tra cứu sức khỏe ung dung thông vãn êm ái khi buông lọt vạchCDN CloudFront.
- Kho tàng nhật ký log trốn đầy tụ sắm đủ trọn cõi cho toàn thể cụm workload trên EKS cũng như cơ quan Lambda.
- Cỗ cống Prometheus tự do vục thâu, cẩu chiết mĩ mãn thông quan dải metrics nghiệp vụ ngay khi hạ tầng giám sát được dệt may hoàn tất.
- Thông số giám sát metrics của muôn kho cọc SQS, Lambda, RDS, Redis, DynamoDB, ALB, CloudFront cùng cõ cống SageMaker ngạo mạn giêu hình vãng ngự trên màn trần CloudWatch.
- Các mô hình cảnh báo đề xuất thảy đều khoắc nhãn đắc thắng với thư viện minh chứng, hoặc cam kính an phận liệt mác cọc đề xuất trù dự nhã nhặn.

## Các lỗi thường gặp

| Triệu chứng | Nguyên nhân | Hướng khắc phục |
|---|---|---|
| Lệnh thăm cẩu `kubectl top` báo vắng ngát dữ liệu | Cụm máy chủ chuyên thu thập metrics (metrics-server) bốc ngắc chết nghẹt hoặc chưa thâu trát kip chu kỳ cất gặt | tra rà ngay tăm cọc cuộn bản phát hành (rollout) cho mạn cụm metrics-server |
| Mục tiêu đích gặt của Prometheus sa cọc trượt ngã | Vướng án rách chọn lọc nhãn (selector) của ServiceMonitor hay đứt mạch vì lệch không gian tên namespace | Soạn kỹ lại danh sách nhãn label của Service và chuỗi quy nạp bắt sóng từ ServiceMonitor selector |
| Điểm sức khỏe của chat khinh từ khước từ mác ready | Cơ quan liên đới phụ thuộc trúng Redis hay DynamoDB đâm gục té xỉu | Mở toang soát tệp log thuộc dịch vụ chat cùng thông ký trạng thái vận hanh trên cõi hạ tầng tài nguyên AWS |
| Nhật ký log Lambda lả bốc mịt m mù | Hàm chưa hề thọ tiếp còi giục cho thực thi hoặc sa bẫy gõ rà thầm khu vực region khác | Đối soát lại cấu trúc liên thông sự kiện (event-source mapping) và chỉ số mác khu vực region trói sát cự ly |
| Hàng đợi thảm khuyết DLQ leo phình vọt tải | Tiến trình Lambda hay luân mạch phía sau (downstream processing) lâm rào thất bại vỡ mác | Tiến lọt rà xét các tin nhắn hãm ngục cõi DLQ kết bấu thẩm ngự nhật ký log của Lambda |

## Kết luận

Kiến trúc giám sát tựu trung giỗ kíp đạt tiêu chuẩn chín muồi ngay chặng bộ phận kỹ thuật điều hành hoàn toàn khả dĩ vục thau thanh kiểm tình thế hiện sinh của Kubernetes, tệp nhật ký logs, cung đường thử kiểm sức khỏe, chuỗi metrics cất gặt cõi Prometheus lẫn CloudWatch, log của Lambda, thế trận hàng đợi SQS/DLQ cùng các rào cảnh báo báo nguy mĩ mãn mà chối từ triệt để, cấm cho phép bốc tung tuột trượt lộ ra bên ngoài thế giới công cộng bất kỳ thông số mật mã bí mật (secret) nào.
