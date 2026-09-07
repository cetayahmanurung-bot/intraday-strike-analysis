"""
Strike Tracking - Detail per candle
Untuk memverifikasi bahwa strikes benar-benar berturut-turut tanpa gap
"""

def get_strike_details(hist, strike_count, direction):
    """
    Extract detailed timeline dari setiap strike
    
    Returns list of strikes dengan:
    - strike_number: 1, 2, 3, ...
    - timestamp: waktu candle
    - price: close price
    - change: % perubahan
    - interval: waktu interval (misal "09:00 - 09:30")
    """
    if len(hist) < 2:
        return []
    
    strikes = []
    
    # Loop dari belakang (newest)
    strike_num = 1
    
    for i in range(len(hist) - 1, 0, -1):
        current_close = hist['Close'].iloc[i]
        prev_close = hist['Close'].iloc[i - 1]
        current_time = hist.index[i]
        prev_time = hist.index[i - 1]
        
        # Check trend
        is_down = current_close < prev_close
        is_up = current_close > prev_close
        
        # Verify match dengan direction yang diharapkan
        if (direction == 'down' and is_down) or (direction == 'up' and is_up):
            change = ((current_close - prev_close) / prev_close) * 100
            
            # Format interval
            try:
                prev_time_str = prev_time.strftime('%H:%M')
                curr_time_str = current_time.strftime('%H:%M')
                date_str = current_time.strftime('%Y-%m-%d')
                interval_str = f"{prev_time_str} - {curr_time_str}"
            except:
                interval_str = f"Candle {i-1} - {i}"
                date_str = "N/A"
            
            strikes.append({
                'strike_number': strike_num,
                'date': date_str,
                'interval': interval_str,
                'prev_time': str(prev_time),
                'curr_time': str(current_time),
                'prev_price': prev_close,
                'current_price': current_close,
                'change_pct': change,
                'direction': 'down' if is_down else 'up'
            })
            
            strike_num += 1
            
            # Stop jika sudah collect semua strikes
            if strike_num > strike_count:
                break
        else:
            # Trend berubah, stop
            break
    
    # Reverse untuk tampil dari strike 1 ke strike N (ascending)
    return list(reversed(strikes))


def format_strike_details(ticker, timeframe, strikes):
    """
    Format strikes detail menjadi readable string
    """
    if not strikes:
        return f"❌ {ticker} [{timeframe}]: No strike data"
    
    output = f"\n📊 {ticker} [{timeframe}] - {len(strikes)} Strikes:\n"
    output += "=" * 70 + "\n"
    
    for strike in strikes:
        output += f"  Strike #{strike['strike_number']}\n"
        output += f"    Date:     {strike['date']}\n"
        output += f"    Interval: {strike['interval']}\n"
        output += f"    Price:    {strike['prev_price']:.2f} → {strike['current_price']:.2f}\n"
        output += f"    Change:   {strike['change_pct']:+.3f}%\n"
        output += f"    Direction: {'📉 DOWN' if strike['direction'] == 'down' else '📈 UP'}\n"
        output += "-" * 70 + "\n"
    
    return output


def format_strike_details_html(ticker, timeframe, strikes):
    """
    Format strikes detail menjadi HTML table
    """
    if not strikes:
        return f"""
        <div class="strike-details">
            <h4>{ticker} [{timeframe}] - ❌ No data</h4>
        </div>
        """
    
    html = f"""
    <div class="strike-details">
        <h4>{ticker} [{timeframe}] - {len(strikes)} Consecutive Strikes ✅</h4>
        <table class="strikes-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Date</th>
                    <th>Interval (US EDT)</th>
                    <th>From Price</th>
                    <th>To Price</th>
                    <th>Change %</th>
                    <th>Direction</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for strike in strikes:
        direction_icon = "📉" if strike['direction'] == 'down' else "📈"
        html += f"""
                <tr>
                    <td class="strike-num">{strike['strike_number']}</td>
                    <td>{strike['date']}</td>
                    <td class="interval">{strike['interval']}</td>
                    <td>${strike['prev_price']:.2f}</td>
                    <td>${strike['current_price']:.2f}</td>
                    <td class="change {'down' if strike['direction'] == 'down' else 'up'}">{strike['change_pct']:+.3f}%</td>
                    <td>{direction_icon}</td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
        <style>
            .strike-details {
                margin: 20px 0;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                background: #f9f9f9;
            }
            .strikes-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            .strikes-table th {
                background: #2c3e50;
                color: white;
                padding: 10px;
                text-align: left;
            }
            .strikes-table td {
                padding: 8px 10px;
                border-bottom: 1px solid #e0e0e0;
            }
            .strikes-table tr:hover {
                background: #f0f0f0;
            }
            .strike-num {
                font-weight: bold;
                text-align: center;
            }
            .interval {
                font-family: monospace;
                font-size: 0.9em;
            }
            .change {
                font-weight: bold;
                text-align: center;
            }
            .change.down {
                color: #e74c3c;
            }
            .change.up {
                color: #27ae60;
            }
        </style>
    </div>
    """
    
    return html


# =============================================
# TESTING
# =============================================

if __name__ == "__main__":
    import yfinance as yf
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    # Test dengan MOMO (dari hasil testing sebelumnya)
    print("Testing Strike Details Tracking\n")
    
    ticker = "MOMO"
    timeframe = "30m"
    
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d", interval=timeframe)
    
    # Filter hari ini
    if hist.index.tz is not None:
        today = datetime.now(hist.index.tz).date()
    else:
        today = datetime.now().date()
    
    hist = hist[hist.index.date == today]
    
    if len(hist) >= 2:
        # Calculate strikes
        strike_count = 0
        direction = None
        
        for i in range(len(hist) - 1, 0, -1):
            current = hist['Close'].iloc[i]
            prev = hist['Close'].iloc[i - 1]
            
            if current < prev:
                if direction is None or direction == 'down':
                    strike_count += 1
                    direction = 'down'
                else:
                    break
            elif current > prev:
                if direction is None or direction == 'up':
                    strike_count += 1
                    direction = 'up'
                else:
                    break
            else:
                break
        
        if strike_count >= 3:
            # Get strike details
            strikes = get_strike_details(hist, strike_count, direction)
            
            # Print details
            print(format_strike_details(ticker, timeframe, strikes))
            
            # Also show HTML
            print("\n" + "="*70)
            print("HTML Version:")
            print("="*70)
            print(format_strike_details_html(ticker, timeframe, strikes))
        else:
            print(f"Not enough consecutive strikes for {ticker} [{timeframe}]")
    else:
        print(f"Not enough data for {ticker} [{timeframe}]")
