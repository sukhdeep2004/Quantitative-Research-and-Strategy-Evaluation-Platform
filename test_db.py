from db.session import engine, SessionLocal
from db.models import Base, BacktestResult
from quant.backtest import run_all_backtests
from quant.risk import compute_metrics
from datetime import datetime, timedelta

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            print("✓ Database connection successful!")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def create_tables():
    """Create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully!")
        return True
    except Exception as e:
        print(f"✗ Table creation failed: {e}")
        return False

def insert_sample_data():
    """Insert REAL backtest results for Power BI"""
    db = SessionLocal()

    try:
        tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
        

        end_date = datetime.now().date() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=365)  # 1 year back
        
        print(f"Running backtests from {start_date} to {end_date}")
        print("Running real backtests and inserting data...")

        for ticker in tickers:
            print(f"Processing {ticker}...")
            backtest_results = run_all_backtests(ticker, start_date, end_date)

            for strategy_name, model in backtest_results.items():
                equity = model['equity_curve']
                returns = model['returns']

                final_equity, total_return, win_rate, num_trades = compute_metrics(
                    equity, returns
                )

                result = BacktestResult(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    strategy_name=strategy_name,
                    sharpe_ratio=round(model['sharpe'], 3),
                    final_equity=round(final_equity, 4),
                    max_drawdown=round(model['max_drawdown'], 4)*100,# Store as percentage
                    total_return=round(total_return, 2),
                    win_rate=round(win_rate, 2),
                    num_trades=int(num_trades),
                    created_at=datetime.now()
                )

                db.add(result)

        db.commit()
        print("✓ Successfully inserted real backtest results!")

        return True

    except Exception as e:
        db.rollback()
        print(f"✗ Failed to insert backtest data: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()

def query_results():
    """Query and display results"""
    db = SessionLocal()
    try:
        results = db.query(BacktestResult).limit(5).all()
        print("\nSample Results:")
        print("-" * 100)
        print(f"{'ID':<5} {'Ticker':<8} {'Strategy':<20} {'Sharpe':<8} {'Return':<10} {'MaxDD':<10}")
        print("-" * 100)
        for r in results:
            print(f"{r.id:<5} {r.ticker:<8} {r.strategy_name:<20} {r.sharpe_ratio:<8.2f} {r.total_return:<10.2f} {r.max_drawdown:<10.2%}")
        print("-" * 100)
        
        total = db.query(BacktestResult).count()
        print(f"\nTotal results in database: {total}")
        return True
    except Exception as e:
        print(f"✗ Query failed: {e}")
        return False
    finally:
        db.close()

def delete_all_results():
    """Delete all backtest results"""
    db = SessionLocal()
    try:
        deleted = db.query(BacktestResult).delete()
        db.commit()
        print(f"✓ Deleted {deleted} backtest results.")
        return True
    except Exception as e:
        print(f"✗ Deletion failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("DATABASE SETUP AND TEST")
    print("=" * 80)
    

    print("\n0. Clearing old data...")
    delete_all_results()
    
    print("\n1. Testing database connection...")
    if not test_connection():
        exit(1)
    
    print("\n2. Creating tables...")
    if not create_tables():
        exit(1)
    

    print("\n3. Inserting sample data...")
    if not insert_sample_data():
        exit(1)

    print("\n4. Querying results...")
    if not query_results():
        exit(1)
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED!")
    print("=" * 80)