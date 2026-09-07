"""
Intraday Alert System - FIXED VERSION
Mendeteksi pergerakan harga dalam 1 hari dengan strike count yang AKURAT

PERBEDAAN UTAMA:
1. ✅ Logic loop BREAK saat trend change (tidak akkumulasi semua candle)
2. ✅ Strict market hour filtering (hanya 09:30-16:00 EDT)
3. ✅ Database state tracking (tahu last strike, detect perubahan)
"""

import yfinance as yf
from datetime import datetime, timedelta, timezone
import time
import json
from pathlib import Path
import threading
import sqlite3
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_FILE = BASE_DIR / "cache" / "intraday_alerts.json"
CACHE_DURATION = 300  # 5 menit

# 🔥 KONFIGURASI
DB_TIMEOUT = 30  # detik
MAX_RETRY = 3


# =============================================
# DATABASE FUNCTIONS
# =============================================

def get_db_connection():
    """Ambil koneksi database dengan timeout"""
    return sqlite3.connect(str(BASE_DIR / "fundvision.db"), timeout=DB_TIMEOUT)


def save_alerts_to_db(alerts, max_retry=MAX_RETRY):
    """Simpan alert ke database dengan retry jika lock"""
    if not alerts:
        return
    
    for attempt in range(max_retry):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Hapus data lebih dari 48 jam
            cutoff = (datetime.now() - timedelta(hours=48)).isoformat()
            cursor.execute("DELETE FROM intraday_data WHERE timestamp < ?", (cutoff,))
            
            for alert in alerts:
                ticker = alert.get('ticker')
                timeframe = alert.get('timeframe')
                strike_count = abs(int(float(alert.get('strike_count', 0) or 0)))
                direction = str(alert.get('direction', '')).lower()
                timestamp = alert.get('timestamp', datetime.now().isoformat())
                
                # ✅ FIX: Cek duplikasi yang lebih ketat
                cursor.execute("""
                    SELECT id FROM intraday_data 
                    WHERE ticker = ? AND timeframe = ? AND strike_count = ? 
                    AND direction = ? AND timestamp > ?
                """, (ticker, timeframe, strike_count, direction, cutoff))
                
                if cursor.fetchone():
                    continue  # Skip duplikasi
                
                cursor.execute("""
                    INSERT INTO intraday_data 
                    (ticker, timeframe, price, change, strike_count, total_change, direction, timestamp, daily_change)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ticker,
                    timeframe,
                    float(alert.get('current_price', 0) or 0),
                    float(alert.get('change', 0) or 0),
                    strike_count,
                    float(alert.get('total_change', 0) or 0),
                    direction,
                    timestamp,
                    float(alert.get('daily_change', 0) or 0)
                ))
            
            conn.commit()
            conn.close()
            print(f"💾 Saved {len(alerts)} alerts to database")
            return  # Sukses
            
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e) and attempt < max_retry - 1:
                wait = (attempt + 1) * 2
                print(f"⏳ DB locked (save_alerts), retry {attempt+1}/{max_retry} in {wait}s")
                time.sleep(wait)
            else:
                print(f"⚠️ Error saving alerts: {e}")
                return


def get_alerts_from_db(strike_min=1, timeframe=None, max_retry=MAX_RETRY):
    """Ambil alert dari database dengan retry jika lock"""
    for attempt in range(max_retry):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT ticker, timeframe, change, strike_count, total_change, direction, price, daily_change
                FROM intraday_data
                WHERE strike_count >= ?
            """
            params = [strike_min]
            
            if timeframe:
                query += " AND timeframe = ?"
                params.append(timeframe)
            
            query += """
                ORDER BY 
                    CASE timeframe
                        WHEN '5m' THEN 1
                        WHEN '15m' THEN 2
                        WHEN '30m' THEN 3
                        WHEN '1h' THEN 4
                    END,
                    timestamp DESC
            """
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alerts.append({
                    'ticker': row[0],
                    'timeframe': row[1],
                    'change': row[2],
                    'strike_count': row[3],
                    'total_change': row[4],
                    'direction': row[5],
                    'current_price': row[6],
                    'daily_change': row[7]
                })
            return alerts
            
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e) and attempt < max_retry - 1:
                wait = (attempt + 1) * 2
                print(f"⏳ DB locked (get_alerts), retry {attempt+1}/{max_retry} in {wait}s")
                time.sleep(wait)
            else:
                print(f"⚠️ Error getting alerts: {e}")
                return []


def get_cached_intraday_alerts_db(max_retry=MAX_RETRY):
    """Ambil cache intraday alerts dari database"""
    for attempt in range(max_retry):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ticker, timeframe, price, change, strike_count, total_change, direction, timestamp, daily_change
                FROM intraday_data
                WHERE strike_count >= 1
                ORDER BY timestamp DESC
            """)
            rows = cursor.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alerts.append({
                    'ticker': row[0],
                    'timeframe': row[1],
                    'current_price': row[2],
                    'change': row[3],
                    'strike_count': row[4],
                    'total_change': row[5],
                    'direction': row[6],
                    'timestamp': row[7],
                    'daily_change': row[8]
                })
            return alerts
            
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e) and attempt < max_retry - 1:
                wait = (attempt + 1) * 2
                print(f"⏳ DB locked (get_cached), retry {attempt+1}/{max_retry} in {wait}s")
                time.sleep(wait)
            else:
                print(f"⚠️ Error getting cached alerts: {e}")
                return []


# =============================================
# HELPER FUNCTIONS
# =============================================

def get_daily_change(ticker):
    """Ambil daily change dari Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if len(hist) >= 2:
            close_today = hist['Close'].iloc[-1]
            close_yesterday = hist['Close'].iloc[-2]
            if close_yesterday != 0:
                return ((close_today - close_yesterday) / close_yesterday) * 100
    except:
        pass
    return 0


def is_market_open():
    """Cek apakah market US sedang buka (09:30-16:00 EDT/EST)"""
    now_us = datetime.now(ZoneInfo("America/New_York"))
    
    # Weekend check
    if now_us.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False
    
    # Time check: 09:30 - 16:00
    current_minutes = now_us.hour * 60 + now_us.minute
    market_open = 9 * 60 + 30   # 09:30
    market_close = 16 * 60      # 16:00
    
    return market_open <= current_minutes < market_close


def get_market_open_time():
    """Dapatkan waktu market open dalam timezone lokal"""
    now = datetime.now(ZoneInfo("America/New_York"))
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    
    # Jika market sudah buka hari ini, return hari ini
    # Jika belum, return kemarin
    if now >= market_open:
        return market_open
    else:
        return market_open - timedelta(days=1)


# =============================================
# CORE LOGIC - FIXED VERSION
# =============================================

def calculate_consecutive_strikes(hist):
    """
    ✅ FIXED: Hitung consecutive strikes dari belakang
    BREAK saat trend berubah (BUKAN hitung semua candle)
    
    Returns: (strike_count, total_change, direction)
    """
    if len(hist) < 2:
        return 0, 0.0, None
    
    strike_count = 0
    total_change = 0.0
    direction = None
    
    # Loop dari belakang (candle terbaru)
    for i in range(len(hist) - 1, 0, -1):
        current_close = hist['Close'].iloc[i]
        prev_close = hist['Close'].iloc[i - 1]
        
        if current_close < prev_close:
            # ✅ Turun
            if direction is None or direction == 'down':
                change = ((current_close - prev_close) / prev_close) * 100
                total_change += change
                strike_count += 1
                direction = 'down'
            else:
                # ✅ BREAK! Trend berubah dari naik ke turun
                break
                
        elif current_close > prev_close:
            # ✅ Naik
            if direction is None or direction == 'up':
                change = ((current_close - prev_close) / prev_close) * 100
                total_change += change
                strike_count += 1
                direction = 'up'
            else:
                # ✅ BREAK! Trend berubah dari turun ke naik
                break
        else:
            # ✅ Flat, stop counting
            break
    
    return strike_count, total_change, direction


def get_intraday_alerts(timeframe=None, force_all=False):
    """
    ✅ FIXED: Scan saham untuk intraday alert
    
    Perbaikan:
    1. Filter candle hanya dari market open (09:30 EDT)
    2. Hitung strike dengan logic BREAK (tidak akkumulasi semua)
    3. Database deduplication yang lebih ketat
    """
    from datetime import datetime
    
    # Tentukan interval yang akan di-scan
    if timeframe:
        intervals = [timeframe]
    else:
        intervals = ['5m', '15m', '30m', '1h']
    
    print(f"🔍 Scanning intervals: {intervals}")
    
    # Ambil semua ticker dari database
    try:
        conn = sqlite3.connect(str(BASE_DIR / "fundvision.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT ticker FROM watchlist")
        all_tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        print(f"Error reading tickers: {e}")
        return []
    
    # Kategorikan ticker berdasarkan daily change (hanya down ticker)
    down_tickers = []
    for ticker in all_tickers:
        daily_change = get_daily_change(ticker)
        if daily_change < 0:
            down_tickers.append(ticker)
    
    print(f"🔍 Scanning {len(down_tickers)} down tickers")
    
    # Hasil scanning baru
    new_alerts = []
    
    # ✅ FIX: Market open time sebagai filter
    market_open_time = get_market_open_time()
    
    for ticker in down_tickers:
        try:
            for interval in intervals:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d", interval=interval)
                
                if hist.empty:
                    continue
                
                # ✅ FIX #1: Filter hanya candle dari market open sampai sekarang
                if hist.index.tz is not None:
                    # Timezone-aware
                    hist = hist[hist.index >= market_open_time]
                else:
                    # Timezone-naive, filter by date
                    today_date = datetime.now().date()
                    hist = hist[hist.index.date == today_date]
                
                if len(hist) < 2:
                    continue
                
                # ✅ FIX #2: Gunakan calculate_consecutive_strikes (logic BREAK)
                strike_count, total_change, direction = calculate_consecutive_strikes(hist)
                
                # Only save if strike >= 3
                if strike_count >= 3:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    
                    if prev_price != 0:
                        last_change = ((current_price - prev_price) / prev_price) * 100
                    else:
                        last_change = 0
                    
                    new_alerts.append({
                        'ticker': ticker,
                        'timeframe': interval,
                        'change': last_change,
                        'strike_count': strike_count,
                        'total_change': total_change,
                        'direction': direction or 'down',
                        'timestamp': datetime.now().isoformat(),
                        'current_price': current_price,
                        'daily_change': get_daily_change(ticker)
                    })
                    
                    print(f"  ✅ {ticker} [{interval}]: {strike_count} {direction} strikes")
        
        except Exception as e:
            print(f"Error scanning {ticker} [{interval}]: {e}")
            continue
    
    print(f"✅ Total new alerts: {len(new_alerts)}")
    return new_alerts


def get_cached_intraday_alerts(timeframe=None):
    """
    ✅ FIXED: Ambil intraday alerts
    - Scan jika market buka
    - Baca dari DB jika market tutup
    """
    
    # Baca cache lama (untuk fallback)
    old_alerts = []
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                old_alerts = cache.get('alerts', [])
                if timeframe:
                    old_alerts = [a for a in old_alerts if a.get('timeframe') == timeframe]
        except:
            pass
    
    # ✅ Check market status
    if not is_market_open():
        print(f"⏳ Market tutup - membaca dari database")
        db_alerts = get_alerts_from_db(strike_min=3, timeframe=timeframe)
        return db_alerts if db_alerts else old_alerts
    
    print(f"✅ Market sedang buka - scanning tickers")
    
    # Scan dan simpan ke database
    alerts = get_intraday_alerts(timeframe=timeframe, force_all=False)
    
    # Simpan ke database
    if alerts:
        save_alerts_to_db(alerts)
    
    # Simpan ke cache (untuk fallback)
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'alerts': alerts
            }, f)
    except:
        pass
    
    return alerts


# =============================================
# FORMATTING & GROUPING
# =============================================

def format_intraday_alert(alert):
    """Format single alert menjadi HTML"""
    timeframe = alert.get('timeframe', '5m')
    ticker = alert.get('ticker', '')
    change = alert.get('change', 0)
    strike = alert.get('strike_count', 0)
    direction = alert.get('direction', 'up')
    
    tf_class = {
        '5m': 'tf-5m',
        '15m': 'tf-15m',
        '30m': 'tf-30m',
        '1h': 'tf-1h'
    }.get(timeframe, 'tf-5m')
    
    change_class = 'down' if change < 0 else 'up'
    change_icon = '📉' if change < 0 else '📈'
    
    # STRIKE COUNT display
    strike_html = f'<span class="strike-count">🔽{strike}</span>' if strike >= 3 else ''
    
    html = f'''
    <div class="alert-item intraday {tf_class}">
        <span class="timeframe">{timeframe.upper()}</span>
        <span class="ticker">{ticker.upper()}</span>
        <span class="change {change_class}">{change_icon} {change:+.2f}%</span>
        {strike_html}
        <a href="/stock/{ticker}" class="btn-analysis">AI</a>
    </div>
    '''
    
    return {'html': html}


def group_intraday_alerts_by_timeframe(alerts):
    """Kelompokkan alert berdasarkan timeframe"""
    grouped = {
        '5m': [],
        '15m': [],
        '30m': [],
        '1h': []
    }
    
    for alert in alerts:
        timeframe = alert.get('timeframe', '5m')
        if timeframe in grouped:
            grouped[timeframe].append(alert)
        else:
            grouped['5m'].append(alert)
    
    return grouped


def render_grouped_intraday_alerts(alerts):
    """Render alert dalam format HTML yang sudah dikelompokkan"""
    if not alerts:
        return """
        <div class="alert-empty">
            <i class="fas fa-clock" style="color: #64748b;"></i><br>
            No intraday alerts
        </div>
        """
    
    # Filter: hanya strike >= 3
    filtered_alerts = [a for a in alerts if a.get('strike_count', 0) >= 3]
    
    if not filtered_alerts:
        return """
        <div class="alert-empty">
            <i class="fas fa-clock" style="color: #64748b;"></i><br>
            No intraday alerts (strike >= 3)
        </div>
        """
    
    grouped = group_intraday_alerts_by_timeframe(filtered_alerts)
    
    html = ""
    timeframe_labels = {
        '5m': '🔵 5 Minutes',
        '15m': '🟢 15 Minutes', 
        '30m': '🟡 30 Minutes',
        '1h': '🩷 1 Hour'
    }
    
    for tf in ['5m', '15m', '30m', '1h']:
        if grouped[tf]:
            html += f"""
            <div class="intraday-group">
                <div class="intraday-group-header">{timeframe_labels[tf]}</div>
                <div class="intraday-group-items">
            """
            for alert in grouped[tf]:
                formatted = format_intraday_alert(alert)
                html += formatted['html']
            html += """
                </div>
            </div>
            """
    
    if not html:
        html = """
        <div class="alert-empty">
            <i class="fas fa-clock" style="color: #64748b;"></i><br>
            No intraday alerts (strike >= 3)
        </div>
        """
    
    return html


# =============================================
# SCHEDULER
# =============================================

def run_intraday_scanner(timeframe=None):
    """Fungsi yang dijalankan scheduler"""
    alerts = get_cached_intraday_alerts(timeframe=timeframe)
    if timeframe:
        alerts = [a for a in alerts if a.get('timeframe') == timeframe]
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 {timeframe}: {len(alerts)} alerts")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Total: {len(alerts)} alerts")
    return alerts


def check_intraday_alerts():
    """Fungsi wrapper untuk scheduler"""
    return get_cached_intraday_alerts()


# =============================================
# TESTING
# =============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 INTRADAY ALERT SYSTEM - FIXED VERSION")
    print("=" * 60)
    
    # Test market status
    print(f"\n📊 Market Status:")
    print(f"   Open? {is_market_open()}")
    print(f"   Current time (US): {datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S EDT')}")
    
    # Test scan
    print(f"\n🔍 Scanning alerts...")
    alerts = get_cached_intraday_alerts()
    
    print(f"\n📈 Results:")
    print(f"   Total alerts: {len(alerts)}")
    
    # Group by timeframe
    grouped = group_intraday_alerts_by_timeframe(alerts)
    for tf in ['5m', '15m', '30m', '1h']:
        count = len(grouped[tf])
        if count > 0:
            print(f"   {tf}: {count} alerts")
            for alert in grouped[tf][:3]:  # Show first 3
                print(f"     - {alert['ticker']} {alert['strike_count']}x {alert['direction']}")
