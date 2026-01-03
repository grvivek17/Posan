# Smart Food Court System

## Overview
The Smart Food Court System is a web application designed to optimize food court operations using AI-driven demand forecasting and real-time order management. It serves both **Vendors** (for tracking orders and insights) and **Customers** (for placing orders).

## Features
### 1. AI Dashboard (Home)
- **Peak Hours Forecast**: Predicts busy hours and recommends staffing levels.
- **Inventory Intelligence**: Optimizes stock levels based on demand.
- **Dynamic Pricing**: Suggests pricing strategies.
- **URL**: `http://127.0.0.1:8000/`

### 2. Ordering System (Customer)
- **Menu Browsing**: View available items (Burger, Pizza, Salad).
- **Cart Management**: Add items and view total cost.
- **Order Placement**: Submit orders to the system.
- **URL**: `http://127.0.0.1:8000/static/order.html` (Requires Login)

### 3. Vendor Dashboard
- **Live Order Tracking**: View incoming orders in real-time.
- **Sales Stats**: Track total orders and revenue.
- **URL**: `http://127.0.0.1:8000/static/vendor.html` (Requires Login)

### 4. Authentication
- **Role-Based Login**: Support for 'Vendor' and 'Customer' roles.
- **Mock Credentials**: Any email, password `password`.
- **URL**: `http://127.0.0.1:8000/static/login.html`

## Technical Architecture
### Backend (`src/`)
- **Framework**: FastAPI (Python)
- **Entry Point**: `main.py`
- **Routers**:
    - `api/v1/routers/forecast.py`: AI forecasting endpoints.
    - `api/v1/routers/auth.py`: Authentication logic (Mock).
    - `api/v1/routers/orders.py`: Order management (In-memory storage).

### Frontend (`src/static/`)
- **Tech Stack**: Vanilla HTML, CSS, JavaScript.
- **Styling**: Custom CSS with dark mode and glassmorphism design.
- **Logic**: `script.js` handles API calls and UI updates.

## How to Run
1.  **Install Dependencies**:
    ```bash
    pip install fastapi uvicorn pandas scikit-learn numpy
    ```
2.  **Start Server**:
    ```bash
    cd src
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
3.  **Access App**: Open `http://127.0.0.1:8000` in your browser.
