# Multi-Agent Homework System Implementation Plan

## Overview
Transform the current homework system into a sophisticated multi-agent architecture for personalized learning, practice generation, and exam analysis.

## Phase 1: Foundation & Core Infrastructure (Week 1-2)

### 1.1 Database Schema Updates
- [ ] Add `material_chunks` table with vector embeddings support
- [ ] Add `practice_sets` table for generated questions
- [ ] Add `exams` and `exam_questions` tables
- [ ] Add `exam_answers` table for student submissions
- [ ] Add `homework_tasks` and `homework_submissions` tables
- [ ] Add `agent_runs` table for logging and traceability
- [ ] Set up pgvector extension OR FAISS integration

### 1.2 Agent Base Framework
- [ ] Create `AgentBase` class with common functionality
- [ ] Implement agent logging and traceability
- [ ] Create `CoordinatorAgent` for orchestration
- [ ] Set up task graph structure
- [ ] Implement retry and fallback mechanisms

### 1.3 Model Setup
- [ ] Install sentence-transformers for embeddings
- [ ] Set up FAISS vector database
- [ ] Download and configure models:
  - `all-MiniLM-L6-v2` for embeddings
  - `t5-base-qg-hl` for question generation
  - `distilbert-base-uncased-distilled-squad` for QA
  - `paraphrase-MiniLM-L6-v2` for similarity scoring

## Phase 2: Core Agents (Week 3-4)

### 2.1 Ingestion Agent
**Status**: Partially implemented (current OCR service)
- [x] PDF text extraction (pdfplumber, PyMuPDF)
- [x] OCR for scanned/handwritten content (pytesseract)
- [ ] Intelligent chunking (500-800 tokens)
- [ ] Topic extraction and tagging
- [ ] Section/heading metadata attachment
- [ ] Integration with vector database

**Files to modify**:
- `backend/app/services/ocr_service.py` → Enhance with chunking
- Create `backend/app/agents/ingestion_agent.py`

### 2.2 Retrieval Agent
- [ ] Embedding generation for chunks
- [ ] FAISS index management
- [ ] Multi-level indexing (material, subject, topic, grade)
- [ ] Semantic search functionality
- [ ] Top-k chunk retrieval with relevance scoring

**Files to create**:
- `backend/app/agents/retrieval_agent.py`
- `backend/app/services/vector_store.py`

### 2.3 Question Generator Agent
- [ ] Load and configure T5-based QG model
- [ ] Implement MCQ generation
- [ ] Implement short-answer generation
- [ ] Implement fill-in-the-blank generation
- [ ] Grade-appropriate vocabulary filtering
- [ ] Answer and hint generation
- [ ] Difficulty level assignment

**Files to create**:
- `backend/app/agents/question_generator_agent.py`
- `backend/app/services/question_generation.py`

### 2.4 Exam Analysis Agent
- [ ] Answer sheet OCR and parsing
- [ ] Question-answer mapping
- [ ] Similarity-based scoring
- [ ] Rule-based math evaluation
- [ ] Rubric application
- [ ] Feedback generation
- [ ] Weak area identification

**Files to create**:
- `backend/app/agents/exam_analysis_agent.py`
- `backend/app/services/exam_scoring.py`

### 2.5 Planner Agent
- [ ] Performance analytics aggregation
- [ ] Study plan generation
- [ ] Targeted practice recommendations
- [ ] Daily task scheduling
- [ ] Readiness index calculation
- [ ] Streak tracking

**Files to create**:
- `backend/app/agents/planner_agent.py`
- `backend/app/services/study_planner.py`

### 2.6 Safety/Guardrail Agent
- [ ] Age-appropriate content filtering
- [ ] Toxicity detection
- [ ] Grade-level vocabulary enforcement
- [ ] Ambiguous phrasing detection
- [ ] Output validation

**Files to create**:
- `backend/app/agents/safety_agent.py`
- `backend/app/services/content_filter.py`

## Phase 3: API Endpoints (Week 5)

### 3.1 Material Management
- [ ] `POST /api/v1/homework/materials/upload` - Upload study material
- [ ] `GET /api/v1/homework/materials/{id}` - Get material details
- [ ] `GET /api/v1/homework/materials` - List user materials
- [ ] `DELETE /api/v1/homework/materials/{id}` - Delete material

### 3.2 Practice Generation
- [ ] `POST /api/v1/homework/practice/generate` - Generate practice set
- [ ] `GET /api/v1/homework/practice/{id}` - Get practice set
- [ ] `POST /api/v1/homework/practice/{id}/submit` - Submit answers
- [ ] `GET /api/v1/homework/practice/history` - Get practice history

### 3.3 Exam Management
- [ ] `POST /api/v1/homework/exams/upload` - Upload exam/answer sheet
- [ ] `POST /api/v1/homework/exams/{id}/analyze` - Analyze exam
- [ ] `GET /api/v1/homework/exams/{id}/results` - Get exam results
- [ ] `GET /api/v1/homework/exams/{id}/feedback` - Get detailed feedback

### 3.4 Daily Planning
- [ ] `POST /api/v1/homework/daily/plan` - Generate daily plan
- [ ] `GET /api/v1/homework/daily/plan/{date}` - Get plan for date
- [ ] `POST /api/v1/homework/daily/task/{id}/complete` - Mark task complete
- [ ] `GET /api/v1/homework/analytics` - Get performance analytics

## Phase 4: Frontend Integration (Week 6)

### 4.1 Material Upload Interface
- [ ] Enhanced upload with subject/topic selection
- [ ] Processing status indicator
- [ ] Chunk preview and topic tags display

### 4.2 Practice Generation UI
- [ ] Topic selection from materials
- [ ] Question count and type configuration
- [ ] Practice session interface
- [ ] Real-time answer validation
- [ ] Progress tracking

### 4.3 Exam Analysis UI
- [ ] Exam upload with question mapping
- [ ] Results dashboard with visualizations
- [ ] Detailed feedback view
- [ ] Weak area highlights
- [ ] Recommendation cards

### 4.4 Daily Planner UI
- [ ] Calendar view with daily tasks
- [ ] Task completion tracking
- [ ] Streak visualization
- [ ] Progress charts
- [ ] Upcoming exam reminders

## Phase 5: Testing & Optimization (Week 7-8)

### 5.1 Agent Testing
- [ ] Unit tests for each agent
- [ ] Integration tests for workflows
- [ ] End-to-end testing
- [ ] Performance benchmarking
- [ ] Error handling validation

### 5.2 Model Optimization
- [ ] Embedding caching strategy
- [ ] Model inference optimization
- [ ] Batch processing implementation
- [ ] GPU utilization (if available)
- [ ] Fallback mechanism testing

### 5.3 User Testing
- [ ] Beta testing with sample students
- [ ] Teacher feedback collection
- [ ] UI/UX refinements
- [ ] Performance tuning
- [ ] Bug fixes

## Technical Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with pgvector OR SQLite + FAISS
- **ML Models**: 
  - Sentence Transformers (embeddings)
  - T5 (question generation, summarization)
  - DistilBERT (QA)
- **OCR**: Tesseract, PyMuPDF
- **Vector Store**: FAISS or pgvector
- **Task Queue**: Celery (optional, for async processing)

### Frontend
- **Framework**: React + Vite
- **State Management**: React hooks
- **Charts**: Recharts or Chart.js
- **UI Components**: Custom components

## Key Considerations

### Scalability
- Async processing for heavy tasks (OCR, embedding generation)
- Caching for embeddings and generated content
- Batch processing for multiple uploads
- Database indexing for fast retrieval

### Reliability
- Comprehensive error handling
- Fallback mechanisms for model failures
- Agent run logging for debugging
- Retry logic with exponential backoff

### User Experience
- Real-time progress indicators
- Clear error messages
- Responsive design
- Offline capability (future)

### Privacy & Security
- Secure file storage
- User data isolation
- Content filtering
- Age-appropriate guardrails

## Success Metrics
- Material processing time < 30s for 20-page PDFs
- Question generation time < 10s for 6 questions
- Exam analysis time < 60s for 20-question exam
- 95%+ accuracy for digital PDF text extraction
- 80%+ accuracy for handwritten text OCR
- User satisfaction score > 4/5

## Next Steps
1. Review and approve this plan
2. Set up development environment with required models
3. Create database migrations
4. Start with Phase 1 implementation
5. Iterative development with weekly reviews
