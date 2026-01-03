from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import tensorflow as tf

from core.dependencies import get_db, get_current_user
from core.ml.demand_forecasting import DemandForecaster
from core.schemas.analytics import (
    VendorAnalyticsResponse,
    PeakHourPredictionResponse,
    InventoryPredictionResponse,
    SalesAnalyticsResponse
)

router = APIRouter()

@router.get("/vendor/{vendor_id}/dashboard")
async def get_vendor_dashboard(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get vendor dashboard analytics."""
    try:
        # Validate vendor access
        if not current_user.is_vendor and not current_user.is_staff:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access vendor analytics"
            )
        
        # Get analytics data
        analytics = await get_vendor_analytics(
            vendor_id,
            start_date,
            end_date,
            db
        )
        
        # Get peak hour predictions
        peak_hours = await get_peak_hour_predictions(
            vendor_id,
            datetime.now().date(),
            db
        )
        
        # Get inventory predictions
        inventory = await get_inventory_predictions(
            vendor_id,
            datetime.now().date(),
            db
        )
        
        return {
            "analytics": analytics,
            "peak_hours": peak_hours,
            "inventory": inventory
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/vendor/{vendor_id}/peak-hours")
async def predict_peak_hours(
    vendor_id: int,
    date: datetime,
    db: Session = Depends(get_db)
):
    """Predict peak hours and resource requirements."""
    try:
        forecaster = DemandForecaster()
        
        # Get historical data
        historical_data = await get_historical_orders(vendor_id, db)
        
        # Prepare features
        features = prepare_peak_hour_features(historical_data, date)
        
        # Get predictions
        predictions = await forecaster.predict_peak_hours(features)
        
        return {
            "date": date,
            "predictions": predictions,
            "confidence_score": forecaster.get_confidence_score()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/vendor/{vendor_id}/inventory-optimization")
async def optimize_inventory(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """Optimize inventory levels based on demand predictions."""
    try:
        # Get historical inventory and sales data
        inventory_data = await get_inventory_data(vendor_id, db)
        sales_data = await get_sales_data(vendor_id, db)
        
        # Prepare features for optimization
        features = prepare_inventory_features(
            inventory_data,
            sales_data,
            start_date,
            end_date
        )
        
        # Run optimization
        recommendations = await optimize_inventory_levels(features)
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/vendor/{vendor_id}/sales-analytics")
async def analyze_sales(
    vendor_id: int,
    period: str,
    db: Session = Depends(get_db)
):
    """Get detailed sales analytics with trends and patterns."""
    try:
        # Get sales data
        sales_data = await get_sales_data(vendor_id, db)
        
        # Analyze trends
        trends = analyze_sales_trends(sales_data, period)
        
        # Generate insights
        insights = generate_sales_insights(trends)
        
        return {
            "period": period,
            "trends": trends,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

async def get_vendor_analytics(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> VendorAnalyticsResponse:
    """Get vendor analytics data."""
    # Query database for analytics
    analytics = db.query(VendorAnalytics).filter(
        VendorAnalytics.vendor_id == vendor_id,
        VendorAnalytics.date.between(start_date, end_date)
    ).all()
    
    # Process and aggregate data
    result = process_vendor_analytics(analytics)
    return result

async def get_peak_hour_predictions(
    vendor_id: int,
    date: datetime,
    db: Session
) -> List[PeakHourPredictionResponse]:
    """Get peak hour predictions."""
    # Query existing predictions
    predictions = db.query(PeakHourPrediction).filter(
        PeakHourPrediction.vendor_id == vendor_id,
        PeakHourPrediction.date == date
    ).all()
    
    if not predictions:
        # Generate new predictions if none exist
        predictions = await generate_peak_hour_predictions(vendor_id, date, db)
    
    return [PeakHourPredictionResponse.from_orm(p) for p in predictions]

async def get_inventory_predictions(
    vendor_id: int,
    date: datetime,
    db: Session
) -> List[InventoryPredictionResponse]:
    """Get inventory requirement predictions."""
    # Query existing predictions
    predictions = db.query(InventoryPrediction).filter(
        InventoryPrediction.menu_item.has(vendor_id=vendor_id),
        InventoryPrediction.date == date
    ).all()
    
    if not predictions:
        # Generate new predictions if none exist
        predictions = await generate_inventory_predictions(vendor_id, date, db)
    
    return [InventoryPredictionResponse.from_orm(p) for p in predictions]
