# Báo cáo Kết quả Benchmark: ReAct vs Reflexion

Dựa trên kết quả từ quá trình chạy benchmark (`hotpot_dev_run`), dưới đây là bảng thống kê chi tiết so sánh hiệu suất giữa hai tác tử **ReAct** và **Reflexion**.

## 📊 Tổng quan (Summary)
- **Tập dữ liệu**: `hotpot_dev_converted.json`
- **Tổng số câu hỏi đánh giá**: 300 (chia đều mỗi agent 150 câu hỏi)
- **Chế độ chạy**: `mock`

## 📈 Kết quả chi tiết

| Chỉ số | ReAct | Reflexion | Chênh lệch (Reflexion - ReAct) |
| --- | --- | --- | --- |
| **Số lượng test (Count)** | 150 | 150 | 0 |
| **Độ chính xác tuyệt đối (EM Score)** | 78.00% | 94.67% | +16.67% |
| **Số lần thử trung bình (Avg Attempts)** | 1.0 | 1.2867 | +0.2867 |
| **Số lượng Token ước tính trung bình** | 1,652.05 | 2,187.86 | +535.81 tokens |
| **Độ trễ trung bình (Latency)** | 3,352.23 ms | 4,631.99 ms | +1,279.76 ms |

## 💡 Phân tích & Nhận xét
1. **Độ chính xác (Exact Match - EM)**: 
   - **Reflexion** đạt tỷ lệ chính xác rất cao (**94.67%**), vượt trội hơn hẳn so với **ReAct** (**78.00%**).
   - Cơ chế tự suy ngẫm (reflection) đã giúp tác tử sửa chữa sai lầm và tăng độ chính xác lên thêm **16.67%**.
2. **Chi phí (Tokens & Latency)**: 
   - Để đổi lấy độ chính xác cao hơn, **Reflexion** tiêu tốn nhiều token hơn (trung bình thêm **535.81 token** mỗi câu hỏi).
   - Thời gian phản hồi của Reflexion cũng dài hơn **1.28 giây** so với ReAct, do phải thực hiện thêm các bước đánh giá và thử lại.
3. **Số lần nỗ lực (Attempts)**: 
   - ReAct luôn chỉ thử 1 lần cho mỗi câu hỏi.
   - Reflexion thử trung bình **~1.29 lần**, chứng tỏ khoảng 30% số câu hỏi đã được Reflexion tự động thử lại sau khi nhận ra câu trả lời đầu tiên có khả năng bị sai.

## ⚠️ Thống kê lỗi (Failure Modes) của ReAct & Reflexion tổng hợp
- **Hoàn thành không lỗi (none)**: 259
- **Trả lời sai kết quả cuối cùng (wrong_final_answer)**: 41
- *(Không có trường hợp nào bị lạc đề (entity drift), lặp vô hạn (looping), trích xuất thiếu bước (incomplete multi hop) hay học vẹt qua phản tư (reflection overfit)).*
