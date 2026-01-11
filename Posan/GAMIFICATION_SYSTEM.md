# 🎮 Gamification System Documentation

## Overview

The POSAN gamification system is a comprehensive points, badges, and levels system designed to encourage user engagement and make learning fun. Users earn points for various activities, unlock badges for achievements, and progress through different levels.

## Features

### 1. **Points System** ⭐

Users earn points for completing various activities:

| Activity | Points | Description |
|----------|--------|-------------|
| Puzzle Solved | 10 | Complete any puzzle |
| Article Read | 5 | Read a magazine article |
| Comment Posted | 2 | Post a comment |
| Content Shared | 3 | Share content |
| Quiz Completed | 15 | Complete a quiz |
| Daily Login | 1 | Login bonus (once per day) |
| Profile Completed | 20 | Complete profile setup |
| Homework Uploaded | 8 | Upload homework |
| Study Plan Created | 12 | Create a study plan |

### 2. **Level System** 🏅

Users progress through 6 levels based on total points:

| Level | Icon | Points Required | Points Range |
|-------|------|----------------|--------------|
| Bronze | 🥉 | 0 | 0 - 99 |
| Silver | 🥈 | 100 | 100 - 299 |
| Gold | 🥇 | 300 | 300 - 599 |
| Platinum | 💎 | 600 | 600 - 999 |
| Diamond | 💠 | 1000 | 1000 - 1999 |
| Master | 👑 | 2000 | 2000+ |

Each level displays:
- Current level name and icon
- Progress bar to next level
- Points needed to reach next level
- Level number

### 3. **Badges System** 🏆

Users can earn badges for specific achievements:

#### Beginner Badges
- **First Steps**: Complete your first activity
- **Puzzle Novice**: Solve your first puzzle
- **Point Collector**: Earn 50 points

#### Intermediate Badges
- **Puzzle Enthusiast**: Solve 10 puzzles
- **Century Club**: Reach 100 points
- **Dedicated Learner**: Reach 250 points
- **Puzzle Master**: Solve 25 puzzles

#### Advanced Badges
- **Half Century**: Solve 50 puzzles
- **Point Champion**: Reach 500 points
- **Elite Solver** ⭐: Solve 100 puzzles (Special)

#### Expert Badges
- **Thousand Club** ⭐: Reach 1000 points (Special)
- **Puzzle Legend** ⭐: Solve 200 puzzles (Special)
- **Ultimate Champion** ⭐: Reach 2000 points AND solve 100 puzzles (Special)

#### Special Event Badges
- **Early Adopter** ⭐: One of the first users
- **Weekend Warrior** ⭐: Complete 20 activities on weekends

### 4. **Daily Streak** 🔥

Track consecutive days of logging in. The streak counter increases each day you log in and resets if you miss a day.

## Technical Implementation

### Backend

#### Models

**UserActivity** (`app/models/activity.py`)
- Tracks all user activities
- Records points earned per activity
- Prevents duplicate point awards

**UserLevel** (`app/models/activity.py`)
- Stores user's current level
- Tracks progress to next level
- Updates automatically when points change

**Badge** (`app/models/gamification.py`)
- Defines available badges
- Sets requirements (points, puzzles)
- Marks special badges

**UserAchievement** (`app/models/gamification.py`)
- Links users to earned badges
- Records when badges were earned

#### Services

**GamificationService** (`app/services/gamification_service.py`)

Key methods:
```python
# Award points for an activity
award_points(user_id, activity_type, reference_id, reference_type)

# Update user level based on points
update_user_level(user_id, total_points)

# Check and award new badges
check_and_award_badges(user_id)

# Get comprehensive user stats
get_user_stats(user_id)

# Calculate daily login streak
get_daily_streak(user_id)
```

#### API Endpoints

**Gamification V2 API** (`/api/v1/gamification-v2/`)

- `POST /award-points` - Award points for an activity
- `GET /stats` - Get user's comprehensive stats
- `GET /stats/{user_id}` - Get stats for specific user
- `GET /level` - Get current level information
- `GET /activity-points` - Get points configuration
- `GET /levels` - Get all level definitions
- `GET /streak` - Get daily login streak
- `POST /daily-login` - Record daily login

### Frontend

#### Components

**PointsDisplay** (`components/common/PointsDisplay.jsx`)
- Shows user's points and level
- Displays progress bar
- Compact mode for header
- Full mode for dashboard
- Animated point updates

**BadgesDisplay** (`components/common/BadgesDisplay.jsx`)
- Grid view of all badges
- Earned vs locked states
- Badge detail modal
- Special badge effects

**GamificationPage** (`pages/GamificationPage.jsx`)
- Complete achievements dashboard
- Points and level display
- Daily streak tracker
- How to earn points guide
- Level system overview
- Badges showcase
- Pro tips section

#### Services

**GamificationService** (`services/gamificationService.js`)

Key methods:
```javascript
// Award points
GamificationService.awardPoints(activityType, referenceId, referenceType)

// Record daily login
GamificationService.recordDailyLogin()

// Get user stats
GamificationService.getUserStats()

// Get activity points config
GamificationService.getActivityPoints()

// Get all levels
GamificationService.getAllLevels()

// Get daily streak
GamificationService.getDailyStreak()
```

## Usage Examples

### Awarding Points (Backend)

```python
from app.services.gamification_service import GamificationService
from app.models.activity import ActivityType

service = GamificationService(db)

# Award points for solving a puzzle
result = service.award_points(
    user_id=user.id,
    activity_type=ActivityType.PUZZLE_SOLVED,
    reference_id=puzzle.id,
    reference_type="puzzle"
)

# Check result
if result['new_badges']:
    print(f"New badges earned: {result['new_badges']}")
if result['level']['level_up']:
    print(f"Level up! Now {result['level']['current_level']}")
```

### Awarding Points (Frontend)

```javascript
import GamificationService from '../services/gamificationService';

// Award points when user reads an article
const handleArticleRead = async (articleId) => {
  await GamificationService.awardPoints(
    'article_read',
    articleId,
    'article'
  );
  // Points notification will show automatically
};

// Award points when puzzle is completed
const handlePuzzleComplete = async (puzzleId) => {
  await GamificationService.awardPoints(
    'puzzle_solved',
    puzzleId,
    'puzzle'
  );
};
```

### Displaying Points

```jsx
import PointsDisplay from '../components/common/PointsDisplay';

// Compact mode (for header)
<PointsDisplay compact={true} />

// Full mode (for dashboard)
<PointsDisplay />
```

## Database Setup

### 1. Create Tables

The tables are automatically created when the app starts. The models include:
- `user_activities`
- `user_levels`
- `badges`
- `user_achievements`

### 2. Seed Badges

Run the badge seeding script:

```bash
cd backend
python seed_badges.py
```

This creates 15 default badges ranging from beginner to expert levels.

## Integration Points

### Puzzle Completion
Already integrated in `app/api/endpoints/puzzles.py`

### Article Reading
Add to magazine article view:
```python
service.award_points(user_id, ActivityType.ARTICLE_READ, article.id, "article")
```

### Comments
Add to comment creation:
```python
service.award_points(user_id, ActivityType.COMMENT_POSTED, comment.id, "comment")
```

### Quiz Completion
Add to quiz submission:
```python
service.award_points(user_id, ActivityType.QUIZ_COMPLETED, quiz.id, "quiz")
```

### Daily Login
Call on app load (already implemented):
```javascript
GamificationService.recordDailyLogin();
```

## UI/UX Features

### Animations
- **Float animation**: Icons gently float up and down
- **Pulse animation**: Points display pulses when updated
- **Shine effect**: Progress bars have animated shine
- **Glow effect**: Special badges have pulsing glow
- **Slide-in notifications**: Points awards show as toast notifications

### Visual Design
- **Gradient backgrounds**: Purple/blue gradients for premium feel
- **Glassmorphism**: Frosted glass effects on cards
- **Smooth transitions**: All interactions have smooth animations
- **Responsive design**: Works on all screen sizes
- **Dark mode ready**: Color scheme supports dark mode

### Accessibility
- Clear visual hierarchy
- High contrast text
- Descriptive labels
- Keyboard navigation support
- Screen reader friendly

## Best Practices

### Backend
1. Always use `GamificationService` for awarding points
2. Check for duplicate activities to prevent gaming
3. Award badges automatically when criteria met
4. Update leaderboard periodically
5. Log all point transactions

### Frontend
1. Show immediate feedback for point awards
2. Display progress clearly
3. Celebrate achievements with animations
4. Make badges visually distinct
5. Update stats in real-time

## Future Enhancements

- [ ] Leaderboard integration
- [ ] Weekly/monthly challenges
- [ ] Team competitions
- [ ] Seasonal events
- [ ] Custom badge creation
- [ ] Point multipliers
- [ ] Streak bonuses
- [ ] Social sharing
- [ ] Achievement notifications
- [ ] Progress analytics

## Troubleshooting

### Points not awarded
- Check if activity already recorded (duplicate prevention)
- Verify user has child profile
- Check database connection
- Review server logs

### Badges not unlocking
- Verify badge requirements met
- Check badge seeding completed
- Review badge criteria logic
- Check user achievement records

### Level not updating
- Verify points are being added to child profile
- Check level threshold configuration
- Review level calculation logic
- Refresh user stats

## Support

For issues or questions about the gamification system:
1. Check this documentation
2. Review the code comments
3. Check server logs
4. Test with seed data
5. Verify database migrations

---

**Last Updated**: January 2026
**Version**: 1.0.0
**Author**: POSAN Development Team
