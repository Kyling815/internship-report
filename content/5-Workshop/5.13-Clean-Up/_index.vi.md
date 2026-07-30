---
title: "Dọn dẹp tài nguyên"
date: 2024-01-01
weight: 13
chapter: false
pre: " <b> 5.13. </b> "
---

## Mục tiêu

Cung cấp quy trình dọn dẹp tài nguyên an toàn, thấu đáo trình tự tựa theo sự ràng buộc và phụ thuộc của các thành phần trong môi trường AWS production sau khi đã triển khai kiểm thử và hoàn thành nghiệm thu báo cáo thành công.

## Cảnh báo (Warning)

Các chuỗi câu lệnh khai báo trong chương này mang tính chất phá vỡ và xóa vĩnh viễn (destructive). Tuyệt đối cấm khởi búng thi thố thực thi chúng chừng nào bạn chưa gặt được sự đồng thuận và phê chuẩn minh khéo từ phía người bảo trợ dự án, người làm chủ tài khoản AWS, và ban tư lệnh tổ đội. Hãy chủ động cẩu xuất cất giữ an thọ toàn bãi thư viện bằng chứng, tệp nhật ký logs, thành quả kiểm nghiệm, bảng báo cáo tài chi cước, cùng muôn ảnh chụp thau chốt nghiệm thu sau cùng ngay trước thềm phất cờ gõ xóa tài nguyên.

Chương tài liệu này có mục đích hướng dẫn và làm tư liệu chuyên môn. Toàn vẹn không một dòng lệnh tháo xóa rũ nào bị đem búng thi thố cẩu chạy trần thực trong chu kỳ dịch may nặn nên cuốn báo cáo này.

## Bối cảnh kiến trúc

Công tác dọn dẹp tài nguyên bắt buộc phải quy theo chuỗi trật tự phụ thuộc tầng lớp. Thao tác cầm đèn sa tay xóa đi cõi mạng ngang hay vai trò IAM trước nhất rất dễ gieo bãi khiến cho các bộ cân bằng tải ALB, giao diện mạng con ENI, các node group, cụm endpoint, con hàng đợi, hòm sọt bucket, hay hệ thống tệp log CloudWatch hãm rách bế thợ tắc nghẽn gầm lì bên thế giới lại. Giải pháp an nộ tối thượng là ra trát cất dừng lực lượng nhà sản xuất tin (producers), bẽ nấc đóng cụm gặt tin (consumers), xóa tan lập tức khối máy chủ phát sinh chi phí cao, và chỉ cho buông vãng xóa bỏ các thành phần nền tảng mạng và vai trò IAM ở khúc cuối cùng.

## Danh sách kiểm tra trước khi dọn dẹp (Pre-cleanup checklist)

- [ ] Xác minh chắc chắn rằng cụm môi trường AWS hiện tại đã mãn cất sứ mệnh và không còn nhuần cầu cho sử dụng nữa.
- [ ] Tải xuất và sao bưu trọn vẹn tệp tài liệu minh chứng thuộc CloudFront, ALB, EKS, RDS, Redis, DynamoDB, SQS, Lambda, SageMaker, cùng hòm S3.
- [ ] Truy xuất cẩn thêu hồ sơ chi tiêu trong AWS Cost Explorer hay bảng tính AWS Pricing Calculator.
- [ ] Export tệp nhật ký log từ Lambda chứng minh cho bước test khói (smoke test) sau cùng.
- [ ] Sao chép nạp an tịnh muôn cõi văn thư sự kiện lâu dài (archive objects) cất giấu trên mạn kho S3 (nếu cần).
- [ ] Thẩm định cẩn kỵ rằng không có bất kỳ cộng đồng người dùng thực tiễn nào kiêng thọ phụ thuộc vào hệ cất hiện hành.
- [ ] Quyết gặt minh bạch việc các bản sao lưu (backups) hay ảnh chụp dữ liệu (snapshots) sẽ được kiên bão bảo lưu hay thống nhất tháo bẻ ra cho xóa bỏ.
- [ ] Đối soát xác thực số hiệu tài khoản AWS hiện tại trúng khớp 100% tài khoản cõi dự án mưu trù thau gõ dọn bãi.
- [ ] Soát cọc khẳng định chắc nịch rằng mã vùng khu vực region thọ thực là `ap-southeast-1`.

Lệnh kiểm chứng:

```bash
aws sts get-caller-identity
aws configure get region
kubectl config current-context
```

## Trình tự dọn dẹp theo phụ thuộc tài nguyên (Dependency-aware cleanup order)

### 1. Vô hiệu hóa processing worker

Khóa vãn trút dừng mọi luông tác vụ bão AI chạy dai cẳng trước thềm gạt tay cẩu chôn cõi SageMaker hoặc chuỗi tài nguyên cơ sở dữ liệu:

```bash
kubectl scale deployment/backend-processing-worker --replicas=0 -n internship
kubectl delete hpa backend-processing-worker -n internship --ignore-not-found
kubectl delete pdb backend-processing-worker -n internship --ignore-not-found
kubectl rollout status deployment/backend-processing-worker -n internship --timeout=120s
```

### 2. Vô hiệu hóa event-source mapping của Lambda SQS

Tra khảo danh bạ mapping:

```bash
aws lambda list-event-source-mappings \
  --function-name internship-outbox-handler \
  --region ap-southeast-1
```

Thực hiện tắt nút gạt (disable) cho từng bản ghi liên kết:

```bash
aws lambda update-event-source-mapping \
  --uuid <EVENT_SOURCE_MAPPING_UUID> \
  --enabled false \
  --region ap-southeast-1
```

### 3. Xóa trạm suy đoán SageMaker endpoint

Số giờ mở máy duy trì thọ của SagMaker endpoint chính là tay ngốn cước phái cọc hung mãnh nhất:

```bash
aws sagemaker delete-endpoint \
  --endpoint-name internship-qwen3-4b \
  --region ap-southeast-1
```

Tiếp nhịp thăm dò tra khảo trù bã ra cấu hình endpoint (endpoint config) kết cùng các cõi mô hình (models) trước phút quyết gõ cho tiễn trát tháo gỡ chúng:

```bash
aws sagemaker list-endpoint-configs --region ap-southeast-1
aws sagemaker list-models --region ap-southeast-1
```

### 4. Xóa hàm Lambda

Ban trát xóa tiệt cọ sau khi kịch bản cản khóa cống liên thông sự kiện event-source mapping thọ thi thành tài:

```bash
aws lambda delete-function \
  --function-name internship-outbox-handler \
  --region ap-southeast-1
```

### 5. Xóa event-source mapping của Lambda

```bash
aws lambda delete-event-source-mapping \
  --uuid <EVENT_SOURCE_MAPPING_UUID> \
  --region ap-southeast-1
```

### 6. Kiểm tra hoặc dọn dẹp tin nhắn kiểm thử (purge)

Kiêm tra soát hiện trạng bên trong hàng đợi:

```bash
aws sqs get-queue-attributes \
  --queue-url <OUTBOX_QUEUE_URL> \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible \
  --region ap-southeast-1
```

Nếu nhở cẩn vinh nhận được lệnh thuận chuẩn cho xóa nạp tệp, thực hiện ra trát xóa sạch (purge) muôn tin test rách:

```bash
aws sqs purge-queue --queue-url <OUTBOX_QUEUE_URL> --region ap-southeast-1
```

### 7. Xóa các hàng đợi SQS

```bash
aws sqs delete-queue --queue-url <OUTBOX_QUEUE_URL> --region ap-southeast-1
aws sqs delete-queue --queue-url <OUTBOX_DLQ_URL> --region ap-southeast-1
```

### 8. Xóa Kubernetes Ingress

Sự biến tháo xô gục tài nguyên Ingress bên mạn k8s lập tức nháy chuồng giục trình AWS Load Balancer Controller ra tay tháo rỡ xóa bãi ALB thực thụ trên AWS:

```bash
kubectl delete ingress internship-public -n internship --ignore-not-found
```

### 9. Chờ quá trình xóa ALB hoàn tất

```bash
aws elbv2 describe-load-balancers --region ap-southeast-1
aws elbv2 describe-target-groups --region ap-southeast-1
```

Kiêm trung sa chìm êm kiên bế nhẫn chờ đợi cho tới khúc khoảnh mác khi thực thể ALB cùng các target group của internship thọ biến tiệt hoàn cõi.

### 10. Xóa các workload trên EKS

```bash
kubectl delete -f k8s/app/autoscaling.yaml --ignore-not-found
kubectl delete -f k8s/app/ai-service.yaml --ignore-not-found
kubectl delete -f k8s/app/backend-processing-worker.yaml --ignore-not-found
kubectl delete -f k8s/app/backend-outbox-dispatcher.yaml --ignore-not-found
kubectl delete -f k8s/app/chat.yaml --ignore-not-found
kubectl delete -f k8s/app/backend.yaml --ignore-not-found
kubectl delete job backend-migrate chat-init -n internship --ignore-not-found
```

Duy trì tuế gõ xóa bỏ không gian tên (namespace) khi và chỉ khi đã thấu đáo cản bão chẳng còn con workload nhát tài nguyên nào gan lì trườn ngụ lại:

```bash
kubectl get all -n internship
kubectl delete namespace internship
```

### 11. Xóa EKS node group

```bash
aws eks list-nodegroups \
  --cluster-name internship-prod \
  --region ap-southeast-1

aws eks delete-nodegroup \
  --cluster-name internship-prod \
  --nodegroup-name <NODEGROUP_NAME> \
  --region ap-southeast-1
```

Kêu còi kiên chờ quy nạp xóa xong:

```bash
aws eks wait nodegroup-deleted \
  --cluster-name internship-prod \
  --nodegroup-name <NODEGROUP_NAME> \
  --region ap-southeast-1
```

### 12. Xóa cụm EKS cluster

```bash
aws eks delete-cluster \
  --name internship-prod \
  --region ap-southeast-1
```

### 13. Xóa cơ sở dữ liệu RDS

Cân nhắc ra quyết chốt có muốn nặn thi một ảnh sao bưu chốt hạ cuối cùng (final snapshot) trước thềm dọn dẹp hay không:

```bash
aws rds delete-db-instance \
  --db-instance-identifier internship-prod-postgres \
  --final-db-snapshot-identifier internship-prod-postgres-final-<DATE> \
  --region ap-southeast-1
```

Chỉ được khôn ra quyết bỏ lơ (skip) việc chụp ảnh sao lưu cuội cùng chặng kỳ nhận được lời đồng thuận cất văn phê chuẩn ranh mạch:

```bash
aws rds delete-db-instance \
  --db-instance-identifier internship-prod-postgres \
  --skip-final-snapshot \
  --region ap-southeast-1
```

### 14. Xóa cụm ElastiCache Redis

```bash
aws elasticache delete-replication-group \
  --replication-group-id internship-prod-redis \
  --region ap-southeast-1
```

### 15. Xóa các bảng DynamoDB

Ra tay xóa bẻ cọ ngay sau khi minh chanh xác thực không ai kêu đòi giữ lại tài sản dữ liệu của bảng nữa:

```bash
aws dynamodb delete-table --table-name ChatUsers --region ap-southeast-1
aws dynamodb delete-table --table-name ChatGroups --region ap-southeast-1
aws dynamodb delete-table --table-name ChatMessages --region ap-southeast-1
aws dynamodb delete-table --table-name InternshipLambdaEventDedupe --region ap-southeast-1
```

### 16. Làm trống và xóa các bucket S3

Khảo rà thẩm sát nội bồi trước khi can thiệp:

```bash
aws s3 ls s3://internship-prod-frontend-<AWS_ACCOUNT_ID> --recursive --summarize
aws s3 ls s3://internship-prod-uploads-<AWS_ACCOUNT_ID> --recursive --summarize
```

Ra lệnh cất bẻ làm trống tệp và thi tháo kho sau nhịp được phê chuẩn:

```bash
aws s3 rm s3://internship-prod-frontend-<AWS_ACCOUNT_ID> --recursive
aws s3 rb s3://internship-prod-frontend-<AWS_ACCOUNT_ID>
aws s3 rm s3://internship-prod-uploads-<AWS_ACCOUNT_ID> --recursive
aws s3 rb s3://internship-prod-uploads-<AWS_ACCOUNT_ID>
```

Nếu cơ chế theo cọc ghi phiên bản (versioning) thọ được nháy cất cho bật, bắt buộc bạn phải quét sạch mọi cọc phiên bản object versions đi kèm các nhãn dập xóa delete markers trước thềm mới tuột bẻ lệnh trù dập bucket được.

### 17. Vô hiệu hóa và xóa CloudFront

Tài nguyên CloudFront khẩn khôn đòi hỏi phải gặt nút tắt (disabled) trước thời khắc cho lệnh ra trát xóa bỏ:

```bash
aws cloudfront get-distribution-config --id EQIGYNECXDYL8
```

Cập nhật tệp cấu hình cõi distribution chuyển trường `Enabled=false`, bảo vẹn nguyên chuế giá trị mã nhãn thẻ `ETag`, và sau đó kiên nhĩ chờ đợi:

```bash
aws cloudfront wait distribution-deployed --id EQIGYNECXDYL8
```

Gõ lệnh cẩu tháo rỡ xóa bãi:

```bash
aws cloudfront delete-distribution \
  --id EQIGYNECXDYL8 \
  --if-match <ETAG>
```

### 18. Xóa NAT Gateway

```bash
aws ec2 describe-nat-gateways --region ap-southeast-1
aws ec2 delete-nat-gateway --nat-gateway-id <NAT_GATEWAY_ID> --region ap-southeast-1
```

### 19. Giải phóng địa chỉ Elastic IP

Ra lệnh phỏng thích trả còi lại địa chỉ IP tĩnh (Elastic IP) cho AWS chỉ ở thời mác khi con cõi NAT Gateway đã tiễn trát ngã cọc xóa bỏ thành tài:

```bash
aws ec2 release-address --allocation-id <ALLOCATION_ID> --region ap-southeast-1
```

### 20. Xóa các vai trò và chính sách IAM (IAM roles and policies)

Xóa nhãn phân quyền IAM ở khúc muộn muôn cùng, cản sau chặng toàn thể các vi workload gặm thọ nhờ chúng đều đã biến đi vào dĩ vãng:

```bash
aws iam detach-role-policy --role-name internship-github-deploy --policy-arn <POLICY_ARN>
aws iam delete-role --role-name internship-github-deploy
```

Lặp lại quy luật tháo dọn này ứng cho từng IAM role sinh ra riêng cho dự án cản bãi, kiên trung thọ thi chỉ sau nhịp cất thẩm minh bạch chẳng có một dịch vụ chia cẩu chung chao nào mạn ngoài kiên cầu vào chúng nữa.

### 21. Xóa các tài nguyên VPC còn lại

Khám xét và thu gọn bã, tháo gỡ tiệt:

- security groups
- route tables
- subnets
- Internet Gateway
- các ranh định tuyến qua NAT (NAT routes)
- VPC endpoints
- những cọc cống kết nối ENIs còn sa kẹt bám lại

Các câu lệnh kiểm chứng:

```bash
aws ec2 describe-network-interfaces --region ap-southeast-1
aws ec2 describe-security-groups --region ap-southeast-1
aws ec2 describe-route-tables --region ap-southeast-1
aws ec2 describe-internet-gateways --region ap-southeast-1
aws ec2 describe-vpc-endpoints --region ap-southeast-1
```

### 22. Kiểm chứng việc xóa các tài nguyên phát sinh chi phí

Những lệnh cất bão khải thông cẩu gạt kiểm rà sau cuối:

```bash
aws eks list-clusters --region ap-southeast-1
aws elbv2 describe-load-balancers --region ap-southeast-1
aws rds describe-db-instances --region ap-southeast-1
aws elasticache describe-replication-groups --region ap-southeast-1
aws sqs list-queues --region ap-southeast-1
aws lambda list-functions --region ap-southeast-1
aws sagemaker list-endpoints --region ap-southeast-1
aws cloudfront list-distributions
```

Đăng nhập tra lại mạn hóa đơn AWS Billing kết cọc cõi Cost Explorer vào ngày kế tiếp (the next day), bởi thói quen kỹ thuật định chốt rằng một số bản ghi thông lượng hao phí tiêu thu có xu thế sa trễ sau một khoảng trần chu kỳ delay nhất định.

## Các lỗi thường gặp

| Triệu chứng | Nguyên nhân | Hướng khắc phục |
|---|---|---|
| Cự tuyệt án gõ tháo dẹp xóa mạng VPC | Các ENI, cổng ALB, trạm NAT, VPC endpoint, hoặc security groups kiên lì còn mắc ngụ | Khảo sát tra cọc các ENI đi đôi cọ danh mục tài nguyên cất bấu phụ thuộc |
| Không thể ra lệnh trát chôn xóa S3 bucket | Vẫn mắc rẹt cộc phiên bản object versions hoặc nhãn dập xóa delete markers | Tra bẻ gõ xóa sạch muôn bản ghi version cùng thẻ marker khỏi hòm |
| Châm trách thề cự tháo tài nguyên CloudFront | Tài nguyên distribution vẫn sa ở mức đang kích bật (enabled) hay sa xéo xô lệch chuỗi ETag | Tắt nút enabled, cẩu chờ trạng thái deployed hoàn trọn, và ra cẩu tháo với mã ETag mới nhất |
| Bất lực rên than không tháo xóa được vai trò IAM | Chính sách (policies) vẫn đang mang tư thế đính trói cọc cõng vào role | Tháo gỡ gạt nhả (detach) các chính sách inline và managed policies trước kỳ thao tác |
| Tin nhắn trong hàng đợi SQS gan bầm lỳ kiếp gieo bục sa múa cọc xuất trồi lại | Cấu trúc rào liên thông sự kiện (event-source mapping) của Lambda kiên trinh buông thả công tắc enabled | Tắt vãn bãi/xóa hẳn con cọc event-source mapping trước thì khoảnh mác khi ra trát gõ dẹp hàng đợi SQS |

## Kết luận

Quy chu trình thau dọn bãi tài nguyên chỉ oai nghiêm giễu còi khải xướng tự mang mác vinh quy chốt hoàn tàn sau khi muôn cụm máy dịch vụ hao tiêu tàn độc nhất (high-cost services), những con hàng đợi, hòm cối bucket, bãi CSDL, hệ bộ cân bằng tải, trạm endpoint, vai trò quyền IAM và mạng VPC đều hoan khải bị nhả dẹp thu gọn, hoặc giả thọ khôn ngoan an tịnh giữ bấu lại muôn kiếp với lời ban trát minh văn cho phép tuất quyền chính khôn.
