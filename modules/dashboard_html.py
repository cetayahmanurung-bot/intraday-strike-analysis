"""
HTML Dashboard untuk Strike Alerts
Tampilin semua strikes dengan format yang rapi dan interaktif
"""

def get_dashboard_html():
    """Generate HTML dashboard untuk strikes"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Strike Alerts Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            :root {
                --primary: #2c3e50;
                --success: #27ae60;
                --danger: #e74c3c;
                --warning: #f39c12;
                --info: #3498db;
                --light: #ecf0f1;
                --dark: #34495e;
            }
            
            * {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .navbar {
                background: var(--primary) !important;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .dashboard-title {
                color: white;
                font-weight: 700;
                font-size: 28px;
                margin-bottom: 30px;
            }
            
            .stats-card {
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            
            .stats-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }
            
            .stats-number {
                font-size: 36px;
                font-weight: 700;
                margin: 10px 0;
            }
            
            .stats-label {
                font-size: 14px;
                color: #7f8c8d;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .alert-container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                overflow: hidden;
                margin-bottom: 20px;
            }
            
            .alert-header {
                background: linear-gradient(135deg, var(--primary), var(--dark));
                color: white;
                padding: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .alert-header h3 {
                margin: 0;
                font-size: 20px;
                font-weight: 600;
            }
            
            .filter-group {
                background: var(--light);
                padding: 20px;
                border-bottom: 1px solid #bdc3c7;
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
            }
            
            .filter-group label {
                font-weight: 600;
                margin-right: 10px;
                display: flex;
                align-items: center;
            }
            
            .filter-group select,
            .filter-group input {
                padding: 8px 12px;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                font-size: 14px;
            }
            
            .strikes-table {
                width: 100%;
                border-collapse: collapse;
            }
            
            .strikes-table thead {
                background: var(--primary);
                color: white;
            }
            
            .strikes-table th {
                padding: 15px;
                text-align: left;
                font-weight: 600;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .strikes-table td {
                padding: 15px;
                border-bottom: 1px solid #ecf0f1;
                font-size: 14px;
            }
            
            .strikes-table tbody tr {
                transition: background 0.2s;
            }
            
            .strikes-table tbody tr:hover {
                background: #f8f9fa;
            }
            
            .ticker-badge {
                background: var(--info);
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }
            
            .timeframe-badge {
                background: var(--warning);
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }
            
            .strike-count {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 700;
                font-size: 14px;
                text-align: center;
                min-width: 50px;
            }
            
            .direction-down {
                color: var(--danger);
                font-weight: 700;
            }
            
            .direction-up {
                color: var(--success);
                font-weight: 700;
            }
            
            .change-down {
                color: var(--danger);
            }
            
            .change-up {
                color: var(--success);
            }
            
            .timestamp {
                color: #95a5a6;
                font-size: 12px;
            }
            
            .btn-detail {
                background: var(--info);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                transition: background 0.3s;
            }
            
            .btn-detail:hover {
                background: #2980b9;
                text-decoration: none;
                color: white;
            }
            
            .empty-state {
                text-align: center;
                padding: 40px 20px;
                color: #7f8c8d;
            }
            
            .empty-state i {
                font-size: 48px;
                margin-bottom: 15px;
                opacity: 0.5;
            }
            
            .chart-container {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            
            .chart-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 20px;
                color: var(--primary);
            }
            
            .stat-row {
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid #ecf0f1;
            }
            
            .stat-row:last-child {
                border-bottom: none;
            }
            
            .stat-row-label {
                font-weight: 600;
                color: var(--dark);
            }
            
            .stat-row-value {
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 700;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #7f8c8d;
            }
            
            .loading i {
                font-size: 32px;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .pagination {
                margin-top: 20px;
            }
            
            .footer {
                text-align: center;
                color: white;
                padding: 20px;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <!-- Navbar -->
        <nav class="navbar navbar-dark sticky-top">
            <div class="container-fluid">
                <span class="navbar-brand mb-0 h1">
                    <i class="fas fa-chart-line"></i> Strike Alerts Dashboard
                </span>
                <span style="color: white; font-size: 12px;" id="lastUpdate">Last update: --:--:--</span>
            </div>
        </nav>
        
        <!-- Main Content -->
        <div class="container-fluid" style="margin-top: 20px;">
            <div class="dashboard-title">
                <i class="fas fa-bolt"></i> Intraday Strike Monitoring
            </div>
            
            <!-- Stats Cards -->
            <div class="row mb-4" id="statsContainer">
                <div class="col-md-3">
                    <div class="stats-card">
                        <div class="stats-label">Total Alerts</div>
                        <div class="stats-number" style="color: var(--info);">-</div>
                        <small style="color: #95a5a6;">Strike >= 3</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <div class="stats-label">Avg Strike Count</div>
                        <div class="stats-number" style="color: var(--warning);">-</div>
                        <small style="color: #95a5a6;">All timeframes</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <div class="stats-label">Down Alerts</div>
                        <div class="stats-number" style="color: var(--danger);">-</div>
                        <small style="color: #95a5a6;">Negative movement</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <div class="stats-label">Up Alerts</div>
                        <div class="stats-number" style="color: var(--success);">-</div>
                        <small style="color: #95a5a6;">Positive movement</small>
                    </div>
                </div>
            </div>
            
            <!-- Alerts Table -->
            <div class="alert-container">
                <div class="alert-header">
                    <h3>Strike Alerts</h3>
                    <button class="btn btn-light btn-sm" onclick="refreshData()">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
                
                <div class="filter-group">
                    <label>Filter by Timeframe:</label>
                    <select id="tfFilter" onchange="filterData()">
                        <option value="">All Timeframes</option>
                        <option value="5m">5 Minutes</option>
                        <option value="15m">15 Minutes</option>
                        <option value="30m">30 Minutes</option>
                        <option value="1h">1 Hour</option>
                    </select>
                    
                    <label>Filter by Direction:</label>
                    <select id="dirFilter" onchange="filterData()">
                        <option value="">All Directions</option>
                        <option value="down">Down</option>
                        <option value="up">Up</option>
                    </select>
                    
                    <label>Min Strike Count:</label>
                    <select id="strikeFilter" onchange="filterData()">
                        <option value="3">3+</option>
                        <option value="4">4+</option>
                        <option value="5">5+</option>
                        <option value="7">7+</option>
                    </select>
                </div>
                
                <div id="alertsContainer" style="padding: 20px;">
                    <div class="loading">
                        <i class="fas fa-spinner"></i> Loading data...
                    </div>
                </div>
            </div>
            
            <!-- Chart Stats -->
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="chart-container">
                        <div class="chart-title">
                            <i class="fas fa-chart-bar"></i> Alerts by Timeframe
                        </div>
                        <div id="timeframeStats"></div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container">
                        <div class="chart-title">
                            <i class="fas fa-chart-pie"></i> Alerts by Direction
                        </div>
                        <div id="directionStats"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>&copy; 2026 Strike Alerts Monitoring System | Real-time intraday analysis</p>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            let allData = [];
            
            async function loadData() {
                try {
                    // Load strikes data
                    const response = await fetch('/api/strikes?limit=100');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        allData = result.data;
                        displayAlerts(allData);
                        updateLastUpdate();
                    }
                    
                    // Load stats
                    const statsResponse = await fetch('/api/stats');
                    const statsResult = await statsResponse.json();
                    
                    if (statsResult.status === 'success') {
                        displayStats(statsResult);
                    }
                } catch (error) {
                    console.error('Error loading data:', error);
                    document.getElementById('alertsContainer').innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-exclamation-circle"></i>
                            <p>Error loading data</p>
                        </div>
                    `;
                }
            }
            
            function displayAlerts(data) {
                if (data.length === 0) {
                    document.getElementById('alertsContainer').innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-inbox"></i>
                            <p>No alerts found</p>
                        </div>
                    `;
                    return;
                }
                
                let html = '<table class="strikes-table"><thead><tr>' +
                    '<th>Ticker</th>' +
                    '<th>Timeframe</th>' +
                    '<th>Strikes</th>' +
                    '<th>Direction</th>' +
                    '<th>Current Price</th>' +
                    '<th>Change</th>' +
                    '<th>Total Change</th>' +
                    '<th>Timestamp</th>' +
                    '<th>Action</th>' +
                    '</tr></thead><tbody>';
                
                data.forEach(alert => {
                    const dirIcon = alert.direction === 'down' ? '📉' : '📈';
                    const dirClass = alert.direction === 'down' ? 'direction-down' : 'direction-up';
                    const changeClass = alert.change < 0 ? 'change-down' : 'change-up';
                    
                    const timestamp = new Date(alert.timestamp).toLocaleString();
                    
                    html += '<tr>' +
                        '<td><span class="ticker-badge">' + alert.ticker + '</span></td>' +
                        '<td><span class="timeframe-badge">' + alert.timeframe + '</span></td>' +
                        '<td><span class="strike-count">' + alert.strike_count + 'x</span></td>' +
                        '<td><span class="' + dirClass + '">' + dirIcon + ' ' + alert.direction.toUpperCase() + '</span></td>' +
                        '<td>$' + alert.price.toFixed(2) + '</td>' +
                        '<td class="' + changeClass + '">' + alert.change.toFixed(3) + '%</td>' +
                        '<td class="' + changeClass + '">' + alert.total_change.toFixed(3) + '%</td>' +
                        '<td class="timestamp">' + timestamp + '</td>' +
                        '<td><a href="/detail/' + alert.ticker + '" class="btn-detail">View Details</a></td>' +
                        '</tr>';
                });
                
                html += '</tbody></table>';
                document.getElementById('alertsContainer').innerHTML = html;
            }
            
            function displayStats(stats) {
                // Timeframe stats
                let tfHtml = '';
                stats.by_timeframe.forEach(tf => {
                    tfHtml += '<div class="stat-row">' +
                        '<span class="stat-row-label">' + tf.timeframe + '</span>' +
                        '<span class="stat-row-value">' + tf.count + ' (' + tf.avg_strike.toFixed(1) + 'x avg)</span>' +
                        '</div>';
                });
                document.getElementById('timeframeStats').innerHTML = tfHtml;
                
                // Direction stats
                let dirHtml = '';
                stats.by_direction.forEach(dir => {
                    dirHtml += '<div class="stat-row">' +
                        '<span class="stat-row-label">' + (dir.direction === 'down' ? '📉 Down' : '📈 Up') + '</span>' +
                        '<span class="stat-row-value">' + dir.count + ' (' + dir.avg_strike.toFixed(1) + 'x avg)</span>' +
                        '</div>';
                });
                document.getElementById('directionStats').innerHTML = dirHtml;
            }
            
            function filterData() {
                const tfFilter = document.getElementById('tfFilter').value;
                const dirFilter = document.getElementById('dirFilter').value;
                const strikeFilter = parseInt(document.getElementById('strikeFilter').value);
                
                let filtered = allData.filter(item => {
                    return (tfFilter === '' || item.timeframe === tfFilter) &&
                           (dirFilter === '' || item.direction === dirFilter) &&
                           (item.strike_count >= strikeFilter);
                });
                
                displayAlerts(filtered);
            }
            
            function refreshData() {
                document.getElementById('alertsContainer').innerHTML = `
                    <div class="loading">
                        <i class="fas fa-spinner"></i> Refreshing...
                    </div>
                `;
                loadData();
            }
            
            function updateLastUpdate() {
                const now = new Date();
                document.getElementById('lastUpdate').textContent = 'Last update: ' + now.toLocaleTimeString();
            }
            
            // Initial load
            loadData();
            
            // Auto refresh every 30 seconds
            setInterval(loadData, 30000);
        </script>
    </body>
    </html>
    """
    return html

def get_detail_page_html(ticker):
    """Generate detail page untuk specific ticker"""
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{ticker} Strike Details</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            :root {{
                --primary: #2c3e50;
                --success: #27ae60;
                --danger: #e74c3c;
                --warning: #f39c12;
                --info: #3498db;
            }}
            
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            
            .navbar {{
                background: var(--primary) !important;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            
            .detail-header {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            
            .ticker-title {{
                font-size: 36px;
                font-weight: 700;
                color: var(--primary);
            }}
            
            .strikes-list {{
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            
            .strike-item {{
                border-bottom: 1px solid #ecf0f1;
                padding: 20px;
                transition: background 0.2s;
            }}
            
            .strike-item:hover {{
                background: #f8f9fa;
            }}
            
            .strike-item:last-child {{
                border-bottom: none;
            }}
            
            .strike-number {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 16px;
                margin-right: 20px;
            }}
            
            .strike-content {{
                flex: 1;
            }}
            
            .strike-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            
            .strike-timeframe {{
                font-size: 16px;
                font-weight: 600;
                color: var(--primary);
            }}
            
            .strike-direction {{
                font-size: 16px;
                font-weight: 600;
            }}
            
            .strike-direction.down {{
                color: var(--danger);
            }}
            
            .strike-direction.up {{
                color: var(--success);
            }}
            
            .strike-info {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-top: 10px;
            }}
            
            .info-box {{
                background: var(--light);
                padding: 10px;
                border-radius: 6px;
                text-align: center;
            }}
            
            .info-label {{
                font-size: 12px;
                color: #7f8c8d;
                text-transform: uppercase;
                font-weight: 600;
            }}
            
            .info-value {{
                font-size: 16px;
                font-weight: 700;
                margin-top: 5px;
                color: var(--primary);
            }}
            
            .back-btn {{
                margin-bottom: 20px;
            }}
            
            .empty-message {{
                text-align: center;
                padding: 40px;
                color: white;
            }}
        </style>
    </head>
    <body>
        <!-- Navbar -->
        <nav class="navbar navbar-dark sticky-top">
            <div class="container-fluid">
                <span class="navbar-brand mb-0 h1">
                    <i class="fas fa-chart-line"></i> Strike Details
                </span>
            </div>
        </nav>
        
        <!-- Main Content -->
        <div class="container-fluid" style="margin-top: 20px;">
            <a href="/" class="btn btn-light back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
            
            <div class="detail-header">
                <div class="ticker-title">
                    <i class="fas fa-bolt"></i> {ticker}
                </div>
                <p style="color: #7f8c8d; margin-top: 10px;">All strikes >= 3 consecutive candles</p>
            </div>
            
            <div class="strikes-list" id="strikesContainer">
                <div class="empty-message">
                    <i class="fas fa-spinner" style="font-size: 32px; animation: spin 1s linear infinite;"></i>
                    <p>Loading data...</p>
                </div>
            </div>
        </div>
        
        <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            async function loadStrikeDetails() {{
                try {{
                    const response = await fetch('/api/strikes/{ticker}');
                    const result = await response.json();
                    
                    if (result.status === 'success' && result.data.length > 0) {{
                        displayStrikes(result.data);
                    }} else {{
                        document.getElementById('strikesContainer').innerHTML = `
                            <div class="empty-message">
                                <i class="fas fa-inbox"></i>
                                <p>No strike data found for {ticker}</p>
                            </div>
                        `;
                    }}
                }} catch (error) {{
                    console.error('Error loading details:', error);
                }}
            }}
            
            function displayStrikes(data) {{
                let html = '';
                let strikeNum = 1;
                
                data.forEach(strike => {{
                    const dirClass = strike.direction === 'down' ? 'down' : 'up';
                    const dirIcon = strike.direction === 'down' ? '📉' : '📈';
                    const timestamp = new Date(strike.timestamp).toLocaleString();
                    
                    html += `
                        <div style="display: flex; align-items: flex-start;">
                            <div class="strike-number">${{strikeNum}}</div>
                            <div class="strike-content" style="width: 100%;">
                                <div class="strike-header">
                                    <span class="strike-timeframe">${{strike.timeframe}} Timeframe</span>
                                    <span class="strike-direction ${{dirClass}}">${{dirIcon}} ${{strike.direction.toUpperCase()}}</span>
                                </div>
                                <div class="strike-info">
                                    <div class="info-box">
                                        <div class="info-label">Price</div>
                                        <div class="info-value">${{strike.price.toFixed(2)}}</div>
                                    </div>
                                    <div class="info-box">
                                        <div class="info-label">Change</div>
                                        <div class="info-value" style="color: ${{strike.change < 0 ? 'var(--danger)' : 'var(--success)'}};">${{strike.change.toFixed(3)}}%</div>
                                    </div>
                                    <div class="info-box">
                                        <div class="info-label">Total Change</div>
                                        <div class="info-value" style="color: ${{strike.total_change < 0 ? 'var(--danger)' : 'var(--success)'}};">${{strike.total_change.toFixed(3)}}%</div>
                                    </div>
                                    <div class="info-box">
                                        <div class="info-label">Timestamp</div>
                                        <div class="info-value" style="font-size: 12px;">${{timestamp}}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    strikeNum++;
                }});
                
                document.getElementById('strikesContainer').innerHTML = html;
            }}
            
            loadStrikeDetails();
            
            // Auto refresh every 30 seconds
            setInterval(loadStrikeDetails, 30000);
        </script>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    print("✅ Dashboard HTML files ready!")
    print("\nUsage:")
    print("  1. Import get_dashboard_html() untuk main dashboard")
    print("  2. Import get_detail_page_html(ticker) untuk detail page")
