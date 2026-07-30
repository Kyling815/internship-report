---
title: "Xử lý sự cố (Troubleshooting)"
date: 2024-01-01
weight: 12
chapter: false
pre: " <b> 5.12. </b> "
---

## Mục tiêu

Tài liệu hóa chi tiết các ca xử lý sự cố trong môi trường production thực tế, truy tìm nguyên nhân gốc rễ, cung cấp chuỗi lệnh chẩn đoán, giải pháp khắc phục và những biện pháp phòng ngừa thiết thực cho hệ thống.

## Bối cảnh kiến trúc

Phần lớn các sự cố phát sinh trong quá trình xây dựng và triển khai dự án đều nằm ở ranh giới tích hợp giữa các thành phần hạ tầng: đường truy cập Internet từ mạng VPC riêng tư, tình trạng sẵn sàng của các node thuộc cụm EKS, trình quản trị AWS Load Balancer Controller, dải biến môi trường trong GitHub Actions, quy tắc định tuyến trên CDN CloudFront, cách đặt tên hàng đợi, quy chuẩn từ khóa trong DynamoDB, phân quyền IAM, và độ vững chãi khi kích hoạt các luồng vi dịch vụ phụ thuộc vào AI.

## Bảng xử lý sự cố (Troubleshooting table)

| Sự cố (Incident) | Triệu chứng | Nguyên nhân (Root cause) | Lệnh chẩn đoán | Hướng khắc phục | Biện pháp phòng ngừa |
|---|---|---|---|---|---|
| Lỗi định tuyến sa hố trên NAT Gateway (NAT Gateway blackhole) | Các con node EKS trong cụm quản lý không thể tiến hành join vào trong cluster | Trục mặc định (default route) trong bảng định tuyến subnet private bấu nhầm sang một con máy NAT Gateway từng bị tháo gục chôn rách, trượt ngã trạng thái bảng định tuyến sang thảm kỵ `blackhole` | `aws ec2 describe-route-tables --region ap-southeast-1` | Tác tạo hoặc hồi phục trạm NAT Gateway, nạp cấu hình mới vào bảng định tuyến private, tiến hành gõ dựng hay thắp khang trang lại cụm node group | Luôn ra lệnh rà soát các đường rẽ default route mạn private trước thời khắc điều chuyển node group |
| Sập trình điều khiển AWS Load Balancer Controller | Trình quản trị load balancer lâm nạn bất lực chớ thể tạc sinh tài nguyên ALB | Trình controller nghẹn ngào chả cẩu trát mò thấu ID của VPC thông qua dịch vụ siêu dữ liệu instance metadata; tệp log vãi thông cáo lỗi `failed to get VPC ID from instance metadata` cõng theo chữ ký thời hạn cẩu sa rách `context deadline exceeded` | `kubectl logs -n kube-system deployment/aws-load-balancer-controller --tail=200` | Chủ động bổ nhĩ ấn thêu cụm tham mác `--aws-region=ap-southeast-1` và `--aws-vpc-id=vpc-0cfee519122ae18b4` bồi thẳng vào lệnh cất | Kiên trinh cấu định tường minh cọc mã khu vực region cùng số VPC ID giữa lòng các cõi môi trường sa rào cản ngăn chặn dịch vụ metadata |
| Tác vụ triển khai frontend trên GitHub Actions trượt bị bỏ bế (skipped) | Chu trình nặn đẩy trang frontend ốm nghẹt chẳng khởi thi hành | Lời điều kiện `if` giêng cài trên đầu thợ job vội bão vồ nhĩ thọ nhầm trúng cọc biến cõi environment trước thời điểm tệp environment của GitHub được cẩu tải thấu bãi | Khảo rà các trường điều kiện cài cạo trên thợ job trong kịch bản workflow và log bảng tóm vãng (run summary) | Ra rãnh bổ nạp cờ tham số bấu theo quy mác cọc biến cấp repository (repository variables); thực hiện bóc cô lập khâu thiêu frontend sa khỏi mác triển còi workload app EKS | Né hẫng kiên khôn việc nài đòi biến gắn chặt vùng environment khi nặn lệnh xét trên các đầu mác thợ job ở nhịp đầu workflow |
| Đính chính quy hoạch rãnh định tuyến CloudFront | Hiểu trượt cấu trúc điều tuyến cõi API và chat | Kho lưu S3 bị ghi khuyết điểm bấu thọ chao lọt ra phía đằng sau lưng ALB | `aws cloudfront get-distribution --id EQIGYNECXDYL8` | Sửa cọc chuẩn mực lại thiết kế: chuỗi mặc định điều bẻ về S3, còn dải `/api/*`, `/chat/*`, `/socket.io/*` thi đấu lao thẳng về origin ALB | Dùng thông ký cẩu rào từ cõi cấu hình behaviors của distribution như cõi chân lý duy nhất cho tài liệu |
| Vênh lệch tên gọi hàng đợi SQS | Lệnh tra khảo qua AWS CLI thông trả kết quả không có hàng đợi hoặc gặt sa vào rãnh sai con đợi | Khối biến `OUTBOX_QUEUE_URL` khai bên trong CloudShell trống rỗng tuế và người thao tác cẩu nhầm trúng cọc hàng đợi cũ rách `internship-outbox` | `aws sqs list-queues --region ap-southeast-1` | Chỉnh gõ cho ứng trói chuẩn con hàng đợi hiện hành `internship-prod-outbox` | An nhĩ đem khóa URL của hàng đợi an ngụ trong cối secret phục vụ triển khai và khẩn tra tên thực tế trước nhịp chạy rà test |
| Lệch thông số hàng đợi giữa tập lệnh kịch bản và môi trường thực ráo (runtime) | Cấu trúc sinh hàng đợi theo tệp kịch bản xô lệch so sánh với cấu cước thực tế của cõi hàng đợi ở thời điểm chay runtime | Các tệp script kho gốc mặc định cẩu gọi tên `internship-outbox-events` với chu kỳ visibility timeout là `60`; giữa lúc minh chứng hạ tầng chay runtime trút ra lại hiển bão con hàng đợi `internship-prod-outbox` đi đôi mốc visibility timeout là `120` | Kiểm tra nội sung `scripts/aws/provision-outbox-sqs.sh` và cẩu so gạt với thông cọc thuộc tính của hàng đợi trên AWS | Tôi tôn vinh và duy trì cọc bấu vào minh chứng lúc chạy (runtime evidence) cho bản tường thuật hiện thực; công tác rà sửa script kho repo cự tuế là một nghiệp vụ riêng biệt | Luôn ý thức nới canh chuế đồng bộ giữa bộ lệnh kịch bản hạ tầng với danh thọ cõi production thực tiễn |
| Dính từ khóa bị cấm của DynamoDB trong hàm Lambda (reserved keyword) | Hàm Lambda dội lỗi thất vọng gào than thông mác DynamoDB `ValidationException` | Lời cẩu cấu tạo chuỗi UpdateExpression thô trần bồi nhét trực tiếp trúng từ khóa bị giấu quyền `result` | Mở rà cọc nhật ký CloudWatch logs của hàm Lambda | Tiến hành thay hoán từ trần `result` ra mác bí ngữ `#result` kết cấu bảng quy nạp ánh xạ `"#result": "result"` | Tuân thủ tôn chỉ dùng cọc bảng ánh xạ nhãn thuộc tính (expression attribute names) cho các từ khóa trùng lặp bị giấu cấm |
| Bị chặn quyền hoán vai `PassRole` | Lệnh ban bố hoặc tác nghiệp gõ gọi cõi SageMaker khóc rêu gục ngã | Vai trò IAM đang dùng thi vắng khuyết chuế quyền hoán bão `iam:PassRole` đối với vai trò cõi SageMaker execution role | Khám xét tệp log thực thi cõi GitHub Actions và truy khảo cọc AWS CloudTrail (nếu bật) | Phối cấp chuỗi quyền hoán cọc `iam:PassRole` có giới hạn thu hẹp cho chuẩn vai trò và cất dịch vụ mong muốn | Cài rào thanh rà cọc quyền hạn IAM trước thì khúc mác bồi cho triển khai |
| Lỗi từ chối quyền truy xuất hoặc tra cứu ảnh `DescribeImages` từ ECR | Thợ job ban bố khốn trát chớ thể kiểm chứng ra nhãn SHA của ảnh image | Vai trò ủy quyền qua GitHub OIDC khốn hụt khuyết quyền rà đọc thông tin ECR | `aws ecr describe-images --repository-name internship-backend --image-ids imageTag=<GITHUB_SHA>` | Cung cẩu thêm quyền rà kiểm ảnh ECR với phạm vi bó hẹp theo tên kho và nhãn | Cẩn mẫn duy trì cọc cấu trúc chính sách (policy) của vai trò deploy tiệm chánh trùng khớp các điểm rà của workflow |
| Lỗi ủy quyền hoán vai qua GitHub OIDC (AssumeRoleWithWebIdentity failure) | Bước gặt cấp phép tài khoản AWS qua lệnh cẩu thất bại thảm lật | Sai sót trong chính sách an ninh cống hoán (trust policy), tham mác đối tượng (audience), rào cản nhánh/môi trường hoặc mã ARN vai trò lệch hẫng | Xem chuế tệp log lỗi của step `aws-actions/configure-aws-credentials` và mở soát cọc trust policy của role | Canh rà chốt chỉnh cấu trúc trust policy đi đôi biến quy `AWS_ROLE_TO_ASSUME` cho chính chánh | Thử nghiệm, kiểm chứng việc hoán quyền qua OIDC kỹ lưỡng trước lúc cài chốt chuối kịch bản deploy thẳng vào workflow |
| Trục trặc trong phép nhồi biến URL cơ sở dữ liệu từ Alembic (Alembic database URL interpolation failure) | Tiến trình migration đâm ngã té gục trước giờ kết nối thục thọ | Chuỗi URL cất CSDL bồi chốt ôm theo những ký tự đặc quấy khiến trình shell hoặc bộ đọc cấu hình sa sa mác tự động thông diễn (interpolation) sai lầm | `kubectl logs job/backend-migrate -n internship` | Chân chánh bấu găm biến `DATABASE_URL` trong hòm bí ẩn secret, tránh can thiệp hay xào gõ nhĩ qua lệnh shell thô bất bạo | Xem chuế mật mã kết nối DB tựa cọc dữ liệu tĩnh thi thoảng vô dạng, cấm thọ biên dịch nhầm |
| Bộ máy Docker ốm nghẹt trên WSL hoặc máy trạm lập trình địa phương | Khâu kiểm chứng tại chỗ/CI vãnh khước từ lệnh nặn build image | Trình nền Docker daemon ngã vắng bóng hoặc đứt gãy luồn kết bấu với WSL/Windows | `docker version` | Kích mở Docker Desktop hay nhả quyền test cho cối CI; thẳng thắn khai trình bước test build Docker là chưa chay thực ráo tại chỗ nếu thiếu docker | Soái rà nấc hiện diện của Docker ngay thì khoảnh mác trước khi ra cọc kiểm chứng container image |
| Cảnh báo cú pháp bash ShellCheck SC2155 | Bước kiểm định cú pháp script (shell lint) bị tuôn từ khước | Lệnh gõ nặn khai báo tên biến kết gộp thẳng cọ cùng phép gán tham con bị ShellCheck điểm còi cảnh giác | `shellcheck scripts/*.sh` | Tác gõ xé bẻ hai khâu khai báo cấu biến và phép gán cho xa tách rời ra | Ép thọ ráo việc test lint cú pháp bash trước khi ra lệnh bung khải workflow dispatch |
| Chẳng cẩu mò ra bóng hình SageMaker endpoint | Bước deploy AI hay thau bật công tắc worker đâm khóc rách | Điểm endpoint chưa thi thố tạc hình, hoặc chớ chịu múa cõi trạng thái `InService` | `aws sagemaker describe-endpoint --endpoint-name internship-qwen3-4b --region ap-southeast-1` | Tác tạo/phục khôi lại cọ endpoint hoặc kiên bám giữ nút gạt worker ở thế giam tịt | Gắn chặt rào cất ban visa cho worker vào tình hình `InService` của endpoint AI |
| Sai lệch trong cấu hình biến môi trường của frontend | Trang web frontend gõ lời cẩu nhầm sang con máy localhost ngay tại chốn production | Bị sót mất tham số cố định `VITE_API_BASE_URL=/api` hoặc cấu sai ranh cho dịch vụ chat | tra rà các biến được nhồi bên trong bản build và mục cẩu thẻ network của trình duyệt | Thi nặn dịch build đi kèm biến chuẩn `VITE_API_BASE_URL=/api` và để trống nhẽo cho mác `VITE_CHAT_API_BASE_URL` | Giữ bấu cố định cụm dải biến phục vụ build frontend chễm trệ trong workflow |
| Xử lý cấu cước chứng chỉ và tên miền trên ALB (ALB certificate/domain handling) | Điểm gõ công cộng bấu vãng theo chuế miền mặc định của ALB và CloudFront | Khuyết thiếu việc cài đặt tên miền riêng (custom domain) cùng chứng chỉ bảo an ACM | `aws elbv2 describe-listeners` kết cọc thám rà cấu cước thẻ certificate cỗi CloudFront viewer | Trưng dụng chứng chỉ mặc định thọ cọc của CloudFront cho chuế tên miền mặc định, hoặc lên kịch bản bồi nạp ACM/domain riêng rẽ sau | Tách bạch cẩu quy hoạch ban bố thi theo miền mặc định sa rã khỏi nghiệp vụ gia cố bảo an cho domain cá nhân biệt lập |

## Chi tiết về một số sự cố

### Lỗi định tuyến sa hố (blackhole) trên NAT Gateway

Các node công nhân mạn private trong EKS đòi hỏi khẩn thiết một tuyến cống mạng đi ra thế giới bên ngoài (outbound connectivity) nhằm chạm tay tới các AWS API và tiến hành kéo (pull) ảnh container. Ngay khoảnh khắc tuyến đi mặc định thuộc subnet private nhắm cẩu trúng mạn một máy NAT Gateway đã bị thu hồi hoặc chôn xóa, thẻ trạng thái con đường lập tức trượt sa hố ngã thành `blackhole`. Các node khốn bế ngã dỗi khước từ việc gia nạp (join) vào cluster hoặc trườn rách gầm lì ở thế ráo lỗi unhealthy.

Một số lệnh hữu ích để xử lý:

```bash
aws ec2 describe-route-tables --region ap-southeast-1
aws ec2 describe-nat-gateways --region ap-southeast-1
aws eks describe-nodegroup --cluster-name internship-prod --nodegroup-name <NODEGROUP_NAME> --region ap-southeast-1
kubectl get nodes -o wide
```

### Sự cố sập trình điều khiển AWS Load Balancer Controller

Trình quản trị controller gào khấn cầu viện hai tham số cấu định rõ ràng về vùng khu vực region cùng số VPC ID:

```text
--aws-region=ap-southeast-1
--aws-vpc-id=vpc-0cfee519122ae18b4
```

Các câu lệnh hữu ích:

```bash
kubectl get deployment,pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller -o wide
kubectl logs -n kube-system deployment/aws-load-balancer-controller --tail=200
kubectl describe ingress internship-public -n internship
```

### Đính chính kiến trúc định tuyến CloudFront

Thiết kế hiện tại chính xác cho hệ thống:

```text
CloudFront default *        -> S3 frontend origin
CloudFront /api/*           -> ALB origin -> backend
CloudFront /chat/*          -> ALB origin -> chat-service
CloudFront /socket.io/*     -> ALB origin -> chat-service
```

Những phác cất sai lệch ngốc nghếch kiên kiêng cấm vướng vào:

```text
S3 behind ALB
frontend running in EKS
```

### Từ khóa bị cấm của DynamoDB trong hàm Lambda (reserved keyword)

Lối gõ cấu lệnh dính án thất bại bắt nguồn do xưng tuế trực tiếp từ trần `result`. Chiêu thức sửa đổi hợp lệ áp dụng quy nạp ánh xạ tên nhãn (expression attribute name):

```json
{
  "UpdateExpression": "SET #result = :result",
  "ExpressionAttributeNames": {
    "#result": "result"
  }
}
```

Mã thông số của sự kiện test khói mĩ mãn thọ chứng là:

```text
lambda-smoke-fixed-1785220478
```

Đường dẫn văn thư nằm bên trong bãi cất S3 archive:

```text
outbox-archive/2026/07/28/lambda-smoke-fixed-1785220478.json
```

## Quy trình chẩn đoán tổng quát (General diagnostic workflow)

1. Xác thực tài khoản AWS đang kết nối và mã khu vực region đang thọ gõ.
2. Kiểm chứng bối cảnh cẩu lệnh Kubernetes context cùng không gian tên namespace.
3. Thanh rà chuế định lập behaviors cỗi CloudFront cùng thẻ trạng thái tài nguyên ALB Ingress.
4. Tra soát hiện trạng cuộn bản phát hành (rollouts) cõi các Deployment và danh bạ sự kiện (events) của các pod.
5. Đọc kỹ cọc nhật ký log nghiệp vụ cựu từ ứng dụng.
6. Soát thẩm tình trạng khỏe múa cõi hạ tầng tài nguyên AWS được quản lý.
7. Thanh kiểm các lỗi từ chối cộc quyền IAM (AccessDenied) đi cõng mạc dò tìm trong AWS CloudTrail (nếu có).
8. Khảo soát tình hình hàng đợi, hàm Lambda, bãi lỗi DLQ và bàn khử lặp dedupe mỗi dịp phát sinh sự cố cho rãnh tác nghiệp bất đồng bộ.
9. Tỉ mẩn ghi chép minh văn chính xấc mốc chu kỳ thời gian (timestamps), tệp kết quả trả ra từ dòng lệnh và giải pháp khắc phục triệt rã sau cùng.

Các câu lệnh kiểm chứng:

```bash
aws sts get-caller-identity
kubectl config current-context
kubectl get deployments,pods,svc,endpoints,ingress -n internship -o wide
kubectl get events -n internship --sort-by=.lastTimestamp
kubectl logs deployment/backend -n internship --tail=200
kubectl logs deployment/chat-service -n internship --tail=200
kubectl logs deployment/backend-outbox-dispatcher -n internship --tail=200
aws logs tail /aws/lambda/internship-outbox-handler --since 1h --region ap-southeast-1
```

## Kết quả mong đợi

Hồ sơ ghi nhận về bất kỳ sự cố nào khi chốt sổ cũng cần hoàn thiện đầy đủ các khía cạnh:

- xác định thành công nguyên nhân gốc rễ
- thu nhập được tệp minh chứng kết quả lệnh tra cứu
- triển khai thành khéo giải pháp khắc phục tháo hỏng
- ghi nhận tường trát kết quả kiểm chứng sau sửa
- tài liệu hóa quy chuẩn và biện pháp phòng ngừa

## Kết luận

Hồ sơ xử lý sự cố đóng vai trò chuyển hóa chuỗi bài học từ những vấp ngã thất bại tại production thành nguồn kiến thức vận hành tái sử dụng giá trị, đồng thời kiến tạo tiền đề hậu thuẫn tích cực cho lực lượng vận hành tương lai khả dĩ chẩn đoán nhanh mượt hơn các khúc mắc xoay around kết cấu mạng, uy quyền IAM, CDN CloudFront, hạ tầng SQS, hàm Lambda, và các dịch vụ AI trên SageMaker.
