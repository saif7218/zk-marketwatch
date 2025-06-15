import logging
import schedule
import time
from threading import Thread
from config import settings

logger = logging.getLogger('Scheduler')

SCHEDULE_TIME = getattr(settings, 'SCHEDULE_TIME', '08:00')

class SchedulerAgent:
    def __init__(self, orchestrator_func):
        self.orchestrator_func = orchestrator_func
        self.thread = None

    def schedule_daily_run(self):
        schedule.every().day.at(SCHEDULE_TIME).do(self.orchestrator_func)
        logger.info(f"Scheduled daily run at {SCHEDULE_TIME}")

    def start_scheduler(self):
        def run():
            logger.info("Starting scheduler...")
            while True:
                schedule.run_pending()
                time.sleep(60)
        self.thread = Thread(target=run, daemon=True)
        self.thread.start()
