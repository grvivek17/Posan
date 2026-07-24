# POSAN - Comprehensive Application Architecture

> **Last Updated:** 2026-05-23
> **Purpose:** Complete reference documentation for the POSAN application. Use this instead of re-scanning the codebase.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Structure](#2-project-structure)
3. [Tech Stack & Dependencies](#3-tech-stack--dependencies)
4. [Backend Architecture](#4-backend-architecture)
5. [API Endpoints Reference](#5-api-endpoints-reference)
6. [Database Models & Schema](#6-database-models--schema)
7. [Services Layer](#7-services-layer)
8. [Multi-Agent System](#8-multi-agent-system)
9. [Frontend Architecture](#9-frontend-architecture)
10. [Routing & Navigation](#10-routing--navigation)
11. [Frontend Components](#11-frontend-components)
12. [Frontend Services & Hooks](#12-frontend-services--hooks)
13. [Authentication & Authorization](#13-authentication--authorization)
14. [External Integrations](#14-external-integrations)
15. [Gamification System](#15-gamification-system)
16. [Subscription & Payments](#16-subscription--payments)
17. [Environment Variables](#17-environment-variables)
18. [Deployment Configuration](#18-deployment-configuration)
19. [Known Issues & Notes](#19-known-issues--notes)

---

## 1. Project Overview

**POSAN** is a kids' educational web application created by Poshika V (Grade 3, KRM Public School). It features digital magazines, AI-powered puzzles, homework assistance, gamification, a store, podcasts, and more.

- **Project Location:** `C:\Users\grviv\projects\Pratices\Posan`
- **Backend:** Python FastAPI (port 8000)
- **Frontend:** React 18 + Vite (port 5173)
- **Database:** PostgreSQL (via Neon serverless)
- **API Version:** v1 (prefix `/api/v1`)

---

## 2. Project Structure

```
Posan/
├── backend/
│   ├── app/
│   │   ├── main.py                          # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── config.py                    # Settings & env vars
│   │   │   ├── database.py                  # SQLAlchemy setup (PostgreSQL)
│   │   │   ├── security.py                  # JWT, bcrypt, auth dependencies
│   │   │   └── subscription_deps.py         # Pro subscription dependency
│   │   ├── api/endpoints/
│   │   │   ├── auth.py                      # Register, login, password reset
│   │   │   ├── users.py                     # User profiles, child profiles
│   │   │   ├── magazines.py                 # Magazines, articles, quizzes
│   │   │   ├── puzzles.py                   # Puzzle CRUD & AI generation
│   │   │   ├── gamification.py              # Badges, achievements, leaderboard
│   │   │   ├── gamification_v2.py           # Points, levels, streaks
│   │   │   ├── ai_content.py               # AI story/article/quiz/test analysis
│   │   │   ├── podcasts.py                  # Podcast script + TTS
│   │   │   ├── homework_agents.py           # Multi-agent homework system
│   │   │   ├── calculator.py                # Speaking calculator
│   │   │   ├── subscription.py              # Subscription & Razorpay
│   │   │   ├── admin.py                     # Admin dashboard
│   │   │   ├── store.py                     # Activity book store
│   │   │   ├── email.py                     # Resend email
│   │   │   └── promotional_email.py         # SMTP promotional emails
│   │   ├── models/
│   │   │   ├── user.py                      # User, ParentAccount, ChildProfile
│   │   │   ├── content.py                   # Magazine, Article, Quiz
│   │   │   ├── puzzle.py                    # Puzzle, UserPuzzleProgress
│   │   │   ├── gamification.py              # Badge, UserAchievement, Leaderboard
│   │   │   ├── subscription.py              # Subscription
│   │   │   ├── activity.py                  # UserActivity, UserLevel
│   │   │   ├── store.py                     # Product, Cart, Order, OrderItem
│   │   │   ├── exam.py                      # Exam, ExamAnswer, Assignment
│   │   │   ├── homework_agents.py           # Material, MaterialChunk, AgentRunLog
│   │   │   └── puzzle_generation.py         # DailyPuzzleGeneration
│   │   ├── schemas/
│   │   │   ├── user.py, content.py, puzzle.py, gamification.py, password_reset.py
│   │   ├── services/
│   │   │   ├── ai_content.py               # HuggingFace content generation
│   │   │   ├── ocr_service.py              # Tesseract OCR (test papers)
│   │   │   ├── email_service.py            # Resend email
│   │   │   ├── smtp_email_service.py       # Gmail SMTP
│   │   │   ├── payment_service.py          # Razorpay
│   │   │   ├── gamification_service.py     # Points, levels, badges
│   │   │   ├── calculator_service.py       # Speaking calculator
│   │   │   ├── tts_service.py              # edge-tts
│   │   │   ├── podcast_service.py          # Podcast scripts
│   │   │   ├── material_service.py         # Study material CRUD
│   │   │   ├── firebase_service.py         # Firebase (optional)
│   │   │   └── vector_store.py             # FAISS vector search
│   │   └── agents/
│   │       ├── __init__.py                 # Agent base class & coordinator
│   │       ├── ingestion_agent.py          # PDF/image processing & chunking
│   │       ├── retrieval_agent.py          # Semantic search
│   │       ├── question_generator_agent.py # Practice question generation
│   │       └── exam_analysis_agent.py      # Exam grading & feedback
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                         # Main router
│   │   ├── main.jsx                        # React entry point
│   │   ├── pages/                          # 23+ page components
│   │   ├── components/
│   │   │   ├── common/                     # Header, Footer, BottomNav, etc.
│   │   │   ├── puzzles/                    # WordSearch, Crossword, Sudoku, Jigsaw
│   │   │   ├── homework/                   # StudyMaterialAssistant, TestAnalysis
│   │   │   ├── magazine/                   # CategoryFilter, SearchBar
│   │   │   ├── podcasts/                   # AudioPlayer
│   │   │   ├── calculator/                 # SpeakingCalculator, VoiceRecorder
│   │   │   └── subscription/               # ProBadge, UpgradeModal
│   │   ├── services/
│   │   │   ├── api.js                      # Axios client + all API functions
│   │   │   └── gamificationService.js      # Points/level utilities
│   │   ├── hooks/
│   │   │   ├── useSubscription.js          # Subscription state hook
│   │   │   └── useAdmin.js                 # Admin dashboard hook
│   │   ├── data/
│   │   │   └── puzzleData.js               # Sample puzzle data
│   │   └── styles/
│   │       ├── global.css                  # CSS variables & global styles
│   │       └── animations.css              # Keyframe animations
│   ├── package.json
│   └── vercel.json
│
├── package.json                            # Root monorepo config
├── render.yaml                             # Render deployment config
├── vercel.json                             # Vercel deployment config
├── requirements.txt                        # Root Python dependencies
└── README.md
```

---

## 3. Tech Stack & Dependencies

### Backend
| Category | Technology | Version |
|----------|-----------|---------|
| Framework | FastAPI | 0.109.0 |
| Server | Uvicorn | 0.27.0 |
| ORM | SQLAlchemy | 2.0.25 |
| Database | PostgreSQL (psycopg2-binary) | 2.9.11 |
| Migrations | Alembic | 1.13.1 |
| Auth | PyJWT + bcrypt | 2.8.0 / 4.0.1 |
| Validation | Pydantic | 2.6.0 |
| AI/ML | huggingface-hub | >=0.24.0 |
| OCR | pytesseract + Pillow + OpenCV | 0.3.10 / 10.2.0 / 4.9.0 |
| Email | resend + SMTP | >=2.1.0 |
| Payments | razorpay | >=1.4.1 |
| TTS | edge-tts | (latest) |
| Vector Search | FAISS + sentence-transformers | - |
| Testing | pytest + httpx | 7.4.4 / 0.26.0 |

### Frontend
| Category | Technology | Version |
|----------|-----------|---------|
| Framework | React | ^18.2.0 |
| Build Tool | Vite | 5.0.8 |
| Router | React Router DOM | ^6.21.0 |
| HTTP Client | Axios | ^1.6.2 |
| Drag & Drop | react-dnd | ^16.0.1 |
| Fonts | Fredoka, Poppins, Inter | - |

---

## 4. Backend Architecture

### FastAPI App Setup (`backend/app/main.py`)
- **Title:** "POSAN"
- **Description:** "Kids Magazine and Puzzle Web Application API"
- **Version:** 1.0.0
- **CORS:** All origins allowed (development mode)
- **Static Files:** Mounted at `/static` for podcast audio
- **Database:** Auto table creation on startup via `Base.metadata.create_all()`
- **Root endpoints:** `GET /` (welcome), `GET /health` (health check)

### Database (`backend/app/core/database.py`)
- **Engine:** PostgreSQL with psycopg2
- **Pool:** size=1, max_overflow=2 (serverless-optimized)
- **Pool recycle:** 300 seconds
- **Pre-ping:** Enabled

### Security (`backend/app/core/security.py`)
- **Password:** bcrypt hashing via passlib
- **JWT:** HS256 algorithm, Bearer scheme
- **Access token:** 30 min (configurable)
- **Refresh token:** 7 days
- **Auth dependency:** `get_current_user()` extracts user from JWT

### 15 Registered Routers
1. `/api/v1/auth` - Authentication
2. `/api/v1/users` - User management
3. `/api/v1/content` - Magazines/articles/quizzes
4. `/api/v1/podcasts` - Podcast generation
5. `/api/v1/email` - Email sending
6. `/api/v1/puzzles` - Puzzle management
7. `/api/v1/gamification` - Badges/achievements
8. `/api/v1/gamification-v2` - Points/levels/streaks
9. `/api/v1/ai` - AI content generation
10. `/api/v1/calculator` - Speaking calculator
11. `/api/v1/subscription` - Subscription management
12. `/api/v1/admin` - Admin operations
13. `/api/v1/store` - Product store
14. `/api/v1/homework-agents` - Multi-agent homework
15. `/api/v1/admin/promotional-email` - Email campaigns

---

## 5. API Endpoints Reference

### 5.1 Authentication (`/api/v1/auth`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Register user (username, email, password, role) | No |
| POST | `/login` | Login (returns access_token, refresh_token, user_id) | No |
| POST | `/parent-account` | Create parent account | No |
| POST | `/forgot-password` | Request password reset email | No |
| POST | `/reset-password` | Reset password with token | No |
| POST | `/verify-reset-token` | Verify reset token validity | No |

### 5.2 Users (`/api/v1/users`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/me` | Get current user profile | Yes |
| POST | `/child-profile` | Create child profile | Yes |
| GET | `/child-profiles` | List child profiles | Yes |
| GET | `/child-profile/{id}` | Get specific child profile | Yes |
| PUT | `/child-profile/{id}` | Update child profile | Yes |

### 5.3 Content (`/api/v1/content`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/magazines` | Create magazine | No |
| GET | `/magazines` | List magazines (filter: age_group, published_only) | No |
| GET | `/magazines/{id}` | Get magazine details | No |
| POST | `/articles` | Create article | No |
| GET | `/articles` | List articles (filter: magazine_id, age_group) | No |
| GET | `/articles/{id}` | Get article | No |
| POST | `/quizzes` | Create quiz | No |
| POST | `/quizzes/submit` | Submit quiz answer | Yes |

### 5.4 Puzzles (`/api/v1/puzzles`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/puzzles` | Create puzzle | No |
| GET | `/puzzles` | List puzzles (filter: type, difficulty, age_group) | No |
| GET | `/puzzles/{id}` | Get puzzle | No |
| POST | `/puzzles/submit` | Submit solution | Yes |
| GET | `/puzzles/progress/{user_id}` | Get progress | Yes |
| GET | `/puzzles/stats/{user_id}` | Get stats | Yes |
| POST | `/generate` | AI-generate puzzle (1/day limit) | Yes |

### 5.5 Gamification V1 (`/api/v1/gamification`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/badges` | Create badge | No |
| GET | `/badges` | List all badges | No |
| GET | `/achievements/{user_id}` | Get user achievements | Yes |
| GET | `/leaderboard` | Get leaderboard | No |
| GET | `/stats/{user_id}` | Get user stats | Yes |

### 5.6 Gamification V2 (`/api/v1/gamification-v2`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/award-points` | Award activity points | Yes |
| GET | `/stats` | Get authenticated user stats | Yes |
| GET | `/stats/{user_id}` | Get user stats (public) | No |
| GET | `/level` | Get user level info | Yes |
| GET | `/activity-points` | Get point values per activity | No |
| GET | `/levels` | Get all level thresholds | No |
| GET | `/streak` | Get daily login streak | Yes |
| POST | `/daily-login` | Record daily login | Yes |

### 5.7 AI Content (`/api/v1/ai`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/generate/story` | Generate story (topic, age_group, word_count) | Yes |
| POST | `/generate/article` | Generate article (topic, article_type) | Yes |
| POST | `/generate/quiz` | Generate quiz questions | Yes |
| POST | `/generate/word-search` | Generate word search words | Yes |
| POST | `/generate/crossword` | Generate crossword clues | Yes |
| GET | `/generate/fun-fact` | Generate fun fact | Yes |
| GET | `/generate/riddle` | Generate riddle | Yes |
| POST | `/analyze/test` | Analyze test results (manual input) | Yes |
| POST | `/analyze/test-upload` | Upload & OCR analyze test paper | Yes |
| POST | `/study-material/upload` | Upload study material PDF | Yes |
| GET | `/topics/suggestions` | Get topic suggestions | No |

### 5.8 Podcasts (`/api/v1/podcasts`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/generate` | Generate podcast script | Yes |
| POST | `/weekly-highlights` | Generate weekly highlights | Yes |
| GET | `/suggestions` | Get topic suggestions | No |
| GET | `/examples` | Get example podcasts | No |
| POST | `/generate-audio` | Generate TTS audio | Yes |
| GET | `/audio/{filename}` | Serve audio file | No |
| GET | `/voices` | List available voices | No |

### 5.9 Calculator (`/api/v1/calculator`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/voice` | Voice-based calculation (audio file) | Yes |
| POST | `/text` | Text-based calculation (natural language) | Yes |
| GET | `/test` | Test calculator endpoint | No |

### 5.10 Subscription (`/api/v1/subscription`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/status` | Get subscription status | Yes |
| POST | `/upgrade` | Upgrade subscription | Yes |
| POST | `/cancel` | Cancel subscription | Yes |
| GET | `/features/{feature}` | Check feature access | Yes |
| GET | `/plans` | Get subscription plans | No |
| POST | `/razorpay/create-order` | Create Razorpay order | Yes |
| POST | `/razorpay/verify-payment` | Verify Razorpay payment | Yes |

### 5.11 Admin (`/api/v1/admin`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users` | List all users (search, pagination) | Admin |
| GET | `/users/{id}` | Get user details | Admin |
| PUT | `/users/{id}` | Update user | Admin |
| DELETE | `/users/{id}` | Delete user | Admin |
| POST | `/users/{id}/upgrade` | Upgrade user subscription | Admin |
| POST | `/users/{id}/reset-password` | Reset user password | Admin |
| GET | `/subscriptions` | List subscriptions | Admin |
| GET | `/stats/overview` | Dashboard overview stats | Admin |
| GET | `/activity/recent` | Recent activity feed | Admin |

### 5.12 Store (`/api/v1/store`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/products` | List products (category, search, bestseller) | No |
| GET | `/products/{id}` | Get product details | No |
| GET | `/categories` | Get product categories | No |
| GET | `/cart` | Get user cart | Yes |
| POST | `/cart/add` | Add item to cart | Yes |
| PUT | `/cart/update/{item_id}` | Update cart item quantity | Yes |
| DELETE | `/cart/remove/{item_id}` | Remove cart item | Yes |
| DELETE | `/cart/clear` | Clear entire cart | Yes |
| POST | `/checkout` | Create order | Yes |
| POST | `/orders/{id}/confirm-payment` | Confirm payment | Yes |
| GET | `/orders` | Get user orders | Yes |
| POST | `/admin/seed-products` | Seed sample products | Admin |
| POST | `/admin/products` | Create product | Admin |
| PUT | `/admin/products/{id}` | Update product | Admin |
| DELETE | `/admin/products/{id}` | Delete product | Admin |

### 5.13 Homework Agents (`/api/v1/homework-agents`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/materials/upload-v2` | Upload study material | Pro |
| GET | `/materials/{id}/chunks` | Get material chunks | No |
| POST | `/workflow/material-to-practice` | One-click upload-to-practice | Pro |
| POST | `/workflows/demo/material-to-practice` | Demo workflow | No |
| POST | `/questions/generate` | Generate practice questions | Pro |
| POST | `/questions/from-material` | Generate from indexed material | Pro |
| GET | `/questions/types` | Get question types | No |
| POST | `/exams/grade` | Grade exam | Pro |
| POST | `/exams/quick-grade` | Quick-grade single question | Pro |
| GET | `/exams/grading-info` | Get grading info | No |
| GET | `/exams/history` | Get exam history | Yes |
| GET | `/exams/{id}/details` | Get exam details | Yes |
| POST | `/search/create-index` | Create FAISS index | No |
| POST | `/search/query` | Semantic search | Pro |
| POST | `/search/multi-index` | Multi-index search | No |
| GET | `/search/indices` | List FAISS indices | Pro |
| DELETE | `/search/indices/{name}` | Delete index | No |
| GET | `/agents/status/{name}` | Get agent run status | Pro |
| GET | `/agents/list` | List all agents | No |
| GET | `/assignments` | Get user assignments | Yes |
| POST | `/assignments` | Create assignment | Yes |
| PUT | `/assignments/{id}/status` | Update assignment status | Yes |
| DELETE | `/assignments/{id}` | Delete assignment | Yes |
| GET | `/stats` | Get homework stats | Yes |

### 5.14 Email (`/api/v1/email`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/send-test` | Send test email | No |
| POST | `/send-welcome` | Send welcome email | No |

### 5.15 Promotional Email (`/api/v1/admin/promotional-email`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/new-arrivals` | Get new content | Admin |
| GET | `/subscribers` | Get email subscribers | Admin |
| POST | `/preview-weekly-arrivals` | Preview email template | Admin |
| POST | `/send-weekly-arrivals` | Send weekly email | Admin |
| POST | `/send-custom` | Send custom email | Admin |
| POST | `/send-to-all-users` | Send to all users | Admin |
| GET | `/smtp-status` | Check SMTP config | Admin |
| POST | `/send-test` | Send test email | Admin |

---

## 6. Database Models & Schema

### 6.1 User Management

**`users`**
- `id` (PK), `email` (unique), `username` (unique, lowercase), `hashed_password`
- `full_name`, `role` (PARENT/CHILD/ADMIN), `is_active`, `is_admin`
- `last_login`, `created_at`, `updated_at`

**`parent_accounts`**
- `id` (PK), `user_id` (FK->users, unique), `full_name`, `phone`

**`child_profiles`**
- `id` (PK), `user_id` (FK->users, unique), `parent_id` (FK->parent_accounts)
- `full_name`, `age`, `age_group` (TODDLER/EARLY/MIDDLE/PRETEEN)
- `avatar_url`, `total_points`

### 6.2 Content

**`magazines`**
- `id` (PK), `title`, `description`, `cover_image_url`
- `issue_number`, `publication_date`, `age_group`, `is_published`, `created_at`

**`articles`**
- `id` (PK), `magazine_id` (FK), `title`, `content` (Text)
- `content_type` (STORY/ARTICLE/COMIC/ACTIVITY)
- `author`, `illustration_url`, `audio_url`
- `reading_time_minutes`, `age_group`, `order_in_magazine`, `created_at`

**`quizzes`**
- `id` (PK), `article_id` (FK), `question` (Text), `options` (JSON)
- `correct_answer`, `explanation`, `points` (default 10)

### 6.3 Puzzles

**`puzzles`**
- `id` (PK), `title`, `description`
- `puzzle_type` (WORD_SEARCH/CROSSWORD/JIGSAW/SUDOKU)
- `difficulty` (EASY/MEDIUM/HARD), `age_group`
- `puzzle_data` (JSON), `solution_data` (JSON)
- `image_url`, `points_reward` (default 50), `time_limit_seconds`
- `is_daily_challenge`, `challenge_date`, `created_at`

**`user_puzzle_progress`**
- `id` (PK), `user_id` (FK), `puzzle_id` (FK)
- `is_completed`, `completion_time_seconds`, `attempts`
- `points_earned`, `started_at`, `completed_at`

**`daily_puzzle_generations`**
- `id` (PK), `user_id` (FK), `generation_date`
- `puzzle_type`, `topic`, `difficulty`, `created_at`

### 6.4 Gamification

**`badges`**
- `id` (PK), `name` (unique), `description`, `icon_url`
- `points_required`, `puzzles_required`, `is_special`, `created_at`

**`user_achievements`**
- `id` (PK), `user_id` (FK), `badge_id` (FK), `earned_at`

**`leaderboard`**
- `id` (PK), `user_id` (FK), `total_points`
- `puzzles_completed`, `badges_earned`, `rank`, `updated_at`

**`user_activities`**
- `id` (PK), `user_id` (FK), `activity_type` (enum)
- `points_earned`, `reference_id`, `reference_type`, `created_at`

**`user_levels`**
- `id` (PK), `user_id` (FK, unique), `current_level`
- `level_number`, `points_to_next_level`, `updated_at`

### 6.5 Subscriptions

**`subscriptions`**
- `id` (PK), `user_id` (FK, unique)
- `tier` (FREE/PRO/PREMIUM), `status` (ACTIVE/EXPIRED/CANCELLED/TRIAL)
- `started_at`, `expires_at`, `cancelled_at`
- `payment_provider`, `payment_id`
- `ai_image_generation`, `advanced_puzzles`, `unlimited_content`, `no_ads` (booleans)

### 6.6 Store

**`products`**
- `id` (PK), `name`, `description`, `price`, `original_price`
- `image_url`, `category` (ACTIVITY_BOOK/PUZZLE_BOOK/COLORING_BOOK/STICKER_BOOK/EDUCATIONAL/STORIES)
- `age_range`, `pages`, `is_bestseller`, `is_new`, `is_available`
- `stock`, `rating`, `reviews_count`, `created_at`, `updated_at`

**`carts`** - `id`, `user_id`, `created_at`, `updated_at`

**`cart_items`** - `id`, `cart_id` (FK), `product_id` (FK), `quantity`, `created_at`

**`orders`**
- `id` (PK), `user_id` (FK), `total_amount`
- `status` (PENDING/PAID/PROCESSING/SHIPPED/DELIVERED/CANCELLED)
- `payment_id`, `payment_provider`, `shipping_address`, `phone`
- `created_at`, `updated_at`

**`order_items`** - `id`, `order_id` (FK), `product_id` (FK), `quantity`, `price`

### 6.7 Homework & Agents

**`materials`**
- `id` (UUID PK), `user_id`, `title`, `subject`, `topic`, `grade`
- `storage_url`, `file_extension`, `is_ocr`
- `total_chunks`, `total_tokens`, `topics_json`, `metadata_json`
- `created_at`, `updated_at`

**`material_chunks`**
- `id` (UUID PK), `material_id` (FK), `chunk_index`
- `text` (Text), `tokens`, `heading`, `topic`
- `embedding_vector` (JSON), `metadata_json`, `created_at`

**`agent_runs`**
- `id` (UUID PK), `agent_name` (indexed), `task_id` (unique, indexed)
- `input_json`, `output_json`, `status` (success/failure/partial), `error`
- `user_id`, `related_entity`, `related_id`
- `execution_time_ms`, `created_at` (indexed)

**`exams`**
- `id` (UUID PK), `user_id`, `title`, `subject`, `grade`
- `total_score`, `max_score`, `percentage`, `letter_grade`
- `performance_level`, `feedback`, `recommendations`
- `knowledge_gaps_json`, `source_type`, `source_material_id`, `created_at`

**`exam_answers`**
- `id` (UUID PK), `exam_id` (FK), `question_number`
- `question_type` (mcq/short_answer/fill_blank)
- `question_text`, `student_answer`, `correct_answer`
- `score`, `max_score`, `is_correct`, `feedback`, `similarity`, `created_at`

**`assignments`**
- `id` (UUID PK), `user_id`, `title`, `subject`, `description`
- `due_date`, `status` (pending/in_progress/completed)
- `file_url`, `file_name`, `created_at`, `updated_at`

---

## 7. Services Layer

### 7.1 AI Content Service (`services/ai_content.py`)
**Class:** `ContentGenerator`
- HuggingFace Inference API for text generation
- Models: Llama 3.2, Qwen 2.5, RoBERTa, BART, T5, DistilBERT
- Methods: `generate_story()`, `generate_article()`, `generate_quiz_questions()`, `generate_word_search_words()`, `generate_crossword_clues()`, `generate_fun_fact()`, `generate_riddle()`, `analyze_test_results()`, `analyze_test_paper_content()`, `generate_sudoku_puzzle()`, `generate_complete_word_search()`, `generate_complete_puzzle()`, `summarize_study_material()`, `generate_practice_questions()`, `evaluate_answer()`, `analyze_weak_topics()`, `generate_study_plan()`
- Has fallback content when API fails

### 7.2 OCR Service (`services/ocr_service.py`)
**Class:** `OCRService`
- **Tesseract path:** `C:\Program Files\Tesseract-OCR\tesseract.exe` (v5.4.0)
- EXIF orientation fixing (`ImageOps.exif_transpose()`)
- Rotation detection & correction (Hough line-based)
- Colored paper background handling (LAB L-channel + CLAHE)
- Red ink teacher marking filtering (HSV-based)
- Auto-deskewing
- Multi-pass OCR with PSM 4
- Question/answer parsing with flexible patterns
- Score detection with validation

### 7.3 Email Service (`services/email_service.py`)
- **Provider:** Resend API
- Methods: `send_email()`, `send_welcome_email()`

### 7.4 SMTP Email Service (`services/smtp_email_service.py`)
- **Provider:** Gmail SMTP
- Methods: `send_email()`, `generate_weekly_arrivals_email()`, `generate_custom_promotional_email()`

### 7.5 Payment Service (`services/payment_service.py`)
**Class:** `RazorpayService`
- Methods: `create_order()`, `verify_payment()`, `get_payment_details()`, `create_subscription_order()`
- Pricing: PRO = INR 99/month, PREMIUM = INR 999/year

### 7.6 Gamification Service (`services/gamification_service.py`)
**Class:** `GamificationService`
- Methods: `award_points()`, `update_user_level()`, `check_and_award_badges()`, `get_user_stats()`, `get_daily_streak()`
- Duplicate activity prevention

### 7.7 Calculator Service (`services/calculator_service.py`)
**Class:** `SpeakingCalculator`
- Pipeline: ASR -> NLU -> Eval -> Response -> TTS
- Number word conversion, safe AST-based evaluation

### 7.8 TTS Service (`services/tts_service.py`)
**Class:** `TTSService`
- Provider: edge-tts (Microsoft)
- Voices: en-US-AriaNeural, en-US-GuyNeural, en-US-JennyNeural
- Audio stored in `static/podcasts/`

### 7.9 Podcast Service (`services/podcast_service.py`)
**Class:** `PodcastGenerator`
- Styles: fun, educational, story
- Durations: short (2-3 min), medium (5 min), long (10 min)

### 7.10 Material Service (`services/material_service.py`)
**Classes:** `MaterialService`, `AgentLogService`
- CRUD for materials and chunks
- Agent run logging

### 7.11 Vector Store (`services/vector_store.py`)
**Class:** `VectorStore`
- **Library:** FAISS
- **Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`
- Methods: `generate_embeddings()`, `create_index()`, `search()`, `search_multi_index()`, `add_to_index()`, `delete_index()`, `list_indices()`

---

## 8. Multi-Agent System

### Architecture
Base class `AgentBase` in `agents/__init__.py` with retry logic, logging, and status tracking.

### Agents

**1. Ingestion Agent** (`ingestion_agent.py`)
- Extracts text from PDF/images, performs OCR
- Intelligent chunking (target: 700 tokens, overlap: 100, min: 200)
- Topic extraction, section/heading metadata

**2. Retrieval Agent** (`retrieval_agent.py`)
- FAISS vector search
- Operations: create_index, search, search_multi, add_chunks, delete_index, list_indices

**3. Question Generator Agent** (`question_generator_agent.py`)
- Generates MCQ, short_answer, fill_blank questions
- Grade-appropriate vocabulary, auto answer generation
- Difficulty: easy/medium/hard

**4. Exam Analysis Agent** (`exam_analysis_agent.py`)
- Grades answers, calculates scores
- Identifies knowledge gaps
- Generates feedback & recommendations

### Workflow
Coordinator orchestrates: Upload -> Ingest -> Index -> Generate Questions -> Grade -> Feedback

---

## 9. Frontend Architecture

### Stack
- **React 18.2.0** with functional components and hooks
- **Vite 5.0.8** for build/dev
- **React Router DOM v6** for routing
- **Axios** for HTTP with interceptors
- **Component-level state** (useState/useEffect) + localStorage for persistence

### API Client (`services/api.js`)
- Base URL: `VITE_API_URL` env var (default: `http://localhost:8000/api/v1`)
- Request interceptor: Adds `Authorization: Bearer {token}` from localStorage
- Response interceptor: Handles 401 by clearing tokens and redirecting to `/login`

### CSS Design System (`styles/global.css`)
- Kid-friendly palette with CSS variables
- Primary: #FFE500 (yellow), Secondary: #4ECDC4 (teal)
- Font stack: Fredoka, Poppins, Inter
- Border radius: 12px-36px (rounded, playful)
- Responsive with mobile breakpoints

---

## 10. Routing & Navigation

### Public Routes (no auth)
| Path | Component | Purpose |
|------|-----------|---------|
| `/` | Home | Landing page with featured content |
| `/about` | About | About POSAN & creator info |
| `/login` | Login | User login |
| `/register` | Register | New account creation |
| `/forgot-password` | ForgotPassword | Password recovery |
| `/reset-password` | ResetPassword | Password reset form |
| `/store` | ActivityBookStore | Product catalog (public) |

### Protected Routes (auth required)
| Path | Component | Purpose |
|------|-----------|---------|
| `/magazines` | MagazinePage | Browse magazines |
| `/magazines/:id` | MagazineDetailPage | Read magazine & articles |
| `/puzzles` | PuzzlePage | Browse & filter puzzles |
| `/puzzle-zone` | PuzzleZone | Interactive AI puzzle games |
| `/profile` | ProfilePage | User profile & achievements |
| `/parent` | ParentPortal | Parent dashboard (coming soon) |
| `/ai-content` | AIContentPage | AI content generator |
| `/homework` | HomeworkPage | AI homework assistant |
| `/achievements` | GamificationPage | Points, badges, leaderboard |
| `/test-subscription` | TestSubscriptionPage | Subscription testing |
| `/store/checkout` | CheckoutPage | Payment checkout |
| `/store/orders` | OrderHistoryPage | Order history |

### Admin Routes (auth + admin role)
| Path | Component | Purpose |
|------|-----------|---------|
| `/admin` | AdminDashboard | Overview stats |
| `/admin/users` | AdminUsersPage | User management |
| `/admin/users/:id` | AdminUserDetailPage | User details |
| `/admin/subscriptions` | AdminSubscriptionsPage | Subscription management |
| `/admin/products` | AdminProductsPage | Product management |
| `/admin/orders` | AdminOrdersPage | Order management |
| `/admin/promotional-email` | AdminPromotionalEmailPage | Email campaigns |

---

## 11. Frontend Components

### Common (`components/common/`)
- **Header.jsx** - Nav links (Magazines, Puzzles, Homework, AI Creator), points display, user menu, admin link, cart link
- **Footer.jsx** - Basic footer
- **BottomNav.jsx** - Mobile bottom navigation (authenticated only)
- **PointsDisplay.jsx** - Level badge, points, progress bar (auto-refreshes every 30s)
- **BadgesDisplay.jsx** - Badge collection
- **Card.jsx** - Reusable card with hover effects
- **Button.jsx** - Reusable button with variants
- **ScrollToTop.jsx** - Auto-scroll on route change

### Puzzles (`components/puzzles/`)
- **WordSearchPuzzle.jsx** - Grid-based word search with cell selection and found-word highlighting
- **CrosswordPuzzle.jsx** - Crossword puzzle implementation
- **JigsawPuzzle.jsx** - Drag & drop jigsaw (uses react-dnd)
- **SudokuPuzzle.jsx** - 4x4 Sudoku grid

### Homework (`components/homework/`)
- **StudyMaterialAssistant.jsx** - Multi-step workflow: upload -> results -> practice -> evaluation. PDF drag & drop, AI auto-grading, hint system
- **TestAnalysis.jsx** - Upload test paper (OCR) or manual entry. Shows performance level, analysis, motivational feedback

### Magazine (`components/magazine/`)
- **SearchBar.jsx** - Search input
- **CategoryFilter.jsx** - Category filter buttons

### Podcasts (`components/podcasts/`)
- **AudioPlayer.jsx** - Audio playback for podcasts

### Calculator (`components/calculator/`)
- **SpeakingCalculator.jsx** - Voice-enabled calculator UI
- **VoiceRecorder.jsx** - Voice recording

### Subscription (`components/subscription/`)
- **UpgradeModal.jsx** - Plan selection (Pro INR 99/month, Premium INR 999/year) with Razorpay integration
- **ProBadge.jsx** - Pro membership badge (variants: inline, small, large)

---

## 12. Frontend Services & Hooks

### API Service (`services/api.js`)
Exports: `authAPI`, `usersAPI`, `contentAPI`, `puzzlesAPI`, `gamificationAPI`, `homeworkAPI` (comprehensive with 20+ methods), plus store/subscription/admin/podcast APIs.

### Gamification Service (`services/gamificationService.js`)
Static methods: `awardPoints()`, `recordDailyLogin()`, `getUserStats()`, `getActivityPoints()`, `getAllLevels()`, `getDailyStreak()`, `addPoints()`, `showPointsNotification()`

### useSubscription Hook (`hooks/useSubscription.js`)
Returns: `subscription`, `loading`, `error`, `hasFeature(name)`, `isPro()`, `refresh()`

### useAdmin Hook (`hooks/useAdmin.js`)
Returns: `stats`, `users`, `subscriptions`, `recentActivity`, loading/error states, and methods: `fetchStats()`, `fetchUsers()`, `fetchUserDetails()`, `fetchSubscriptions()`, `fetchRecentActivity()`, `upgradeUser()`, `deleteUser()`, `updateUser()`, `resetPassword()`

---

## 13. Authentication & Authorization

### Roles
- **CHILD** - Standard content access
- **PARENT** - Child management + content
- **ADMIN** - Full access to admin endpoints

### Flow
1. Register/Login -> API returns `access_token`, `refresh_token`, `user_id`
2. Tokens stored in `localStorage`
3. Axios interceptor adds `Bearer` token to all requests
4. 401 response -> clear tokens, redirect to `/login`
5. Admin check: Header reads `is_admin` from user profile

### Pro Subscription Gating
- Backend dependency: `require_pro_subscription()`
- Checks tier (PRO/PREMIUM), active status, expiration
- Gated features: homework agents, advanced puzzles, unlimited content, no ads

---

## 14. External Integrations

| Service | Purpose | Config Key |
|---------|---------|-----------|
| **HuggingFace** | AI text generation (stories, articles, quizzes, puzzles) | `HUGGINGFACE_TOKEN` |
| **Razorpay** | Payment gateway (subscriptions, store) | `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` |
| **Resend** | Transactional email | `RESEND_API_KEY` |
| **Gmail SMTP** | Promotional email campaigns | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` |
| **Tesseract OCR** | Test paper text extraction | Installed at `C:\Program Files\Tesseract-OCR\tesseract.exe` |
| **edge-tts** | Text-to-speech for podcasts/calculator | Built-in (no API key) |
| **FAISS** | Vector similarity search for materials | Built-in |
| **sentence-transformers** | Text embeddings (`all-MiniLM-L6-v2`) | Built-in |
| **Firebase** | Optional auth/storage integration | Firebase config |

---

## 15. Gamification System

### Activity Points
| Activity | Points |
|----------|--------|
| PUZZLE_SOLVED | 10 |
| ARTICLE_READ | 5 |
| COMMENT_POSTED | 2 |
| CONTENT_SHARED | 3 |
| QUIZ_COMPLETED | 15 |
| DAILY_LOGIN | 1 |
| PROFILE_COMPLETED | 20 |
| HOMEWORK_UPLOADED | 8 |
| STUDY_PLAN_CREATED | 12 |

### Level System
| Level | Points Range |
|-------|-------------|
| Bronze | 0 - 99 |
| Silver | 100 - 299 |
| Gold | 300 - 599 |
| Platinum | 600 - 999 |
| Diamond | 1000 - 1999 |
| Master | 2000+ |

### Puzzle Points
| Difficulty | Points |
|-----------|--------|
| Easy | 50 |
| Medium | 75 |
| Hard | 100 |

---

## 16. Subscription & Payments

### Tiers
| Tier | Price | Features |
|------|-------|----------|
| FREE | Free | Limited daily content |
| PRO | INR 99/month | AI tools, advanced puzzles, unlimited content, no ads |
| PREMIUM | INR 999/year | Same as PRO (save ~17%) |

### Razorpay Integration
- Create order -> User pays via Razorpay widget -> Verify signature -> Activate subscription
- Payment verification uses HMAC SHA256 signature check

---

## 17. Environment Variables

### Backend (`.env`)
```bash
# Database
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/posan

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=POSAN
DEBUG=True
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=uploads

# AI
HUGGINGFACE_TOKEN=hf_...

# Payments
RAZORPAY_KEY_ID=...
RAZORPAY_KEY_SECRET=...

# Email (Resend)
RESEND_API_KEY=...

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_NAME=POSAN Kids Magazine

# Frontend URL (for emails)
FRONTEND_URL=http://localhost:5173
```

### Frontend (`.env`)
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 18. Deployment Configuration

### Backend (Render)
- **File:** `render.yaml`
- **Runtime:** Python 3.11
- **Start:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Database:** External PostgreSQL (Neon)

### Frontend (Vercel)
- **File:** `vercel.json`
- **Build:** `npm run build`
- **Output:** `frontend/dist`
- **Rewrites:** All routes -> `/index.html` (SPA)

### Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 19. Known Issues & Notes

1. **Unicode emoji error:** `ai_content.py` line 46 has a Unicode emoji encoding error on Windows cp1252 (`UnicodeEncodeError` with checkmark emoji). Not critical but causes console logging errors.

2. **OCR fixes applied (2025-01):** `ocr_service.py` was rewritten (~908 lines) to handle phone-camera photos of school answer papers (yellow/green paper, rotated images, red ink markings).

3. **CORS:** Currently allows all origins (`["*"]`) - should be restricted for production.

4. **Parent Portal:** Placeholder only - "coming soon".

5. **Agent system:** Planner and Safety agents are registered but not fully implemented.

6. **Daily puzzle limit:** Users can only AI-generate 1 puzzle per day.

7. **Sample products:** 12 pre-seeded activity books (INR 179-549) via `/admin/seed-products`.

---

*This document was auto-generated from codebase analysis. Keep it updated when making significant changes.*
