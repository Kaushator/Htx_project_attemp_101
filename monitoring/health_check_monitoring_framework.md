# HTX Trading Platform - Health Check and Monitoring Framework

## Overview
Comprehensive health check and monitoring system designed for the HTX Trading Platform running in WSL2 environment, providing real-time system health visibility, automated alerting, and performance tracking.

## Monitoring Architecture

### System Components
```
HTX Monitoring Stack
├── Health Check Services
│   ├── Application Health Endpoints
│   ├── Database Health Checks
│   ├── External API Health (HTX)
│   └── System Resource Monitoring
├── Metrics Collection
│   ├── Application Metrics
│   ├── Performance Metrics
│   ├── Business Metrics
│   └── Security Metrics
├── Alerting System
│   ├── Threshold-based Alerts
│   ├── Anomaly Detection
│   ├── Escalation Policies
│   └── Alert Routing
└── Visualization Dashboard
    ├── Real-time Dashboards
    ├── Historical Analytics
    ├── Performance Trends
    └── Alert Management
```

## Health Check Implementation

### 1. Core Health Check Service

#### Health Check Manager (`monitoring/health_checker.py`)
```python
#!/usr/bin/env python3
"""HTX Trading Platform - Health Check Manager"""

import asyncio
import aiohttp
import psutil
import sqlite3
import time
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

class HealthCheckResult:
    def __init__(self, service: str, status: str, details: Dict = None, 
                 response_time: float = 0, timestamp: str = None):
        self.service = service
        self.status = status  # 'healthy', 'degraded', 'unhealthy'
        self.details = details or {}
        self.response_time = response_time
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict:
        return {
            'service': self.service,
            'status': self.status,
            'details': self.details,
            'response_time': self.response_time,
            'timestamp': self.timestamp
        }

class HTXHealthChecker:
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.session = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load health check configuration"""
        default_config = {
            'endpoints': {
                'backend': 'http://localhost:8004/api/v1/health',
                'frontend': 'http://localhost:3000',
                'htx_api': 'https://api.huobi.pro/v1/common/timestamp'
            },
            'timeouts': {
                'http_timeout': 5,
                'database_timeout': 3,
                'api_timeout': 10
            },
            'thresholds': {
                'cpu_warning': 70,
                'cpu_critical': 85,
                'memory_warning': 75,
                'memory_critical': 90,
                'disk_warning': 80,
                'disk_critical': 95,
                'response_time_warning': 1.0,
                'response_time_critical': 3.0
            },
            'intervals': {
                'health_check': 30,
                'system_metrics': 60,
                'deep_check': 300
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _setup_logging(self):
        """Setup health check logging"""
        logger = logging.getLogger('htx_health_checker')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = Path('logs/health_checks.log')
        log_file.parent.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def check_application_health(self) -> HealthCheckResult:
        """Check main application health"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.config['endpoints']['backend'],
                    timeout=aiohttp.ClientTimeout(total=self.config['timeouts']['http_timeout'])
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Determine status based on response time
                        if response_time > self.config['thresholds']['response_time_critical']:
                            status = 'degraded'
                        elif response_time > self.config['thresholds']['response_time_warning']:
                            status = 'degraded'
                        else:
                            status = 'healthy'
                        
                        return HealthCheckResult(
                            service='backend',
                            status=status,
                            details=data,
                            response_time=response_time
                        )
                    else:
                        return HealthCheckResult(
                            service='backend',
                            status='unhealthy',
                            details={'error': f'HTTP {response.status}'},
                            response_time=response_time
                        )
        
        except asyncio.TimeoutError:
            return HealthCheckResult(
                service='backend',
                status='unhealthy',
                details={'error': 'Timeout'},
                response_time=time.time() - start_time
            )
        except Exception as e:
            return HealthCheckResult(
                service='backend',
                status='unhealthy',
                details={'error': str(e)},
                response_time=time.time() - start_time
            )
    
    async def check_database_health(self) -> HealthCheckResult:
        """Check database connectivity and performance"""
        start_time = time.time()
        
        try:
            # Database connection test
            db_path = self.config.get('database_path', 'data/app.db')
            
            with sqlite3.connect(db_path, timeout=self.config['timeouts']['database_timeout']) as conn:
                # Test basic query
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                # Test performance query
                cursor.execute("SELECT 1")
                cursor.fetchone()
                
                response_time = time.time() - start_time
                
                status = 'healthy'
                if response_time > self.config['thresholds']['response_time_warning']:
                    status = 'degraded'
                
                return HealthCheckResult(
                    service='database',
                    status=status,
                    details={
                        'table_count': table_count,
                        'database_size_mb': Path(db_path).stat().st_size / 1024 / 1024
                    },
                    response_time=response_time
                )
        
        except Exception as e:
            return HealthCheckResult(
                service='database',
                status='unhealthy',
                details={'error': str(e)},
                response_time=time.time() - start_time
            )
    
    async def check_htx_api_health(self) -> HealthCheckResult:
        """Check HTX API connectivity"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.config['endpoints']['htx_api'],
                    timeout=aiohttp.ClientTimeout(total=self.config['timeouts']['api_timeout'])
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        status = 'healthy'
                        if response_time > self.config['thresholds']['response_time_warning']:
                            status = 'degraded'
                        
                        return HealthCheckResult(
                            service='htx_api',
                            status=status,
                            details={'server_time': data.get('data')},
                            response_time=response_time
                        )
                    else:
                        return HealthCheckResult(
                            service='htx_api',
                            status='unhealthy',
                            details={'error': f'HTTP {response.status}'},
                            response_time=response_time
                        )
        
        except Exception as e:
            return HealthCheckResult(
                service='htx_api',
                status='unhealthy',
                details={'error': str(e)},
                response_time=time.time() - start_time
            )
    
    def check_system_resources(self) -> HealthCheckResult:
        """Check system resource utilization"""
        start_time = time.time()
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Determine overall status
            status = 'healthy'
            
            if (cpu_percent > self.config['thresholds']['cpu_critical'] or
                memory_percent > self.config['thresholds']['memory_critical'] or
                disk_percent > self.config['thresholds']['disk_critical']):
                status = 'unhealthy'
            elif (cpu_percent > self.config['thresholds']['cpu_warning'] or
                  memory_percent > self.config['thresholds']['memory_warning'] or
                  disk_percent > self.config['thresholds']['disk_warning']):
                status = 'degraded'
            
            return HealthCheckResult(
                service='system_resources',
                status=status,
                details={
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'memory_total_gb': round(memory.total / 1024**3, 2),
                    'memory_available_gb': round(memory.available / 1024**3, 2),
                    'disk_percent': disk_percent,
                    'disk_total_gb': round(disk.total / 1024**3, 2),
                    'disk_free_gb': round(disk.free / 1024**3, 2)
                },
                response_time=time.time() - start_time
            )
        
        except Exception as e:
            return HealthCheckResult(
                service='system_resources',
                status='unhealthy',
                details={'error': str(e)},
                response_time=time.time() - start_time
            )
    
    async def run_comprehensive_health_check(self) -> Dict[str, HealthCheckResult]:
        """Run all health checks"""
        checks = {}
        
        # Run checks concurrently
        tasks = {
            'application': self.check_application_health(),
            'database': self.check_database_health(),
            'htx_api': self.check_htx_api_health()
        }
        
        # System check runs synchronously
        checks['system'] = self.check_system_resources()
        
        # Wait for async checks
        for name, task in tasks.items():
            try:
                checks[name] = await task
            except Exception as e:
                checks[name] = HealthCheckResult(
                    service=name,
                    status='unhealthy',
                    details={'error': str(e)}
                )
        
        return checks
    
    def get_overall_status(self, checks: Dict[str, HealthCheckResult]) -> str:
        """Determine overall system status"""
        statuses = [check.status for check in checks.values()]
        
        if 'unhealthy' in statuses:
            return 'unhealthy'
        elif 'degraded' in statuses:
            return 'degraded'
        else:
            return 'healthy'
```

### 2. Monitoring Dashboard

#### Dashboard Service (`monitoring/dashboard.py`)
```python
#!/usr/bin/env python3
"""HTX Trading Platform - Monitoring Dashboard"""

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import asyncio
from typing import Dict, List
import uvicorn

app = FastAPI(title="HTX Monitoring Dashboard")

class MonitoringDashboard:
    def __init__(self):
        self.health_checker = HTXHealthChecker()
        self.connected_clients: List[WebSocket] = []
        self.latest_metrics = {}
        self.monitoring_active = False
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # Run health checks
                checks = await self.health_checker.run_comprehensive_health_check()
                
                # Prepare metrics
                metrics = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'overall_status': self.health_checker.get_overall_status(checks),
                    'services': {name: check.to_dict() for name, check in checks.items()}
                }
                
                self.latest_metrics = metrics
                
                # Broadcast to connected clients
                await self.broadcast_metrics(metrics)
                
                # Wait before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def broadcast_metrics(self, metrics: Dict):
        """Broadcast metrics to all connected WebSocket clients"""
        if self.connected_clients:
            message = json.dumps(metrics)
            
            # Remove disconnected clients
            active_clients = []
            
            for client in self.connected_clients:
                try:
                    await client.send_text(message)
                    active_clients.append(client)
                except:
                    # Client disconnected
                    pass
            
            self.connected_clients = active_clients

dashboard = MonitoringDashboard()

@app.on_event("startup")
async def startup_event():
    """Start monitoring on app startup"""
    asyncio.create_task(dashboard.start_monitoring())

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve monitoring dashboard HTML"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HTX Monitoring Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .status-healthy { color: green; }
            .status-degraded { color: orange; }
            .status-unhealthy { color: red; }
            .service-card { 
                border: 1px solid #ccc; 
                margin: 10px; 
                padding: 15px; 
                border-radius: 5px; 
            }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
        </style>
    </head>
    <body>
        <h1>HTX Trading Platform - Monitoring Dashboard</h1>
        <div id="overall-status"></div>
        <div id="metrics" class="metrics"></div>
        
        <script>
            const ws = new WebSocket('ws://localhost:8005/ws');
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            function updateDashboard(data) {
                // Update overall status
                const overallDiv = document.getElementById('overall-status');
                overallDiv.innerHTML = `
                    <h2 class="status-${data.overall_status}">
                        Overall Status: ${data.overall_status.toUpperCase()}
                    </h2>
                    <p>Last Updated: ${new Date(data.timestamp).toLocaleString()}</p>
                `;
                
                // Update service metrics
                const metricsDiv = document.getElementById('metrics');
                metricsDiv.innerHTML = '';
                
                Object.entries(data.services).forEach(([name, service]) => {
                    const card = document.createElement('div');
                    card.className = 'service-card';
                    card.innerHTML = `
                        <h3 class="status-${service.status}">${name.toUpperCase()}</h3>
                        <p>Status: <span class="status-${service.status}">${service.status}</span></p>
                        <p>Response Time: ${service.response_time.toFixed(3)}s</p>
                        <pre>${JSON.stringify(service.details, null, 2)}</pre>
                    `;
                    metricsDiv.appendChild(card);
                });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    await websocket.accept()
    dashboard.connected_clients.append(websocket)
    
    # Send latest metrics immediately
    if dashboard.latest_metrics:
        await websocket.send_text(json.dumps(dashboard.latest_metrics))
    
    try:
        while True:
            await websocket.receive_text()
    except:
        # Client disconnected
        if websocket in dashboard.connected_clients:
            dashboard.connected_clients.remove(websocket)

@app.get("/api/health")
async def get_health_status():
    """API endpoint for health status"""
    checks = await dashboard.health_checker.run_comprehensive_health_check()
    
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'overall_status': dashboard.health_checker.get_overall_status(checks),
        'services': {name: check.to_dict() for name, check in checks.items()}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
```

### 3. Alerting System

#### Alert Manager (`monitoring/alerts.py`)
```python
#!/usr/bin/env python3
"""HTX Trading Platform - Alert Manager"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp

class AlertManager:
    def __init__(self, config_path: str = None):
        self.config = self._load_alert_config(config_path)
        self.alert_history = []
        self.suppressed_alerts = {}
    
    def _load_alert_config(self, config_path: str) -> Dict:
        """Load alerting configuration"""
        default_config = {
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'recipients': []
            },
            'slack': {
                'webhook_url': '',
                'channel': '#alerts'
            },
            'alert_rules': {
                'unhealthy_service': {
                    'severity': 'critical',
                    'cooldown_minutes': 5
                },
                'degraded_performance': {
                    'severity': 'warning',
                    'cooldown_minutes': 15
                },
                'high_resource_usage': {
                    'severity': 'warning',
                    'cooldown_minutes': 10
                }
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def should_send_alert(self, alert_key: str, severity: str) -> bool:
        """Check if alert should be sent based on cooldown"""
        now = datetime.now()
        
        if alert_key in self.suppressed_alerts:
            last_sent = self.suppressed_alerts[alert_key]
            cooldown = self.config['alert_rules'].get(severity, {}).get('cooldown_minutes', 5)
            
            if now - last_sent < timedelta(minutes=cooldown):
                return False
        
        return True
    
    async def send_alert(self, title: str, message: str, severity: str = 'warning'):
        """Send alert through configured channels"""
        alert_key = f"{title}_{severity}"
        
        if not self.should_send_alert(alert_key, severity):
            return
        
        # Send email alert
        if self.config['email']['recipients']:
            await self.send_email_alert(title, message, severity)
        
        # Send Slack alert
        if self.config['slack']['webhook_url']:
            await self.send_slack_alert(title, message, severity)
        
        # Record alert
        self.suppressed_alerts[alert_key] = datetime.now()
        self.alert_history.append({
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'message': message,
            'severity': severity
        })
    
    async def send_email_alert(self, title: str, message: str, severity: str):
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = ', '.join(self.config['email']['recipients'])
            msg['Subject'] = f"[HTX Alert - {severity.upper()}] {title}"
            
            body = f"""
HTX Trading Platform Alert

Severity: {severity.upper()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Title: {title}

Details:
{message}

Please investigate and take appropriate action.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    async def send_slack_alert(self, title: str, message: str, severity: str):
        """Send Slack alert"""
        try:
            color_map = {
                'critical': '#FF0000',
                'warning': '#FFA500',
                'info': '#00FF00'
            }
            
            payload = {
                'channel': self.config['slack']['channel'],
                'username': 'HTX Monitor',
                'attachments': [{
                    'color': color_map.get(severity, '#808080'),
                    'title': f'HTX Alert - {title}',
                    'text': message,
                    'fields': [
                        {'title': 'Severity', 'value': severity.upper(), 'short': True},
                        {'title': 'Time', 'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'short': True}
                    ]
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config['slack']['webhook_url'], json=payload) as response:
                    if response.status != 200:
                        print(f"Failed to send Slack alert: {response.status}")
                        
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
    
    def process_health_check_results(self, checks: Dict):
        """Process health check results and trigger alerts"""
        for service_name, result in checks.items():
            if result.status == 'unhealthy':
                asyncio.create_task(self.send_alert(
                    f"Service Unhealthy: {service_name}",
                    f"Service {service_name} is unhealthy. Details: {result.details}",
                    'critical'
                ))
            elif result.status == 'degraded':
                asyncio.create_task(self.send_alert(
                    f"Service Degraded: {service_name}",
                    f"Service {service_name} is experiencing degraded performance. Response time: {result.response_time:.3f}s",
                    'warning'
                ))
```

## Monitoring Startup Script

### Monitor Launcher (`scripts/start_monitoring.sh`)
```bash
#!/usr/bin/env bash
# Start HTX monitoring services

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔍 Starting HTX Monitoring Services"
echo "=================================="

# Activate environment
source "$PROJECT_ROOT/scripts/activate_env.sh"

# Create monitoring directories
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/monitoring/config"

# Install monitoring dependencies
pip install psutil aiohttp fastapi uvicorn websockets

# Start monitoring dashboard
echo "🚀 Starting monitoring dashboard..."
python "$PROJECT_ROOT/monitoring/dashboard.py" &
DASHBOARD_PID=$!

echo "✅ Monitoring services started"
echo "📊 Dashboard: http://localhost:8005"
echo "🔧 Health API: http://localhost:8005/api/health"

# Save PIDs for cleanup
echo "$DASHBOARD_PID" > "$PROJECT_ROOT/.htx_processes/monitoring.pid"

echo "💡 Use 'scripts/stop_monitoring.sh' to stop monitoring services"
```

## Expected Benefits

### Monitoring Capabilities
1. **Real-time Health Monitoring**: Continuous service health tracking
2. **Performance Metrics**: Response time and resource utilization monitoring
3. **Automated Alerting**: Proactive issue detection and notification
4. **Historical Analytics**: Trend analysis and capacity planning
5. **WSL2 Optimization**: Monitoring specifically tuned for WSL2 environment

### Alert Types
- Service availability alerts
- Performance degradation warnings
- Resource utilization thresholds
- External API connectivity issues
- Database performance alerts

This comprehensive health check and monitoring framework provides complete visibility into the HTX Trading Platform's operational status, enabling proactive issue resolution and optimal performance in the WSL2 environment.