# Cá nhân Reflection - Nguyễn Đức Hải (2A202600149)

## 1. Công việc đảm nhận
Tôi đã đảm nhận triển khai toàn bộ 5 module (Chunking, Search, Rerank, Evaluation, Enrichment) và cấu trúc lại pipeline để hoàn thiện Lab 18 với vai trò cá nhân.

## 2. Khó khăn gặp phải
- Khó khăn lớn nhất là việc xử lý các file cấu hình và môi trường chạy Docker Desktop trên Windows bị lỗi, buộc phải implement fallback in-memory cho Qdrant để đảm bảo hệ thống vẫn chạy được.
- Việc tùy chỉnh OpenAI client để gọi được Gemini API đòi hỏi phải set đúng base URL và model name phù hợp với prompt.

## 3. Bài học rút ra
- Quá trình phát triển các RAG pipeline phức tạp yêu cầu phải có một hệ thống Chunking và Search vững chắc trước khi áp dụng Reranking hay Enrichment.
- Tầm quan trọng của việc có bộ test tự động (pytest) và Evaluation framework (RAGAS) giúp nhận diện rõ ràng pipeline đang yếu ở đâu (VD: Context Recall thấp chứng tỏ Chunking/Search kém).

## 4. Hướng cải thiện
Trong tương lai, tôi sẽ tìm hiểu cách triển khai Qdrant lên cloud (VD: Qdrant Cloud) thay vì local Docker để tăng tính ổn định, và tối ưu hóa thời gian chạy của Enrichment bằng cách batch processing.
