"""
Flask API untuk Strike Alerts
Serve data strikes dengan format JSON
"""

from flask import Flask, jsonify, request
from datetime import datetime
from pathlib import Path
import sqlite3
import yfinance as yf
from strike_tracking import get_strike_details

BASE_DIR = Path(__file__).resolve().parent.parent
app = Flask(__name__)

# =============================================
# DATABASE FUNCTIONS
# =============================================

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

# =============================================
# API ENDPOINTS
# =============================================

@app.route('/api/strikes', methods=['GET'])
def api_strikes():
    """Get all strikes alerts"""
    strike_min = request.args.get('strike_min', 3, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    alerts = get_alerts_with_strikes(strike_min=strike_min, limit=limit)
    
    return jsonify({
        'status': 'success',
        'count': len(alerts),
        'data': alerts
    })

@app.route('/api/strikes/<ticker>', methods=['GET'])
def api_strike_detail(ticker):
    """Get strikes detail untuk ticker specific"""
    timeframe = request.args.get('timeframe', None)
    
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
    
    return jsonify({
        'status': 'success',
        'ticker': ticker.upper(),
        'count': len(alerts),
        'data': alerts
    })

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get statistics dari semua strikes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count by timeframe
    cursor.execute("""
        SELECT timeframe, COUNT(*) as count, AVG(strike_count) as avg_strike
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
            'avg_strike': round(row[2], 2)
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
            'avg_strike': round(row[2], 2)
        })
    
    # Total count
    cursor.execute("SELECT COUNT(*) FROM intraday_data WHERE strike_count >= 3")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'status': 'success',
        'total_alerts': total,
        'by_timeframe': timeframe_stats,
        'by_direction': direction_stats
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

# =============================================
# ERROR HANDLERS
# =============================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Strike API Server...")
    print("📍 Available endpoints:")
    print("   GET /api/strikes - Get all strikes")
    print("   GET /api/strikes/<ticker> - Get ticker details")
    print("   GET /api/stats - Get statistics")
    print("   GET /api/health - Health check")
    print("\n💻 Running on http://localhost:5000")
    app.run(debug=True, port=5000)
