"""
GI4C Task Scheduler
Handles scheduled tasks and automation
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from models import db, ScheduledTask, Program, ImpactData
from data_processor import DataProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskScheduler:
    """Scheduler for automated tasks"""
    
    def __init__(self, app):
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.data_processor = DataProcessor()
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("Task scheduler started")
        
        # Load scheduled tasks from database
        self.load_tasks()
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Task scheduler stopped")
    
    def load_tasks(self):
        """Load tasks from database and schedule them"""
        with self.app.app_context():
            tasks = ScheduledTask.query.filter_by(is_active=True).all()
            
            for task in tasks:
                self.schedule_task(task)
    
    def schedule_task(self, task: ScheduledTask):
        """Schedule a single task"""
        try:
            # Parse cron expression
            cron_parts = task.schedule.split()
            if len(cron_parts) == 5:
                minute, hour, day, month, day_of_week = cron_parts
                
                self.scheduler.add_job(
                    func=self.execute_task,
                    trigger=CronTrigger(
                        minute=minute,
                        hour=hour,
                        day=day,
                        month=month,
                        day_of_week=day_of_week
                    ),
                    args=[task.id],
                    id=f"task_{task.id}",
                    name=task.name
                )
                
                logger.info(f"Scheduled task: {task.name}")
        except Exception as e:
            logger.error(f"Failed to schedule task {task.name}: {str(e)}")
    
    def execute_task(self, task_id: int):
        """Execute a scheduled task"""
        with self.app.app_context():
            try:
                task = ScheduledTask.query.get(task_id)
                if not task:
                    logger.error(f"Task {task_id} not found")
                    return
                
                logger.info(f"Executing task: {task.name}")
                
                # Update last run time
                task.last_run = datetime.utcnow()
                
                # Execute based on task type
                if task.task_type == 'data_sync':
                    self._execute_data_sync(task)
                elif task.task_type == 'report_gen':
                    self._execute_report_generation(task)
                elif task.task_type == 'alert':
                    self._execute_alert_check(task)
                elif task.task_type == 'backup':
                    self._execute_backup(task)
                
                db.session.commit()
                logger.info(f"Task completed: {task.name}")
                
            except Exception as e:
                logger.error(f"Task execution failed: {str(e)}")
                db.session.rollback()
    
    def _execute_data_sync(self, task: ScheduledTask):
        """Execute data synchronization"""
        logger.info("Running data synchronization")
        # This would sync data from external sources
        # For now, just log
        pass
    
    def _execute_report_generation(self, task: ScheduledTask):
        """Execute automated report generation"""
        logger.info("Generating automated report")
        
        # Generate situation report
        report = self.data_processor.generate_report('situation')
        
        # Save to database (would need Report model integration)
        logger.info(f"Report generated: {report.get('title')}")
    
    def _execute_alert_check(self, task: ScheduledTask):
        """Execute alert/check for issues"""
        logger.info("Running alert checks")
        
        # Check for anomalies in data
        # This would check KPIs, thresholds, etc.
        pass
    
    def _execute_backup(self, task: ScheduledTask):
        """Execute database backup"""
        logger.info("Running database backup")
        # This would backup the database
        pass
    
    def add_task(self, name: str, task_type: str, schedule: str):
        """Add a new scheduled task"""
        with self.app.app_context():
            task = ScheduledTask(
                name=name,
                task_type=task_type,
                schedule=schedule,
                is_active=True
            )
            db.session.add(task)
            db.session.commit()
            
            # Schedule the task
            self.schedule_task(task)
            
            return task
    
    def remove_task(self, task_id: int):
        """Remove a scheduled task"""
        with self.app.app_context():
            task = ScheduledTask.query.get(task_id)
            if task:
                # Remove from scheduler
                try:
                    self.scheduler.remove_job(f"task_{task_id}")
                except:
                    pass
                
                # Deactivate in database
                task.is_active = False
                db.session.commit()
                
                logger.info(f"Task removed: {task.name}")


# Example task schedules
EXAMPLE_TASKS = [
    {
        'name': 'Daily Data Sync',
        'task_type': 'data_sync',
        'schedule': '0 2 * * *'  # 2:00 AM daily
    },
    {
        'name': 'Weekly Report Generation',
        'task_type': 'report_gen',
        'schedule': '0 8 * * 1'  # 8:00 AM every Monday
    },
    {
        'name': 'Hourly Alert Check',
        'task_type': 'alert',
        'schedule': '0 * * * *'  # Every hour
    },
    {
        'name': 'Daily Backup',
        'task_type': 'backup',
        'schedule': '0 3 * * *'  # 3:00 AM daily
    }
]
