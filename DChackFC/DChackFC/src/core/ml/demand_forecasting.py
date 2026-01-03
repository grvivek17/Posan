import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class DemandForecaster:
    """Class for predicting demand and optimizing inventory."""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        self.scaler = StandardScaler()
        self._confidence_score = 0.0
        
    async def predict_peak_hours(
        self,
        features: pd.DataFrame,
        historical_data: Optional[pd.DataFrame] = None
    ) -> List[Dict]:
        """Predict peak hours and demand for each hour."""
        try:
            if historical_data is not None:
                # Train model if historical data provided
                await self._train_model(historical_data)
            
            # Scale features
            scaled_features = self.scaler.transform(features)
            
            # Make predictions
            predictions = self.model.predict(scaled_features)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(predictions)
            
            # Format results
            results = []
            for i, pred in enumerate(predictions):
                results.append({
                    'hour': features.index[i].hour,
                    'predicted_orders': int(pred),
                    'confidence_score': confidence_scores[i],
                    'recommended_staff': self._calculate_staff_needed(pred)
                })
            
            return results
            
        except Exception as e:
            print(f"Error in peak hour prediction: {str(e)}")
            return []
    
    async def predict_inventory_needs(
        self,
        menu_items: List[Dict],
        historical_data: pd.DataFrame
    ) -> List[Dict]:
        """Predict inventory requirements for menu items."""
        try:
            # Prepare features for each item
            predictions = []
            
            for item in menu_items:
                # Get item-specific historical data
                item_data = historical_data[
                    historical_data['item_id'] == item['id']
                ]
                
                if len(item_data) < 7:  # Minimum data requirement
                    continue
                
                # Prepare features
                features = self._prepare_inventory_features(item_data)
                
                # Scale features
                scaled_features = self.scaler.transform(features)
                
                # Predict demand
                predicted_demand = self.model.predict(scaled_features)
                
                # Calculate optimal stock levels
                stock_levels = self._calculate_stock_levels(
                    predicted_demand[0],
                    item_data
                )
                
                predictions.append({
                    'item_id': item['id'],
                    'predicted_demand': int(predicted_demand[0]),
                    'recommended_stock': stock_levels['recommended'],
                    'min_stock': stock_levels['min'],
                    'max_stock': stock_levels['max'],
                    'confidence_score': self._calculate_confidence_score(
                        predicted_demand[0],
                        item_data['actual_demand'].std()
                    )
                })
            
            return predictions
            
        except Exception as e:
            print(f"Error in inventory prediction: {str(e)}")
            return []
    
    async def optimize_pricing(
        self,
        menu_items: List[Dict],
        historical_data: pd.DataFrame
    ) -> List[Dict]:
        """Optimize pricing based on demand and competition."""
        try:
            optimized_prices = []
            
            for item in menu_items:
                # Get item-specific data
                item_data = historical_data[
                    historical_data['item_id'] == item['id']
                ]
                
                if len(item_data) < 14:  # Minimum 2 weeks of data
                    continue
                
                # Calculate price elasticity
                elasticity = self._calculate_price_elasticity(item_data)
                
                # Find optimal price
                optimal_price = self._find_optimal_price(
                    item['current_price'],
                    elasticity,
                    item_data
                )
                
                optimized_prices.append({
                    'item_id': item['id'],
                    'current_price': item['current_price'],
                    'recommended_price': optimal_price,
                    'expected_demand_change': self._calculate_demand_change(
                        item['current_price'],
                        optimal_price,
                        elasticity
                    ),
                    'confidence_score': self._calculate_price_confidence(
                        elasticity,
                        len(item_data)
                    )
                })
            
            return optimized_prices
            
        except Exception as e:
            print(f"Error in price optimization: {str(e)}")
            return []
    
    async def _train_model(self, historical_data: pd.DataFrame):
        """Train the forecasting model."""
        try:
            # Prepare features and targets
            features = self._prepare_training_features(historical_data)
            targets = historical_data['demand'].values
            
            # Scale features
            scaled_features = self.scaler.fit_transform(features)
            
            # Train model
            self.model.fit(scaled_features, targets)
            
            # Update confidence score
            self._confidence_score = self.model.score(scaled_features, targets)
            
        except Exception as e:
            print(f"Error in model training: {str(e)}")
    
    def _prepare_training_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for model training."""
        features = []
        
        # Time-based features
        data['hour'] = data.index.hour
        data['day_of_week'] = data.index.dayofweek
        data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
        
        # Rolling statistics
        data['demand_ma'] = data['demand'].rolling(window=24).mean()
        data['demand_std'] = data['demand'].rolling(window=24).std()
        
        # Lag features
        data['demand_lag1'] = data['demand'].shift(1)
        data['demand_lag24'] = data['demand'].shift(24)
        
        # Weather features if available
        if 'temperature' in data.columns:
            features.extend(['temperature', 'is_rainy'])
        
        return data[features].fillna(0)
    
    def _calculate_confidence_scores(
        self,
        predictions: np.ndarray
    ) -> np.ndarray:
        """Calculate confidence scores for predictions."""
        # Base confidence on model score and prediction variance
        base_confidence = self._confidence_score
        prediction_std = predictions.std()
        
        confidence_scores = np.ones_like(predictions) * base_confidence
        
        # Adjust confidence based on prediction variance
        confidence_scores *= (1 - (predictions.std() / predictions.mean()) * 0.5)
        
        return np.clip(confidence_scores, 0, 1)
    
    def _calculate_staff_needed(self, predicted_orders: float) -> int:
        """Calculate recommended staff based on predicted orders."""
        # Basic calculation: 1 staff per 20 orders per hour
        # Minimum 2 staff, maximum 10
        base_staff = max(2, min(10, int(predicted_orders / 20)))
        
        # Add buffer during peak hours
        if predicted_orders > 50:
            base_staff += 1
        
        return base_staff
    
    def _calculate_stock_levels(
        self,
        predicted_demand: float,
        historical_data: pd.DataFrame
    ) -> Dict:
        """Calculate optimal stock levels."""
        demand_std = historical_data['actual_demand'].std()
        
        return {
            'recommended': int(predicted_demand * 1.2),  # 20% buffer
            'min': int(predicted_demand * 0.8),  # 20% below prediction
            'max': int(predicted_demand * 1.5)  # 50% above prediction
        }
    
    def get_confidence_score(self) -> float:
        """Get the current model's confidence score."""
        return self._confidence_score
