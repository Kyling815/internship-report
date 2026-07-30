---
title: "Triển khai backend"
date: 2024-01-01
weight: 7
chapter: false
pre: " <b> 5.7. </b> "
---

## Mục tiêu

Triển khai và kiểm chứng hoạt động của toàn bộ các workload ứng dụng trên cụm EKS bao gồm: dịch vụ FastAPI backend, dịch vụ chat, tiến trình outbox dispatcher, processing worker và vi dịch vụ trung gian AI service adapter.

## Bối cảnh kiến trúc

Frontend không được vác thiêu thọ ngụ bên trong cụm EKS. Cụm EKS sắm vai chuyên nuôi ngọ cho các dịch vụ và các cụm worker chạy dài kỳ, ẩn cẩn khôn sát phía sau một cổng xuất phát ALB origin do cống mạng CloudFront vinh quy kêu xướng.

## Các thông số đầu vào cho triển khai

Dây chuyền sản xuất production tính toán tự túc ra địa chỉ định tuyến image URIs dựa từ chuỗi tham mác tài khoản AWS, mã khu vực region, kho ECR cùng mã chốt Commit `github.sha`:

| Workload | Biến image | Kho ECR mặc định |
|---|---|---|
| Backend và các worker | `BACKEND_IMAGE` | `internship-backend` |
| Dịch vụ chat | `CHAT_IMAGE` | `internship-chat` |
| Bộ đệm AI adapter | `AI_IMAGE` | `internship-ai` |

Tập lệnh kịch bản triển khai đòi hỏi các khóa:

- `BACKEND_IMAGE`
- `CHAT_IMAGE`
- `SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `AWS_REGION`
- `OUTBOX_QUEUE_URL`

Nhóm thông số mang tính tự nguyện nhưng hàm trọ trọng lượng lớn:

- `AI_DEPLOY_ENABLED`
- `AI_IMAGE`
- `PROCESSING_WORKER_ENABLED`
- `SAGEMAKER_ENDPOINT_NAME`
- `AI_SERVICE_BASE_URL`
- `IRSA_ROLE_ARN`
- `S3_BUCKET`
- `AI_SERVICE_API_KEY`

## Đóng gói image và đẩy lên ECR

Tập lệnh phụ thủ cho luồng CI là `scripts/ci/deploy-eks-pipeline.sh` gánh vác sứ mạng dịch biên nặn image và hất đẩy trót lọt lên bãi:

```bash
bash scripts/ci/deploy-eks-pipeline.sh
```

Dây chuyền ngay tức khắc thẩm soát dấu ấn nhãn SHA vừa gán cho hai image của backend và chat:

```bash
aws ecr describe-images \
  --region ap-southeast-1 \
  --repository-name internship-backend \
  --image-ids imageTag=<GITHUB_SHA>

aws ecr describe-images \
  --region ap-southeast-1 \
  --repository-name internship-chat \
  --image-ids imageTag=<GITHUB_SHA>
```

Bất giác nhịp còi khóa `AI_DEPLOY_ENABLED=true` vang khởi, tệp image cho bộ trung gian AI adapter lập tức được thiếc nặn với chuỗi lệnh:

```bash
docker build --file Dockerfile.ai-service --tag <AI_IMAGE> .
docker push <AI_IMAGE>
```

## Namespace Kubernetes và ServiceAccount

Quy trình thọ tác ban khải cho ban bố:

```bash
kubectl apply -f k8s/app/namespace.yaml
kubectl apply -f k8s/app/serviceaccount.yaml
```

Mỗi khoảnh khắc biến cọc tham số `IRSA_ROLE_ARN` mang giá trị truyền qua, hồ sơ bản vẽ ServiceAccount trứ danh thuyên dành riêng cho EKS lập tức trải qua luồng compile render rồi được ra áp trúng theo văn kiện từ `k8s/eks/serviceaccount.yaml`.

Kiểm chứng:

```bash
kubectl get namespace internship
kubectl get serviceaccount internship-app -n internship -o yaml
```

## Sử dụng ConfigMap và Secret

Hồ sơ ConfigMap thi triển ra production bắt nguồn xuất nạp từ văn kiện `k8s/eks/configmap.yaml`. Các trường định nghĩa mạn trọng cốt yếu gồm có:

| Khóa | Giá trị hoặc mục đích |
|---|---|
| `APP_ENV` | `eks` |
| `OUTBOX_PUBLISHER` | `sqs` |
| `AI_SERVICE_BASE_URL` | `http://ai-service:8010` |
| `AI_SERVICE_PARSE_TIMEOUT_SECONDS` | `120` |
| `AI_SERVICE_MATCH_TIMEOUT_SECONDS` | `600` |
| `STORAGE_BACKEND` | `s3` |
| `AWS_REGION` | `ap-southeast-1` |
| `DYNAMODB_USERS_TABLE` | `ChatUsers` |
| `DYNAMODB_GROUPS_TABLE` | `ChatGroups` |
| `DYNAMODB_MESSAGES_TABLE` | `ChatMessages` |

Tiến trình triển khai kiến dựng hoặc cập nhật thẳng cho Kubernetes Secret mang danh nhãn `internship-secrets` vặt nạp thông số tự trong cối lưu bí mật của GitHub. Nghiêm cấm hão huyền in tuế ngã sa ra mạn minh văn đối với mọi giá trị mật mã bí ẩn.

Kiểm chứng:

```bash
kubectl get configmap internship-config -n internship -o yaml
kubectl describe secret internship-secrets -n internship
```

## Các job migration và khởi tạo dữ liệu chat

Học theo tôn chỉ gọn gàng, hệ triển khai sẽ dẹp cạn sạch mọi xác tàn job cũ rách, rồi tự do tạc phác đẩy lên các job mới tinh sành, kiêm mẫn chìm an đợi còi ra lệnh thành khơi trót lọt:

```bash
kubectl delete job backend-migrate chat-init -n internship --ignore-not-found
kubectl apply -f <rendered-backend-migration-job.yaml>
kubectl apply -f <rendered-chat-init-job.yaml>
kubectl wait --for=condition=complete job/backend-migrate -n internship --timeout=300s
kubectl wait --for=condition=complete job/chat-init -n internship --timeout=300s
```

Job `backend-migrate` ra rã thọ thi lệnh `alembic upgrade head`. Còn `chat-init` hoan hỷ khai mở cất cọc cho chuỗi cơ quan bảng chat tại DynamoDB.

## Triển khai các workload

| Deployment | Lệnh container (Container command) | Port | Replicas | Mục đích |
|---|---|---:|---:|---|
| `backend` | `uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers` | 8000 | 2 | Phục vụ dịch vụ REST API trên FastAPI |
| `chat-service` | `node server.js` thông qua chuỗi lệnh khởi xướng tự bản thể image | 3000 | 2 | Dịch vụ Chat REST kết hợp Socket.IO |
| `backend-outbox-dispatcher` | `python -m app.workers.outbox_dispatcher` | 9101 cho metrics | 1 | Trích xuất và phát thông tin sự kiện từ outbox qua SQS |
| `backend-processing-worker` | `python -m app.workers.processing_worker` | 9102 cho metrics | 2 trong manifest, tự chủ ngả dãn xuống 0 | Gánh tải xử lý tài liệu cùng thao tác AI bất đồng bộ |
| `ai-service` | Lệnh mặc định gắn trong image AI | 8010 | 1 | Bộ đệm trung gian cho SageMaker |

Khải chạy ban bố và rà kiểm chứng:

```bash
bash scripts/k8s/deploy-eks.sh
kubectl rollout status deployment/backend -n internship --timeout=300s
kubectl rollout status deployment/chat-service -n internship --timeout=300s
kubectl rollout status deployment/backend-outbox-dispatcher -n internship --timeout=300s
kubectl rollout status deployment/backend-processing-worker -n internship --timeout=300s
kubectl rollout status deployment/ai-service -n internship --timeout=900s
```

Lưu tâm khẩn thiết thọ thi dòng lệnh rà cuộn bản phát hành (rollout status) cho `ai-service` duy chỉ các dịp cơ chế cho phép triển khai cống AI vỗ tay gạt bật.

## Chốt kiểm soát cho dịch vụ AI và processing worker

Tập lệnh kịch bản cản rào ngăn kiêng mọi ý định gạt rẽ cho worker ngạo mạn bật vùng bãi khuyết thiếu an nộ:

- Biến cấu hình `PROCESSING_WORKER_ENABLED=true` khẩn khoản kham thấu đòi hỏi `AI_DEPLOY_ENABLED=true`.
- Tham số `PROCESSING_WORKER_ENABLED=true` kiên kỵ rêu đòi nạp biến `AI_IMAGE`.
- Trạng thái cất vây cho SageMaker endpoint `internship-qwen3-4b` bắt bấu ngã về mác `InService`.

Thăm viếng tình thế cọ endpoint trước phút ban trát cấp visa cho worker hoạt động:

```bash
aws sagemaker describe-endpoint \
  --endpoint-name internship-qwen3-4b \
  --region ap-southeast-1 \
  --query EndpointStatus \
  --output text
```

Kết quả mong đợi:

```text
InService
```

## Các điểm kiểm tra sức khỏe (Health probes)

| Workload | Startup probe | Readiness probe | Liveness probe |
|---|---|---|---|
| `backend` | `/health/live` | `/health/ready` | `/health/live` |
| `chat-service` | `/health/live` | `/health/ready` | `/health/live` |
| `ai-service` | Không cấu hình phân định ra riêng | `/health/ready` | `/health/ready` |
| `backend-outbox-dispatcher` | TCP `9101` | TCP `9101` | TCP `9101` |
| `backend-processing-worker` | TCP `9102` | TCP `9102` | TCP `9102` |

## HPA và PDB

Văn kiện `k8s/app/autoscaling.yaml` quy bạo định nghĩa rõ ràng:

| Tài nguyên | HPA | PDB |
|---|---|---|
| `backend` | tối thiểu 2, tối đa 5, mục tiêu nhịp CPU ở 70% | số lượng tối thiểu duy trì available là 1 |
| `chat-service` | tối thiểu 2, tối đa 5, mục tiêu nhịp CPU ở 70% | số lượng tối thiểu duy trì available là 1 |
| `backend-processing-worker` | tối thiểu 2, tối đa 5, mục tiêu nhịp CPU ở 70% | số lượng tối thiểu duy trì available là 1 (chỉ thi khi cọc worker được bật) |

Trong các kịch bản tiến trình processing worker bị thiêng cho đóng tịt khóa vãn (disabled), tập kịch bản sẽ tháo rách xao hạ xóa luôn chuỗi HPA cùng PDB gắn theo nó, và kiên khôn dãn cọc số replica nháo ép trúng mức 0.

Kiểm chứng:

```bash
kubectl get hpa,pdb -n internship
kubectl describe hpa backend -n internship
kubectl describe hpa chat-service -n internship
```

## Ingress và định tuyến ALB

Thực thể ALB Ingress vinh mang định dạng public nằm gọn tại cõi `k8s/eks/ingress-alb-no-domain.yaml`. Con đường rẽ sóng bao vây chia tải ngã trúng:

- `/api` vãng trúng tới Service `backend`
- `/chat` trao cho Service `chat-service`
- `/socket.io` điều thẳng cho Service `chat-service`

Thi trổ tung cọc phân tuyến ALB public qua dây chuyền workflow mang chế độ `deploy-public`, hoặc bốc gọi cẩu qua tập lệnh hỗ thủ:

```bash
ENABLE_ALB_INGRESS=true bash scripts/aws/deploy-public-ingress.sh
```

Kiểm chứng:

```bash
kubectl get ingress internship-public -n internship
curl -fsS http://k8s-internshippublic-48101b50ad-85486086.ap-southeast-1.elb.amazonaws.com/api/health/ready
curl -fsS http://k8s-internshippublic-48101b50ad-85486086.ap-southeast-1.elb.amazonaws.com/chat/health/ready
```

## Lệnh kiểm tra nhanh qua Port-forward

Tập lệnh ban bố trung thọ viện binh các chốt tra chuyển tiếp cổng nội bồi (local port-forwards) phục vụ luồng test thử nghìn nhịp khói ngạo:

```bash
kubectl port-forward service/backend 18080:8000 -n internship
curl -fsS http://127.0.0.1:18080/health/ready
```

```bash
kubectl port-forward service/chat-service 18081:3000 -n internship
curl -fsS http://127.0.0.1:18081/health/ready
```

```bash
kubectl port-forward service/ai-service 18082:8010 -n internship
curl -fsS http://127.0.0.1:18082/health/ready
```

## Kết quả mong đợi

- Hai thợ job migration và khởi tạo dữ liệu chat reo hò kết hoang thành tựu trọn vẹn.
- Tiến trình cuộn gác mác triển khai của backend, chat cùng dispatcher xuôi luông êm mượt vãng quan.
- Tiến trình processing worker chễm trệ tựa cọc trạng thái Ready, hoặc kiên chánh ngọ yên ở quy mô 0 replica đúng kịch bản thiết lập chủ trạch.
- Dịch vụ AI nghênh ngang an tọa trạng thái Ready bất cứ kì luồng bật cống AI thi thố mở ra.
- Toàn diện các cụm Service hoành khai rước rẽ đầy đủ trường endpoints gắn đệm.
- Cuộc thi rà soát sức khỏe từ ALB thông quan vãn phúc trát danh cho backend và chat.
- Mạng CDN CloudFront không trầy một vảy băng qua chạm tới origin của ALB dành riêng cho ranh gới chuỗi `/api`, `/chat`, và `/socket.io`.

## Các lỗi thường gặp

| Triệu chứng | Nguyên nhân | Hướng khắc phục |
|---|---|---|
| Lên tiếng phan ca `Missing required environment variable` | Thông số mật mã secret hoặc biến môi trường bắt buộc của luồng ban bố biến đâu bặt vô âm tín | Kíp mau cẩu bồi bổ nạp thẳng trúng biến cấu hình hay bí ẩn secret còn khuyết trống cho bên mạn GitHub |
| Ngứa xao còi tháo `Unable to compute backend/chat image URIs` | Sa khuyết biến định hình của workflow hay gặt hỏng trong nhịp tự động sinh chuỗi định danh ảnh bám theo nhãn SHA | Vận chuân chuẩn xác chuỗi lắp kết bấu từ tài khoản, vùng khu vực region, danh tước kho ECR cùng tham mác cọc `github.sha` |
| Bồi tra thất chốn chẳng thấy container image trên kho ECR | Bước test tác nghiệp build/push hãi hỏng chưa nạp thăng chùm thẻ tag mang chữ ký SHA | Xâm nhập điều rã nguyên rễ tại job `build-images` và mục trần tình trạng kho lưu trữ ECR repository |
| Cọc `PROCESSING_WORKER_ENABLED=true` chửi thề khước vãn lệnh rào | Đàn hạ tầng rào cản phụ thuộc của AI nằm phó hỏng trượt dốc sa mác | Nảy lệnh bật image AI trước ra tiễn còi thanh tra tình huống cọc SageMaker ngã trúng trạng thái `InService` |
| Lệnh thăm dò sức khỏe dịch vụ chat trả về bế quẫn trượt vãng | Cơ quan tài nguyên phụ thuộc mang tên Redis hoặc DynamoDB chìm lim ngắc gục | Truy nạp thám rà tệp log của dịch vụ chat kết hợp kiểm chứng hiện trạng sức khỏe cõi DynamoDB cùng Redis |
| Bước khảo sát sức khỏe của backend khóc rêu than gục ngã | Kho cọc CSDL PostgreSQL chìm phỉ vắng dạng hoặc luồng thọ di cư migration trồi sập lọt khuyết | Khai quan coi soi nhật ký log thuộc về backend song song soát tra khả năng vươn luồn kết nối rào tới RDS |

## Kết luận

Toàn cõi quy trình đưa lên EKS cho hệ thống backend ca rền khúc hoan khải, trọn trào trát vinh danh thành tài vãng trát ngay tại khúc khoảnh mác khi backend, dịch vụ chat, dispatcher, cùng các chuỗi tùy nhĩ của worker và bộ đệm AI adapter đồng loạt thi thố vũ múa vững vàng, bám khôn bính sát cấu hình đo dò sức khỏe probess chuẩn chỉnh, dịch vụ minh bạch endpoint trứ rêu, luật gò dãn dẻo thau chu toàn kiêm vây luân cọ phân luồng giao thông mạch lạc theo chân ALB routing.
