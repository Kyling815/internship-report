---
title: "Triển khai frontend"
date: 2024-01-01
weight: 8
chapter: false
pre: " <b> 5.8. </b> "
---

## Mục tiêu

Thực hiện build mã nguồn frontend trên React/Vite, đăng tải bộ tệp đầu ra thẳng vào một S3 bucket riêng tư, và tổ chức phân phối an toàn thông qua CloudFront.

## Bối cảnh kiến trúc

Hiện tại, frontend được triển khai theo quy chuẩn của các tệp tĩnh đơn thuần, loại trừ mọi yếu tố ràng buộc chạy như workload trên EKS. Những tài nguyên Kubernetes cũ mang tên frontend gồm Deployment, Service, HPA, PDB, đi kèm khối ALB Ingress cũ đã bị bóc tháo tiệt cọ, nhằm chặn đứng nguy cơ các đợt áp triển khai mã app vào EKS trong tương lai lầm lọt thi thoảng vô ý vác còi tự nặn sinh ra lại chúng.

Điểm truy cập công cộng hiện thời của người dùng:

```text
https://dhm2rz5nmsibj.cloudfront.net
```

Mã số định danh cọ CloudFront distribution:

```text
EQIGYNECXDYL8
```

## Cấu hình môi trường Vite

Quy chuỗi build tĩnh mạn production cho frontend sử dụng các tham mác:

| Biến | Giá trị production | Mục đích |
|---|---|---|
| `VITE_API_BASE_URL` | `/api` | Ép toàn bạo các lời gõ gọi backend API luân chảy trót lọt qua CloudFront cùng rãnh ALB |
| `VITE_CHAT_API_BASE_URL` | chuỗi rỗng | Ban visa cho bộ máy runtime trình duyệt ung dung trút lời qua cung đường `/chat` ngoài cõi localhost |

Bộ gọi giao dịch API client phía frontend giữ nguyên thông số gán định ở chế độ lập trình tại chỗ khi khuyết thiếu tham số truyền cấu hình:

- Chuỗi mặc định của API: `http://localhost:8001`
- Chuỗi mặc định của Chat ở trình duyệt cá nhân tại chỗ: `http://localhost:3000`
- Chuỗi mặc định của Chat ở thế giới ngoại localhost: `/chat`
- Đường dẫn Socket.IO path: `/socket.io`

## Các lệnh build

Ra lệnh thao tác thi thực tại gốc thư mục repo:

```bash
cd frontend
npm ci
VITE_API_BASE_URL=/api VITE_CHAT_API_BASE_URL= npm run build
```

Thư mục kết quả đầu ra theo kỳ vọng:

```text
frontend/dist
```

Trình lệnh script bạt khai thâm kiểm tra tự dọn bãi nhận diện cả `frontend/dist` lẫn `frontend/build`, thế nhưng đầu ra sinh tệp mĩ mãn hiện hành do Vite ban xuất luôn nằm ngụ yên ổn tại con rãnh `frontend/dist`.

## Đăng tải lên S3

Tập kịch bản chiêu xuất lực lượng cho môi trường production đóng lệnh:

```bash
bash scripts/ci/deploy-frontend.sh
```

Các biến ràng buộc bắt buộc:

| Biến | Mục đích |
|---|---|
| `FRONTEND_DEPLOY_ENABLED` | Bất di bất dịch thi định giá trị `true` |
| `FRONTEND_BUCKET` | Hòm S3 đích nhắm, chẳng hạn kiểu dạng `internship-prod-frontend-<AWS_ACCOUNT_ID>` |
| `CLOUDFRONT_DISTRIBUTION_ID` | Mã định danh distribution phục vụ việc gõ xóa bộ đệm cache (invalidate) |
| `VITE_API_BASE_URL` | Gán bằng `/api` |
| `VITE_CHAT_API_BASE_URL` | Gán rỗng tuột |

Tập script tuân thủ cảnh giác khóa nhốt kiên kỵ ranh giới bucket ở tư thế vô danh bí hiểm riêng tư:

```bash
aws s3api put-public-access-block \
  --bucket internship-prod-frontend-<AWS_ACCOUNT_ID> \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

Toàn thể dải tệp tĩnh (static assets) buông mình trôi thâu tải lên vân gắn kèm trường mác giữ cache dài hạn thọ sinh bền lâu:

```bash
aws s3 sync frontend/dist s3://internship-prod-frontend-<AWS_ACCOUNT_ID> \
  --delete \
  --exclude index.html \
  --cache-control public,max-age=31536000,immutable
```

Riêng tệp `index.html` vinh hoa hưởng luồng nạp bồi cô lập, cắm rào kiêu sa chối cự việc bấu giữ trong cối nhớ tạm (no-cache semantics):

```bash
aws s3 cp frontend/dist/index.html s3://internship-prod-frontend-<AWS_ACCOUNT_ID>/index.html \
  --cache-control no-cache \
  --content-type text/html
```

## Cấu hình CloudFront

Trình kịch bản giúp tay `scripts/aws/ensure-cloudfront.sh` sắm vóc dáng uyên thâm đảm nhận rà thẩm hoặc tác sinh ra tài nguyên distribution mới. Thiết lập kiến trúc hiện hành được nạp dải:

| Behavior | Origin | Ghi chú |
|---|---|---|
| Mặc định `*` | S3 frontend bucket | Giao diện tĩnh của frontend cùng các tệp nền cho SPA |
| `/api/*` | ALB | Dữ liệu REST API backend |
| `/chat/*` | ALB | REST API thuộc về dịch vụ chat |
| `/socket.io/*` | ALB | Giao thông luân chuyển cho Socket.IO |

CloudFront khôn ngoan giêu thiết lập cơ chế cứu rỗi điều bẻ dự phòng cho SPA (SPA fallback):

| Lỗi (Error) | Đường dẫn phản hồi | Mã phản hồi |
|---|---|---|
| 403 | `/index.html` | 200 |
| 404 | `/index.html` | 200 |

Ra lệnh xóa bỏ nội dung bộ nhớ đệm cũ kỹ lạc hậu (CloudFront invalidation):

```bash
aws cloudfront create-invalidation \
  --distribution-id EQIGYNECXDYL8 \
  --paths "/*"
```

## Triển khai frontend qua GitHub Actions

Ra tay gõ chọn điều rũ thực thi chế độ workflow dispatch theo mô hình:

```text
GitHub -> Actions -> CI/CD -> Run workflow -> mode: deploy-frontend
```

Quy tắc bước nhảy của thợ job `deploy-frontend`:

1. Tiến hành ủy quyền và nạp định danh tài khoản AWS credentials cẩn kỵ thông qua luồng an ninh OIDC.
2. Thiết định môi trường máy Node.js bám theo giá trị ghi ở biến workflow `NODE_VERSION`.
3. Thẩm định cẩn mật sức khỏe đường rẽ cọc ALB tại điểm trạm `/api/health/ready` lẫn `/chat/health/ready`.
4. Gọi khởi nháy tệp lệnh `scripts/ci/deploy-frontend.sh`.
5. Đẩy tút mượt chuỗi tập tin giao diện tĩnh của frontend an trú vào lòng hòm S3.
6. Phát đi trát thi thoảng xóa bạt tàn nhẫn cọc dữ liệu đệm cũ qua lệnh CloudFront invalidation.

## Kiểm chứng

Khảo rà tình hình CDN CloudFront:

```bash
curl -I https://dhm2rz5nmsibj.cloudfront.net/
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/api/health/ready
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/chat/health/ready
```

Thanh rà rào cản ngăn công khai trần tuột của hòm S3:

```bash
aws s3api get-public-access-block \
  --bucket internship-prod-frontend-<AWS_ACCOUNT_ID>
```

Khám xét thông số cấu hình tài nguyên distribution:

```bash
aws cloudfront get-distribution --id EQIGYNECXDYL8
aws cloudfront list-invalidations --distribution-id EQIGYNECXDYL8
```

## Kết quả mong đợi

- Trang frontend hoành nghênh hiện múa êm thắm từ sau vây cống mạng CloudFront.
- Ranh giới cản phá ngăn mạn cất chặn việc mở cửa lộ thiên (public access) của hòm S3 tiếp chặng đứng sừng sững gác vững vàng.
- Dải luân điều hướng tuyến `/api/*`, `/chat/*`, kết mác cùng `/socket.io/*` răm rắp dốc đầu về rẽorigin ALB hợp hiền.
- Chuỗi tra truy nhập thẳng (deep links) bỗng chốc bốc sa hẫng đều khôn lanh được CDN nén trả quay đầu theo vạch `index.html`.
- Một bản trát ban lệnh xóa cối đệm (invalidation) hiển lộ oai phong ngay tại hồi sau đợt bung ban triển khai.

## Các lỗi thường gặp

| Triệu chứng | Nguyên nhân | Hướng khắc phục |
|---|---|---|
| Tác vụ thợ job của frontend khinh bạc giễu lướt qua bẻ bỏ | cọc biến mác `FRONTEND_DEPLOY_ENABLED` trượt giá trị true ở tầm bắt không gian biến cho job vồ vỗ | Hãy cẩn thêu định trát cờ cho cọc biến ở cấu hình biến GitHub environment theo đúng thói gặm nhấm workflow |
| Trục trặc lời gõ gọi API chao bốc lao húc sai về cọc localhost ở cõi production | Quên bẳng mang cắp cho tham mác biến trường `VITE_API_BASE_URL=/api` | Thi nặn build lại từ gốc phối nạp sung túc tham mác biến Vite chốn production |
| Trang CDN CloudFront ngậm mồi khước trần giao diện bộ cũ kỹ | Tập file tĩnh gõ nhầm kho cối đệm cache hay sẩy bãi sót việc phát lệnh invalidation | Kiểm kê trạng thái danh bạ invalidation kết cọc thẩm quy chế cache control của tệp `index.html` |
| Luồng chui vãng kho S3 thề khước cự tuế từ cất sau cánh CloudFront | Quyền hạn bucket policy khiếm khuyết chuỗi cam gạt giao tình OAC | Kích chuông thi thi rào cho kịch bản `ensure-cloudfront.sh` kèm thông ký số tài khoản cùng ID của distribution |
| Điểm gõ thẳng vào website tĩnh qua origin S3 chọc chát cự tuệ dội bãi | Trạng thái kiên cố 100% đúng quy luật thiết lập an ninh thọ thi | Hòm frontend vững chí giam cọc ở thế private ngặt nghẽo, chỉ đón nhở ngọ rẽ cẩu nhờCDN CloudFront buông thả |
| Trượt rách kênh thời gian thực Socket.IO | Sa sẩy quên cất behavior mang ranh `/socket.io/*` bên trong cống CloudFront hoặc tuột trượt trên vạch định tuyến ALB | Thanh soát tỉ mẩn behavior bên CloudFront đi đôi cọc đường dẫn Ingress của ALB |

## Việc tháo rỡ các tài nguyên frontend cũ trên Kubernetes

Cấu hình hạ tầng nay vững chí kiên định cất tay trục hủy tiệt toàn thể dải tài nguyên frontend khai trên Kubernetes. Tuyệt đối kiên răn không được lầm tưởng dựng ra phác lại:

- `Deployment/frontend`
- `Service/frontend`
- ranh giới HPA chuyên trách cho frontend
- ngân sách PDB cống hiến cho frontend
- cọc ALB Ingress gánh phần cự rẽ riêng tư của frontend
- chốt đường rãnh triển khai `FRONTEND_IMAGE` thọ cọc bên trong luồng thi app vào EKS

Frontend kiên cọc vinh thọ duy nhất một lần dịch build tĩnh rẽ phân cất gửi trên hai cọc trụ bộ đôi S3 kết cống CloudFront CDN.

## Kết luận

Thao tác triển khai frontend cất mốc ăn còi thông vãn chính cống ngay chặng các tệp build sinh từ Vite nhở cẩu im lặng an ngự trong lòng S3, mạng CloudFront ra trát trút xóa rũ nhẵn củi xác đệm cũ rách, và trọn muôn ngọ cộng đồng có thể hưng múa chiêu nghênh giao diện ứng dụng từ cung rễ địa chỉ web chính danh `https://dhm2rz5nmsibj.cloudfront.net`, giữa lúc luông API/realtime mỉm cười chao lướt êm trót lọt sang mạn backend/chat thi nhau bám cống CloudFront cùng cánh cổng ALB.
