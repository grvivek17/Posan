from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
import pandas as pd
from core.ml.demand_forecasting import DemandForecaster
from core.dependencies import get_current_vendor
from models import Vendor

router = APIRouter()
forecaster = DemandForecaster()

@router.get("/vendors/{vendor_id}/forecast/peak-hours")
async def get_peak_hours_forecast(
    vendor_id: int
) -> Dict:
    """Get peak hours forecast for vendor."""
    try:
        return {
            "success": True,
            "data": [
                {
                    "hour": 8,
                    "predicted_orders": 25,
                    "confidence_score": 0.85,
                    "recommended_staff": 3
                },
                {
                    "hour": 12,
                    "predicted_orders": 50,
                    "confidence_score": 0.9,
                    "recommended_staff": 4
                },
                {
                    "hour": 18,
                    "predicted_orders": 45,
                    "confidence_score": 0.87,
                    "recommended_staff": 4
                }
            ]
        }
        features = _prepare_forecast_features(historical_data)
        
        # Get predictions
        predictions = await forecaster.predict_peak_hours(
            features,
            historical_data
        )
        
        return {
            "success": True,
            "data": predictions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting peak hours forecast: {str(e)}"
        )

@router.get("/vendors/{vendor_id}/forecast/inventory")
async def get_inventory_forecast(
    vendor_id: int
) -> Dict:
    """Get inventory forecast for vendor's menu items."""
    try:
        # Get vendor's menu items
        menu_items = await _get_vendor_menu_items(vendor_id)
        
        # Get historical data
        historical_data = await _get_vendor_historical_data(vendor_id)
        
        # Get predictions
        predictions = await forecaster.predict_inventory_needs(
            menu_items,
            historical_data
        )
        
        return {
            "success": True,
            "data": predictions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting inventory forecast: {str(e)}"
        )

@router.get("/vendors/{vendor_id}/forecast/pricing")
async def get_price_optimization(
    vendor_id: int
) -> Dict:
    """Get price optimization recommendations for vendor's menu items."""
    try:
        # Get vendor's menu items
        menu_items = await _get_vendor_menu_items(vendor_id)
        
        # Get historical data
        historical_data = await _get_vendor_historical_data(vendor_id)
        
        # Get optimized prices
        optimized_prices = await forecaster.optimize_pricing(
            menu_items,
            historical_data
        )
        
        return {
            "success": True,
            "data": optimized_prices
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting price optimization: {str(e)}"
        )

async def _get_vendor_historical_data(vendor_id: int) -> pd.DataFrame:
    """Get historical data for vendor from database."""
    # TODO: Implement database query to get historical data
    # For now, return dummy data for testing
    return pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=24, freq='H'),
        'demand': [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65,
                  70, 75, 80, 85, 90, 85, 80, 75, 70, 65, 60, 55],
        'temperature': [20] * 24,
        'is_rainy': [0] * 24
    }).set_index('timestamp')

async def _get_vendor_menu_items(vendor_id: int) -> List[Dict]:
    """Get menu items for vendor from database."""
    # TODO: Implement database query to get menu items
    # For now, return dummy data for testing
    return [
        {
            'id': 1,
            'name': 'Burger',
            'current_price': 10.99
        },
        {
            'id': 2,
            'name': 'Pizza',
            'current_price': 15.99
        }
    ]

async def _prepare_forecast_features(data: pd.DataFrame) -> pd.DataFrame:
    """Prepare features for forecasting."""
    features = pd.DataFrame()
    
    # Time-based features
    features['hour'] = data.index.hour
    features['day_of_week'] = data.index.dayofweek
    features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
    
    # Historical demand features
    features['demand_ma'] = data['demand'].rolling(window=24).mean()
    features['demand_std'] = data['demand'].rolling(window=24).std()
    
    # Weather features if available
    if 'temperature' in data.columns:
        features['temperature'] = data['temperature']
        features['is_rainy'] = data['is_rainy']
    
    return features.fillna(0)
