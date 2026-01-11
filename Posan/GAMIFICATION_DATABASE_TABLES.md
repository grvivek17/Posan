# Database Tables for Gamification System

## Overview

The gamification system uses **5 PostgreSQL tables** to track user activities, levels, badges, and achievements.

## Tables Summary

| Table Name | Purpose | Status |
|------------|---------|--------|
| `user_activities` | Track all user activities and points earned | ✅ **NEW** |
| `user_levels` | Store user's current level and progress | ✅ **NEW** |
| `badges` | Define available achievement badges | ✅ Existing |
| `user_achievements` | Track which badges users have earned | ✅ Existing |
| `leaderboard` | Store competitive rankings | ✅ Existing |

---

## 1. user_activities (NEW)

**Purpose**: Records every activity a user performs and the points they earn.

### Schema

```sql
CREATE TABLE user_activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    activity_type VARCHAR NOT NULL,  -- ENUM: puzzle_solved, article_read, etc.
    points_earned INTEGER DEFAULT 0,
    reference_id INTEGER,             -- Optional: ID of puzzle, article, etc.
    reference_type VARCHAR,           -- Optional: 'puzzle', 'article', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_user_activities_user_id ON user_activities(user_id);
CREATE INDEX idx_user_activities_type ON user_activities(activity_type);
CREATE INDEX idx_user_activities_created ON user_activities(created_at);
```

### Activity Types & Points

| Activity Type | Points | Description |
|---------------|--------|-------------|
| `puzzle_solved` | 10 | Complete a puzzle |
| `article_read` | 5 | Read a magazine article |
| `comment_posted` | 2 | Post a comment |
| `content_shared` | 3 | Share content |
| `quiz_completed` | 15 | Complete a quiz |
| `daily_login` | 1 | Daily login bonus |
| `profile_completed` | 20 | Complete profile setup |
| `homework_uploaded` | 8 | Upload homework |
| `study_plan_created` | 12 | Create a study plan |

### Example Data

```sql
-- User solved a puzzle
INSERT INTO user_activities (user_id, activity_type, points_earned, reference_id, reference_type)
VALUES (1, 'puzzle_solved', 10, 42, 'puzzle');

-- User read an article
INSERT INTO user_activities (user_id, activity_type, points_earned, reference_id, reference_type)
VALUES (1, 'article_read', 5, 15, 'article');

-- Daily login
INSERT INTO user_activities (user_id, activity_type, points_earned)
VALUES (1, 'daily_login', 1);
```

### Queries

```sql
-- Get user's total points
SELECT SUM(points_earned) as total_points
FROM user_activities
WHERE user_id = 1;

-- Get activity breakdown
SELECT activity_type, COUNT(*) as count, SUM(points_earned) as total_points
FROM user_activities
WHERE user_id = 1
GROUP BY activity_type;

-- Get recent activities
SELECT activity_type, points_earned, created_at
FROM user_activities
WHERE user_id = 1
ORDER BY created_at DESC
LIMIT 10;

-- Calculate daily streak
SELECT COUNT(DISTINCT DATE(created_at)) as streak_days
FROM user_activities
WHERE user_id = 1
  AND activity_type = 'daily_login'
  AND created_at >= CURRENT_DATE - INTERVAL '30 days';
```

---

## 2. user_levels (NEW)

**Purpose**: Stores each user's current level and progress to the next level.

### Schema

```sql
CREATE TABLE user_levels (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    current_level VARCHAR DEFAULT 'Bronze',
    level_number INTEGER DEFAULT 1,
    points_to_next_level INTEGER DEFAULT 100,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX idx_user_levels_user_id ON user_levels(user_id);
```

### Level Definitions

| Level Number | Level Name | Icon | Points Range |
|--------------|------------|------|--------------|
| 1 | Bronze | 🥉 | 0 - 99 |
| 2 | Silver | 🥈 | 100 - 299 |
| 3 | Gold | 🥇 | 300 - 599 |
| 4 | Platinum | 💎 | 600 - 999 |
| 5 | Diamond | 💠 | 1000 - 1999 |
| 6 | Master | 👑 | 2000+ |

### Example Data

```sql
-- User at Bronze level
INSERT INTO user_levels (user_id, current_level, level_number, points_to_next_level)
VALUES (1, 'Bronze', 1, 100);

-- User at Gold level
INSERT INTO user_levels (user_id, current_level, level_number, points_to_next_level)
VALUES (2, 'Gold', 3, 250);
```

### Queries

```sql
-- Get user's current level
SELECT current_level, level_number, points_to_next_level
FROM user_levels
WHERE user_id = 1;

-- Update user's level
UPDATE user_levels
SET current_level = 'Silver',
    level_number = 2,
    points_to_next_level = 200,
    updated_at = NOW()
WHERE user_id = 1;

-- Get all users by level
SELECT u.username, ul.current_level, ul.level_number
FROM user_levels ul
JOIN users u ON u.id = ul.user_id
ORDER BY ul.level_number DESC, ul.points_to_next_level ASC;
```

---

## 3. badges (Existing)

**Purpose**: Defines all available achievement badges.

### Schema

```sql
CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    icon_url VARCHAR,
    points_required INTEGER DEFAULT 0,
    puzzles_required INTEGER DEFAULT 0,
    is_special BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Seeded Badges (15 total)

#### Beginner (3 badges)
- **First Steps**: Complete your first activity
- **Puzzle Novice**: Solve your first puzzle (1 puzzle)
- **Point Collector**: Earn 50 points

#### Intermediate (4 badges)
- **Puzzle Enthusiast**: Solve 10 puzzles
- **Century Club**: Reach 100 points
- **Dedicated Learner**: Reach 250 points
- **Puzzle Master**: Solve 25 puzzles

#### Advanced (3 badges)
- **Half Century**: Solve 50 puzzles
- **Point Champion**: Reach 500 points
- **Elite Solver** ⭐: Solve 100 puzzles (SPECIAL)

#### Expert (3 badges)
- **Thousand Club** ⭐: Reach 1000 points (SPECIAL)
- **Puzzle Legend** ⭐: Solve 200 puzzles (SPECIAL)
- **Ultimate Champion** ⭐: Reach 2000 points AND solve 100 puzzles (SPECIAL)

#### Special Event (2 badges)
- **Early Adopter** ⭐: One of the first users (10 points)
- **Weekend Warrior** ⭐: Complete 20 activities on weekends (100 points)

---

## 4. user_achievements (Existing)

**Purpose**: Tracks which badges each user has earned.

### Schema

```sql
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    badge_id INTEGER NOT NULL REFERENCES badges(id),
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, badge_id)
);

CREATE INDEX idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_badge_id ON user_achievements(badge_id);
```

---

## 5. leaderboard (Existing)

**Purpose**: Stores competitive rankings for users.

### Schema

```sql
CREATE TABLE leaderboard (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    total_points INTEGER DEFAULT 0,
    puzzles_completed INTEGER DEFAULT 0,
    badges_earned INTEGER DEFAULT 0,
    rank INTEGER,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_leaderboard_rank ON leaderboard(rank);
CREATE INDEX idx_leaderboard_points ON leaderboard(total_points DESC);
```

---

## Migration & Setup

### 1. Create Tables

```bash
cd backend
python migrate_gamification_tables.py
```

This creates the `user_activities` and `user_levels` tables.

### 2. Seed Badges

```bash
python seed_badges.py
```

This populates the `badges` table with 15 default achievement badges.

### 3. Verify Tables

```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('user_activities', 'user_levels', 'badges', 'user_achievements', 'leaderboard')
ORDER BY table_name;

-- Check badge count
SELECT COUNT(*) FROM badges;  -- Should return 15

-- Check table structures
\d user_activities
\d user_levels
```

---

## Relationships

```
users
  ↓
  ├─→ user_activities (one-to-many)
  ├─→ user_levels (one-to-one)
  ├─→ user_achievements (one-to-many)
  └─→ leaderboard (one-to-one)

badges
  ↓
  └─→ user_achievements (one-to-many)
```

---

## Performance Considerations

### Indexes Created

1. **user_activities**:
   - `user_id` - Fast user activity lookups
   - `activity_type` - Filter by activity type
   - `created_at` - Time-based queries

2. **user_levels**:
   - `user_id` - Unique constraint + fast lookup

3. **user_achievements**:
   - `user_id` - User's badges
   - `badge_id` - Badge holders
   - Unique constraint on `(user_id, badge_id)`

4. **leaderboard**:
   - `rank` - Leaderboard ordering
   - `total_points DESC` - Points-based ranking

### Query Optimization

```sql
-- Efficient: Get user stats in one query
SELECT 
    u.username,
    cp.total_points,
    ul.current_level,
    ul.level_number,
    COUNT(DISTINCT ua.id) FILTER (WHERE ua.activity_type = 'puzzle_solved') as puzzles_solved,
    COUNT(DISTINCT uach.id) as badges_earned
FROM users u
LEFT JOIN child_profiles cp ON cp.user_id = u.id
LEFT JOIN user_levels ul ON ul.user_id = u.id
LEFT JOIN user_activities ua ON ua.user_id = u.id
LEFT JOIN user_achievements uach ON uach.user_id = u.id
WHERE u.id = 1
GROUP BY u.id, u.username, cp.total_points, ul.current_level, ul.level_number;
```

---

## Backup & Maintenance

### Backup Tables

```bash
# Backup all gamification tables
pg_dump -h your-host -U your-user -d your-db \
  -t user_activities \
  -t user_levels \
  -t badges \
  -t user_achievements \
  -t leaderboard \
  > gamification_backup.sql
```

### Clean Old Activities (Optional)

```sql
-- Archive activities older than 1 year
DELETE FROM user_activities
WHERE created_at < NOW() - INTERVAL '1 year';
```

---

## Status

✅ **Tables Created**: `user_activities`, `user_levels`  
✅ **Badges Seeded**: 15 achievement badges  
✅ **Indexes Created**: Performance optimized  
✅ **Ready to Use**: System is fully operational  

---

**Last Updated**: January 2026  
**Database**: PostgreSQL (Neon DB)  
**Status**: Production Ready
