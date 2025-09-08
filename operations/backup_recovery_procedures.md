# HTX Trading Platform - Backup and Recovery Procedures

## Overview
Comprehensive backup and recovery system designed for the HTX Trading Platform running in WSL2 environment, ensuring data protection, business continuity, and rapid disaster recovery capabilities.

## Backup Strategy Overview

### Data Classification
```
HTX Data Categories
├── Critical Data (RTO: 15min, RPO: 5min)
│   ├── Trading Data & Analytics
│   ├── User Configurations
│   ├── API Keys & Secrets
│   └── Process Registry
├── Important Data (RTO: 1hr, RPO: 30min)
│   ├── Application Logs
│   ├── Performance Metrics
│   ├── File Processing Results
│   └── System Configurations
└── Archival Data (RTO: 4hr, RPO: 24hr)
    ├── Historical Analytics
    ├── Audit Logs
    ├── Debug Information
    └── Legacy File Backups
```

### Backup Architecture
```
Backup System Architecture
├── Automated Backup Services
│   ├── Database Backup (SQLite → WSL2 FS)
│   ├── File System Backup
│   ├── Configuration Backup
│   └── Environment Backup
├── Storage Locations
│   ├── Local Backup (WSL2 FS)
│   ├── Windows Host Backup
│   ├── Network Storage (Optional)
│   └── Cloud Backup (Optional)
├── Recovery Tools
│   ├── Database Recovery Scripts
│   ├── Environment Restoration
│   ├── Service Recovery Automation
│   └── Validation Testing
└── Monitoring & Alerts
    ├── Backup Success/Failure Alerts
    ├── Storage Usage Monitoring
    ├── Recovery Testing Validation
    └── Retention Policy Enforcement
```

## Backup Implementation

### 1. Database Backup System

#### Database Backup Manager (`scripts/backup_manager.py`)
```python
#!/usr/bin/env python3
"""HTX Trading Platform - Backup Manager"""

import sqlite3
import shutil
import gzip
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

class HTXBackupManager:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_root = self.project_root / 'backups'
        self.config_file = self.project_root / '.backup_config.json'
        
        # Create backup directories
        self.backup_root.mkdir(exist_ok=True)
        (self.backup_root / 'daily').mkdir(exist_ok=True)
        (self.backup_root / 'weekly').mkdir(exist_ok=True)
        (self.backup_root / 'monthly').mkdir(exist_ok=True)
        
        self.logger = self._setup_logging()
        self.config = self._load_config()
    
    def _setup_logging(self):
        """Setup backup logging"""
        log_file = self.project_root / 'logs' / 'backup.log'
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('htx_backup')
    
    def _load_config(self) -> Dict:
        """Load backup configuration"""
        default_config = {
            'database_path': 'data/app.db',
            'retention_policy': {
                'daily': 7,    # Keep 7 daily backups
                'weekly': 4,   # Keep 4 weekly backups  
                'monthly': 12  # Keep 12 monthly backups
            },
            'compression': True,
            'backup_schedule': {
                'daily': '02:00',
                'weekly': 'Sunday 03:00',
                'monthly': '1st 04:00'
            },
            'critical_files': [
                'data/',
                '.env',
                '.ports_config',
                'scripts/',
                'monitoring/config/'
            ],
            'exclude_patterns': [
                '*.pyc',
                '__pycache__',
                'node_modules',
                '.git',
                'logs/*.log',
                '.htx_processes'
            ]
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def backup_database(self, backup_type: str = 'daily') -> Path:
        """Create database backup with integrity check"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.backup_root / backup_type / f'backup_{timestamp}'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        db_path = self.project_root / self.config['database_path']
        
        if not db_path.exists():
            self.logger.warning(f"Database not found: {db_path}")
            return None
        
        try:
            # Create database backup with integrity check
            backup_file = backup_dir / 'app.db'
            
            # SQLite backup using .backup command (ensures consistency)
            with sqlite3.connect(str(db_path)) as source_conn:
                # Check database integrity
                cursor = source_conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                
                if integrity_result != 'ok':
                    raise Exception(f"Database integrity check failed: {integrity_result}")
                
                # Create backup database
                with sqlite3.connect(str(backup_file)) as backup_conn:
                    source_conn.backup(backup_conn)
            
            # Compress backup if enabled
            if self.config['compression']:
                compressed_file = backup_file.with_suffix('.db.gz')
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_file.unlink()  # Remove uncompressed file
                backup_file = compressed_file
            
            # Create backup metadata
            metadata = {
                'timestamp': timestamp,
                'backup_type': backup_type,
                'database_size': db_path.stat().st_size,
                'backup_size': backup_file.stat().st_size,
                'compressed': self.config['compression'],
                'integrity_check': integrity_result
            }
            
            with open(backup_dir / 'metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Database backup completed: {backup_file}")
            return backup_file
            
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return None
    
    def backup_files(self, backup_type: str = 'daily') -> Path:
        """Backup critical files and configurations"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.backup_root / backup_type / f'backup_{timestamp}'
        files_backup_dir = backup_dir / 'files'
        files_backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            backed_up_files = []
            
            for file_pattern in self.config['critical_files']:
                source_path = self.project_root / file_pattern
                
                if source_path.is_file():
                    # Single file
                    dest_path = files_backup_dir / file_pattern
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                    backed_up_files.append(str(file_pattern))
                    
                elif source_path.is_dir():
                    # Directory - copy with exclusions
                    dest_path = files_backup_dir / file_pattern
                    self._copy_directory_with_exclusions(source_path, dest_path)
                    backed_up_files.append(str(file_pattern))
            
            # Create file backup metadata
            file_metadata = {
                'timestamp': timestamp,
                'backup_type': backup_type,
                'files_backed_up': backed_up_files,
                'total_size': self._get_directory_size(files_backup_dir)
            }
            
            with open(backup_dir / 'files_metadata.json', 'w') as f:
                json.dump(file_metadata, f, indent=2)
            
            self.logger.info(f"File backup completed: {files_backup_dir}")
            return files_backup_dir
            
        except Exception as e:
            self.logger.error(f"File backup failed: {e}")
            return None
    
    def _copy_directory_with_exclusions(self, src: Path, dst: Path):
        """Copy directory excluding patterns"""
        dst.mkdir(parents=True, exist_ok=True)
        
        for item in src.rglob('*'):
            relative_path = item.relative_to(src)
            
            # Check exclusion patterns
            excluded = False
            for pattern in self.config['exclude_patterns']:
                if item.match(pattern) or any(part.startswith('.') for part in relative_path.parts):
                    excluded = True
                    break
            
            if not excluded:
                dest_item = dst / relative_path
                
                if item.is_file():
                    dest_item.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_item)
    
    def _get_directory_size(self, path: Path) -> int:
        """Calculate directory size recursively"""
        total_size = 0
        for item in path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
        return total_size
    
    def create_full_backup(self, backup_type: str = 'daily') -> Dict:
        """Create complete system backup"""
        self.logger.info(f"Starting {backup_type} backup...")
        
        backup_results = {
            'timestamp': datetime.now().isoformat(),
            'backup_type': backup_type,
            'database_backup': None,
            'files_backup': None,
            'success': False
        }
        
        try:
            # Backup database
            db_backup = self.backup_database(backup_type)
            backup_results['database_backup'] = str(db_backup) if db_backup else None
            
            # Backup files
            files_backup = self.backup_files(backup_type)
            backup_results['files_backup'] = str(files_backup) if files_backup else None
            
            # Check if backup was successful
            backup_results['success'] = db_backup is not None and files_backup is not None
            
            if backup_results['success']:
                self.logger.info(f"{backup_type.capitalize()} backup completed successfully")
            else:
                self.logger.error(f"{backup_type.capitalize()} backup failed")
            
            return backup_results
            
        except Exception as e:
            self.logger.error(f"Full backup failed: {e}")
            backup_results['error'] = str(e)
            return backup_results
    
    def cleanup_old_backups(self):
        """Remove old backups according to retention policy"""
        for backup_type, retention_days in self.config['retention_policy'].items():
            backup_dir = self.backup_root / backup_type
            
            if not backup_dir.exists():
                continue
            
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for backup_folder in backup_dir.iterdir():
                if backup_folder.is_dir():
                    try:
                        # Extract timestamp from folder name
                        folder_timestamp = datetime.strptime(
                            backup_folder.name.split('_', 1)[1], 
                            '%Y%m%d_%H%M%S'
                        )
                        
                        if folder_timestamp < cutoff_date:
                            shutil.rmtree(backup_folder)
                            self.logger.info(f"Removed old backup: {backup_folder}")
                            
                    except (ValueError, IndexError):
                        # Skip folders that don't match expected format
                        continue
```

### 2. Recovery System

#### Recovery Manager (`scripts/recovery_manager.py`)
```python
#!/usr/bin/env python3
"""HTX Trading Platform - Recovery Manager"""

import sqlite3
import shutil
import gzip
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

class HTXRecoveryManager:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_root = self.project_root / 'backups'
        self.logger = logging.getLogger('htx_recovery')
    
    def list_available_backups(self) -> Dict:
        """List all available backups"""
        backups = {'daily': [], 'weekly': [], 'monthly': []}
        
        for backup_type in backups.keys():
            backup_dir = self.backup_root / backup_type
            
            if backup_dir.exists():
                for backup_folder in sorted(backup_dir.iterdir(), reverse=True):
                    if backup_folder.is_dir():
                        metadata_file = backup_folder / 'metadata.json'
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                
                                backups[backup_type].append({
                                    'path': str(backup_folder),
                                    'timestamp': metadata.get('timestamp'),
                                    'size': metadata.get('backup_size', 0)
                                })
                            except Exception as e:
                                self.logger.warning(f"Failed to read metadata for {backup_folder}: {e}")
        
        return backups
    
    def restore_database(self, backup_path: str, target_path: str = None) -> bool:
        """Restore database from backup"""
        backup_folder = Path(backup_path)
        
        if target_path is None:
            target_path = self.project_root / 'data' / 'app.db'
        else:
            target_path = Path(target_path)
        
        try:
            # Find database backup file
            db_backup_file = None
            for file in backup_folder.iterdir():
                if file.name.startswith('app.db'):
                    db_backup_file = file
                    break
            
            if not db_backup_file:
                self.logger.error(f"No database backup found in {backup_folder}")
                return False
            
            # Create backup of current database
            if target_path.exists():
                backup_current = target_path.with_suffix('.db.pre_restore')
                shutil.copy2(target_path, backup_current)
                self.logger.info(f"Current database backed up to {backup_current}")
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Restore database
            if db_backup_file.suffix == '.gz':
                # Decompress and restore
                with gzip.open(db_backup_file, 'rb') as f_in:
                    with open(target_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Direct copy
                shutil.copy2(db_backup_file, target_path)
            
            # Verify restored database
            with sqlite3.connect(str(target_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                
                if result != 'ok':
                    self.logger.error(f"Restored database failed integrity check: {result}")
                    return False
            
            self.logger.info(f"Database restored successfully from {db_backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Database restoration failed: {e}")
            return False
    
    def restore_files(self, backup_path: str) -> bool:
        """Restore files from backup"""
        backup_folder = Path(backup_path)
        files_backup_dir = backup_folder / 'files'
        
        if not files_backup_dir.exists():
            self.logger.error(f"No files backup found in {backup_folder}")
            return False
        
        try:
            # Restore files
            for item in files_backup_dir.rglob('*'):
                if item.is_file():
                    relative_path = item.relative_to(files_backup_dir)
                    target_path = self.project_root / relative_path
                    
                    # Create backup of existing file
                    if target_path.exists():
                        backup_existing = target_path.with_suffix(f'{target_path.suffix}.pre_restore')
                        shutil.copy2(target_path, backup_existing)
                    
                    # Restore file
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target_path)
            
            self.logger.info(f"Files restored successfully from {files_backup_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"File restoration failed: {e}")
            return False
    
    def emergency_restore(self, backup_timestamp: str = None) -> bool:
        """Emergency restore from most recent backup"""
        self.logger.info("Starting emergency restore procedure...")
        
        # Find most recent backup
        available_backups = self.list_available_backups()
        
        target_backup = None
        if backup_timestamp:
            # Find specific backup
            for backup_type, backups in available_backups.items():
                for backup in backups:
                    if backup_timestamp in backup['timestamp']:
                        target_backup = backup['path']
                        break
                if target_backup:
                    break
        else:
            # Use most recent backup
            for backup_type in ['daily', 'weekly', 'monthly']:
                if available_backups[backup_type]:
                    target_backup = available_backups[backup_type][0]['path']
                    break
        
        if not target_backup:
            self.logger.error("No backups available for emergency restore")
            return False
        
        self.logger.info(f"Using backup: {target_backup}")
        
        # Stop services before restore
        from .process_manager import HTXProcessManager
        process_manager = HTXProcessManager(str(self.project_root))
        process_manager.stop_all_processes()
        
        # Perform restore
        success = True
        success &= self.restore_database(target_backup)
        success &= self.restore_files(target_backup)
        
        if success:
            self.logger.info("Emergency restore completed successfully")
            
            # Restart services
            import subprocess
            subprocess.run([str(self.project_root / 'scripts' / 'start_safe.sh')])
        else:
            self.logger.error("Emergency restore failed")
        
        return success
```

### 3. Automated Backup Scheduler

#### Backup Scheduler (`scripts/backup_scheduler.sh`)
```bash
#!/usr/bin/env bash
# Automated backup scheduler for HTX Platform

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$PROJECT_ROOT/logs/backup_scheduler.log"
}

# Daily backup function
run_daily_backup() {
    log "Starting daily backup..."
    
    if python3 "$SCRIPT_DIR/backup_manager.py" --type daily; then
        log "✅ Daily backup completed successfully"
        return 0
    else
        log "❌ Daily backup failed"
        return 1
    fi
}

# Weekly backup function  
run_weekly_backup() {
    log "Starting weekly backup..."
    
    if python3 "$SCRIPT_DIR/backup_manager.py" --type weekly; then
        log "✅ Weekly backup completed successfully"
        
        # Cleanup old daily backups
        python3 "$SCRIPT_DIR/backup_manager.py" --cleanup
        return 0
    else
        log "❌ Weekly backup failed"
        return 1
    fi
}

# Monthly backup function
run_monthly_backup() {
    log "Starting monthly backup..."
    
    if python3 "$SCRIPT_DIR/backup_manager.py" --type monthly; then
        log "✅ Monthly backup completed successfully"
        
        # Cleanup old backups
        python3 "$SCRIPT_DIR/backup_manager.py" --cleanup
        return 0
    else
        log "❌ Monthly backup failed"
        return 1
    fi
}

# Health check before backup
pre_backup_check() {
    # Check if services are running
    if ! python3 "$SCRIPT_DIR/process_manager.py" status >/dev/null 2>&1; then
        log "⚠️ No running services detected"
        return 1
    fi
    
    # Check disk space (need at least 1GB free)
    available_space=$(df "$PROJECT_ROOT" | awk 'NR==2{print $4}')
    if [ "$available_space" -lt 1048576 ]; then  # 1GB in KB
        log "❌ Insufficient disk space for backup"
        return 1
    fi
    
    return 0
}

# Main backup routine
main() {
    local backup_type="${1:-daily}"
    
    log "Starting $backup_type backup routine..."
    
    # Pre-backup checks
    if ! pre_backup_check; then
        log "❌ Pre-backup checks failed"
        exit 1
    fi
    
    # Run appropriate backup
    case "$backup_type" in
        "daily")
            run_daily_backup
            ;;
        "weekly")
            run_weekly_backup
            ;;
        "monthly")
            run_monthly_backup
            ;;
        *)
            log "❌ Unknown backup type: $backup_type"
            exit 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        log "🎉 Backup routine completed successfully"
    else
        log "❌ Backup routine failed"
        
        # Send alert notification
        python3 "$PROJECT_ROOT/monitoring/alerts.py" \
            --title "Backup Failed" \
            --message "HTX Platform $backup_type backup failed" \
            --severity critical
        
        exit 1
    fi
}

# Setup cron jobs
setup_cron() {
    log "Setting up automated backup cron jobs..."
    
    # Create crontab entries
    cat > /tmp/htx_backup_cron << EOF
# HTX Platform Automated Backups
0 2 * * * $SCRIPT_DIR/backup_scheduler.sh daily
0 3 * * 0 $SCRIPT_DIR/backup_scheduler.sh weekly  
0 4 1 * * $SCRIPT_DIR/backup_scheduler.sh monthly
EOF

    # Install crontab
    crontab /tmp/htx_backup_cron
    rm /tmp/htx_backup_cron
    
    log "✅ Cron jobs installed successfully"
}

# Command line interface
case "${1:-}" in
    "setup")
        setup_cron
        ;;
    "daily"|"weekly"|"monthly")
        main "$1"
        ;;
    "")
        main "daily"
        ;;
    *)
        echo "Usage: $0 {setup|daily|weekly|monthly}"
        echo "  setup  - Install automated backup cron jobs"
        echo "  daily  - Run daily backup"
        echo "  weekly - Run weekly backup" 
        echo "  monthly- Run monthly backup"
        exit 1
        ;;
esac
```

## Disaster Recovery Procedures

### 1. Recovery Testing Script (`scripts/test_recovery.py`)
```python
#!/usr/bin/env python3
"""Recovery testing and validation"""

import subprocess
import time
from pathlib import Path
from backup_manager import HTXBackupManager
from recovery_manager import HTXRecoveryManager

class RecoveryTester:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_manager = HTXBackupManager(project_root)
        self.recovery_manager = HTXRecoveryManager(project_root)
    
    def test_backup_restore_cycle(self) -> bool:
        """Test complete backup and restore cycle"""
        print("🧪 Testing backup and restore cycle...")
        
        # Create test backup
        backup_result = self.backup_manager.create_full_backup('test')
        if not backup_result['success']:
            print("❌ Test backup creation failed")
            return False
        
        # Test database restore
        test_db_path = self.project_root / 'data' / 'test_restore.db'
        if not self.recovery_manager.restore_database(
            backup_result['database_backup'], 
            str(test_db_path)
        ):
            print("❌ Database restore test failed")
            return False
        
        # Cleanup test files
        if test_db_path.exists():
            test_db_path.unlink()
        
        print("✅ Backup and restore cycle test passed")
        return True
    
    def validate_recovery_procedures(self) -> bool:
        """Validate all recovery procedures"""
        print("🔍 Validating recovery procedures...")
        
        # Test backup listing
        backups = self.recovery_manager.list_available_backups()
        if not any(backups.values()):
            print("⚠️ No backups available for testing")
            return False
        
        # Test backup metadata
        for backup_type, backup_list in backups.items():
            if backup_list:
                backup_path = Path(backup_list[0]['path'])
                metadata_file = backup_path / 'metadata.json'
                
                if not metadata_file.exists():
                    print(f"❌ Missing metadata for {backup_type} backup")
                    return False
        
        print("✅ Recovery procedures validation passed")
        return True

if __name__ == "__main__":
    tester = RecoveryTester('.')
    
    success = True
    success &= tester.test_backup_restore_cycle()
    success &= tester.validate_recovery_procedures()
    
    if success:
        print("🎉 All recovery tests passed")
    else:
        print("❌ Recovery tests failed")
        exit(1)
```

## Expected Benefits

### Data Protection
- **Automated Backups**: Daily, weekly, and monthly backup cycles
- **Multiple Storage Locations**: WSL2 FS, Windows host, and optional cloud storage
- **Data Integrity**: SQLite integrity checks and metadata validation
- **Retention Management**: Automatic cleanup of old backups

### Recovery Capabilities
- **Rapid Recovery**: 15-minute RTO for critical data
- **Point-in-Time Recovery**: Multiple backup versions available
- **Emergency Procedures**: Automated disaster recovery processes
- **Testing Framework**: Regular validation of backup and recovery procedures

### WSL2 Optimization
- **Performance**: Native WSL2 filesystem for backup storage
- **Integration**: Seamless integration with existing process management
- **Automation**: Cron-based scheduling with monitoring integration

This comprehensive backup and recovery system ensures business continuity and data protection for the HTX Trading Platform in the WSL2 environment.