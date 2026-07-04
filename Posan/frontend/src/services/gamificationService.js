/**
 * Gamification Service
 * Helper functions for awarding points and tracking activities
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class GamificationService {
    /**
     * Get user ID from localStorage
     */
    static getUserId() {
        const userId = localStorage.getItem('user_id');
        if (!userId) {
            console.warn('No user_id found in localStorage');
            return null;
        }
        return parseInt(userId);
    }

    /**
     * Award points for an activity
     * @param {string} activityType - Type of activity (puzzle_solved, article_read, etc.)
     * @param {number} referenceId - Optional ID of the related entity
     * @param {string} referenceType - Optional type of the reference
     * @returns {Promise} Response with points awarded and level info
     */
    static async awardPoints(activityType, referenceId = null, referenceType = null) {
        try {
            const token = localStorage.getItem('token');
            const userId = this.getUserId();

            if (!token || !userId) {
                console.warn('No auth token or user_id found');
                return null;
            }

            const response = await axios.post(
                `${API_BASE_URL}/gamification-v2/award-points`,
                {
                    activity_type: activityType,
                    reference_id: referenceId,
                    reference_type: referenceType
                },
                {
                    params: { user_id: userId },
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            // Show notification if points were awarded
            if (response.data.points_awarded > 0) {
                this.showPointsNotification(response.data);
            }

            return response.data;
        } catch (error) {
            console.error('Error awarding points:', error);
            return null;
        }
    }

    /**
     * Show a notification when points are awarded
     */
    static showPointsNotification(data) {
        const { points_awarded, new_total, level, new_badges } = data;

        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'points-notification';

        let content = `
      <div class="points-notification-content">
        <div class="points-earned">+${points_awarded} points!</div>
        <div class="points-total">Total: ${new_total}</div>
    `;

        // Add level up notification
        if (level && level.level_up) {
            content += `
        <div class="level-up">
          🎉 Level Up! ${level.current_level} ${level.level_icon}
        </div>
      `;
        }

        // Add new badges
        if (new_badges && new_badges.length > 0) {
            content += `<div class="new-badges">`;
            new_badges.forEach(badge => {
                content += `<div class="badge-earned">🏆 ${badge.name}</div>`;
            });
            content += `</div>`;
        }

        content += `</div>`;
        notification.innerHTML = content;

        // Add to page
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);

        // Remove after 4 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    /**
     * Record daily login
     */
    static async recordDailyLogin() {
        try {
            const token = localStorage.getItem('token');
            const userId = this.getUserId();

            if (!token || !userId) return null;

            const response = await axios.post(
                `${API_BASE_URL}/gamification-v2/daily-login`,
                {},
                {
                    params: { user_id: userId },
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            if (response.data.points_awarded > 0) {
                this.showPointsNotification(response.data);
            }

            return response.data;
        } catch (error) {
            console.error('Error recording daily login:', error);
            return null;
        }
    }

    /**
     * Get user stats
     */
    static async getUserStats() {
        try {
            const token = localStorage.getItem('token');
            const userId = this.getUserId();

            if (!token || !userId) return null;

            const response = await axios.get(
                `${API_BASE_URL}/gamification-v2/stats`,
                {
                    params: { user_id: userId },
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            return response.data;
        } catch (error) {
            console.error('Error fetching stats:', error);
            return null;
        }
    }

    /**
     * Get activity points configuration
     */
    static async getActivityPoints() {
        try {
            const response = await axios.get(`${API_BASE_URL}/gamification-v2/activity-points`);
            return response.data;
        } catch (error) {
            console.error('Error fetching activity points:', error);
            return [];
        }
    }

    /**
     * Get all levels
     */
    static async getAllLevels() {
        try {
            const response = await axios.get(`${API_BASE_URL}/gamification-v2/levels`);
            return response.data;
        } catch (error) {
            console.error('Error fetching levels:', error);
            return [];
        }
    }

    /**
     * Get daily streak
     */
    static async getDailyStreak() {
        try {
            const token = localStorage.getItem('token');
            const userId = this.getUserId();

            if (!token || !userId) return null;

            const response = await axios.get(
                `${API_BASE_URL}/gamification-v2/streak`,
                {
                    params: { user_id: userId },
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            return response.data;
        } catch (error) {
            console.error('Error fetching streak:', error);
            return null;
        }
    }
    /**
     * Convenience method for adding points
     * @param {string} activityType - Type of activity
     * @param {object} metadata - Optional metadata (puzzle_type, etc.)
     */
    static async addPoints(activityType, metadata = {}) {
        return await this.awardPoints(
            activityType,
            metadata.reference_id || null,
            metadata.reference_type || activityType
        );
    }
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
  .points-notification {
    position: fixed;
    top: 80px;
    right: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px 24px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    z-index: 10000;
    transform: translateX(400px);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    min-width: 250px;
  }

  .points-notification.show {
    transform: translateX(0);
  }

  .points-notification-content {
    text-align: center;
  }

  .points-earned {
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 4px;
    animation: bounce 0.6s ease;
  }

  .points-total {
    font-size: 14px;
    opacity: 0.9;
    margin-bottom: 8px;
  }

  .level-up {
    background: rgba(255, 255, 255, 0.2);
    padding: 8px 12px;
    border-radius: 8px;
    margin-top: 12px;
    font-weight: 700;
    animation: pulse 0.6s ease;
  }

  .new-badges {
    margin-top: 12px;
  }

  .badge-earned {
    background: rgba(255, 255, 255, 0.2);
    padding: 6px 12px;
    border-radius: 8px;
    margin-top: 6px;
    font-size: 13px;
    font-weight: 600;
  }

  @keyframes bounce {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }

  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }

  @media (max-width: 768px) {
    .points-notification {
      right: 10px;
      left: 10px;
      min-width: auto;
    }
  }
`;
document.head.appendChild(style);

// Export both the class and an instance
export const gamificationService = GamificationService;
export default GamificationService;
