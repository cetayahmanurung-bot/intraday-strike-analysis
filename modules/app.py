"""
Complete Flask Application - Strike Alerts Dashboard
Integrate API, HTML Dashboard, dan Detail Pages
"""

from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
from pathlib import Path
import sqlite3
import yfinance as yf
from strike_tracking import get_strike_details
from dashboard_html import get_dashboard_html, get_detail_page_html

BASE_DIR = Path(__file__).resolve().parent.parent
app = Flask(__name__, static_folder='static', template_folder='templates')

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

# =============================================
# HTML ROUTES
# =============================================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template_string(get_dashboard_html())

@app.route('/detail/<ticker>')
def detail(ticker):
    """Detail page untuk specific ticker"""
    return render_template_string(get_detail_page_html(ticker))

# =============================================
# API ENDPOINTS - STRIKES
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
        'timestamp': datetime.now().isoformat(),
        'data': alerts
    })

@app.route('/api/strikes/<ticker>', methods=['GET'])
def api_strike_detail(ticker):
    """Get strikes detail untuk ticker specific"""
    timeframe = request.args.get('timeframe', None)
    
    alerts = get_ticker_alerts(ticker, timeframe)
    
    return jsonify({
        'status': 'success',
        'ticker': ticker.upper(),
        'count': len(alerts),
        'timestamp': datetime.now().isoformat(),
        'data': alerts
    })

# =============================================
# API ENDPOINTS - STATISTICS
# =============================================

@app.route('/api/stats', methods=['GET'])
def api_stats():
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
            'avg_strike': round(row[2], 2),
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
            'avg_strike': round(row[2], 2)
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
    
    return jsonify({
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'total_alerts': total,
        'by_timeframe': timeframe_stats,
        'by_direction': direction_stats,
        'strike_distribution': strike_distribution
    })

@app.route('/api/stats/summary', methods=['GET'])
def api_stats_summary():
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
    
    return jsonify({
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total': total,
            'down': down,
            'up': up,
            'avg_strike': round(avg_strike, 2),
            'max_strike': max_strike,
            'by_timeframe': tf_counts
        }
    })

# =============================================
# API ENDPOINTS - HEALTH & INFO
# =============================================

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM intraday_data")
        db_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'records': db_count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/info', methods=['GET'])
def api_info():
    """API info endpoint"""
    return jsonify({
        'name': 'Strike Alerts API',
        'version': '1.0.0',
        'description': 'Real-time intraday strike monitoring system',
        'endpoints': {
            'html': {
                'dashboard': 'GET /',
                'detail': 'GET /detail/<ticker>'
            },
            'api': {
                'strikes': 'GET /api/strikes?strike_min=3&limit=50',
                'strike_detail': 'GET /api/strikes/<ticker>?timeframe=1h',
                'statistics': 'GET /api/stats',
                'summary': 'GET /api/stats/summary',
                'health': 'GET /api/health',
                'info': 'GET /api/info'
            }
        },
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
    return jsonify({'status': 'error', 'message': 'Internal server error', 'error': str(e)}), 500

# =============================================
# STATIC FILES
# =============================================

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    from flask import send_from_directory
    return send_from_directory('static', filename)

# =============================================
# MAIN
# =============================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 STRIKE ALERTS DASHBOARD - COMPLETE APPLICATION")
    print("="*70)
    print("\n📍 HTML Pages:")
    print("   • Dashboard:        http://localhost:5000")
    print("   • Ticker Details:   http://localhost:5000/detail/<TICKER>")
    print("\n📊 API Endpoints:")
    print("   • Get Strikes:      http://localhost:5000/api/strikes")
    print("   • Ticker Details:   http://localhost:5000/api/strikes/<TICKER>")
    print("   • Statistics:       http://localhost:5000/api/stats")
    print("   • Summary:          http://localhost:5000/api/stats/summary")
    print("   • Health Check:     http://localhost:5000/api/health")
    print("   • API Info:         http://localhost:5000/api/info")
    print("\n💡 Examples:")
    print("   curl http://localhost:5000/api/strikes?limit=20")
    print("   curl http://localhost:5000/api/strikes/MOMO")
    print("   curl http://localhost:5000/api/stats/summary")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
