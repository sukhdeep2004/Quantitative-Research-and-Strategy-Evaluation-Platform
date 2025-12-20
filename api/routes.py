from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
from quant.data import fetch_price_data
from quant.backtest import backtest
from quant.risk import sharpe_ratio, max_drawdown
from db.models import BacktestResult
from db.session import get_db
from api.schemas import BacktestRequest
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

@router.get("/backtest-results")
def get_backtest_results(db: Session = Depends(get_db), limit: int = 100):
    """Get all backtest results"""
    results = db.query(BacktestResult).order_by(BacktestResult.created_at.desc()).limit(limit).all()
    return results

@router.get("/backtest-results/{result_id}")
def get_backtest_result(result_id: int, db: Session = Depends(get_db)):
    """Get specific backtest result"""
    result = db.query(BacktestResult).filter(BacktestResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result
@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    """Serve Power BI embedded dashboard"""

    report_id = os.getenv("POWERBI_REPORT_ID", "")
    group_id = os.getenv("POWERBI_GROUP_ID", "")
    embed_url = os.getenv("POWERBI_EMBED_URL", "")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quant Research Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/powerbi-client@2.22.0/dist/powerbi.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
                background: #f5f5f5;
            }}
            .header {{
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                margin: 0;
                color: #333;
            }}
            #reportContainer {{
                height: 800px;
                border: 1px solid #ddd;
                border-radius: 8px;
                background: white;
            }}
            .info {{
                background: #e3f2fd;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
                border-left: 4px solid #2196f3;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Quant Research Dashboard</h1>
        </div>
        
        <div class="info">
            <strong>Setup Instructions:</strong>
            <ol>
                <li>Configure Power BI credentials in your .env file</li>
                <li>Set POWERBI_REPORT_ID, POWERBI_GROUP_ID, and POWERBI_EMBED_URL</li>
                <li>Refresh this page to see your dashboard</li>
            </ol>
        </div>
        
        <div id="reportContainer"></div>
        
        <script>
            // Power BI embed configuration
            var models = window['powerbi-client'].models;
            
            var embedConfiguration = {{
                type: 'report',
                id: '{report_id}',
                embedUrl: '{embed_url}',
                tokenType: models.TokenType.Embed,
                permissions: models.Permissions.Read,
                settings: {{
                    panes: {{
                        filters: {{
                            expanded: false,
                            visible: true
                        }}
                    }},
                    background: models.BackgroundType.Transparent,
                }}
            }};
            
            // Embed the report
            var reportContainer = document.getElementById('reportContainer');
            var powerbi = new window['powerbi-client'].service.Service();
            
            if ('{report_id}' && '{embed_url}') {{
                var report = powerbi.embed(reportContainer, embedConfiguration);
                
                report.on("loaded", function() {{
                    console.log("Report loaded successfully");
                }});
                
                report.on("error", function(event) {{
                    console.error("Report error:", event.detail);
                }});
            }} else {{
                reportContainer.innerHTML = '<div style="padding: 40px; text-align: center; color: #666;">Please configure Power BI settings in your .env file</div>';
            }}
        </script>
    </body>
    </html>
    """
    return html_content