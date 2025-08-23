"""
Scheduler service for background tasks
"""

import logging
from typing import Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from core.config import settings

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for scheduling background tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped")
    
    def add_sync_htx_job(self, func, **kwargs):
        """Add HTX data sync job"""
        self.scheduler.add_job(
            func,
            CronTrigger(hour='*/1'),  # Every hour
            id='sync_htx_data',
            name='Sync HTX Data',
            **kwargs
        )
        logger.info("Added HTX sync job")
    
    def add_sync_3commas_job(self, func, **kwargs):
        """Add 3Commas data sync job"""
        self.scheduler.add_job(
            func,
            CronTrigger(minute='*/30'),  # Every 30 minutes
            id='sync_3commas_data',
            name='Sync 3Commas Data',
            **kwargs
        )
        logger.info("Added 3Commas sync job")
    
    def add_cleanup_job(self, func, **kwargs):
        """Add cleanup job"""
        self.scheduler.add_job(
            func,
            CronTrigger(hour=2, minute=0),  # Daily at 2 AM
            id='cleanup_old_data',
            name='Cleanup Old Data',
            **kwargs
        )
        logger.info("Added cleanup job")
    
    def get_jobs(self) -> Dict[str, Any]:
        """Get all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return {
            'scheduler_running': self.is_running,
            'jobs': jobs
        }
