from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from quant.data import fetch_price_data
from quant.backtest import backtest
from quant.risk import sharpe_ratio, max_drawdown
from db.models import BacktestResult
from db.session import get_db
from api.schemas import BacktestRequest
from sqlalchemy import func
import os

router = APIRouter()
@router.post("/run-backtest")
def run_backtest(req: BacktestRequest, db: Session = Depends(get_db)):
    try:
        df = fetch_price_data(req.ticker, req.start, req.end)
        signals = df['returns'].rolling(20).mean().apply(lambda x: -1 if x > 0 else 1)
        equity, strat_returns = backtest(df['returns'], signals)

        #metrics
        sharpe = sharpe_ratio(strat_returns)
        final_eq = float(equity.iloc[-1])
        max_dd = max_drawdown(equity)
        total_ret = ((final_eq - 1) * 100)

        #trades number
        num_trades = (signals.diff() != 0).sum()

        #win rate
        winning_trades= strat_returns[strat_returns > 0].count()
        total_trades = strat_returns[strat_returns != 0].count()
        win_rate = winning_trades / (total_trades*100) if total_trades > 0 else 0

        result={
            "ticker": req.ticker,
            "start_date": req.start,
            "end_date": req.end,
            "strategy_name": "Moving Average",
            "sharpe_ratio": float(sharpe),
            "final_equity": final_eq,
            "max_drawdown": float(max_dd),
            "total_return": float(total_ret),
            "win_rate": float(win_rate),
            "num_trades": int(num_trades),
            "created_at": datetime.utcnow()
        }
        BacktestResult_instance = BacktestResult(**result)
        db.add(BacktestResult_instance)
        db.commit()
        db.refresh(BacktestResult_instance)
        return {
            "id": BacktestResult_instance.id,
            "ticker": BacktestResult_instance.ticker,
            "sharpe": float(sharpe),
            "final_equity": final_eq,
            "max_drawdown": float(max_dd),
            "total_return": float(total_ret),
            "win_rate": float(win_rate),
            "num_trades": int(num_trades),
            "created_at": BacktestResult_instance.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/backtest-results", response_class=HTMLResponse)
def get_backtest_results(db: Session = Depends(get_db), limit: int = 100):
    """Get all backtest results as HTML table"""
    results = db.query(BacktestResult).order_by(BacktestResult.created_at.desc()).limit(limit).all()
    
    # Calculate summary stats
    total = len(results)
    avg_sharpe = sum(r.sharpe_ratio for r in results) / total if total > 0 else 0
    profitable = sum(1 for r in results if r.total_return > 0)
    success_rate = (profitable / total * 100) if total > 0 else 0
    
    # Generate table rows
    rows_html = ""
    for r in results:
        sharpe_class = "excellent" if r.sharpe_ratio >= 1.5 else "good" if r.sharpe_ratio >= 1 else "average" if r.sharpe_ratio >= 0.5 else "poor"
        return_class = "positive" if r.total_return >= 0 else "negative"
        
        rows_html += f"""
        <tr>
            <td>{r.id}</td>
            <td><strong>{r.ticker}</strong></td>
            <td>{r.strategy_name}</td>
            <td>{r.start_date.strftime('%Y-%m-%d')}</td>
            <td>{r.end_date.strftime('%Y-%m-%d')}</td>
            <td class="{sharpe_class}">{r.sharpe_ratio:.2f}</td>
            <td class="{return_class}">{r.total_return:.2f}%</td>
            <td>{r.win_rate:.1f}%</td>
            <td class="negative">{r.max_drawdown:.2f}%</td>
            <td>{r.final_equity:.4f}</td>
            <td>{r.num_trades}</td>
            <td>{r.created_at.strftime('%Y-%m-%d %H:%M')}</td>
        </tr>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Backtest Results</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .header {{
                background: white;
                padding: 20px 30px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 15px;
            }}
            
            .header h1 {{
                color: #333;
                font-size: 28px;
            }}
            
            .nav-buttons {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }}
            
            .btn {{
                padding: 10px 20px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background 0.3s;
                border: none;
                cursor: pointer;
                font-size: 14px;
            }}
            
            .btn:hover {{
                background: #5568d3;
            }}
            
            .btn-secondary {{
                background: #6c757d;
            }}
            
            .btn-secondary:hover {{
                background: #5a6268;
            }}
            
            .summary-cards {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }}
            
            .summary-card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                text-align: center;
            }}
            
            .summary-value {{
                font-size: 32px;
                font-weight: bold;
                color: #667eea;
                margin: 10px 0;
            }}
            
            .summary-label {{
                color: #666;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .table-container {{
                background: white;
                padding: 0;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .table-header {{
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            
            .table-header h2 {{
                font-size: 20px;
                margin: 0;
            }}
            
            .table-wrapper {{
                overflow-x: auto;
                max-height: 70vh;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            thead {{
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            
            th {{
                background: #f8f9fa;
                color: #333;
                padding: 15px 12px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #dee2e6;
                white-space: nowrap;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            td {{
                padding: 12px;
                border-bottom: 1px solid #eee;
                font-size: 14px;
            }}
            
            tr:hover {{
                background: #f8f9fa;
            }}
            
            tr:nth-child(even) {{
                background: #fafafa;
            }}
            
            tr:nth-child(even):hover {{
                background: #f0f0f0;
            }}
            
            .positive {{
                color: #28a745;
                font-weight: bold;
            }}
            
            .negative {{
                color: #dc3545;
                font-weight: bold;
            }}
            
            .excellent {{
                color: #28a745;
                font-weight: bold;
            }}
            
            .good {{
                color: #20c997;
                font-weight: bold;
            }}
            
            .average {{
                color: #ffc107;
                font-weight: bold;
            }}
            
            .poor {{
                color: #dc3545;
                font-weight: bold;
            }}
            
            .filter-bar {{
                background: white;
                padding: 15px 20px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                align-items: center;
            }}
            
            .filter-bar label {{
                font-weight: 600;
                color: #333;
            }}
            
            .filter-bar select, .filter-bar input {{
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }}
            
            .no-results {{
                text-align: center;
                padding: 40px;
                color: #666;
                font-size: 16px;
            }}
            
            .export-btn {{
                background: #28a745;
            }}
            
            .export-btn:hover {{
                background: #218838;
            }}
            
            @media (max-width: 768px) {{
                .header {{
                    flex-direction: column;
                    align-items: flex-start;
                }}
                
                .table-wrapper {{
                    max-height: 60vh;
                }}
                
                td, th {{
                    font-size: 12px;
                    padding: 8px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Backtest Results</h1>
            <div class="nav-buttons">
                <a href="/" class="btn btn-secondary">← Home</a>
                <a href="/docs" class="btn">📚 API Docs</a>
                <button onclick="exportToCSV()" class="btn export-btn">📥 Export CSV</button>
            </div>
        </div>
        
        <div class="summary-cards">
            <div class="summary-card">
                <div class="summary-label">Total Results</div>
                <div class="summary-value">{total}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Avg Sharpe Ratio</div>
                <div class="summary-value">{avg_sharpe:.2f}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Success Rate</div>
                <div class="summary-value">{success_rate:.0f}%</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Profitable Tests</div>
                <div class="summary-value">{profitable}</div>
            </div>
        </div>
        
        <div class="filter-bar">
            <label>Filter by Ticker:</label>
            <select id="tickerFilter" onchange="filterTable()">
                <option value="">All Tickers</option>
            </select>
            
            <label>Filter by Strategy:</label>
            <select id="strategyFilter" onchange="filterTable()">
                <option value="">All Strategies</option>
            </select>
            
            <label>Min Sharpe:</label>
            <input type="number" id="minSharpe" placeholder="0.0" step="0.1" onchange="filterTable()" style="width: 80px;">
            
            <label>Show:</label>
            <select id="showFilter" onchange="filterTable()">
                <option value="all">All Results</option>
                <option value="profitable">Profitable Only</option>
                <option value="loss">Losses Only</option>
            </select>
        </div>
        
        <div class="table-container">
            <div class="table-header">
                <h2>All Backtest Results ({total} total)</h2>
            </div>
            <div class="table-wrapper">
                {'<table id="resultsTable"><thead><tr><th>ID</th><th>Ticker</th><th>Strategy</th><th>Start Date</th><th>End Date</th><th>Sharpe Ratio</th><th>Total Return</th><th>Win Rate</th><th>Max Drawdown</th><th>Final Equity</th><th>Trades</th><th>Created</th></tr></thead><tbody>' + rows_html + '</tbody></table>' if total > 0 else '<div class="no-results">No backtest results found. Run some backtests to see data here!</div>'}
            </div>
        </div>
        
        <script>
            // Populate filter dropdowns
            const table = document.getElementById('resultsTable');
            if (table) {{
                const rows = table.querySelectorAll('tbody tr');
                const tickers = new Set();
                const strategies = new Set();
                
                rows.forEach(row => {{
                    tickers.add(row.cells[1].textContent.trim());
                    strategies.add(row.cells[2].textContent.trim());
                }});
                
                const tickerFilter = document.getElementById('tickerFilter');
                [...tickers].sort().forEach(ticker => {{
                    const option = document.createElement('option');
                    option.value = ticker;
                    option.textContent = ticker;
                    tickerFilter.appendChild(option);
                }});
                
                const strategyFilter = document.getElementById('strategyFilter');
                [...strategies].sort().forEach(strategy => {{
                    const option = document.createElement('option');
                    option.value = strategy;
                    option.textContent = strategy;
                    strategyFilter.appendChild(option);
                }});
            }}
            
            function filterTable() {{
                const table = document.getElementById('resultsTable');
                if (!table) return;
                
                const ticker = document.getElementById('tickerFilter').value;
                const strategy = document.getElementById('strategyFilter').value;
                const minSharpe = parseFloat(document.getElementById('minSharpe').value) || -999;
                const showFilter = document.getElementById('showFilter').value;
                const rows = table.querySelectorAll('tbody tr');
                
                let visibleCount = 0;
                
                rows.forEach(row => {{
                    const rowTicker = row.cells[1].textContent.trim();
                    const rowStrategy = row.cells[2].textContent.trim();
                    const rowSharpe = parseFloat(row.cells[5].textContent);
                    const rowReturn = parseFloat(row.cells[6].textContent);
                    
                    let show = true;
                    
                    if (ticker && rowTicker !== ticker) show = false;
                    if (strategy && rowStrategy !== strategy) show = false;
                    if (rowSharpe < minSharpe) show = false;
                    if (showFilter === 'profitable' && rowReturn < 0) show = false;
                    if (showFilter === 'loss' && rowReturn >= 0) show = false;
                    
                    row.style.display = show ? '' : 'none';
                    if (show) visibleCount++;
                }});
                
                document.querySelector('.table-header h2').textContent = 
                    `All Backtest Results (${{visibleCount}} shown of {total} total)`;
            }}
            
            function exportToCSV() {{
                const table = document.getElementById('resultsTable');
                if (!table) {{
                    alert('No data to export');
                    return;
                }}
                
                let csv = [];
                const rows = table.querySelectorAll('tr');
                
                rows.forEach(row => {{
                    const cols = row.querySelectorAll('td, th');
                    const csvRow = [];
                    cols.forEach(col => csvRow.push(col.textContent.trim()));
                    csv.push(csvRow.join(','));
                }});
                
                const csvContent = csv.join('\\n');
                const blob = new Blob([csvContent], {{ type: 'text/csv' }});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'backtest_results.csv';
                a.click();
            }}
            
        </script>
    </body>
    </html>
    """
    
    return html_content
@router.get("/download-powerbi")
def download_powerbi():
    """Download Power BI file if available"""
    pbix_path = "Quant Research Dashboard.pbix"
    if os.path.exists(pbix_path):
        return FileResponse(
            pbix_path, 
            media_type="application/octet-stream",
            filename="Quant_Research_Dashboard.pbix"
        )
    else:
        raise HTTPException(
            status_code=404, 
            detail="Power BI file not found. Please place your .pbix file in the project root directory."
        )
# @router.get("/dashboard", response_class=HTMLResponse)
# def get_dashboard():
#     """Serve Power BI embedded dashboard"""

#     report_id = os.getenv("POWERBI_REPORT_ID", "")
#     group_id = os.getenv("POWERBI_GROUP_ID", "")
#     embed_url = os.getenv("POWERBI_EMBED_URL", "")
    
#     html_content = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Quant Research Dashboard</title>
#         <script src="https://cdn.jsdelivr.net/npm/powerbi-client@2.22.0/dist/powerbi.min.js"></script>
#         <style>
#             body {{
#                 margin: 0;
#                 padding: 20px;
#                 font-family: Arial, sans-serif;
#                 background: #f5f5f5;
#             }}
#             .header {{
#                 background: white;
#                 padding: 20px;
#                 margin-bottom: 20px;
#                 border-radius: 8px;
#                 box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#             }}
#             h1 {{
#                 margin: 0;
#                 color: #333;
#             }}
#             #reportContainer {{
#                 height: 800px;
#                 border: 1px solid #ddd;
#                 border-radius: 8px;
#                 background: white;
#             }}
#             .info {{
#                 background: #e3f2fd;
#                 padding: 15px;
#                 margin: 20px 0;
#                 border-radius: 8px;
#                 border-left: 4px solid #2196f3;
#             }}
#         </style>
#     </head>
#     <body>
#         <div class="header">
#             <h1>📊 Quant Research Dashboard</h1>
#         </div>
        
#         <div class="info">
#             <strong>Setup Instructions:</strong>
#             <ol>
#                 <li>Configure Power BI credentials in your .env file</li>
#                 <li>Set POWERBI_REPORT_ID, POWERBI_GROUP_ID, and POWERBI_EMBED_URL</li>
#                 <li>Refresh this page to see your dashboard</li>
#             </ol>
#         </div>
        
#         <div id="reportContainer"></div>
        
#         <script>
#             // Power BI embed configuration
#             var models = window['powerbi-client'].models;
            
#             var embedConfiguration = {{
#                 type: 'report',
#                 id: '{report_id}',
#                 embedUrl: '{embed_url}',
#                 tokenType: models.TokenType.Embed,
#                 permissions: models.Permissions.Read,
#                 settings: {{
#                     panes: {{
#                         filters: {{
#                             expanded: false,
#                             visible: true
#                         }}
#                     }},
#                     background: models.BackgroundType.Transparent,
#                 }}
#             }};
            
#             // Embed the report
#             var reportContainer = document.getElementById('reportContainer');
#             var powerbi = new window['powerbi-client'].service.Service();
            
#             if ('{report_id}' && '{embed_url}') {{
#                 var report = powerbi.embed(reportContainer, embedConfiguration);
                
#                 report.on("loaded", function() {{
#                     console.log("Report loaded successfully");
#                 }});
                
#                 report.on("error", function(event) {{
#                     console.error("Report error:", event.detail);
#                 }});
#             }} else {{
#                 reportContainer.innerHTML = '<div style="padding: 40px; text-align: center; color: #666;">Please configure Power BI settings in your .env file</div>';
#             }}
#         </script>
#     </body>
#     </html>
#     """
    return html_content
@router.get("/dashboard-data")
def get_dashboard_data(db: Session = Depends(get_db)):
    """Get aggregated data for dashboard"""
    try:
        # Get all results
        results = db.query(BacktestResult).all()
        
        # Calculate KPIs
        total_tests = len(results)
        avg_sharpe = sum(r.sharpe_ratio for r in results) / total_tests if total_tests > 0 else 0
        best_return = max((r.total_return for r in results), default=0)
        profitable_count = sum(1 for r in results if r.total_return > 0)
        success_rate = (profitable_count / total_tests * 100) if total_tests > 0 else 0
        avg_win_rate = sum(r.win_rate for r in results) / total_tests if total_tests > 0 else 0
        
        # Sharpe by ticker
        ticker_data = db.query(
            BacktestResult.ticker,
            func.avg(BacktestResult.sharpe_ratio).label('avg_sharpe'),
            func.avg(BacktestResult.total_return).label('avg_return'),
            func.count(BacktestResult.id).label('count')
        ).group_by(BacktestResult.ticker).all()
        
        # Timeline data
        timeline_data = db.query(
            BacktestResult.created_at,
            BacktestResult.ticker,
            BacktestResult.final_equity,
            BacktestResult.sharpe_ratio
        ).order_by(BacktestResult.created_at).all()
        
        # Risk vs Return scatter data
        scatter_data = [{
            'ticker': r.ticker,
            'max_drawdown': float(r.max_drawdown),
            'total_return': float(r.total_return),
            'num_trades': r.num_trades,
            'sharpe_ratio': float(r.sharpe_ratio)
        } for r in results]
        
        # Recent results table
        recent_results = db.query(BacktestResult).order_by(
            BacktestResult.created_at.desc()
        ).limit(10).all()
        
        return {
            'kpis': {
                'total_tests': total_tests,
                'avg_sharpe': round(avg_sharpe, 2),
                'best_return': round(best_return, 2),
                'success_rate': round(success_rate, 1),
                'avg_win_rate': round(avg_win_rate, 1)
            },
            'ticker_performance': [
                {
                    'ticker': t.ticker,
                    'avg_sharpe': round(float(t.avg_sharpe), 2),
                    'avg_return': round(float(t.avg_return), 2),
                    'count': t.count
                } for t in ticker_data
            ],
            'timeline': [
                {
                    'date': t.created_at.strftime('%Y-%m-%d %H:%M'),
                    'ticker': t.ticker,
                    'equity': float(t.final_equity),
                    'sharpe': float(t.sharpe_ratio)
                } for t in timeline_data
            ],
            'scatter': scatter_data,
            'recent_results': [
                {
                    'id': r.id,
                    'ticker': r.ticker,
                    'strategy': r.strategy_name,
                    'sharpe': round(float(r.sharpe_ratio), 2),
                    'return': round(float(r.total_return), 2),
                    'win_rate': round(float(r.win_rate), 1),
                    'drawdown': round(float(r.max_drawdown), 2),
                    'trades': r.num_trades,
                    'date': r.created_at.strftime('%Y-%m-%d')
                } for r in recent_results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))