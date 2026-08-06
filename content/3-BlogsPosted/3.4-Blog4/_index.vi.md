---
title: "Blog 4"
date: 2026-07-29
weight: 4
chapter: false
pre: " <b> 3.4. </b> "
---

# AWS Networking Advanced: 3 kỹ thuật nâng cấp VPC chuẩn doanh nghiệp

## Giới thiệu

Mô hình Amazon VPC cơ bản gồm Public Subnet, Private Subnet và NAT Gateway là nền tảng phù hợp để bắt đầu triển khai ứng dụng trên AWS. Kiến trúc này giúp tách các tài nguyên cần truy cập trực tiếp từ Internet khỏi những thành phần nội bộ như application server, database và cache.

Tuy nhiên, khi hệ thống mở rộng thành nhiều môi trường như Development, Staging và Production hoặc được chia thành nhiều microservices và VPC khác nhau, kiến trúc cơ bản có thể bắt đầu xuất hiện ba hạn chế lớn:

- Chi phí NAT Gateway tăng cao khi các tài nguyên trong Private Subnet thường xuyên truy cập Amazon S3, Amazon DynamoDB và những dịch vụ AWS khác.
- Rủi ro Single Point of Failure nếu toàn bộ lưu lượng outbound chỉ phụ thuộc vào một NAT Gateway trong một Availability Zone.
- Việc quản lý kết nối trở nên phức tạp khi nhiều VPC được kết nối với nhau bằng VPC Peering theo mô hình mạng lưới.

Bài viết này trình bày ba kỹ thuật nâng cấp kiến trúc VPC theo hướng phù hợp hơn với hệ thống doanh nghiệp, bao gồm VPC Endpoints, Multi-AZ networking và AWS Transit Gateway.


## 1. Giảm chi phí và tăng bảo mật với VPC Endpoints

### Vấn đề khi sử dụng NAT Gateway

Các EC2 instances, container hoặc application servers nằm trong Private Subnet thường không có địa chỉ IP công cộng. Khi những tài nguyên này cần truy cập Amazon S3, DynamoDB hoặc các AWS services khác, lưu lượng có thể phải đi qua NAT Gateway.

Luồng kết nối cơ bản có thể được mô tả như sau:

```text
Private Subnet
      |
      v
NAT Gateway
      |
      v
AWS Public Service Endpoint
```

Cách triển khai này có thể phát sinh phí NAT Gateway theo giờ và phí xử lý dữ liệu. Lưu lượng cũng phải đi qua public service endpoint dù cả ứng dụng và dịch vụ đích đều hoạt động bên trong hạ tầng AWS.

### Gateway Endpoint

Gateway Endpoint được sử dụng cho hai dịch vụ chính:

- Amazon S3.
- Amazon DynamoDB.

Sau khi Gateway Endpoint được tạo và liên kết với route table của Private Subnet, lưu lượng đến S3 hoặc DynamoDB có thể được chuyển trực tiếp qua mạng nội bộ của AWS mà không cần đi qua NAT Gateway.

Luồng kết nối mới:

```text
Private Subnet
      |
      v
VPC Gateway Endpoint
      |
      v
Amazon S3 hoặc Amazon DynamoDB
```

Gateway Endpoint mang lại các lợi ích:

- Không cần sử dụng NAT Gateway cho lưu lượng đến S3 và DynamoDB.
- Giữ lưu lượng bên trong mạng AWS.
- Giảm chi phí xử lý dữ liệu qua NAT Gateway.
- Có thể kiểm soát quyền truy cập bằng endpoint policy.
- Giảm việc phụ thuộc vào kết nối Internet outbound.

Gateway Endpoint cho S3 và DynamoDB không thu phí theo giờ sử dụng endpoint, vì vậy đây thường là một trong những giải pháp đầu tiên nên cân nhắc khi tối ưu chi phí network.

### Interface Endpoint và AWS PrivateLink

Đối với những dịch vụ không hỗ trợ Gateway Endpoint, hệ thống có thể sử dụng Interface Endpoint.

Interface Endpoint tạo các Elastic Network Interface trong subnet và gán địa chỉ IP nội bộ cho chúng. Ứng dụng có thể sử dụng private IP hoặc private DNS để truy cập dịch vụ AWS mà không cần đi qua Internet công cộng.

Một số dịch vụ thường được truy cập thông qua Interface Endpoint gồm:

- Amazon CloudWatch.
- AWS Secrets Manager.
- Amazon ECR.
- AWS Systems Manager.
- AWS Key Management Service.
- Amazon Kinesis.

Interface Endpoint sử dụng AWS PrivateLink để duy trì lưu lượng trong mạng AWS.

So với việc truy cập thông qua NAT Gateway, giải pháp này có thể:

- Giảm lưu lượng Internet outbound.
- Kiểm soát truy cập bằng Security Group.
- Hạn chế phạm vi tấn công.
- Hỗ trợ kiến trúc private networking rõ ràng hơn.
- Cho phép workload trong Private Subnet truy cập dịch vụ AWS bằng private IP.

Interface Endpoint vẫn có chi phí theo giờ và lưu lượng xử lý, vì vậy cần so sánh với chi phí NAT Gateway dựa trên lưu lượng thực tế của hệ thống.

## 2. Triển khai Multi-AZ và tránh chi phí Cross-AZ không cần thiết

### Tại sao cần nhiều Availability Zones?

Một Availability Zone có thể gặp sự cố độc lập. Nếu toàn bộ application server, database và network egress đều được đặt trong cùng một AZ, hệ thống có thể bị gián đoạn khi AZ đó gặp vấn đề.

Để tăng tính sẵn sàng, kiến trúc production thường được triển khai trên ít nhất hai Availability Zones.

Ví dụ:

```text
Availability Zone A
- Public Subnet A
- Private Subnet A
- NAT Gateway A
- Application instances A

Availability Zone B
- Public Subnet B
- Private Subnet B
- NAT Gateway B
- Application instances B
```

Trong mô hình này, mỗi Availability Zone có một đường outbound độc lập. Nếu một AZ gặp sự cố, workload trong AZ còn lại vẫn có thể sử dụng NAT Gateway và các tài nguyên còn hoạt động trong AZ đó.

### Tránh Single Point of Failure

Nếu hệ thống chỉ sử dụng một NAT Gateway trong AZ-A, các workload nằm trong AZ-B phải truyền lưu lượng sang AZ-A trước khi truy cập Internet.

Mô hình này tạo ra hai vấn đề:

1. NAT Gateway trong AZ-A trở thành điểm phụ thuộc duy nhất.
2. Lưu lượng từ AZ-B sang AZ-A có thể phát sinh chi phí truyền dữ liệu Cross-AZ.

Một kiến trúc phù hợp hơn là triển khai một NAT Gateway trong mỗi Availability Zone đang hoạt động. Route table của từng Private Subnet sẽ trỏ đến NAT Gateway nằm trong cùng AZ.

Ví dụ:

```text
Private Subnet A -> NAT Gateway A
Private Subnet B -> NAT Gateway B
```

Nếu AZ-A gặp sự cố, tài nguyên trong AZ-B vẫn có đường outbound riêng và không phụ thuộc vào NAT Gateway A.

### AZ-Aware Routing

AZ-Aware Routing là cách ưu tiên kết nối giữa các workload và dependency nằm trong cùng Availability Zone.

Ví dụ:

- Application instance trong AZ-A ưu tiên sử dụng NAT Gateway A.
- Workload trong AZ-B ưu tiên kết nối cache node trong AZ-B.
- Load balancer phân phối request đến các target phù hợp.
- Database replica hoặc cache node được phân bố giữa nhiều AZ.
- Service discovery ưu tiên endpoint gần workload hơn khi kiến trúc hỗ trợ.

Cách bố trí này giúp:

- Giảm lưu lượng Cross-AZ không cần thiết.
- Giảm độ trễ network.
- Hạn chế chi phí truyền dữ liệu giữa các AZ.
- Giúp mỗi AZ có khả năng vận hành độc lập tốt hơn.

Tuy nhiên, việc ưu tiên kết nối trong cùng AZ vẫn phải được cân bằng với yêu cầu High Availability. Ứng dụng không nên phụ thuộc hoàn toàn vào một tài nguyên trong cùng AZ nếu tài nguyên đó không có cơ chế failover.

## 3. Quản lý kết nối nhiều VPC bằng AWS Transit Gateway

### Hạn chế của VPC Peering

VPC Peering phù hợp khi hệ thống chỉ có một số lượng nhỏ VPC. Hai VPC có thể được kết nối trực tiếp và giao tiếp với nhau bằng private IP.

Tuy nhiên, VPC Peering không hỗ trợ transitive routing.

Ví dụ:

```text
VPC-A <-> VPC-B
VPC-B <-> VPC-C
```

Việc VPC-A kết nối với VPC-B và VPC-B kết nối với VPC-C không có nghĩa là VPC-A có thể tự động giao tiếp với VPC-C.

Nếu nhiều VPC cần kết nối trực tiếp với nhau, số lượng VPC Peering connections có thể tăng theo công thức:

```text
N(N - 1) / 2
```

Ví dụ, với 10 VPC, mô hình full mesh có thể cần đến 45 kết nối peering.

Khi đó, việc quản lý route table, CIDR, Security Group và network policy trở nên phức tạp. Việc thêm một VPC mới cũng có thể yêu cầu tạo nhiều kết nối và cập nhật nhiều route table khác nhau.

### Transit Gateway như một Cloud Router

AWS Transit Gateway hoạt động như một router trung tâm cho nhiều VPC và hệ thống mạng khác nhau.

Các thành phần có thể kết nối với Transit Gateway gồm:

- Amazon VPC.
- Site-to-Site VPN.
- AWS Direct Connect thông qua Direct Connect Gateway.
- VPC thuộc nhiều AWS accounts.
- Các môi trường Development, Staging và Production.
- Shared Services VPC.
- Mạng từ Data Center On-Premises.

Thay vì tạo kết nối trực tiếp giữa từng cặp VPC, mỗi VPC chỉ cần tạo một attachment đến Transit Gateway.

```text
             Development VPC
                    |
                    |
Shared VPC ---- Transit Gateway ---- Production VPC
                    |
                    |
             On-Premises Network
```

Mô hình hub-and-spoke này giúp đơn giản hóa network topology và tập trung việc quản lý routing.

### Phân vùng mạng bằng Transit Gateway Route Tables

Transit Gateway có thể sử dụng nhiều route table để kiểm soát VPC nào được phép giao tiếp với VPC nào.

Ví dụ:

- Development VPC có thể truy cập Shared Services VPC.
- Production VPC có thể truy cập Shared Services VPC.
- Development VPC không được phép kết nối trực tiếp đến Production VPC.
- On-Premises Network chỉ được truy cập một số subnet nhất định.
- Security VPC có thể kiểm tra lưu lượng trước khi chuyển đến các VPC khác.

Việc phân vùng này giúp:

- Hạn chế lateral movement giữa các môi trường.
- Phân tách Development, Staging và Production rõ ràng hơn.
- Quản lý network policy từ một vị trí tập trung.
- Đơn giản hóa việc thêm VPC mới.
- Hỗ trợ kiến trúc multi-account với AWS Organizations.

## So sánh mô hình VPC cơ bản và kiến trúc nâng cao

| Tiêu chí | Mô hình cơ bản | Mô hình nâng cao |
|---|---|---|
| Truy cập S3 và DynamoDB | Đi qua NAT Gateway hoặc public endpoint | Đi qua Gateway Endpoint |
| Truy cập các AWS services khác | Thường sử dụng NAT Gateway | Sử dụng Interface Endpoint và AWS PrivateLink khi phù hợp |
| High Availability | Có thể chỉ sử dụng một NAT Gateway | NAT Gateway độc lập trong từng Availability Zone |
| Cross-AZ traffic | Dễ phát sinh nếu routing không được tối ưu | Hạn chế bằng AZ-aware routing |
| Kết nối nhiều VPC | VPC Peering được cấu hình thủ công từng cặp | Transit Gateway quản lý tập trung |
| Phân tách Dev và Prod | Phụ thuộc vào nhiều route và peering connections | Sử dụng Transit Gateway route tables |
| Khả năng mở rộng | Phù hợp với hệ thống nhỏ | Phù hợp hơn với hệ thống nhiều VPC và nhiều account |
| Quản trị | Dễ triển khai ban đầu nhưng khó kiểm soát khi mở rộng | Phức tạp hơn lúc thiết kế nhưng dễ quản lý tập trung |

## Khi nào nên sử dụng từng giải pháp?

### Sử dụng VPC Endpoints khi:

- Workload trong Private Subnet thường xuyên truy cập Amazon S3 hoặc DynamoDB.
- Ứng dụng cần truy cập AWS services mà không đi qua Internet công cộng.
- Muốn giảm lưu lượng và chi phí xử lý qua NAT Gateway.
- Hệ thống có yêu cầu cao về bảo mật dữ liệu.
- Muốn giới hạn quyền truy cập bằng endpoint policy.

### Sử dụng Multi-AZ NAT Gateway khi:

- Hệ thống yêu cầu High Availability.
- Workload được triển khai trên nhiều Availability Zones.
- Không muốn một NAT Gateway trở thành Single Point of Failure.
- Muốn hạn chế lưu lượng Cross-AZ không cần thiết.
- Hệ thống cần duy trì outbound connectivity khi một AZ gặp sự cố.

### Sử dụng AWS Transit Gateway khi:

- Hệ thống có nhiều VPC hoặc nhiều AWS accounts.
- Cần kết nối mạng On-Premises với AWS.
- VPC Peering bắt đầu trở nên khó quản lý.
- Cần phân tách Development, Staging và Production.
- Muốn kiểm soát routing từ một vị trí trung tâm.
- Cần xây dựng mô hình Shared Services hoặc Security Inspection tập trung.

## Lưu ý về chi phí

Kiến trúc network nâng cao không có nghĩa là mọi thành phần đều rẻ hơn.

Gateway Endpoint cho S3 và DynamoDB có thể giúp giảm lưu lượng qua NAT Gateway. Tuy nhiên, Interface Endpoint, NAT Gateway và Transit Gateway đều có mô hình tính phí riêng.

Trước khi triển khai, cần phân tích:

- Tổng lưu lượng dữ liệu hàng tháng.
- Các dịch vụ AWS được truy cập thường xuyên.
- Số lượng Availability Zones.
- Số lượng VPC và Transit Gateway attachments.
- Tần suất truyền dữ liệu giữa các AZ.
- Lưu lượng Internet outbound.
- Yêu cầu bảo mật và tính sẵn sàng.
- Chi phí vận hành và độ phức tạp trong quản trị.

Mục tiêu không phải là giảm chi phí bằng mọi cách, mà là tìm được sự cân bằng giữa chi phí, bảo mật, hiệu năng, khả năng mở rộng và High Availability.

## Kết luận

Mô hình Public Subnet, Private Subnet và NAT Gateway là nền tảng tốt để bắt đầu xây dựng hệ thống trên AWS. Tuy nhiên, khi hệ thống phát triển thành nhiều môi trường, nhiều VPC hoặc nhiều AWS accounts, network architecture cũng cần được nâng cấp.

Ba kỹ thuật quan trọng gồm:

1. Sử dụng VPC Endpoints để giữ lưu lượng truy cập AWS services trong mạng nội bộ và giảm phụ thuộc vào NAT Gateway.
2. Triển khai Multi-AZ với NAT Gateway độc lập trong từng Availability Zone để tăng tính sẵn sàng và hạn chế Cross-AZ traffic.
3. Sử dụng AWS Transit Gateway để quản lý kết nối giữa nhiều VPC theo mô hình tập trung.

Tối ưu kiến trúc VPC không chỉ là bài toán routing. Đây còn là quá trình cân bằng giữa bảo mật, khả năng mở rộng, tính sẵn sàng, hiệu năng và chi phí.

Một Enterprise VPC Architecture tốt cần được thiết kế dựa trên nhu cầu thực tế của hệ thống. Không nên bổ sung thêm nhiều dịch vụ chỉ để kiến trúc trở nên phức tạp hơn mà không tạo ra giá trị rõ ràng.

## Thông tin bài đăng

- **Chủ đề:** Nâng cấp kiến trúc Amazon VPC cho hệ thống doanh nghiệp.
- **Ngày đăng:** 29/07/2026.
- **Nền tảng:** AWS Study Groups.
- **Trạng thái:** Published.
- **Public link:** [Blog 4 trên AWS Study Groups](https://www.facebook.com/groups/awsstudygroupfcj/permalink/2225997548165205/#)

