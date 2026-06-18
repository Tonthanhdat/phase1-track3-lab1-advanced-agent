# Lab Report: Reflexion Agent

## (a) Mục tiêu của Lab
Mục tiêu của bài lab này là triển khai một **Reflexion Agent** - một kiến trúc cho phép LLM tự động nhận diện sai sót (evaluate), phân tích nguyên nhân và đề xuất chiến thuật sửa lỗi (reflect), sau đó thực hiện lại (retry) để đưa ra kết quả chính xác hơn. 
Nhiệm vụ chính là chuyển đổi từ một mô hình giả lập (Mock Runtime) sang việc tích hợp gọi LLM API thực tế.

## (b) Các bước đã thực hiện và Kỹ thuật áp dụng

1. **Cài đặt môi trường:** 
   - **Cách làm:** Sử dụng Python venv để tạo môi trường ảo (`python -m venv .venv`), sau đó cài đặt các dependencies qua `pip install -r requirements.txt`. Cài thêm thư viện `openai` để gọi API và `python-dotenv` để load cấu hình.

2. **Hoàn thiện Schema (`schemas.py`):** 
   - **Kỹ thuật:** Sử dụng `Pydantic BaseModel` để định nghĩa cấu trúc dữ liệu chặt chẽ (Structured Output).
   - **Cách làm:** Định nghĩa `JudgeResult` (gồm `score` kiểu int và `reason` kiểu string) và `ReflectionEntry` (gồm `attempt_id`, `failure_reason`, `lesson`, và `next_strategy`) để hứng dữ liệu JSON từ LLM.

3. **Triển khai Logic Reflexion (`agents.py`):** 
   - **Kỹ thuật:** Cơ chế Vòng lặp (Retry/Loop mechanism) kết hợp với Self-Reflection & Prompt Chaining.
   - **Cách làm:** Xây dựng vòng lặp để lấy câu trả lời. Nếu Evaluator đánh giá sai (`judge.score == 0`), hệ thống gọi Reflector để sinh ra `ReflectionEntry`. Chuỗi text phản tư này được nối vào danh sách `reflection_memory` và truyền ngược lại vào context của Actor trong lần thử tiếp theo để LLM tự khắc phục lỗi.

4. **Cập nhật Prompt (`prompts.py`):** 
   - **Kỹ thuật:** Prompt Engineering với phân tách vai trò (Role-playing Prompts).
   - **Cách làm:** Thiết kế System Prompt độc lập cho từng Agent. Actor đóng vai người giải quyết vấn đề, Evaluator làm giám khảo chấm điểm đúng/sai, và Reflector đóng vai trò chuyên gia phân tích nguyên nhân sai sót.

5. **Tích hợp LLM thực (`mock_runtime.py` / `runtime.py`):** 
   - **Kỹ thuật:** Sử dụng tính năng Structured Outputs của OpenAI API (`response_format`).
   - **Cách làm:** Dùng `client.beta.chat.completions.parse` gọi model `gpt-4o-mini` để ép kết quả trả về đúng chuẩn schema Pydantic. Đồng thời áp dụng Tracking bằng cách tạo class `LLMTracker` lưu lại `response.usage.total_tokens` và đo độ trễ bằng `time.time()`.

6. **Tạo Test Data (`generate_data.py`):** 
   - **Kỹ thuật:** Xử lý và thao tác dữ liệu (Data manipulation).
   - **Cách làm:** Đọc tập gốc `hotpot_mini.json`, trích lọc 104 samples và ghi vào file `test_100.json` để vừa thoả mãn điều kiện chạy của Autograder (>100 câu) vừa rút ngắn thời gian test.

## (c) Logic cốt lõi của các phần TODO

### 1. `schemas.py` (Cấu trúc dữ liệu)
Đã định nghĩa:
- `JudgeResult`: Cần có `score` (int, 1=đúng, 0=sai) và `reason` (str) giải thích. 
- `ReflectionEntry`: Cần có `attempt_id` (lần thử), `failure_reason` (lỗi là gì), `lesson` (bài học rút ra) và `next_strategy` (kế hoạch tiếp theo).

### 2. `agents.py` (Vòng lặp Reflexion)
Trong vòng lặp sinh answer, nếu `judge.score == 0` và chưa quá `max_attempts`:
```python
if self.agent_type == "reflexion" and attempt_id < self.max_attempts:
    reflection = reflector(example, attempt_id, judge)
    reflections.append(reflection)
    trace.reflection = reflection
    reflection_memory.append(
        f"Attempt {attempt_id} failed. Reason: {reflection.failure_reason}. "
        f"Lesson: {reflection.lesson} Strategy: {reflection.next_strategy}"
    )
```
**Logic:** Ghi nhận lỗi và thêm `reflection_memory` để truyền cho LLM ở lượt gọi Actor kế tiếp, giúp LLM "biết" mình vừa sai ở đâu để tránh lặp lại.

3. Tích hợp LLM Tracker (`agents.py` & `mock_runtime.py`)
Sử dụng một class tĩnh `LLMTracker` trong `mock_runtime.py` để cộng dồn latency và số token (`response.usage.total_tokens`) cho mỗi câu hỏi, sau đó truy xuất nó bên `agents.py`.

## (d) Các lệnh test đã sử dụng
Để chạy đánh giá kết quả, bạn dùng các câu lệnh sau:

**1. Chạy sinh script test 100 dòng:**
```bash
.venv/bin/python generate_data.py
```

**2. Chạy benchmark (yêu cầu file `.env` có chứa `OPENAI_API_KEY`):**
```bash
# Chạy benchmark trên 100 samples
.venv/bin/python run_benchmark.py --dataset data/test_100.json --out-dir outputs/final_run
```

**3. Chạy chấm điểm Autograde:**
```bash
.venv/bin/python autograde.py --report-path outputs/final_run/report.json
```

## (e) Báo cáo Kết quả Benchmark

Dựa trên kết quả từ quá trình chạy benchmark (`hotpot_dev_run`), dưới đây là bảng thống kê chi tiết so sánh hiệu suất giữa hai tác tử **ReAct** và **Reflexion**.

### Tổng quan (Summary)
- **Tập dữ liệu**: `hotpot_dev_converted.json`
- **Tổng số câu hỏi đánh giá**: 300 (chia đều mỗi agent 150 câu hỏi)
- **Chế độ chạy**: `mock`

### Kết quả chi tiết

| Chỉ số | ReAct | Reflexion | Chênh lệch (Reflexion - ReAct) |
| --- | --- | --- | --- |
| **Số lượng test (Count)** | 150 | 150 | 0 |
| **Độ chính xác tuyệt đối (EM Score)** | 78.00% | 94.67% | +16.67% |
| **Số lần thử trung bình (Avg Attempts)** | 1.0 | 1.2867 | +0.2867 |
| **Số lượng Token ước tính trung bình** | 1,652.05 | 2,187.86 | +535.81 tokens |
| **Độ trễ trung bình (Latency)** | 3,352.23 ms | 4,631.99 ms | +1,279.76 ms |

### Phân tích & Nhận xét
1. **Độ chính xác (Exact Match - EM)**: 
   - **Reflexion** đạt tỷ lệ chính xác rất cao (**94.67%**), vượt trội hơn hẳn so với **ReAct** (**78.00%**).
   - Cơ chế tự suy ngẫm (reflection) đã giúp tác tử sửa chữa sai lầm và tăng độ chính xác lên thêm **16.67%**.
2. **Chi phí (Tokens & Latency)**: 
   - Để đổi lấy độ chính xác cao hơn, **Reflexion** tiêu tốn nhiều token hơn (trung bình thêm **535.81 token** mỗi câu hỏi).
   - Thời gian phản hồi của Reflexion cũng dài hơn **1.28 giây** so với ReAct, do phải thực hiện thêm các bước đánh giá và thử lại.
3. **Số lần nỗ lực (Attempts)**: 
   - ReAct luôn chỉ thử 1 lần cho mỗi câu hỏi.
   - Reflexion thử trung bình **~1.29 lần**, chứng tỏ khoảng 30% số câu hỏi đã được Reflexion tự động thử lại sau khi nhận ra câu trả lời đầu tiên có khả năng bị sai.

### Thống kê lỗi (Failure Modes) của ReAct & Reflexion tổng hợp
- **Hoàn thành không lỗi (none)**: 259
- **Trả lời sai kết quả cuối cùng (wrong_final_answer)**: 41
- *(Không có trường hợp nào bị lạc đề (entity drift), lặp vô hạn (looping), trích xuất thiếu bước (incomplete multi hop) hay học vẹt qua phản tư (reflection overfit)).*
