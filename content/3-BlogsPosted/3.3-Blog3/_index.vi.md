---
title: "Blog 3"
date: 2026-07-28
weight: 3
chapter: false
pre: " <b> 3.3. </b> "
---

# Một chút “thu hoạch” sau hành trình làm Software Engineer: từ viết code đến lúc tự tay làm hệ thống sập rồi tự cứu lại

## Giới thiệu

Trước đây, tôi từng nghĩ công việc của một Software Engineer chủ yếu là tiếp nhận yêu cầu, viết code, hoàn thiện tính năng và đưa source code lên repository. Tuy nhiên, sau khi trực tiếp tham gia phát triển một hệ thống tương đối đầy đủ, tôi nhận ra rằng viết được code chỉ là bước đầu tiên.

Phần khó hơn nằm ở việc làm sao để đoạn code đó có thể hoạt động ổn định trong một hệ thống thật, nơi có nhiều thành phần phụ thuộc lẫn nhau như frontend, backend API, database, message queue, container, Kubernetes, CI/CD và hạ tầng AWS.

Trong quá trình phát triển AI-Powered Internship Application Tracker, tôi đã có cơ hội làm việc với FastAPI, React, PostgreSQL, Redis, DynamoDB, Amazon SQS, Docker, Kubernetes, GitHub Actions và nhiều dịch vụ AWS khác. Quá trình này không chỉ giúp tôi học thêm công nghệ mà còn thay đổi cách tôi nhìn nhận việc xây dựng, triển khai và vận hành phần mềm.


## Chạy được ở local chưa có nghĩa là chạy được trong production

Trong môi trường local, các thành phần thường được đặt gần nhau và dễ kiểm soát. Database có thể chạy trong Docker Compose, Redis nằm trong cùng network, còn các biến môi trường được khai báo trong file `.env`.

Tuy nhiên, khi hệ thống được chuyển sang Kubernetes hoặc AWS, cách các thành phần giao tiếp trở nên phức tạp hơn. Một service muốn kết nối với service khác cần sử dụng đúng DNS, namespace, port và network configuration. Ứng dụng muốn kết nối đến database cần có connection string, route và security group phù hợp. Các pod nằm trong private subnet cũng cần có đường outbound thích hợp để truy cập Internet hoặc các dịch vụ bên ngoài.

Từ đó, tôi hiểu rằng khả năng vận hành của một ứng dụng không chỉ phụ thuộc vào source code mà còn phụ thuộc vào toàn bộ môi trường bao quanh nó.

## Docker và bài học về môi trường chạy

Docker giúp chuẩn hóa môi trường chạy giữa các máy, nhưng việc container hóa hệ thống cũng phát sinh nhiều vấn đề mới.

Một container có thể đang chạy nhưng health check vẫn thất bại. Ứng dụng có thể khởi động trước khi database sẵn sàng. Biến môi trường có thể tồn tại trên máy nhưng chưa được truyền đúng vào container. Ngoài ra, các vấn đề liên quan đến port, volume, Docker Desktop và WSL cũng có thể làm hệ thống không hoạt động dù code hoàn toàn không thay đổi.

Những trải nghiệm này giúp tôi hình thành thói quen kiểm tra không chỉ code mà còn cả môi trường thực thi:

- Container đang nhận những biến môi trường nào?
- Dependency đã sẵn sàng chưa?
- Các service có nằm trong cùng network không?
- Port có được expose và mapping chính xác không?
- Health check đang kiểm tra hành vi nào của ứng dụng?

## CI/CD không phải là một file YAML thần kỳ

GitHub Actions mang lại khả năng tự động hóa lint, test, build image, scan security và deployment. Tuy nhiên, pipeline chỉ hoạt động khi tất cả giả định bên trong nó đều chính xác.

Workflow có thể thất bại do thiếu secret, sai điều kiện branch, image tag không đồng nhất hoặc runner thiếu công cụ. Một job cũng có thể bị bỏ qua vì biến môi trường hoặc điều kiện thực thi không đúng.

Qua quá trình xử lý các workflow thất bại, tôi nhận ra rằng CI/CD không chỉ là viết một file cấu hình. Người phát triển cần hiểu rõ từng bước đang làm gì, dữ liệu nào được truyền giữa các job và hệ thống đích cần ở trạng thái nào trước khi deployment được thực hiện.

## IAM và nguyên tắc không đoán quyền truy cập

AWS IAM là một trong những phần khiến tôi mất nhiều thời gian nhất. Ban đầu, tôi nghĩ rằng khi gặp lỗi thiếu quyền thì chỉ cần thêm một policy có action tương ứng.

Tuy nhiên, quyền truy cập AWS còn phụ thuộc vào trust policy, principal, condition, repository, branch, resource ARN và cách từng AWS action hỗ trợ resource-level permission.

Một policy nhìn có vẻ chặt chẽ chưa chắc đã hoạt động đúng. Ví dụ, một số action bắt buộc phải sử dụng resource `"*"`, trong khi các action khác có thể giới hạn vào một ARN cụ thể.

Thay vì tiếp tục phỏng đoán, tôi bắt đầu sử dụng công cụ mô phỏng policy để kiểm tra từng action. Bài học quan trọng được rút ra là:

> Không nên đoán quyền truy cập. Cần kiểm chứng chính xác action nào được phép và action nào đang bị từ chối.

## Kubernetes: trạng thái Running chưa chắc có nghĩa là hệ thống khỏe

Kubernetes có thể hiển thị một pod ở trạng thái `Running`, nhưng điều đó chỉ cho biết container vẫn đang tồn tại. Nó không đảm bảo rằng ứng dụng bên trong đang hoạt động chính xác.

Pod có thể không kết nối được Redis, migration chưa chạy, API không phản hồi hoặc service không có kết nối outbound. Vì vậy, ngoài trạng thái pod, cần kiểm tra thêm:

- Application logs.
- Readiness và liveness probes.
- Kubernetes Service và Ingress.
- Database migration.
- Network connectivity.
- Các dependency bên dưới.

Điều này giúp tôi hiểu rằng không nên chỉ quan sát trạng thái hạ tầng. Cần kiểm tra hành vi thật của ứng dụng thông qua endpoint và luồng người dùng thực tế.

## Sự cố NAT Gateway và bài học về network

Một trong những sự cố đáng nhớ nhất là khi tôi tắt NAT Gateway để giảm chi phí. Sau đó, các pod trong private subnet không còn truy cập được Internet, một số kết nối đến AWS services bị gián đoạn và quá trình deployment bắt đầu thất bại.

Do code, IAM và security group không thay đổi, nguyên nhân ban đầu khá khó nhận ra. Sau khi kiểm tra lại network architecture, tôi phát hiện route outbound đã bị mất vì NAT Gateway không còn hoạt động.

Sự cố này giúp tôi hiểu rõ hơn về public subnet, private subnet, Internet Gateway, NAT Gateway, route table và VPC Endpoint. Những khái niệm trước đây chỉ tồn tại trên sơ đồ kiến trúc đã trở thành kiến thức thực tế sau khi tôi trực tiếp gặp và khắc phục sự cố.

## Database, concurrency và idempotency

Nhiều lỗi backend không xuất hiện khi chỉ có một người sử dụng hệ thống. Chúng thường xuất hiện khi hai hoặc nhiều request được gửi gần như đồng thời.

Nếu hai request cùng kiểm tra một bản ghi chưa tồn tại rồi cùng insert, dữ liệu trùng lặp có thể được tạo ra. Để hạn chế vấn đề này, hệ thống cần sử dụng:

- Unique constraints trong database.
- Transaction và rollback.
- HTTP 409 cho các trường hợp conflict.
- Optimistic locking.
- Idempotency key cho các thao tác quan trọng.

Ví dụ, thao tác nộp hồ sơ ứng tuyển không nên tạo ra hai application chỉ vì người dùng bấm nút nhiều lần hoặc client tự động retry request.

## Message queue và transactional outbox

Một vấn đề khác xuất hiện khi hệ thống cần vừa ghi dữ liệu vào database vừa gửi message lên queue.

Nếu database commit thành công nhưng việc gửi message thất bại, dữ liệu đã được tạo nhưng event lại bị mất. Nếu message được gửi trước nhưng database commit thất bại thì trạng thái giữa hai hệ thống cũng không còn nhất quán.

Transactional outbox giải quyết vấn đề này bằng cách ghi dữ liệu chính và event vào cùng một transaction. Một dispatcher riêng sau đó đọc các event trong outbox và gửi chúng lên Amazon SQS. Nếu việc gửi thất bại, hệ thống có thể retry. Consumer cũng cần hỗ trợ deduplication để cùng một event không bị xử lý nhiều lần.

Đây là một ví dụ cho thấy nhiều phần quan trọng của Software Engineering không trực tiếp xuất hiện trên giao diện người dùng, nhưng lại quyết định độ tin cậy của toàn bộ hệ thống.

## Cách tiếp cận debug có hệ thống

Điều quan trọng nhất tôi học được không phải là ghi nhớ thật nhiều câu lệnh, mà là biết cách chia nhỏ một vấn đề.

Khi có lỗi, tôi bắt đầu kiểm tra theo từng tầng:

1. Lỗi nằm ở application hay infrastructure?
2. Lỗi xuất hiện trước hay sau deployment?
3. Container và pod có đang chạy không?
4. Service có expose đúng port không?
5. DNS có resolve được không?
6. Network có route được không?
7. IAM có cho phép action cần thiết không?
8. Database và dependency đã sẵn sàng chưa?
9. Bước cuối cùng hoạt động thành công là bước nào?

Thay vì thay đổi nhiều thứ cùng lúc, tôi cố gắng xác định điểm gãy đầu tiên trong chuỗi xử lý. Cách tiếp cận này giúp quá trình debug có định hướng và tiết kiệm thời gian hơn.

## Kết luận

Sau hành trình này, cách tôi nhìn nhận Software Engineering đã thay đổi đáng kể.

Trước đây, khi hệ thống xảy ra lỗi, phản xạ đầu tiên của tôi là sửa code. Hiện tại, tôi hiểu rằng lỗi có thể nằm ở configuration, environment variables, container, network, database, permission, infrastructure hoặc CI/CD.

Tôi cũng bắt đầu quan tâm đến nhiều tình huống hơn ngoài việc tính năng có chạy được hay không:

- Điều gì xảy ra khi request được gửi hai lần?
- Nếu database commit nhưng queue thất bại thì sao?
- Nếu hai người cùng cập nhật một dữ liệu thì sao?
- Nếu pod restart thì hệ thống phục hồi như thế nào?
- Nếu deployment thất bại thì có thể rollback hay không?

Một Software Engineer không phải là người không bao giờ làm hệ thống xảy ra lỗi. Quan trọng hơn, đó là người có thể hiểu hệ thống rõ hơn sau mỗi sự cố, khắc phục lỗi có phương pháp và thiết kế để lỗi đó khó lặp lại hơn.

## Thông tin bài đăng

- **Chủ đề:** Bài học thực tế từ quá trình phát triển, triển khai và vận hành một hệ thống phần mềm.
- **Ngày đăng:** 28/07/2026.
- **Nền tảng:** AWS Study Groups.
- **Trạng thái:** Pending.
- **Public link:** [Blog 3 trên AWS Study Groups](https://www.facebook.com/groups/awsstudygroupfcj/permalink/2227122848052675/#)
