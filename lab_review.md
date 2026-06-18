# Lab Review: Reflexion Agent

## 🎯 (a) Mục tiêu của Lab
Mục tiêu của bài lab này là triển khai một **Reflexion Agent** - một kiến trúc cho phép LLM tự động nhận diện sai sót (evaluate), phân tích nguyên nhân và đề xuất chiến thuật sửa lỗi (reflect), sau đó thực hiện lại (retry) để đưa ra kết quả chính xác hơn. 
Nhiệm vụ chính là chuyển đổi từ một mô hình giả lập (Mock Runtime) sang việc tích hợp gọi LLM API thực tế.

## 🛠️ (b) Các bước đã thực hiện
1. **Cài đặt môi trường:** Tạo virtual environment `.venv`, cài đặt thư viện từ `requirements.txt` và cài thêm `openai`, `python-dotenv`.
2. **Hoàn thiện Schema:** Bổ sung các trường dữ liệu còn thiếu cho `JudgeResult` (đánh giá đúng/sai) và `ReflectionEntry` (phân tích lỗi) trong `schemas.py`.
3. **Triển khai Logic Reflexion:** Viết đoạn code lưu lại đánh giá (judge) khi agent trả lời sai, gọi hàm reflector để phân tích, và cập nhật `reflection_memory` trong `agents.py`.
4. **Cập nhật Prompt:** Khai báo cụ thể System Prompts cho 3 Agent (Actor, Evaluator, Reflector) trong `prompts.py`.
5. **Tích hợp LLM thực:** Thay thế mock logic trong `mock_runtime.py` thành các lệnh gọi API OpenAI (`gpt-4o-mini`), đồng thời tạo class `LLMTracker` để tính toán chính xác số lượng tokens và độ trễ (latency).
6. **Tạo Test Data:** Sinh ra tập dữ liệu 104 samples (`test_100.json`) từ `hotpot_mini.json` nhằm thoả mãn điều kiện của Autograder.

## 🧠 (c) Logic cốt lõi của các phần TODO

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

## 🧪 (d) Các lệnh test đã sử dụng
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
