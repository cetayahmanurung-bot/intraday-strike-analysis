"""
Script untuk test dan verify alert distribution
Cek apakah fix sudah bekerja dengan benar
"""

from intraday_alert import get_alerts_from_db

# Ambil semua alerts
alerts = get_alerts_from_db(strike_min=1)
print(f"\n{'='*60}")
print(f"📊 INTRADAY ALERTS VERIFICATION")
print(f"{'='*60}")
print(f"Total alerts in DB: {len(alerts)}\n")

# Kelompok per timeframe
by_timeframe = {}
for a in alerts:
    tf = a['timeframe']
    if tf not in by_timeframe:
        by_timeframe[tf] = []
    by_timeframe[tf].append(a)

# Analisis per timeframe
print(f"{'Timeframe':<10} {'Count':<8} {'Max Strike':<12} {'Status':<15}")
print(f"{'-'*45}")

for tf in ['5m', '15m', '30m', '1h']:
    if tf in by_timeframe:
        strikes = by_timeframe[tf]
        count = len(strikes)
        max_strike = max([s['strike_count'] for s in strikes]) if strikes else 0
        
        # Determine expected max
        expected_max = {
            '5m': 84,    # 7 hours / 5m = 84 candles
            '15m': 28,   # 7 hours / 15m = 28 candles
            '30m': 14,   # 7 hours / 30m = 14 candles
            '1h': 7      # 7 hours / 1h = 7 candles
        }.get(tf, 0)
        
        # Status check
        if max_strike <= expected_max:
            status = "✅ CORRECT"
        else:
            status = f"❌ TOO HIGH ({max_strike}>{expected_max})"
        
        print(f"{tf:<10} {count:<8} {max_strike:<12} {status:<15}")
        
        # Show top 5 alerts untuk timeframe ini
        top = sorted(strikes, key=lambda x: x['strike_count'], reverse=True)[:5]
        for i, t in enumerate(top, 1):
            direction_icon = "📉" if t['direction'] == 'down' else "📈"
            print(f"  {i}. {t['ticker']:6} {direction_icon} {t['strike_count']:2}x {t['direction']:4} (change: {t['change']:+.2f}%)")
    else:
        print(f"{tf:<10} {'0':<8} {'N/A':<12} {'No data':<15}")
    
    print()

print(f"{'='*60}")
print(f"✅ Test: Max 1h strikes should be <= 7 (market hours)")
print(f"✅ If all status show 'CORRECT', then FIX is working!")
print(f"{'='*60}\n")

# Additional stats
print(f"\n📈 DETAILED ANALYSIS:\n")

total_by_direction = {'up': 0, 'down': 0}
for a in alerts:
    direction = a.get('direction', 'unknown')
    if direction in total_by_direction:
        total_by_direction[direction] += 1

print(f"Direction breakdown:")
print(f"  📉 Down: {total_by_direction['down']}")
print(f"  📈 Up:   {total_by_direction['up']}")

# Strike distribution
print(f"\nStrike count distribution:")
strike_dist = {}
for a in alerts:
    strike = a['strike_count']
    strike_dist[strike] = strike_dist.get(strike, 0) + 1

for strike in sorted(strike_dist.keys()):
    count = strike_dist[strike]
    bar = "█" * count
    print(f"  {strike:2}x strikes: {count:3} alerts {bar}")

print(f"\n{'='*60}\n")
