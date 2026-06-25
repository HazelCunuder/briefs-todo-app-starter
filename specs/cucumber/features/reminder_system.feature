# language: en
# encoding: utf-8

@reminder_system
Feature: Reminder System
  As a To-Do App user
  I want to configure reminders on my todos
  So that I don't forget important tasks and deadlines

  Background:
    Given the To-Do App API is running
    And the database is available
    And I am authenticated as user "alice"

  # ============================================================================
  # Deadline Reminders
  # ============================================================================

  @deadline
  Scenario: Set a deadline reminder on a todo
    Given I have a todo titled "Complete project documentation"
    When I set a deadline of "2024-12-31" on that todo
    And I configure a reminder for "1 day before" the deadline
    Then the reminder should be scheduled for "2024-12-30"
    And the reminder type should be "deadline"
    And the reminder channel should default to "in_app"

  @deadline
  Scenario: Set multiple deadline reminders on a todo
    Given I have a todo titled "Submit tax documents"
    When I set a deadline of "2024-04-15" on that todo
    And I add a reminder for "3 days before" the deadline
    And I add a reminder for "1 day before" the deadline
    And I add a reminder for "1 hour before" the deadline
    Then the todo should have 3 reminders scheduled
    And the reminder dates should be "2024-04-12", "2024-04-14", and "2024-04-15T13:00:00"

  @deadline
  Scenario: Receive reminder notification when deadline approaches
    Given I have a todo titled "Pay electricity bill" with deadline "2024-01-05"
    And I have a reminder set for "1 day before" the deadline
    And the current date is "2024-01-04"
    When the reminder scheduler runs
    Then I should receive a reminder notification
    And the notification should contain the todo title "Pay electricity bill"
    And the notification should contain the deadline "2024-01-05"

  @deadline
  Scenario: Handle overdue todos with reminders
    Given I have a todo titled "File quarterly report" with deadline "2024-01-01"
    And I have a reminder set for "on the day" of the deadline
    And the current date is "2024-01-02"
    When the reminder scheduler runs
    Then the todo should be marked as "overdue"
    And I should receive an overdue notification
    And the notification should indicate the todo is overdue by "1 day"

  # ============================================================================
  # Recurrence Patterns
  # ============================================================================

  @recurrence
  Scenario: Set a recurring reminder on a todo
    Given I have a todo titled "Weekly team meeting"
    When I set a recurrence pattern of "weekly" on that todo
    And I set the recurrence to end after "10 occurrences"
    And I set a reminder for "1 hour before" each occurrence
    Then the todo should have a recurrence configuration
    And the recurrence type should be "weekly"
    And the recurrence should have 10 scheduled instances
    And each instance should have a reminder scheduled for "1 hour before"

  @recurrence
  Scenario: Set a daily recurring reminder
    Given I have a todo titled "Daily standup"
    When I set a recurrence pattern of "daily" on that todo
    And I set the recurrence to end on "2024-12-31"
    And I set a reminder for "30 minutes before" each occurrence
    Then the todo should have daily recurrence
    And the recurrence should end on "2024-12-31"
    And reminders should be scheduled for each day at the specified time

  @recurrence
  Scenario: Set a monthly recurring reminder
    Given I have a todo titled "Pay rent"
    When I set a recurrence pattern of "monthly" on that todo
    And I set the recurrence to occur on "day 1 of each month"
    And I set a reminder for "2 days before" each occurrence
    Then the todo should have monthly recurrence
    And the recurrence should occur on the 1st of each month
    And reminders should be scheduled for the 29th/30th/31st of each month

  @recurrence
  Scenario: Set a yearly recurring reminder
    Given I have a todo titled "Annual review"
    When I set a recurrence pattern of "yearly" on that todo
    And I set the recurrence to occur on "January 1st"
    And I set a reminder for "1 week before" each occurrence
    Then the todo should have yearly recurrence
    And the recurrence should occur on January 1st each year
    And reminders should be scheduled for December 25th each year

  # ============================================================================
  # Time Window Configuration
  # ============================================================================

  @time_window
  Scenario: Configure a time window for reminder delivery
    Given I have a todo titled "Important presentation"
    When I set a deadline of "2024-03-15T14:00:00" on that todo
    And I configure a time window for reminders between "09:00" and "17:00"
    And I set a reminder for "2 hours before" the deadline
    Then the reminder should be scheduled for "2024-03-15T12:00:00"
    And the reminder should be within the time window

  @time_window
  Scenario: Adjust reminder time to fit within time window
    Given I have a todo titled "Late night task"
    When I set a deadline of "2024-03-15T02:00:00" on that todo
    And I configure a time window for reminders between "09:00" and "17:00"
    And I set a reminder for "2 hours before" the deadline
    Then the reminder should be adjusted to "2024-03-14T17:00:00"
    And the reminder should be at the end of the time window

  @time_window
  Scenario: Skip reminder if it falls outside time window
    Given I have a todo titled "Weekend task"
    When I set a deadline of "2024-03-16T10:00:00" on that todo (Saturday)
    And I configure a time window for reminders between "09:00" and "17:00" on weekdays only
    And I set a reminder for "1 day before" the deadline
    Then the reminder should be skipped
    And a warning should be logged that the reminder falls outside the time window

  # ============================================================================
  # Notification Channels
  # ============================================================================

  @notification_channel
  Scenario: Configure email notification channel
    Given I have a todo titled "Important email task"
    When I set a deadline of "2024-02-01" on that todo
    And I set a reminder for "1 day before" the deadline
    And I configure the notification channel as "email"
    And I provide my email address as "alice@example.com"
    Then the reminder should be configured for email delivery
    And the email should be sent to "alice@example.com"

  @notification_channel
  Scenario: Configure webhook notification channel
    Given I have a todo titled "Webhook task"
    When I set a deadline of "2024-02-01" on that todo
    And I set a reminder for "1 day before" the deadline
    And I configure the notification channel as "webhook"
    And I provide a webhook URL as "https://hooks.example.com/todo-reminder"
    Then the reminder should be configured for webhook delivery
    And the webhook should be called with the todo details

  @notification_channel
  Scenario: Configure multiple notification channels
    Given I have a todo titled "Critical task"
    When I set a deadline of "2024-02-01" on that todo
    And I set a reminder for "1 day before" the deadline
    And I configure notification channels as "email" and "webhook"
    And I provide my email as "alice@example.com"
    And I provide a webhook URL as "https://hooks.example.com/todo-reminder"
    Then the reminder should be configured for both channels
    And both email and webhook should be triggered when the reminder fires

  @notification_channel
  Scenario: Default to in-app notification channel
    Given I have a todo titled "Regular task"
    When I set a deadline of "2024-02-01" on that todo
    And I set a reminder for "1 day before" the deadline
    And I do not specify a notification channel
    Then the reminder should default to "in_app" notification
    And the notification should appear in the application UI

  # ============================================================================
  # Reminder Management
  # ============================================================================

  @management
  Scenario: List all reminders for a todo
    Given I have a todo titled "Task with reminders"
    And I have set 3 reminders on that todo
    When I request the list of reminders for that todo
    Then I should receive a list of 3 reminders
    And each reminder should have an id, type, when, and channel

  @management
  Scenario: Update a reminder configuration
    Given I have a todo titled "Task with reminder"
    And I have a reminder set for "1 day before" the deadline with channel "email"
    When I update the reminder to be "2 days before" the deadline
    And I change the channel to "webhook"
    Then the reminder should be updated
    And the new reminder should be for "2 days before" the deadline
    And the new channel should be "webhook"

  @management
  Scenario: Delete a reminder from a todo
    Given I have a todo titled "Task with reminder"
    And I have 2 reminders set on that todo
    When I delete one of the reminders
    Then the todo should have 1 reminder remaining
    And the deleted reminder should no longer appear in the list

  @management
  Scenario: Disable all reminders for a todo
    Given I have a todo titled "Task with reminders"
    And I have 3 reminders set on that todo
    When I disable all reminders for that todo
    Then all 3 reminders should be disabled
    And no reminder notifications should be sent

  @management
  Scenario: Enable previously disabled reminders
    Given I have a todo titled "Task with disabled reminders"
    And I have 2 reminders that are currently disabled
    When I enable the reminders for that todo
    Then both reminders should be enabled
    And reminder notifications should be sent according to their schedule

  # ============================================================================
  # Recurrence Management
  # ============================================================================

  @recurrence_management
  Scenario: Update recurrence pattern for a todo
    Given I have a todo titled "Recurring task" with weekly recurrence
    When I update the recurrence pattern to "monthly"
    And I set it to occur on "day 15 of each month"
    Then the recurrence should be updated to monthly
    And the next occurrence should be on the 15th of the current month
    And all future reminders should follow the new pattern

  @recurrence_management
  Scenario: End recurrence for a todo
    Given I have a todo titled "Recurring task" with weekly recurrence
    And it has 10 more scheduled occurrences
    When I end the recurrence
    Then the todo should no longer recur
    And no new occurrences should be created
    And existing scheduled occurrences should remain

  @recurrence_management
  Scenario: Skip a single occurrence of a recurring todo
    Given I have a todo titled "Weekly meeting" with weekly recurrence
    And the next occurrence is on "2024-01-15"
    When I skip the occurrence on "2024-01-15"
    Then the occurrence on "2024-01-15" should be marked as skipped
    And the following occurrence should still be scheduled for "2024-01-22"

  @recurrence_management
  Scenario: Modify a single occurrence of a recurring todo
    Given I have a todo titled "Weekly meeting" with weekly recurrence
    And the next occurrence is on "2024-01-15"
    When I modify the occurrence on "2024-01-15" to be on "2024-01-16"
    Then the occurrence should be rescheduled to "2024-01-16"
    And the following occurrences should remain on their original schedule
