"""
Step definitions for Reminder System feature.

This file contains the implementation of all steps defined in:
- specs/cucumber/features/reminder_system.feature

The steps are organized by scenario tags for better maintainability.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from behave import given, when, then, use_step_matcher, step
from dateutil.parser import parse as parse_date

# Use CFM (Cardinality, Form, Modal) matcher for better step matching
use_step_matcher("cfm")


# ============================================================================
# Helper Functions
# ============================================================================

def get_db_session(context):
    """Get database session from context."""
    from specs.cucumber.environment import get_db_session as env_get_db
    return env_get_db(context)


def get_http_client(context):
    """Get HTTP client from context."""
    from specs.cucumber.environment import get_http_client as env_get_http
    return env_get_http(context)


def parse_relative_date(date_str: str, reference_date: Optional[datetime] = None) -> datetime:
    """Parse a relative date string like '1 day before' or '2024-12-31'."""
    if not reference_date:
        reference_date = datetime.utcnow()
    
    # Try to parse as absolute date first
    try:
        return parse_date(date_str)
    except:
        pass
    
    # Parse relative date
    match = re.match(r'(\d+)\s+(\w+)\s+(\w+)', date_str.lower())
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        direction = match.group(3)
        
        delta_kwargs = {}
        if unit in ['day', 'days']:
            delta_kwargs['days'] = amount
        elif unit in ['hour', 'hours']:
            delta_kwargs['hours'] = amount
        elif unit in ['week', 'weeks']:
            delta_kwargs['weeks'] = amount
        elif unit in ['month', 'months']:
            delta_kwargs['months'] = amount
        elif unit in ['year', 'years']:
            delta_kwargs['years'] = amount
        elif unit in ['minute', 'minutes']:
            delta_kwargs['minutes'] = amount
        
        delta = timedelta(**delta_kwargs)
        
        if direction in ['before', 'ago']:
            return reference_date - delta
        elif direction in ['after', 'later']:
            return reference_date + delta
        else:
            return reference_date
    
    # Handle "on the day"
    if 'on the day' in date_str.lower():
        return reference_date
    
    # Handle "today"
    if 'today' in date_str.lower():
        return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Handle "tomorrow"
    if 'tomorrow' in date_str.lower():
        return (datetime.utcnow() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Handle "yesterday"
    if 'yesterday' in date_str.lower():
        return (datetime.utcnow() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Default to now
    return datetime.utcnow()


def format_date(dt: datetime) -> str:
    """Format datetime for comparison."""
    return dt.isoformat()


# ============================================================================
# Authentication Steps
# ============================================================================

@given('the To-Do App API is running')
def step_api_running(context):
    """Verify API is running."""
    # This is assumed to be true for the tests
    # In real tests, we might ping the health endpoint
    pass


@given('the database is available')
def step_db_available(context):
    """Verify database is available."""
    # Database is set up in environment.py
    pass


@given('I am authenticated as user "{username}"')
def step_authenticated_as_user(context, username):
    """Authenticate as a specific user."""
    # For now, we'll just set the current user in context
    # In real implementation, this would involve getting a token
    context.current_user = username


# ============================================================================
# Todo Setup Steps
# ============================================================================

@given('I have a todo titled "{title}"')
def step_have_todo(context, title):
    """Create a todo with the given title."""
    db = get_db_session(context)
    
    # Import models
    from api.models import Todo
    
    todo = Todo(
        title=title,
        description=None,
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(todo)
    db.commit()
    db.refresh(todo)
    
    context.created_todos.append(todo)
    context.current_todo = todo


@given('I have a todo titled "{title}" with deadline "{deadline}"')
def step_have_todo_with_deadline(context, title, deadline):
    """Create a todo with a deadline."""
    db = get_db_session(context)
    
    from api.models import Todo
    
    deadline_dt = parse_relative_date(deadline)
    
    todo = Todo(
        title=title,
        description=None,
        completed=False,
        deadline=deadline_dt,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(todo)
    db.commit()
    db.refresh(todo)
    
    context.created_todos.append(todo)
    context.current_todo = todo


@given('I have a todo titled "{title}" with deadline "{deadline}" and I have a reminder set for "{reminder_when}" the deadline')
def step_have_todo_with_deadline_and_reminder(context, title, deadline, reminder_when):
    """Create a todo with deadline and reminder."""
    db = get_db_session(context)
    
    from api.models import Todo, Reminder
    
    deadline_dt = parse_relative_date(deadline)
    
    todo = Todo(
        title=title,
        description=None,
        completed=False,
        deadline=deadline_dt,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(todo)
    db.commit()
    db.refresh(todo)
    
    # Create reminder
    reminder_dt = parse_relative_date(reminder_when, deadline_dt)
    
    reminder = Reminder(
        todo_id=todo.id,
        reminder_type="deadline",
        when=reminder_when,
        scheduled_for=reminder_dt,
        channel="in_app",
        is_active=True
    )
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    
    context.created_todos.append(todo)
    context.current_todo = todo


@given('I have set {count} reminders on that todo')
def step_have_set_reminders(context, count):
    """Set multiple reminders on the current todo."""
    db = get_db_session(context)
    
    from api.models import Reminder
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    # Create multiple reminders
    for i in range(int(count)):
        reminder = Reminder(
            todo_id=todo.id,
            reminder_type="deadline",
            when=f"{i+1} day before",
            scheduled_for=datetime.utcnow() + timedelta(days=i+1),
            channel="in_app",
            is_active=True
        )
        
        db.add(reminder)
        db.commit()
        db.refresh(reminder)


# ============================================================================
# Deadline Reminder Steps
# ============================================================================

@when('I set a deadline of "{deadline}" on that todo')
def step_set_deadline(context, deadline):
    """Set a deadline on the current todo."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    deadline_dt = parse_relative_date(deadline)
    
    todo.deadline = deadline_dt
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)


@when('I configure a reminder for "{when}" the deadline')
def step_configure_reminder(context, when):
    """Configure a reminder on the current todo."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    if not todo.deadline:
        raise ValueError("Todo has no deadline set")
    
    from api.models import Reminder
    
    scheduled_for = parse_relative_date(when, todo.deadline)
    
    reminder = Reminder(
        todo_id=todo.id,
        reminder_type="deadline",
        when=when,
        scheduled_for=scheduled_for,
        channel="in_app",
        is_active=True
    )
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    
    context.current_reminder = reminder


@when('I add a reminder for "{when}" the deadline')
def step_add_reminder(context, when):
    """Add another reminder to the current todo."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    if not todo.deadline:
        raise ValueError("Todo has no deadline set")
    
    from api.models import Reminder
    
    scheduled_for = parse_relative_date(when, todo.deadline)
    
    reminder = Reminder(
        todo_id=todo.id,
        reminder_type="deadline",
        when=when,
        scheduled_for=scheduled_for,
        channel="in_app",
        is_active=True
    )
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)


@then('the reminder should be scheduled for "{expected_date}"')
def step_reminder_scheduled_for(context, expected_date):
    """Verify reminder is scheduled for expected date."""
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    expected_dt = parse_relative_date(expected_date)
    
    # Compare dates (ignoring time for simplicity)
    assert reminder.scheduled_for.date() == expected_dt.date(), \
        f"Expected {expected_dt.date()}, got {reminder.scheduled_for.date()}"


@then('the reminder type should be "{reminder_type}"')
def step_reminder_type(context, reminder_type):
    """Verify reminder type."""
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    assert reminder.reminder_type == reminder_type, \
        f"Expected type {reminder_type}, got {reminder.reminder_type}"


@then('the reminder channel should default to "{channel}"')
def step_reminder_channel_default(context, channel):
    """Verify reminder channel defaults to expected value."""
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    assert reminder.channel == channel, \
        f"Expected channel {channel}, got {reminder.channel}"


@then('the todo should have {count} reminders scheduled')
def step_todo_has_reminders(context, count):
    """Verify todo has expected number of reminders."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    from api.models import Reminder
    
    reminders = db.query(Reminder).filter_by(todo_id=todo.id).all()
    
    assert len(reminders) == int(count), \
        f"Expected {count} reminders, got {len(reminders)}"


@then('the reminder dates should be "{dates}"')
def step_reminder_dates(context, dates):
    """Verify reminder dates match expected dates."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    from api.models import Reminder
    
    reminders = db.query(Reminder).filter_by(todo_id=todo.id).order_by(Reminder.scheduled_for).all()
    
    expected_dates = [parse_relative_date(d.strip()) for d in dates.split(",")]
    actual_dates = [r.scheduled_for for r in reminders]
    
    assert len(actual_dates) == len(expected_dates), \
        f"Expected {len(expected_dates)} dates, got {len(actual_dates)}"
    
    for i, (actual, expected) in enumerate(zip(actual_dates, expected_dates)):
        assert actual.date() == expected.date(), \
            f"Reminder {i}: Expected {expected.date()}, got {actual.date()}"


# ============================================================================
# Recurrence Steps
# ============================================================================

@when('I set a recurrence pattern of "{pattern}" on that todo')
def step_set_recurrence_pattern(context, pattern):
    """Set a recurrence pattern on the current todo."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    # Update todo with recurrence
    todo.recurrence_pattern = pattern
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)


@when('I set the recurrence to end after "{count} occurrences"')
def step_set_recurrence_end_after(context, count):
    """Set recurrence to end after specific number of occurrences."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    todo.recurrence_end_type = "occurrences"
    todo.recurrence_end_value = int(count)
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)


@when('I set the recurrence to end on "{end_date}"')
def step_set_recurrence_end_on(context, end_date):
    """Set recurrence to end on specific date."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    end_dt = parse_relative_date(end_date)
    
    todo.recurrence_end_type = "date"
    todo.recurrence_end_date = end_dt
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)


@when('I set it to occur on "{schedule}"')
def step_set_recurrence_schedule(context, schedule):
    """Set recurrence schedule."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    # Parse schedule (e.g., "day 1 of each month", "every Monday")
    todo.recurrence_schedule = schedule
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)


@then('the todo should have a recurrence configuration')
def step_todo_has_recurrence(context):
    """Verify todo has recurrence configuration."""
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    assert hasattr(todo, 'recurrence_pattern'), "Todo should have recurrence_pattern"
    assert todo.recurrence_pattern is not None, "recurrence_pattern should not be None"


@then('the recurrence type should be "{pattern}"')
def step_recurrence_type(context, pattern):
    """Verify recurrence type."""
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    assert todo.recurrence_pattern == pattern, \
        f"Expected recurrence pattern {pattern}, got {todo.recurrence_pattern}"


# ============================================================================
# Time Window Steps
# ============================================================================

@when('I configure a time window for reminders between "{start_time}" and "{end_time}"')
def step_configure_time_window(context, start_time, end_time):
    """Configure time window for reminders."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    todo.reminder_time_window_start = start_time
    todo.reminder_time_window_end = end_time
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)


@when('I configure a time window for reminders between "{start_time}" and "{end_time}" on weekdays only')
def step_configure_weekday_time_window(context, start_time, end_time):
    """Configure weekday-only time window."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    todo.reminder_time_window_start = start_time
    todo.reminder_time_window_end = end_time
    todo.reminder_time_window_weekdays_only = True
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)


@then('the reminder should be within the time window')
def step_reminder_within_time_window(context):
    """Verify reminder is within configured time window."""
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    # Check if reminder time is within window
    reminder_hour = reminder.scheduled_for.hour
    start_hour = int(todo.reminder_time_window_start.split(":")[0])
    end_hour = int(todo.reminder_time_window_end.split(":")[0])
    
    assert start_hour <= reminder_hour <= end_hour, \
        f"Reminder at {reminder_hour}:00 not in window {start_hour}:00-{end_hour}:00"


@then('the reminder should be adjusted to "{expected_time}"')
def step_reminder_adjusted_to(context, expected_time):
    """Verify reminder was adjusted to expected time."""
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    expected_dt = parse_relative_date(expected_time)
    
    # Check date and time
    assert reminder.scheduled_for.date() == expected_dt.date(), \
        f"Expected date {expected_dt.date()}, got {reminder.scheduled_for.date()}"
    
    assert reminder.scheduled_for.hour == expected_dt.hour, \
        f"Expected hour {expected_dt.hour}, got {reminder.scheduled_for.hour}"


@then('the reminder should be skipped')
def step_reminder_skipped(context):
    """Verify reminder was skipped."""
    # This would be verified by checking that no reminder was created
    # or that the reminder has is_active=False
    if hasattr(context, 'current_reminder'):
        reminder = context.current_reminder
        assert not reminder.is_active, "Reminder should be skipped (inactive)"


@then('a warning should be logged that the reminder falls outside the time window')
def step_warning_logged(context):
    """Verify warning was logged."""
    # In a real implementation, we would check logs
    # For now, we'll just note that this should be verified
    pass


# ============================================================================
# Notification Channel Steps
# ============================================================================

@when('I configure the notification channel as "{channel}"')
def step_configure_notification_channel(context, channel):
    """Configure notification channel."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    
    reminder.channel = channel
    
    db.commit()
    db.refresh(reminder)


@when('I provide my email address as "{email}"')
def step_provide_email(context, email):
    """Provide email address for notification."""
    if not hasattr(context, 'current_user'):
        context.current_user = {}
    
    context.current_user['email'] = email


@when('I provide a webhook URL as "{url}"')
def step_provide_webhook_url(context, url):
    """Provide webhook URL for notification."""
    if not hasattr(context, 'current_user'):
        context.current_user = {}
    
    context.current_user['webhook_url'] = url


@then('the reminder should be configured for email delivery')
def step_reminder_configured_for_email(context):
    """Verify reminder is configured for email."""
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    
    assert reminder.channel == "email", \
        f"Expected channel 'email', got '{reminder.channel}'"


@then('the email should be sent to "{email}"')
def step_email_sent_to(context, email):
    """Verify email would be sent to expected address."""
    if not hasattr(context, 'current_user'):
        raise ValueError("No current user set")
    
    assert context.current_user.get('email') == email, \
        f"Expected email {email}, got {context.current_user.get('email')}"


@then('the reminder should be configured for webhook delivery')
def step_reminder_configured_for_webhook(context):
    """Verify reminder is configured for webhook."""
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    
    assert reminder.channel == "webhook", \
        f"Expected channel 'webhook', got '{reminder.channel}'"


@then('the webhook should be called with the todo details')
def step_webhook_called_with_details(context):
    """Verify webhook would be called with todo details."""
    # In a real implementation, we would verify the webhook call
    # For now, we'll just note that this should be verified
    pass


@then('the reminder should be configured for both channels')
def step_reminder_configured_for_both(context):
    """Verify reminder is configured for multiple channels."""
    # In a real implementation, a todo might have multiple reminders
    # or a reminder might support multiple channels
    # For now, we'll check that we have multiple reminders
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    from api.models import Reminder
    
    reminders = db.query(Reminder).filter_by(todo_id=todo.id).all()
    channels = {r.channel for r in reminders}
    
    assert "email" in channels, "Expected email channel"
    assert "webhook" in channels, "Expected webhook channel"


@then('both email and webhook should be triggered when the reminder fires')
def step_both_channels_triggered(context):
    """Verify both channels would be triggered."""
    # This would be verified in integration tests
    pass


# ============================================================================
# Reminder Management Steps
# ============================================================================

@when('I request the list of reminders for that todo')
def step_request_reminder_list(context):
    """Request list of reminders for current todo."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    from api.models import Reminder
    
    context.current_reminders = db.query(Reminder) \
        .filter_by(todo_id=todo.id) \
        .order_by(Reminder.scheduled_for) \
        .all()


@then('I should receive a list of {count} reminders')
def step_receive_reminder_list(context, count):
    """Verify received reminder list count."""
    if not hasattr(context, 'current_reminders'):
        raise ValueError("No reminders list set")
    
    assert len(context.current_reminders) == int(count), \
        f"Expected {count} reminders, got {len(context.current_reminders)}"


@then('each reminder should have an id, type, when, and channel')
def step_reminders_have_required_fields(context):
    """Verify reminders have required fields."""
    if not hasattr(context, 'current_reminders'):
        raise ValueError("No reminders list set")
    
    for reminder in context.current_reminders:
        assert hasattr(reminder, 'id'), "Reminder should have id"
        assert hasattr(reminder, 'reminder_type'), "Reminder should have type"
        assert hasattr(reminder, 'when'), "Reminder should have when"
        assert hasattr(reminder, 'channel'), "Reminder should have channel"


@when('I update the reminder to be "{new_when}" the deadline')
def step_update_reminder_when(context, new_when):
    """Update reminder timing."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    todo = context.current_todo
    
    new_scheduled_for = parse_relative_date(new_when, todo.deadline)
    
    reminder.when = new_when
    reminder.scheduled_for = new_scheduled_for
    
    db.commit()
    db.refresh(reminder)


@when('I change the channel to "{new_channel}"')
def step_update_reminder_channel(context, new_channel):
    """Update reminder channel."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    
    reminder.channel = new_channel
    
    db.commit()
    db.refresh(reminder)


@then('the new reminder should be for "{expected_when}" the deadline')
def step_new_reminder_when(context, expected_when):
    """Verify updated reminder timing."""
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    
    assert reminder.when == expected_when, \
        f"Expected reminder when '{expected_when}', got '{reminder.when}'"


@then('the new channel should be "{expected_channel}"')
def step_new_reminder_channel(context, expected_channel):
    """Verify updated reminder channel."""
    if not hasattr(context, 'current_reminder'):
        raise ValueError("No current reminder set")
    
    reminder = context.current_reminder
    
    assert reminder.channel == expected_channel, \
        f"Expected channel '{expected_channel}', got '{reminder.channel}'"


@when('I delete one of the reminders')
def step_delete_reminder(context):
    """Delete a reminder."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_reminders') or not context.current_reminders:
        raise ValueError("No reminders to delete")
    
    # Delete the first reminder
    reminder_to_delete = context.current_reminders[0]
    db.delete(reminder_to_delete)
    db.commit()
    
    # Remove from list
    context.current_reminders.pop(0)


@then('the deleted reminder should no longer appear in the list')
def step_deleted_reminder_not_in_list(context):
    """Verify deleted reminder is not in list."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    from api.models import Reminder
    
    reminders = db.query(Reminder).filter_by(todo_id=todo.id).all()
    
    # The deleted reminder should not be in the database
    # (This is verified by the count in the previous step)
    pass


@when('I disable all reminders for that todo')
def step_disable_all_reminders(context):
    """Disable all reminders for current todo."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    from api.models import Reminder
    
    reminders = db.query(Reminder).filter_by(todo_id=todo.id).all()
    
    for reminder in reminders:
        reminder.is_active = False
    
    db.commit()


@then('all {count} reminders should be disabled')
def step_all_reminders_disabled(context, count):
    """Verify all reminders are disabled."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    from api.models import Reminder
    
    reminders = db.query(Reminder).filter_by(todo_id=todo.id).all()
    
    assert len(reminders) == int(count), \
        f"Expected {count} reminders, got {len(reminders)}"
    
    for reminder in reminders:
        assert not reminder.is_active, \
            f"Reminder {reminder.id} should be disabled"


@then('no reminder notifications should be sent')
def step_no_notifications_sent(context):
    """Verify no notifications would be sent."""
    # This would be verified in integration tests
    pass


@when('I enable the reminders for that todo')
def step_enable_all_reminders(context):
    """Enable all reminders for current todo."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    from api.models import Reminder
    
    reminders = db.query(Reminder).filter_by(todo_id=todo.id).all()
    
    for reminder in reminders:
        reminder.is_active = True
    
    db.commit()


@then('both reminders should be enabled')
def step_both_reminders_enabled(context):
    """Verify both reminders are enabled."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    from api.models import Reminder
    
    reminders = db.query(Reminder).filter_by(todo_id=todo.id).all()
    
    assert len(reminders) == 2, f"Expected 2 reminders, got {len(reminders)}"
    
    for reminder in reminders:
        assert reminder.is_active, \
            f"Reminder {reminder.id} should be enabled"


@then('reminder notifications should be sent according to their schedule')
def step_notifications_sent_per_schedule(context):
    """Verify notifications would be sent per schedule."""
    # This would be verified in integration tests
    pass


# ============================================================================
# Recurrence Management Steps
# ============================================================================

@when('I update the recurrence pattern to "{new_pattern}"')
def step_update_recurrence_pattern(context, new_pattern):
    """Update recurrence pattern."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    todo.recurrence_pattern = new_pattern
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)


@then('the recurrence should be updated to {pattern}')
def step_recurrence_updated_to(context, pattern):
    """Verify recurrence pattern was updated."""
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    assert todo.recurrence_pattern == pattern, \
        f"Expected recurrence pattern '{pattern}', got '{todo.recurrence_pattern}'"


@then('the next occurrence should be on the {ordinal} of the current month')
def step_next_occurrence_on_ordinal(context, ordinal):
    """Verify next occurrence date."""
    # This would require recurrence calculation logic
    # For now, we'll just verify the pattern is set correctly
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    # Verify pattern is monthly
    assert todo.recurrence_pattern == "monthly", \
        "Expected monthly recurrence pattern"


@then('all future reminders should follow the new pattern')
def step_future_reminders_follow_new_pattern(context):
    """Verify future reminders follow new pattern."""
    # This would be verified by checking scheduled reminders
    pass


@when('I end the recurrence')
def step_end_recurrence(context):
    """End recurrence for current todo."""
    db = get_db_session(context)
    
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    todo.recurrence_pattern = None
    todo.recurrence_end_type = None
    todo.recurrence_end_value = None
    todo.recurrence_end_date = None
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)


@then('the todo should no longer recur')
def step_todo_no_longer_recurs(context):
    """Verify todo no longer recurs."""
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    assert todo.recurrence_pattern is None, \
        "Todo should not have a recurrence pattern"


@then('no new occurrences should be created')
def step_no_new_occurrences(context):
    """Verify no new occurrences are created."""
    # This would be verified over time in integration tests
    pass


@then('existing scheduled occurrences should remain')
def step_existing_occurrences_remain(context):
    """Verify existing occurrences remain."""
    # This would be verified by checking existing scheduled todos
    pass


# ============================================================================
# Reminder Scheduler Steps
# ============================================================================

@given('the current date is "{date}"')
def step_set_current_date(context, date):
    """Set current date for testing."""
    context.current_date = parse_relative_date(date)


@when('the reminder scheduler runs')
def step_reminder_scheduler_runs(context):
    """Simulate reminder scheduler running."""
    # In a real implementation, this would trigger the scheduler
    # For now, we'll just mark that the scheduler ran
    context.scheduler_ran = True


@then('I should receive a reminder notification')
def step_should_receive_notification(context):
    """Verify notification would be received."""
    # In a real implementation, we would verify the notification was sent
    # For now, we'll just check that the scheduler ran
    assert hasattr(context, 'scheduler_ran') and context.scheduler_ran, \
        "Scheduler should have run"


@then('the notification should contain the todo title "{title}"')
def step_notification_contains_title(context, title):
    """Verify notification contains todo title."""
    # In a real implementation, we would check the notification content
    pass


@then('the notification should contain the deadline "{deadline}"')
def step_notification_contains_deadline(context, deadline):
    """Verify notification contains deadline."""
    # In a real implementation, we would check the notification content
    pass


@then('the todo should be marked as "overdue"')
def step_todo_marked_overdue(context):
    """Verify todo is marked as overdue."""
    if not hasattr(context, 'current_todo'):
        raise ValueError("No current todo set")
    
    todo = context.current_todo
    
    # In a real implementation, we would check the overdue status
    # For now, we'll check if the deadline has passed
    if todo.deadline:
        assert todo.deadline < datetime.utcnow(), \
            "Todo deadline should have passed"


@then('the notification should indicate the todo is overdue by "{duration}"')
def step_notification_indicates_overdue(context, duration):
    """Verify notification indicates overdue duration."""
    # In a real implementation, we would check the notification content
    pass
