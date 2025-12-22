# Quantitative Research and Strategy Evaluation Platform
A comprehensive quantitative trading research platform with automated backtesting, risk analytics, and interactive data visualization. Built with FastAPI, Azure SQL Database, and integrated Power BI dashboards.

🌟 Features
🎯 Core Functionality

Automated Backtesting Engine - Test trading strategies on historical data
Multiple Risk Metrics - Sharpe Ratio, Max Drawdown, Value at Risk, Expected Shortfall
Real-time Market Data - Integration with Yahoo Finance API
Strategy Library - Moving Average, RSI, MACD, Cointegration, and more
Azure SQL Storage - Persistent storage of all backtest results

📊 Visualization & Reporting

Interactive Dashboard - Real-time charts and analytics using Chart.js
Power BI Integration - Advanced analytics with downloadable .pbix files
HTML Table Views - Sortable, filterable results with color coding
Export Options - CSV and JSON export for further analysis

🔌 API

RESTful API - FastAPI with automatic OpenAPI documentation
Swagger UI - Interactive API testing at /docs
JSON Responses - Machine-readable data for integration

Install dependencies

pip install -r requirements.txt

aDD YOUR DATABSE URL FOR AZURE IN CONFIG FILE
 DATABASE_URL =???


Initialize database

python init_db.py

Run the application

uvicorn main:app --reload

Open your browser
http://localhost:8000
