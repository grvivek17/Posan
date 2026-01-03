import numpy as np
from typing import List, Dict
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime, time

class MenuRecommender:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
    async def train_model(self, historical_data: pd.DataFrame):
        """Train the recommendation model using historical order data."""
        try:
            # Prepare features
            features = self._prepare_features(historical_data)
            
            # Define model architecture
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(64, activation='relu', input_shape=(features.shape[1],)),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(16, activation='relu'),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            
            # Compile model
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Train model
            self.model = model
            return True
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return False
    
    async def get_recommendations(
        self,
        user_id: int,
        user_preferences: Dict,
        current_time: datetime,
        available_items: List[Dict]
    ) -> List[Dict]:
        """Get personalized menu recommendations for a user."""
        try:
            # Prepare input features
            features = self._prepare_prediction_features(
                user_preferences,
                current_time,
                available_items
            )
            
            # Get predictions
            predictions = self.model.predict(features)
            
            # Sort items by prediction score
            recommended_items = []
            for idx, score in enumerate(predictions):
                if score > 0.5:  # Threshold for recommendation
                    item = available_items[idx].copy()
                    item['recommendation_score'] = float(score)
                    recommended_items.append(item)
            
            # Sort by score
            recommended_items.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            return recommended_items
            
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            return []
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for model training."""
        features = []
        
        # Time-based features
        data['hour'] = data['order_time'].apply(lambda x: x.hour)
        data['day_of_week'] = data['order_time'].apply(lambda x: x.weekday())
        
        # User preference features
        data['preference_match'] = data.apply(
            lambda row: self._calculate_preference_match(
                row['item_attributes'],
                row['user_preferences']
            ),
            axis=1
        )
        
        # Historical popularity
        data['popularity'] = data.groupby('item_id')['ordered'].transform('mean')
        
        # Prepare final feature matrix
        feature_columns = ['hour', 'day_of_week', 'preference_match', 'popularity']
        features = data[feature_columns].values
        
        # Scale features
        features = self.scaler.fit_transform(features)
        
        return features
    
    def _prepare_prediction_features(
        self,
        user_preferences: Dict,
        current_time: datetime,
        available_items: List[Dict]
    ) -> np.ndarray:
        """Prepare features for prediction."""
        features = []
        
        for item in available_items:
            # Time features
            hour = current_time.hour
            day_of_week = current_time.weekday()
            
            # Preference match
            preference_match = self._calculate_preference_match(
                item['attributes'],
                user_preferences
            )
            
            # Popularity (assuming it's included in item data)
            popularity = item.get('popularity', 0.0)
            
            features.append([hour, day_of_week, preference_match, popularity])
        
        # Convert to numpy array and scale
        features = np.array(features)
        features = self.scaler.transform(features)
        
        return features
    
    def _calculate_preference_match(
        self,
        item_attributes: Dict,
        user_preferences: Dict
    ) -> float:
        """Calculate how well an item matches user preferences."""
        match_score = 0.0
        total_preferences = len(user_preferences)
        
        if total_preferences == 0:
            return 0.5  # Neutral score if no preferences
            
        for pref, value in user_preferences.items():
            if pref in item_attributes:
                if item_attributes[pref] == value:
                    match_score += 1
                    
        return match_score / total_preferences
