# Phân tích lỗi (Failure Analysis)

Dựa trên báo cáo `ragas_report.json`, đây là phân tích 5 câu hỏi có điểm số RAGAS thấp nhất:

## 1. Câu hỏi: Có thể mang thú cưng đi làm không?
- **Worst Metric:** Answer Relevancy (0.0)
- **Diagnosis:** Answer doesn't match question
- **Phân tích:** Tài liệu không có bất kỳ thông tin nào đề cập đến thú cưng. LLM trả lời "Không tìm thấy thông tin" nhưng do câu hỏi không liên quan đến ngữ cảnh, chỉ số Answer Relevancy thấp.
- **Suggested Fix:** Thêm bước tiền xử lý (Guardrails) để từ chối trả lời các câu hỏi out-of-domain trước khi đi qua RAG pipeline.

## 2. Câu hỏi: Thời gian thử việc là bao lâu?
- **Worst Metric:** Context Recall (0.6)
- **Diagnosis:** Missing relevant chunks
- **Phân tích:** Mặc dù tài liệu có đề cập (60 ngày cho chuyên viên), nhưng hệ thống chunking có thể cắt ngữ cảnh làm mất thông tin "cho chuyên viên".
- **Suggested Fix:** Tinh chỉnh kích thước chunk, đặc biệt áp dụng Structure-aware chunking để không phá vỡ logic các đoạn mô tả điều kiện.

## 3. Câu hỏi: Quy định về nghỉ ốm như thế nào?
- **Worst Metric:** Context Precision (0.65)
- **Diagnosis:** Too many irrelevant chunks
- **Phân tích:** Keyword "nghỉ" xuất hiện rất nhiều trong tài liệu (nghỉ phép, nghỉ ốm, nghỉ thai sản). Hệ thống Search kéo theo nhiều chunk về nghỉ phép thông thường.
- **Suggested Fix:** Cải thiện việc trích xuất Metadata. Bổ sung keyword/topic mapping và sử dụng Hybrid Search với Reranking có trọng số cao hơn.

## 4. Câu hỏi: Lương thử việc là bao nhiêu phần trăm?
- **Worst Metric:** Faithfulness (0.8)
- **Diagnosis:** LLM hallucinating
- **Phân tích:** Thay vì trả lời "85% lương cơ bản", LLM tự nội suy ra một con số khác dựa trên kiến thức bên ngoài do prompt quá lỏng.
- **Suggested Fix:** Giảm temperature=0, sử dụng prompt chặt chẽ hơn (Strict Instruction: CHỈ TRẢ LỜI DỰA TRÊN NGỮ CẢNH ĐƯỢC CUNG CẤP).

## 5. Câu hỏi: Nhân viên được nghỉ phép bao nhiêu ngày?
- **Worst Metric:** Context Precision (0.78)
- **Diagnosis:** Too many irrelevant chunks
- **Phân tích:** Tương tự câu 3, quá nhiều đoạn văn nhắc tới số ngày nghỉ nhưng lại dành cho các đối tượng khác nhau (bán thời gian, thực tập sinh).
- **Suggested Fix:** Tăng cường Reranker (sử dụng CrossEncoder mạnh hơn) để đẩy các kết quả chính xác nhất lên top 1.
