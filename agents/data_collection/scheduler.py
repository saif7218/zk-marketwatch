"""
Smart scheduler for data collection jobs.
Handles job scheduling, retries, and error tracking.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from .collector import collect_data, save_data

class SmartScheduler:
    def __init__(self, config_path: str, output_path: str = "data/raw"):
        """
        Initialize scheduler with configuration.
        
        Args:
            config_path: Path to scheduler config JSON
            output_path: Directory to save collected data
        """
        self.output_path = output_path
        self.config = self._load_config(config_path)
        self.scheduler = BackgroundScheduler()
        self.error_counts: Dict[str, int] = {}
        
        # Configure error handling
        self.scheduler.add_listener(self._handle_job_event, 
                                  EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
        
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load and validate scheduler configuration."""
        try:
            with open(path) as f:
                config = json.load(f)
                
            required = ["jobs", "retry_limit", "backoff_base"]
            if not all(k in config for k in required):
                raise ValueError(f"Missing required config keys: {required}")
                
            return config
            
        except Exception as e:
            logging.error(f"Failed to load scheduler config: {str(e)}")
            raise
            
    def _handle_job_event(self, event):
        """Handle job execution events for error tracking."""
        job_id = event.job_id
        
        if event.code == EVENT_JOB_ERROR:
            self.error_counts[job_id] = self.error_counts.get(job_id, 0) + 1
            retries = self.error_counts[job_id]
            
            if retries <= self.config["retry_limit"]:
                # Calculate exponential backoff
                delay = self.config["backoff_base"] ** (retries - 1)
                next_run = datetime.now() + timedelta(minutes=delay)
                
                logging.warning(
                    f"Job {job_id} failed, retry {retries}/{self.config['retry_limit']} "
                    f"scheduled for {next_run}"
                )
                
                # Reschedule with backoff
                self.scheduler.modify_job(
                    job_id,
                    next_run_time=next_run
                )
            else:
                logging.error(f"Job {job_id} failed after {retries} retries, disabled")
                self.scheduler.remove_job(job_id)
                
        elif event.code == EVENT_JOB_EXECUTED:
            # Reset error count on successful execution
            self.error_counts.pop(job_id, None)
            
    def add_collection_job(self, 
                          competitor: str,
                          category: str,
                          schedule: Dict[str, Any]) -> Optional[str]:
        """
        Add a new collection job to the scheduler.
        
        Args:
            competitor: Competitor name
            category: Product category
            schedule: Schedule configuration with type and params
            
        Returns:
            Job ID if successfully added, None otherwise
        """
        try:
            job_id = f"{competitor}_{category}"
            
            # Create trigger based on schedule type
            if schedule["type"] == "cron":
                trigger = CronTrigger(**schedule["params"])
            elif schedule["type"] == "interval":
                trigger = IntervalTrigger(**schedule["params"])
            else:
                raise ValueError(f"Invalid schedule type: {schedule['type']}")
                
            # Add job with retry handling
            self.scheduler.add_job(
                func=self._run_collection,
                trigger=trigger,
                args=[competitor, category],
                id=job_id,
                name=f"Collect {competitor}/{category}",
                replace_existing=True
            )
            
            logging.info(f"Added collection job: {job_id}")
            return job_id
            
        except Exception as e:
            logging.error(f"Failed to add collection job: {str(e)}")
            return None
            
    def _run_collection(self, competitor: str, category: str):
        """Execute collection job with output handling."""
        data = collect_data(competitor, category)
        if data:
            save_data(data, self.output_path, competitor, category)
            
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logging.info("Scheduler started")
            
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logging.info("Scheduler stopped")
            
    def get_jobs(self):
        """Get list of scheduled jobs."""
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time
            }
            for job in self.scheduler.get_jobs()
        ]
