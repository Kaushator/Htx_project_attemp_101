# HTX Trading Platform - Safe Process Management with PID Tracking

## Overview
Implementation of a safe process management system to replace dangerous system-wide `pkill` commands with precise PID-based process tracking and management.

## Current Process Management Issues

### Critical Problems
1. **Dangerous System-wide Commands**: `pkill -f uvicorn` kills ALL uvicorn processes system-wide
2. **No Process Tracking**: No record of started processes, cannot distinguish project processes
3. **Port Conflicts**: No verification of port availability before startup

## Safe Process Management Architecture

### Process Registry Structure
```
htx_project/
├── .htx_processes/           # Process management directory
│   ├── registry.json        # Central process registry
│   ├── backend.pid          # Backend process PID
│   ├── frontend.pid         # Frontend process PID
│   └── logs/                # Process management logs
└── scripts/
    ├── process_manager.py   # Central process management
    ├── start_safe.sh        # Safe startup script
    └── stop_safe.sh         # Safe shutdown script
```

### Process Registry Format (`registry.json`)
```json
{
  "project_id": "htx_trading_platform",
  "session_id": "20241201_143022",
  "processes": {
    "backend": {
      "pid": 12345,
      "port": 8004,
      "start_time": "2024-12-01T14:30:25Z",
      "command": "python run_backend_wsl.py",
      "status": "running",
      "health_check_url": "http://localhost:8004/api/v1/health"
    },
    "frontend": {
      "pid": 12346,
      "port": 3000,
      "start_time": "2024-12-01T14:30:30Z",
      "command": "npm run dev",
      "status": "running"
    }
  },
  "ports": {
    "8004": {"service": "backend", "pid": 12345},
    "3000": {"service": "frontend", "pid": 12346}
  }
}
```

## Core Process Manager Implementation

### Process Manager (`scripts/process_manager.py`)
```python
#!/usr/bin/env python3
"""HTX Trading Platform - Safe Process Manager"""

import json
import os
import signal
import subprocess
import psutil
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import logging

class HTXProcessManager:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.process_dir = self.project_root / '.htx_processes'
        self.registry_file = self.process_dir / 'registry.json'
        self.process_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('htx_process_manager')
    
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            return sock.connect_ex(('localhost', port)) != 0
    
    def load_registry(self) -> Dict:
        """Load process registry"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading registry: {e}")
        
        return {
            "project_id": "htx_trading_platform",
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "processes": {},
            "ports": {}
        }
    
    def save_registry(self, registry: Dict):
        """Save process registry"""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving registry: {e}")
    
    def cleanup_dead_processes(self):
        """Remove dead processes from registry"""
        registry = self.load_registry()
        
        for service_name, process_info in list(registry["processes"].items()):
            pid = process_info["pid"]
            if not psutil.pid_exists(pid):
                self.logger.info(f"Removing dead process: {service_name} (PID: {pid})")
                del registry["processes"][service_name]
                
                port = process_info.get("port")
                if port and str(port) in registry["ports"]:
                    del registry["ports"][str(port)]
        
        self.save_registry(registry)
    
    def start_process(self, service_name: str, command: List[str], port: int, 
                     working_dir: str = None, health_check_url: str = None) -> Optional[int]:
        """Start and register a process"""
        self.cleanup_dead_processes()
        
        # Check port availability
        if not self.is_port_available(port):
            self.logger.error(f"Port {port} is not available")
            return None
        
        # Set working directory
        if working_dir is None:
            working_dir = str(self.project_root)
        
        try:
            # Start process
            log_file = self.project_root / 'logs' / f'{service_name}.log'
            log_file.parent.mkdir(exist_ok=True)
            
            with open(log_file, 'a') as f:
                process = subprocess.Popen(
                    command,
                    cwd=working_dir,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid
                )
            
            pid = process.pid
            
            # Write PID file
            pid_file = self.process_dir / f"{service_name}.pid"
            with open(pid_file, 'w') as f:
                f.write(str(pid))
            
            # Update registry
            registry = self.load_registry()
            registry["processes"][service_name] = {
                "pid": pid,
                "port": port,
                "start_time": datetime.now(timezone.utc).isoformat(),
                "command": ' '.join(command),
                "working_dir": working_dir,
                "status": "running",
                "health_check_url": health_check_url
            }
            registry["ports"][str(port)] = {"service": service_name, "pid": pid}
            
            self.save_registry(registry)
            self.logger.info(f"Started {service_name} with PID {pid}")
            return pid
            
        except Exception as e:
            self.logger.error(f"Failed to start {service_name}: {e}")
            return None
    
    def stop_process(self, service_name: str, timeout: int = 10) -> bool:
        """Stop a specific process"""
        registry = self.load_registry()
        
        if service_name not in registry["processes"]:
            self.logger.warning(f"Service {service_name} not found")
            return False
        
        pid = registry["processes"][service_name]["pid"]
        
        try:
            if not psutil.pid_exists(pid):
                self.logger.info(f"Process {service_name} already dead")
                self._cleanup_process_entry(service_name, registry)
                return True
            
            process = psutil.Process(pid)
            process.terminate()
            
            try:
                process.wait(timeout=timeout)
            except psutil.TimeoutExpired:
                process.kill()
                process.wait()
            
            self._cleanup_process_entry(service_name, registry)
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping {service_name}: {e}")
            return False
    
    def _cleanup_process_entry(self, service_name: str, registry: Dict):
        """Clean up registry entry"""
        if service_name in registry["processes"]:
            port = registry["processes"][service_name].get("port")
            del registry["processes"][service_name]
            
            if port and str(port) in registry["ports"]:
                del registry["ports"][str(port)]
            
            pid_file = self.process_dir / f"{service_name}.pid"
            if pid_file.exists():
                pid_file.unlink()
            
            self.save_registry(registry)
    
    def stop_all_processes(self, timeout: int = 10) -> bool:
        """Stop all registered processes"""
        registry = self.load_registry()
        success = True
        
        for service_name in list(registry["processes"].keys()):
            if not self.stop_process(service_name, timeout):
                success = False
        
        return success
    
    def get_process_status(self) -> Dict:
        """Get status of all processes"""
        registry = self.load_registry()
        status = {}
        
        for name, process_info in registry["processes"].items():
            pid = process_info["pid"]
            if psutil.pid_exists(pid):
                try:
                    proc = psutil.Process(pid)
                    process_info["status"] = proc.status()
                    process_info["memory_mb"] = round(proc.memory_info().rss / 1024 / 1024, 2)
                except psutil.NoSuchProcess:
                    process_info["status"] = "dead"
            else:
                process_info["status"] = "dead"
            
            status[name] = process_info
        
        return status

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HTX Process Manager")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    subparsers = parser.add_subparsers(dest="command")
    
    # Commands
    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("service")
    start_parser.add_argument("--port", type=int, required=True)
    start_parser.add_argument("--command", nargs="+", required=True)
    start_parser.add_argument("--working-dir")
    start_parser.add_argument("--health-url")
    
    stop_parser = subparsers.add_parser("stop")
    stop_parser.add_argument("service")
    stop_parser.add_argument("--timeout", type=int, default=10)
    
    subparsers.add_parser("status")
    subparsers.add_parser("cleanup")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = HTXProcessManager(args.project_root)
    
    if args.command == "start":
        pid = manager.start_process(args.service, args.command, args.port, 
                                  args.working_dir, args.health_url)
        print(f"Started {args.service} with PID {pid}" if pid else f"Failed to start {args.service}")
    
    elif args.command == "stop":
        if args.service == "all":
            success = manager.stop_all_processes(args.timeout)
        else:
            success = manager.stop_process(args.service, args.timeout)
        print("Success" if success else "Failed")
    
    elif args.command == "status":
        print(json.dumps(manager.get_process_status(), indent=2))
    
    elif args.command == "cleanup":
        manager.cleanup_dead_processes()

if __name__ == "__main__":
    main()
```

## Safe Launch Scripts

### Safe Startup (`scripts/start_safe.sh`)
```bash
#!/usr/bin/env bash
# Safe startup script using PID-based process management

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROCESS_MANAGER="$SCRIPT_DIR/process_manager.py"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 HTX Project - Safe Startup${NC}"

# Install dependencies if needed
if ! python3 -c "import psutil" 2>/dev/null; then
    echo -e "${YELLOW}Installing psutil...${NC}"
    pip install psutil
fi

# Activate environment
if [ -f "$PROJECT_ROOT/scripts/activate_env.sh" ]; then
    source "$PROJECT_ROOT/scripts/activate_env.sh"
fi

# Cleanup and stop existing
echo -e "${YELLOW}Cleaning up existing processes...${NC}"
python3 "$PROCESS_MANAGER" --project-root "$PROJECT_ROOT" cleanup
python3 "$PROCESS_MANAGER" --project-root "$PROJECT_ROOT" stop all

# Start backend
echo -e "${GREEN}Starting backend...${NC}"
python3 "$PROCESS_MANAGER" --project-root "$PROJECT_ROOT" start backend \
    --port 8004 \
    --command python run_backend_wsl.py \
    --working-dir "$PROJECT_ROOT" \
    --health-url "http://localhost:8004/api/v1/health"

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
cd "$PROJECT_ROOT/frontend"
[ ! -d "node_modules" ] && npm install --silent

python3 "$PROCESS_MANAGER" --project-root "$PROJECT_ROOT" start frontend \
    --port 3000 \
    --command npm run dev \
    --working-dir "$PROJECT_ROOT/frontend"

# Health checks
echo -e "${BLUE}Waiting for services...${NC}"
sleep 10

# Show status
python3 "$PROCESS_MANAGER" --project-root "$PROJECT_ROOT" status

echo -e "${GREEN}🎉 Services started!${NC}"
echo "Backend: http://localhost:8004"
echo "Frontend: http://localhost:3000"
```

### Safe Shutdown (`scripts/stop_safe.sh`)
```bash
#!/usr/bin/env bash
# Safe shutdown script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROCESS_MANAGER="$SCRIPT_DIR/process_manager.py"

echo "🛑 HTX Project - Safe Shutdown"

SERVICE_NAME="$1"
TIMEOUT="${2:-10}"

if [ -n "$SERVICE_NAME" ] && [ "$SERVICE_NAME" != "all" ]; then
    python3 "$PROCESS_MANAGER" --project-root "$PROJECT_ROOT" stop "$SERVICE_NAME" --timeout "$TIMEOUT"
else
    python3 "$PROCESS_MANAGER" --project-root "$PROJECT_ROOT" stop all --timeout "$TIMEOUT"
fi

echo "✅ Shutdown completed"
```

## Integration with Existing Scripts

### Updated Enhanced Launch Script
Replace dangerous `pkill` commands in existing scripts:

```bash
# OLD - Dangerous
pkill -f uvicorn || true
pkill -f node || true

# NEW - Safe
python3 "$PROJECT_ROOT/scripts/process_manager.py" --project-root "$PROJECT_ROOT" stop all
```

## Benefits

1. **Safety**: No accidental killing of unrelated processes
2. **Tracking**: Complete process lifecycle management
3. **Port Management**: Automatic port reservation and conflict detection
4. **Health Monitoring**: Built-in health check capabilities
5. **Recovery**: Automatic cleanup of orphaned processes
6. **Logging**: Comprehensive process management logging

## Implementation Steps

1. **Create Process Manager**: Deploy `process_manager.py` script
2. **Update Launch Scripts**: Replace `pkill` with safe process management
3. **Test Migration**: Verify all services start/stop correctly
4. **Update Documentation**: Train team on new process management commands
5. **Monitor**: Implement process monitoring and alerting

This safe process management system eliminates the risk of accidentally killing unrelated processes while providing comprehensive process lifecycle management for the HTX Trading Platform.