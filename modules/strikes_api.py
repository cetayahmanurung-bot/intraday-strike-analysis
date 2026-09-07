"""
Strike Alerts Module untuk FastAPI
Berisi fungsi helper untuk strikes dashboard
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from strike_tracking import get_strike_details

BASE_DIR = Path(__file__).resolve().parent.parent

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(str(BASE_DIR / "fundvision.db"), timeout=30)

def get_alerts_with_strikes(strike_min=3, limit=50):
    """Get all alerts with strike count >= strike_min"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ticker, timeframe, strike_count, direction, timestamp, change, total_change, price
        FROM intraday_data
        WHERE strike_count >= ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (strike_min, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    alerts = []
    for row in rows:
        alerts.append({
            'ticker': row[0],
            'timeframe': row[1],
            'strike_count': row[2],
            'direction': row[3],
            'timestamp': row[4],
            'change': row[5],
            'total_change': row[6],
            'price': row[7]
        })
    
    return alerts

def get_ticker_alerts(ticker, timeframe=None):
    """Get strikes for specific ticker"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT ticker, timeframe, strike_count, direction, timestamp, change, total_change, price
        FROM intraday_data
        WHERE ticker = ? AND strike_count >= 3
    """
    params = [ticker.upper()]
    
    if timeframe:
        query += " AND timeframe = ?"
        params.append(timeframe)
    
    query += " ORDER BY timestamp DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    alerts = []
    for row in rows:
        alerts.append({
            'ticker': row[0],
            'timeframe': row[1],
            'strike_count': row[2],
            'direction': row[3],
            'timestamp': row[4],
            'change': row[5],
            'total_change': row[6],
            'price': row[7]
        })
    
    return alerts

def get_strikes_statistics():
    """Get statistics dari semua strikes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count by timeframe
    cursor.execute("""
        SELECT timeframe, COUNT(*) as count, AVG(strike_count) as avg_strike, 
               COUNT(CASE WHEN direction='down' THEN 1 END) as down_count,
               COUNT(CASE WHEN direction='up' THEN 1 END) as up_count
        FROM intraday_data
        WHERE strike_count >= 3
        GROUP BY timeframe
        ORDER BY timeframe
    """)
    
    timeframe_stats = []
    for row in cursor.fetchall():
        timeframe_stats.append({
            'timeframe': row[0],
            'count': row[1],
            'avg_strike': round(row[2], 2) if row[2] else 0,
            'down': row[3],
            'up': row[4]
        })
    
    # Count by direction
    cursor.execute("""
        SELECT direction, COUNT(*) as count, AVG(strike_count) as avg_strike
        FROM intraday_data
        WHERE strike_count >= 3
        GROUP BY direction
    """)
    
    direction_stats = []
    for row in cursor.fetchall():
        direction_stats.append({
            'direction': row[0],
            'count': row[1],
            'avg_strike': round(row[2], 2) if row[2] else 0
        })
    
    # Total count
    cursor.execute("SELECT COUNT(*) FROM intraday_data WHERE strike_count >= 3")
    total = cursor.fetchone()[0]
    
    # Count by strike level
    cursor.execute("""
        SELECT strike_count, COUNT(*) as count
        FROM intraday_data
        WHERE strike_count >= 3
        GROUP BY strike_count
        ORDER BY strike_count
    """)
    
    strike_distribution = []
    for row in cursor.fetchall():
        strike_distribution.append({
            'strikes': row[0],
            'count': row[1]
        })
    
    conn.close()
    
    return {
        'total_alerts': total,
        'by_timeframe': timeframe_stats,
        'by_direction': direction_stats,
        'strike_distribution': strike_distribution
    }

def get_strikes_summary():
    """Get quick summary stats"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total
    cursor.execute("SELECT COUNT(*) FROM intraday_data WHERE strike_count >= 3")
    total = cursor.fetchone()[0]
    
    # Down
    cursor.execute("SELECT COUNT(*) FROM intraday_data WHERE strike_count >= 3 AND direction='down'")
    down = cursor.fetchone()[0]
    
    # Up
    cursor.execute("SELECT COUNT(*) FROM intraday_data WHERE strike_count >= 3 AND direction='up'")
    up = cursor.fetchone()[0]
    
    # Average strike
    cursor.execute("SELECT AVG(strike_count) FROM intraday_data WHERE strike_count >= 3")
    avg_strike = cursor.fetchone()[0] or 0
    
    # Max strike
    cursor.execute("SELECT MAX(strike_count) FROM intraday_data WHERE strike_count >= 3")
    max_strike = cursor.fetchone()[0] or 0
    
    # By timeframe
    cursor.execute("""
        SELECT timeframe, COUNT(*) as count
        FROM intraday_data
        WHERE strike_count >= 3
        GROUP BY timeframe
    """)
    
    tf_counts = {}
    for row in cursor.fetchall():
        tf_counts[row[0]] = row[1]
    
    conn.close()
    
    return {
        'total': total,
        'down': down,
        'up': up,
        'avg_strike': round(avg_strike, 2),
        'max_strike': max_strike,
        'by_timeframe': tf_counts
    }
