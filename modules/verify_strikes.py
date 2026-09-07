"""
Strike Tracking - Test dengan data dari database
Menampilkan detail setiap strike yang tersimpan
"""

import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from strike_tracking import get_strike_details, format_strike_details, format_strike_details_html

BASE_DIR = Path(__file__).resolve().parent.parent

def get_strike_data_from_db():
    """Ambil alert dengan strike >= 3 dari database"""
    conn = sqlite3.connect(str(BASE_DIR / "fundvision.db"))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ticker, timeframe, strike_count, direction, timestamp
        FROM intraday_data
        WHERE strike_count >= 3
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def get_candle_history(ticker, timeframe, days_back=5):
    """Ambil historical candle data"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f"{days_back}d", interval=timeframe)
        return hist
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def main():
    print("\n" + "="*70)
    print("🔍 STRIKE TRACKING - VERIFICATION FROM DATABASE")
    print("="*70 + "\n")
    
    # Ambil alerts dengan strike >= 3
    alerts = get_strike_data_from_db()
    
    if not alerts:
        print("❌ No alerts with strike >= 3 in database")
        return
    
    print(f"Found {len(alerts)} alerts with strike >= 3\n")
    
    # Process setiap alert
    for idx, alert in enumerate(alerts[:5], 1):  # Show top 5
        ticker, timeframe, strike_count, direction, timestamp = alert
        
        print(f"\n{idx}. {ticker} [{timeframe}] - {strike_count}x {direction}")
        print(f"   Stored: {timestamp}")
        print("-" * 70)
        
        # Fetch historical data
        hist = get_candle_history(ticker, timeframe, days_back=5)
        
        if hist is None or len(hist) < 2:
            print(f"   ❌ Not enough historical data\n")
            continue
        
        # Get strike details
        strikes = get_strike_details(hist, strike_count, direction.lower())
        
        if strikes:
            # Display details
            for strike in strikes:
                print(f"   Strike #{strike['strike_number']}")
                print(f"     Date:     {strike['date']}")
                print(f"     Interval: {strike['interval']}")
                print(f"     Price:    ${strike['prev_price']:.2f} → ${strike['current_price']:.2f}")
                print(f"     Change:   {strike['change_pct']:+.3f}%")
                print(f"     Direction: {'📉 DOWN' if strike['direction'] == 'down' else '📈 UP'}")
                print()
        else:
            print(f"   ⚠️ Could not extract strike details\n")
    
    print("\n" + "="*70)
    print("✅ Strike verification complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
