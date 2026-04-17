# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **API key hardcode trong source code:** Gán cứng (`sk-hardcoded-...`) ngay trong code, nếu đẩy code lên GitHub sẽ bị lộ thông tin nhạy cảm (secrets) ngay lập tức.
2. **Không có config management:** Hardcode cấu hình trực tiếp như `DEBUG = True`, `MAX_TOKENS = 500` và cả thông tin kết nối `DATABASE_URL` thay vì truyền qua biến môi trường.
3. **Dùng lệnh `print()` để log (và lộ secret):** Thiếu structured logging khiến log khó trace trên cloud, đặc biệt nguy hiểm khi print trực tiếp API KEY (`print(f"[DEBUG] Using key: {OPENAI_API_KEY}")`).
4. **Không có health check endpoints:** Thiếu endpoint (`/health`, `/ready`) khiến cho Cloud platform hoặc Container orchestrator không thể biết agent có crash hay không để restart, gây downtime.
5. **Cấu hình server nội bộ chết (Hardcoded Host, Port, Reload mode):** Cài cố định `host="localhost"` (chỉ nội bộ máy host truy cập được), `port=8000` (cloud platforms thường gán PORT động), và `reload=True` (chỉ dành cho dev, debug).

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcode giá trị cấu hình trực tiếp vào code file. | Đọc từ biến môi trường (Environment Variables). | Đảm bảo an toàn bảo mật cho secrets, cho phép linh hoạt cấu hình theo từng môi trường deploy mà không cần sửa đổi hoặc build lại source code. |
| Health check | Không có | Có thiết lập endpoints (`/health` cho liveness probe và `/ready` cho readiness). | Theo dõi trạng thái app. Cho phép Load Balancer điều hướng lưu lượng khi server thực sự sẵn sàng, và tự động khởi động (restart) container nếu server bị treo. |
| Logging | Dùng lệnh `print()` thô sơ lên màn hình terminal theo plaintext. | Cấu trúc JSON logging (Sử dụng Python Logger chuyên nghiệp sinh output định dạng JSON). | Định dạng chuẩn hoá json hỗ trợ đắc lực cho Log Aggregators (Datadog, Loki) phân tích, trích xuất metrics, cảnh báo lỗi và ẩn các thông tin nhạy cảm. |
| Shutdown | Dừng đột ngột và ngay lập tức (Hard kill / Ctrl+C không handle). | Có thiết lập Handle Lifecycle Graceful Shutdown qua tín hiệu `SIGTERM`. | Cho phép các request đang xử lý dở dang có thời gian hoàn thành (in-flight requests) và từ chối các request mới đến trước khi tắt hoàn toàn, giúp không rơi data của client. |
| Network binding | Chạy với host `localhost:` và port cứng `8000` cùng với reload mode. | Chạy với host `0.0.0.0` (mở kết nối cho container) và cổng động lấy từ biến `PORT`. | Để có thể chạy container/Docker đúng cách và chạy được trên hầu hết mọi nền tảng Cloud yêu cầu port động. |


## Part 2: Production Deployment

### Exercise 2.1: Build Production Image
```bash
# Build production image
docker build -f 02-docker/production/Dockerfile -t my-agent:production .

# Run production image
docker run -p 8000:8000 my-agent:production
```
### Exercise 2.3: Image size comparison
- Develop: 1.66 GB
- Production: 236 MB
- Difference: ~85.8% reduction

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://ai-agent-production-8kv9.onrender.com
- Screenshot: [Screenshots included in screenshots/ folder]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- **Authentication**: Trả về 401 Unauthorized khi thiếu hoặc sai API Key. Trả về 200 OK khi cung cấp đúng `X-API-Key`.
- **Rate Limiting**: Giới hạn 20 req/min được thực thi chính xác. Request thứ 21 trong cùng phút trả về lỗi 429 Too Many Requests.
- **Cost Guard**: Chặn request và trả về lỗi 503/402 khi tổng chi phí trong ngày vượt ngưỡng budget ($5.0).

### Exercise 4.4: Cost guard implementation
Đã triển khai logic kiểm tra budget trong `app/cost_guard.py` sử dụng Redis để lưu trữ số tiền đã chi tiêu theo ngày. Trước mỗi lần gọi LLM, hệ thống tính toán chi phí ước tính và kiểm tra xem có vượt quá hạn mức không.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **Health Checks**: Endpoint `/health` cung cấp thông tin liveness, uptime và các chỉ số cơ bản. Endpoint `/ready` đảm bảo traffic chỉ được dẫn đến khi app đã khởi tạo xong.
- **Graceful Shutdown**: Xử lý tín hiệu `SIGTERM` để dừng nhận request mới và hoàn thành nốt các request đang xử lý trước khi tiến hành đóng kết nối và tắt server an toàn.
- **Stateless Design**: Chuyển toàn bộ quản lý Rate Limit và Budget từ bộ nhớ đệm (In-memory) sang Redis, cho phép hệ thống scale ngang (nhiều instances) mà vẫn đồng bộ được trạng thái.
- **Load Balancing**: Sử dụng Nginx làm Reverse Proxy giúp phân phối tải đồng đều giữa các agent instances.