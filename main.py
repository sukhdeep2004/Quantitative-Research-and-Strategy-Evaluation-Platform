from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from api.routes import router

app = FastAPI(title="Quant Research Platform")

@app.get("/", response_class=HTMLResponse)
def home():
    """Homepage with navigation"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quant Research Platform</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                width: 100%;
            }
            
            .hero {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 60px;
                text-align: center;
            }
            
            h1 {
                font-size: 48px;
                color: #333;
                margin-bottom: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                font-size: 20px;
                color: #666;
                margin-bottom: 40px;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 30px;
                margin: 40px 0;
            }
            
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px;
                border-radius: 15px;
                color: white;
            }
            
            .stat-value {
                font-size: 36px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            
            .stat-label {
                font-size: 14px;
                opacity: 0.9;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .button-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            
            .btn {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 30px;
                text-decoration: none;
                border-radius: 15px;
                transition: all 0.3s;
                border: 3px solid transparent;
                background: #f8f9fa;
                min-height: 180px;
            }
            
            .btn:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .btn-primary:hover {
                opacity: 0.9;
            }
            
            .btn-secondary {
                border-color: #667eea;
            }
            
            .btn-secondary:hover {
                background: #667eea;
                color: white;
            }
            
            .btn-icon {
                font-size: 48px;
                margin-bottom: 15px;
            }
            
            .btn-title {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
                color: inherit;
            }
            
            .btn-desc {
                font-size: 14px;
                opacity: 0.8;
                color: inherit;
            }
            
            .footer {
                margin-top: 40px;
                padding-top: 30px;
                border-top: 2px solid #eee;
                color: #666;
                font-size: 14px;
            }
            
            .status-badge {
                display: inline-block;
                padding: 8px 16px;
                background: #4CAF50;
                color: white;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            
            @media (max-width: 768px) {
                .hero {
                    padding: 30px;
                }
                
                h1 {
                    font-size: 32px;
                }
                
                .button-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <div class="status-badge">🟢 System Online</div>
                <h1>📊 Quant Research Platform</h1>
                <p class="subtitle">Advanced quantitative trading analytics and backtesting</p>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value" id="total-tests">-</div>
                        <div class="stat-label">Total Backtests</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="avg-sharpe">-</div>
                        <div class="stat-label">Avg Sharpe Ratio</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="success-rate">-</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                </div>
                
                <div class="button-grid">

                     <a href="/run-all-backtests" class="btn btn-primary">
                        <div class="btn-icon">🚀</div>
                        <div class="btn-title">Run All Backtests</div>
                        <div class="btn-desc">Test multiple strategies on any stock</div>
                    </a>
                    <a href="/docs" class="btn btn-secondary">
                        <div class="btn-icon">📚</div>
                        <div class="btn-title">API Documentation</div>
                        <div class="btn-desc">Explore REST API endpoints</div>
                    </a>
                    
                    <a href="/backtest-results" class="btn btn-secondary">
                        <div class="btn-icon">🔍</div>
                        <div class="btn-title">Raw Data</div>
                        <div class="btn-desc">View Tabular backtest results</div>
                    </a>
                    
                    <a href="/download-powerbi" class="btn btn-secondary" download>
                        <div class="btn-icon">📥</div>
                        <div class="btn-title">Download Power BI</div>
                        <div class="btn-desc">Get .pbix file for offline analysis</div>
                    </a>
                </div>
                
                <div class="footer">
                    <p><strong>Quick Start:</strong></p>
                    <p>1. Click "Raw Data" to see THE TABLE</p>
                    <p>2. Use "API Documentation" to run backtests via POST /run-backtest</p>
                    <p>3. Download Power BI file for advanced custom analysis</p>
                    <br>
                    <p>Built with FastAPI • Azure SQL • Power BI</p>
                </div>
            </div>
        </div>
        
        <script>
            // Load stats
            fetch('/dashboard-data')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('total-tests').textContent = data.kpis.total_tests;
                    document.getElementById('avg-sharpe').textContent = data.kpis.avg_sharpe.toFixed(2);
                    document.getElementById('success-rate').textContent = data.kpis.success_rate.toFixed(0) + '%';
                })
                .catch(err => {
                    console.error('Error loading stats:', err);
                    document.getElementById('total-tests').textContent = '0';
                    document.getElementById('avg-sharpe').textContent = '0.00';
                    document.getElementById('success-rate').textContent = '0%';
                });
        </script>
    </body>
    </html>
    """
    return html_content

app.include_router(router)