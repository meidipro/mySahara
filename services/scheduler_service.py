"""
Scheduler Service for Automated Notifications
Sends daily summaries to all users at configured times
"""
import os
import asyncio
from datetime import datetime, time
from typing import List
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from services.supabase_client import get_supabase_client

# Import notification function
try:
    from api.notifications import send_family_daily_summary as send_summary_func
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    logger.warning("Notifications module not available for scheduler")


class SchedulerService:
    """Service for scheduling automated notifications"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.supabase = None

    async def initialize(self):
        """Initialize the scheduler service"""
        try:
            self.supabase = get_supabase_client()
            logger.info("Scheduler service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize scheduler service: {e}")

    async def send_daily_summaries_to_all_users(self):
        """
        Send daily summary notifications to all users with FCM tokens
        This runs at the scheduled time (default: 8:00 AM)
        """
        try:
            logger.info("Starting daily summary batch send...")

            # Get all users with FCM tokens
            response = self.supabase.table('users').select('id, fcm_token').not_.is_('fcm_token', 'null').execute()

            users = response.data
            logger.info(f"Found {len(users)} users with FCM tokens")

            success_count = 0
            failed_count = 0

            # Send to each user
            for user in users:
                try:
                    user_id = user['id']

                    # Use the existing notification endpoint logic
                    # Note: We're calling the function directly, not via HTTP
                    logger.info(f"Sending daily summary to user {user_id}")

                    # Import here to avoid circular dependency
                    import requests
                    backend_url = os.getenv('BACKEND_URL', 'https://mysahara.onrender.com')

                    response = requests.post(
                        f"{backend_url}/api/notifications/family-daily-summary/{user_id}",
                        timeout=30
                    )

                    if response.status_code == 200:
                        success_count += 1
                        logger.info(f"✓ Sent daily summary to user {user_id}")
                    else:
                        failed_count += 1
                        logger.warning(f"✗ Failed to send to user {user_id}: {response.text}")

                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error sending to user {user.get('id', 'unknown')}: {e}")

            logger.info(f"Daily summary batch complete: {success_count} success, {failed_count} failed")

        except Exception as e:
            logger.error(f"Error in daily summary batch: {e}")

    def start_daily_summary_job(self, hour: int = 8, minute: int = 0):
        """
        Start the daily summary job

        Args:
            hour: Hour to send (0-23), default 8 AM
            minute: Minute to send (0-59), default 0
        """
        try:
            # Add job to run daily at specified time
            self.scheduler.add_job(
                self.send_daily_summaries_to_all_users,
                CronTrigger(hour=hour, minute=minute),
                id='daily_summary',
                name='Send Daily Summary Notifications',
                replace_existing=True
            )

            logger.info(f"Daily summary job scheduled for {hour:02d}:{minute:02d} every day")

        except Exception as e:
            logger.error(f"Failed to schedule daily summary job: {e}")

    def start_vaccine_reminder_job(self):
        """
        Start vaccine reminder job
        Checks for upcoming vaccines and sends reminders
        Runs daily at 9:00 AM
        """
        try:
            self.scheduler.add_job(
                self.check_and_send_vaccine_reminders,
                CronTrigger(hour=9, minute=0),
                id='vaccine_reminders',
                name='Check and Send Vaccine Reminders',
                replace_existing=True
            )

            logger.info("Vaccine reminder job scheduled for 09:00 every day")

        except Exception as e:
            logger.error(f"Failed to schedule vaccine reminder job: {e}")

    async def check_and_send_vaccine_reminders(self):
        """Check for upcoming vaccines and send reminders"""
        try:
            logger.info("Checking for upcoming vaccine reminders...")

            from datetime import timedelta

            # Get vaccines due in 7 days, 3 days, 1 day, or today
            reminder_days = [7, 3, 1, 0]

            for days in reminder_days:
                target_date = (datetime.now() + timedelta(days=days)).date()

                # Find vaccines due on this date
                response = self.supabase.table('vaccines').select(
                    'id, user_id, vaccine_name, dose_number, total_doses, family_member_id'
                ).eq('next_due_date', target_date.isoformat()).execute()

                vaccines = response.data

                if vaccines:
                    logger.info(f"Found {len(vaccines)} vaccines due in {days} days")

                    for vaccine in vaccines:
                        await self.send_vaccine_reminder(vaccine, days)

            logger.info("Vaccine reminder check complete")

        except Exception as e:
            logger.error(f"Error checking vaccine reminders: {e}")

    async def send_vaccine_reminder(self, vaccine: dict, days_until_due: int):
        """Send reminder for a specific vaccine"""
        try:
            import requests
            backend_url = os.getenv('BACKEND_URL', 'https://mysahara.onrender.com')

            # Get family member name if applicable
            owner_name = "You"
            relationship = None

            if vaccine.get('family_member_id'):
                member_response = self.supabase.table('family_members').select(
                    'full_name, relationship'
                ).eq('id', vaccine['family_member_id']).single().execute()

                if member_response.data:
                    owner_name = member_response.data['full_name']
                    relationship = member_response.data.get('relationship')

            # Send notification
            response = requests.post(
                f"{backend_url}/api/notifications/vaccine-reminder",
                json={
                    "user_id": vaccine['user_id'],
                    "vaccine_id": vaccine['id'],
                    "owner_name": owner_name,
                    "relationship": relationship,
                    "days_until_due": days_until_due
                },
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"✓ Sent vaccine reminder for {vaccine['vaccine_name']}")
            else:
                logger.warning(f"✗ Failed to send vaccine reminder: {response.text}")

        except Exception as e:
            logger.error(f"Error sending vaccine reminder: {e}")

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def get_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()


# Global scheduler instance
_scheduler_instance = None


def get_scheduler() -> SchedulerService:
    """Get or create scheduler instance"""
    global _scheduler_instance

    if _scheduler_instance is None:
        _scheduler_instance = SchedulerService()

    return _scheduler_instance


async def initialize_scheduler():
    """Initialize and start the scheduler"""
    scheduler = get_scheduler()
    await scheduler.initialize()

    # Schedule daily summary at 8:00 AM
    scheduler.start_daily_summary_job(hour=8, minute=0)

    # Schedule vaccine reminders at 9:00 AM
    scheduler.start_vaccine_reminder_job()

    # Start the scheduler
    scheduler.start()

    logger.info("All scheduled jobs initialized")

    return scheduler
