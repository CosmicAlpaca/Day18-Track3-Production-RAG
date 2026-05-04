# Báo cáo Nhóm - Lab 18: Production RAG System

## 1. Tổng quan hệ thống
Hệ thống Production RAG được xây dựng theo kiến trúc module hóa với 5 thành phần chính: Chunking, Search, Reranking, Evaluation, và Enrichment. Hệ thống sử dụng Qdrant cho Vector Database, BM25 cho Sparse Retrieval và Gemini (thông qua OpenAI wrapper) cho LLM generation.

## 2. Chi tiết triển khai các Module
- **M1 (Chunking):** Thực hiện 3 chiến lược chunking (Basic, Semantic, Hierarchical, Structure-aware) để tối ưu hóa việc phân chia tài liệu.
- **M2 (Search):** Áp dụng Hybrid Search kết hợp Sparse (BM25 với underthesea) và Dense (Qdrant). Kết quả được hợp nhất thông qua thuật toán Reciprocal Rank Fusion (RRF).
- **M3 (Reranking):** Sử dụng BAAI/bge-reranker-v2-m3 và FlashRank để sắp xếp lại kết quả trả về từ Hybrid Search, cải thiện độ chính xác.
- **M4 (Evaluation):** Tích hợp RAGAS framework để đánh giá 4 chỉ số: Faithfulness, Answer Relevancy, Context Precision, Context Recall. Hỗ trợ tự động chuẩn đoán lỗi thông qua failure analysis.
- **M5 (Enrichment):** Nâng cao chất lượng chunk thông qua AI-generated summaries, HyQA (Hypothetical Questions), contextual prepend và metadata extraction, qua đó tăng cường khả năng retrieval.

## 3. Tích hợp & Đánh giá
Các module được ghép nối liền mạch trong `pipeline.py`. Việc kết hợp BM25 và Dense Search giúp khắc phục yếu điểm của mỗi phương pháp riêng lẻ. Kỹ thuật Reranking giúp chọn ra top-k văn bản phù hợp nhất, giảm thiểu context window và tăng độ chính xác của LLM.

## 4. Team Coordination
Dự án được phân chia rõ ràng theo từng module, tuy nhiên các thành viên phải liên tục trao đổi để đảm bảo định dạng dữ liệu (I/O) giữa các module được thống nhất, đặc biệt là giữa M1 (Chunking) và M2 (Search).
