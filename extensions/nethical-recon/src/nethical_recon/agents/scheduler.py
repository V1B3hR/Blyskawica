"""
Job Scheduler - Scheduled reconnaissance and automation

Manages recurring scans, playbook execution schedules, and time-based triggers.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4


class ScheduleType(str, Enum):
    """Types of schedules"""

    ONCE = "once"  # Run once at specific time
    INTERVAL = "interval"  # Run at fixed intervals
    CRON = "cron"  # Run on cron schedule
    DAILY = "daily"  # Run daily at specific time
    WEEKLY = "weekly"  # Run weekly on specific day
    MONTHLY = "monthly"  # Run monthly on specific day


@dataclass
class Schedule:
    """Schedule definition"""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    schedule_type: ScheduleType = ScheduleType.ONCE
    playbook_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

    # Schedule-specific fields
    run_at: Optional[datetime] = None  # For ONCE
    interval_seconds: Optional[int] = None  # For INTERVAL
    cron_expression: Optional[str] = None  # For CRON
    time_of_day: Optional[str] = None  # For DAILY (HH:MM format)
    day_of_week: Optional[int] = None  # For WEEKLY (0-6, Monday=0)
    day_of_month: Optional[int] = None  # For MONTHLY (1-31)


class JobScheduler:
    """
    Job scheduler for automated reconnaissance and playbook execution.

    Supports various scheduling patterns:
    - One-time execution
    - Recurring intervals
    - Cron-like schedules
    - Daily/weekly/monthly patterns
    """

    def __init__(self, orchestrator=None):
        self.schedules: Dict[UUID, Schedule] = {}
        self.orchestrator = orchestrator
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None

    def create_schedule(
        self,
        name: str,
        playbook_name: str,
        schedule_type: ScheduleType,
        parameters: Optional[Dict[str, Any]] = None,
        **schedule_params,
    ) -> UUID:
        """
        Create new schedule.

        Args:
            name: Schedule name
            playbook_name: Playbook to execute
            schedule_type: Type of schedule
            parameters: Playbook parameters
            **schedule_params: Schedule-specific parameters

        Returns:
            Schedule ID

        Examples:
            # Run once at specific time
            scheduler.create_schedule(
                "one_time_scan",
                "domain_recon",
                ScheduleType.ONCE,
                {"domain": "example.com"},
                run_at=datetime(2024, 1, 15, 10, 0)
            )

            # Run every 6 hours
            scheduler.create_schedule(
                "periodic_scan",
                "domain_recon",
                ScheduleType.INTERVAL,
                {"domain": "example.com"},
                interval_seconds=6*3600
            )

            # Run daily at 02:00
            scheduler.create_schedule(
                "daily_scan",
                "domain_recon",
                ScheduleType.DAILY,
                {"domain": "example.com"},
                time_of_day="02:00"
            )
        """
        schedule = Schedule(
            name=name,
            schedule_type=schedule_type,
            playbook_name=playbook_name,
            parameters=parameters or {},
            **schedule_params,
        )

        # Calculate next run time
        schedule.next_run = self._calculate_next_run(schedule)

        self.schedules[schedule.id] = schedule
        return schedule.id

    def update_schedule(self, schedule_id: UUID, **updates):
        """Update schedule parameters"""
        if schedule_id not in self.schedules:
            raise ValueError(f"Schedule {schedule_id} not found")

        schedule = self.schedules[schedule_id]

        for key, value in updates.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)

        # Recalculate next run
        schedule.next_run = self._calculate_next_run(schedule)

    def delete_schedule(self, schedule_id: UUID):
        """Delete schedule"""
        self.schedules.pop(schedule_id, None)

    def enable_schedule(self, schedule_id: UUID):
        """Enable schedule"""
        if schedule_id in self.schedules:
            self.schedules[schedule_id].enabled = True

    def disable_schedule(self, schedule_id: UUID):
        """Disable schedule"""
        if schedule_id in self.schedules:
            self.schedules[schedule_id].enabled = False

    def list_schedules(self, enabled_only: bool = False) -> List[Schedule]:
        """List all schedules"""
        schedules = list(self.schedules.values())
        if enabled_only:
            schedules = [s for s in schedules if s.enabled]
        return schedules

    def get_schedule(self, schedule_id: UUID) -> Optional[Schedule]:
        """Get schedule by ID"""
        return self.schedules.get(schedule_id)

    async def start(self):
        """Start scheduler"""
        if self._running:
            return

        self._running = True
        self._scheduler_task = asyncio.create_task(self._run_scheduler())

    async def stop(self):
        """Stop scheduler"""
        self._running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass

    async def _run_scheduler(self):
        """Main scheduler loop"""
        while self._running:
            try:
                await self._check_and_execute_schedules()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(60)

    async def _check_and_execute_schedules(self):
        """Check schedules and execute due jobs"""
        now = datetime.now(timezone.utc)

        for schedule in self.schedules.values():
            if not schedule.enabled:
                continue

            if schedule.next_run and schedule.next_run <= now:
                # Execute schedule
                await self._execute_schedule(schedule)

                # Update schedule
                schedule.last_run = now

                if schedule.schedule_type == ScheduleType.ONCE:
                    # Disable one-time schedules after execution
                    schedule.enabled = False
                    schedule.next_run = None
                else:
                    # Calculate next run for recurring schedules
                    schedule.next_run = self._calculate_next_run(schedule)

    async def _execute_schedule(self, schedule: Schedule):
        """Execute scheduled playbook"""
        if self.orchestrator:
            try:
                # Create and execute job via orchestrator
                job_id = self.orchestrator.create_job(
                    playbook_name=schedule.playbook_name,
                    parameters=schedule.parameters,
                )
                await self.orchestrator.execute_job(job_id)
            except Exception as e:
                print(f"Error executing schedule {schedule.name}: {e}")

    def _calculate_next_run(self, schedule: Schedule) -> Optional[datetime]:
        """Calculate next run time for schedule"""
        now = datetime.now(timezone.utc)

        if schedule.schedule_type == ScheduleType.ONCE:
            return schedule.run_at

        elif schedule.schedule_type == ScheduleType.INTERVAL:
            if schedule.interval_seconds:
                if schedule.last_run:
                    return schedule.last_run + timedelta(seconds=schedule.interval_seconds)
                else:
                    return now

        elif schedule.schedule_type == ScheduleType.DAILY:
            if schedule.time_of_day:
                # Parse time_of_day (HH:MM format)
                hour, minute = map(int, schedule.time_of_day.split(":"))
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                # If time already passed today, schedule for tomorrow
                if next_run <= now:
                    next_run += timedelta(days=1)

                return next_run

        elif schedule.schedule_type == ScheduleType.WEEKLY:
            if schedule.day_of_week is not None and schedule.time_of_day:
                hour, minute = map(int, schedule.time_of_day.split(":"))

                # Calculate days until next occurrence
                days_ahead = schedule.day_of_week - now.weekday()
                if days_ahead <= 0:  # Target day already passed this week
                    days_ahead += 7

                next_run = now + timedelta(days=days_ahead)
                next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)

                return next_run

        elif schedule.schedule_type == ScheduleType.MONTHLY:
            if schedule.day_of_month and schedule.time_of_day:
                hour, minute = map(int, schedule.time_of_day.split(":"))

                # Start with current month
                next_run = now.replace(
                    day=min(schedule.day_of_month, 28),  # Avoid invalid dates
                    hour=hour,
                    minute=minute,
                    second=0,
                    microsecond=0,
                )

                # If time already passed this month, go to next month
                if next_run <= now:
                    if next_run.month == 12:
                        next_run = next_run.replace(year=next_run.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=next_run.month + 1)

                return next_run

        return None
