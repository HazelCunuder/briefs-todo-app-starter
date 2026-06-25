# language: en
# encoding: utf-8

@collaboration
Feature: Multi-user Collaboration
  As a To-Do App user
  I want to collaborate with other users on todos
  So that we can work together on shared tasks and lists

  Background:
    Given the To-Do App API is running
    And the database is available
    And I am authenticated as user "alice"
    And there exists a user "bob" with email "bob@example.com"
    And there exists a user "charlie" with email "charlie@example.com"

  # ============================================================================
  # User Management
  # ============================================================================

  @user_management
  Scenario: Create a new user with avatar
    Given I provide user details:
      | username | john_doe |
      | email | john@example.com |
      | full_name | John Doe |
      | avatar_url | https://example.com/avatars/john.jpg |
    When I create a new user
    Then the user should be created successfully
    And the user should have username "john_doe"
    And the user should have email "john@example.com"
    And the user should have avatar URL "https://example.com/avatars/john.jpg"
    And the user should be active

  @user_management
  Scenario: Update user avatar
    Given I am authenticated as user "alice"
    And my current avatar URL is null
    When I update my avatar URL to "https://example.com/avatars/alice.jpg"
    Then my avatar should be updated
    And my new avatar URL should be "https://example.com/avatars/alice.jpg"

  @user_management
  Scenario: Get user profile with avatar
    Given I am authenticated as user "alice"
    And my avatar URL is "https://example.com/avatars/alice.jpg"
    When I request my user profile
    Then I should receive my user details
    And the response should include my avatar URL
    And the avatar URL should be "https://example.com/avatars/alice.jpg"

  # ============================================================================
  # List Sharing
  # ============================================================================

  @list_sharing
  Scenario: Create a shared todo list
    Given I am authenticated as user "alice"
    When I create a new todo list named "Team Projects"
    And I set the list visibility to "shared"
    Then the list should be created
    And the list should have name "Team Projects"
    And the list should be marked as shared
    And I should be the owner of the list

  @list_sharing
  Scenario: Share a list with another user
    Given I am authenticated as user "alice"
    And I have a todo list named "Team Projects"
    And user "bob" exists
    When I share the "Team Projects" list with user "bob"
    And I grant "read" permission
    Then user "bob" should have access to the "Team Projects" list
    And user "bob" should have "read" permission on the list
    And user "bob" should be able to view todos in the list

  @list_sharing
  Scenario: Share a list with multiple users with different permissions
    Given I am authenticated as user "alice"
    And I have a todo list named "Team Projects"
    And user "bob" exists
    And user "charlie" exists
    When I share the "Team Projects" list with user "bob" with "write" permission
    And I share the "Team Projects" list with user "charlie" with "read" permission
    Then user "bob" should have "write" permission on the list
    And user "charlie" should have "read" permission on the list
    And user "bob" should be able to create todos in the list
    And user "charlie" should only be able to view todos in the list

  @list_sharing
  Scenario: Revoke access to a shared list
    Given I am authenticated as user "alice"
    And I have a todo list named "Team Projects"
    And user "bob" has "read" access to the list
    When I revoke user "bob"'s access to the "Team Projects" list
    Then user "bob" should no longer have access to the list
    And user "bob" should not be able to view todos in the list

  @list_sharing
  Scenario: List all users with access to a shared list
    Given I am authenticated as user "alice"
    And I have a todo list named "Team Projects"
    And user "bob" has "write" access to the list
    And user "charlie" has "read" access to the list
    When I request the list of users with access to "Team Projects"
    Then I should receive a list of 3 users (alice, bob, charlie)
    And the list should show alice as owner
    And the list should show bob with "write" permission
    And the list should show charlie with "read" permission

  # ============================================================================
  # Todo Assignment
  # ============================================================================

  @todo_assignment
  Scenario: Assign a todo to another user
    Given I am authenticated as user "alice"
    And I have a todo titled "Review documentation"
    And user "bob" exists
    When I assign the todo "Review documentation" to user "bob"
    Then the todo should be assigned to user "bob"
    And the todo should show "bob" as the assignee
    And user "bob" should see the todo in their assigned todos

  @todo_assignment
  Scenario: Assign a todo to multiple users
    Given I am authenticated as user "alice"
    And I have a todo titled "Team brainstorming"
    And user "bob" exists
    And user "charlie" exists
    When I assign the todo "Team brainstorming" to users "bob" and "charlie"
    Then the todo should have 2 assignees
    And both "bob" and "charlie" should see the todo in their assigned todos

  @todo_assignment
  Scenario: Reassign a todo from one user to another
    Given I am authenticated as user "alice"
    And I have a todo titled "Code review" assigned to user "bob"
    And user "charlie" exists
    When I reassign the todo "Code review" from "bob" to "charlie"
    Then the todo should no longer be assigned to "bob"
    And the todo should be assigned to "charlie"
    And "bob" should no longer see the todo in their assigned todos
    And "charlie" should see the todo in their assigned todos

  @todo_assignment
  Scenario: Unassign a todo from all users
    Given I am authenticated as user "alice"
    And I have a todo titled "General task" assigned to user "bob"
    When I unassign the todo "General task"
    Then the todo should have no assignees
    And "bob" should no longer see the todo in their assigned todos

  @todo_assignment
  Scenario: View todos assigned to me
    Given I am authenticated as user "bob"
    And user "alice" has assigned me 3 todos
    When I request my assigned todos
    Then I should receive a list of 3 todos
    And each todo should have me as the assignee

  # ============================================================================
  # Permission Model
  # ============================================================================

  @permission_model
  Scenario: Owner can perform all actions on their list
    Given I am authenticated as user "alice"
    And I have a todo list named "My List"
    And the list contains 3 todos
    When I perform the following actions on "My List":
      | action | expected_result |
      | view list | success |
      | create todo | success |
      | update todo | success |
      | delete todo | success |
      | delete list | success |
      | share list | success |
    Then all actions should succeed

  @permission_model
  Scenario: User with write permission can modify todos
    Given I am authenticated as user "bob"
    And user "alice" has shared a list "Team Projects" with me with "write" permission
    And the list contains a todo "Fix bug"
    When I perform the following actions on the "Team Projects" list:
      | action | expected_result |
      | view list | success |
      | create todo | success |
      | update todo | success |
      | delete todo | success |
      | delete list | failure |
      | share list | failure |
    Then the allowed actions should succeed
    And the disallowed actions should fail with permission error

  @permission_model
  Scenario: User with read permission can only view todos
    Given I am authenticated as user "charlie"
    And user "alice" has shared a list "Team Projects" with me with "read" permission
    And the list contains a todo "Fix bug"
    When I perform the following actions on the "Team Projects" list:
      | action | expected_result |
      | view list | success |
      | view todo | success |
      | create todo | failure |
      | update todo | failure |
      | delete todo | failure |
      | delete list | failure |
      | share list | failure |
    Then only view actions should succeed
    And all modification actions should fail with permission error

  @permission_model
  Scenario: User without access cannot view or modify list
    Given I am authenticated as user "charlie"
    And user "alice" has a private list "Private List"
    And I do not have access to "Private List"
    When I try to perform any action on "Private List":
      | action |
      | view list |
      | view todo |
      | create todo |
      | update todo |
      | delete todo |
    Then all actions should fail with access denied error

  @permission_model
  Scenario: Admin user can perform all actions on any list
    Given I am authenticated as an admin user
    And user "alice" has a private list "Private List"
    When I perform the following actions on "Private List":
      | action | expected_result |
      | view list | success |
      | create todo | success |
      | update todo | success |
      | delete todo | success |
      | delete list | success |
    Then all actions should succeed due to admin privileges

  # ============================================================================
  # Invitation System
  # ============================================================================

  @invitation_system
  Scenario: Send an invitation to share a list
    Given I am authenticated as user "alice"
    And I have a todo list named "Team Projects"
    And user "bob" exists with email "bob@example.com"
    When I send an invitation to user "bob" to join "Team Projects" with "write" permission
    Then an invitation should be created
    And the invitation should be for user "bob"
    And the invitation should be for list "Team Projects"
    And the invitation should have "write" permission
    And the invitation status should be "pending"

  @invitation_system
  Scenario: Accept an invitation to join a list
    Given I am authenticated as user "bob"
    And user "alice" has sent me an invitation to join "Team Projects" with "write" permission
    And the invitation status is "pending"
    When I accept the invitation
    Then the invitation status should be updated to "accepted"
    And I should have "write" access to "Team Projects"
    And I should be able to view and create todos in the list

  @invitation_system
  Scenario: Reject an invitation to join a list
    Given I am authenticated as user "bob"
    And user "alice" has sent me an invitation to join "Team Projects"
    And the invitation status is "pending"
    When I reject the invitation
    Then the invitation status should be updated to "rejected"
    And I should not have access to "Team Projects"

  @invitation_system
  Scenario: Cancel a sent invitation
    Given I am authenticated as user "alice"
    And I have sent an invitation to user "bob" to join "Team Projects"
    And the invitation status is "pending"
    When I cancel the invitation
    Then the invitation should be deleted
    And user "bob" should not receive the invitation

  @invitation_system
  Scenario: List all pending invitations
    Given I am authenticated as user "bob"
    And user "alice" has sent me 2 invitations
    And user "charlie" has sent me 1 invitation
    When I request my pending invitations
    Then I should receive a list of 3 invitations
    And each invitation should have the sender, list name, and permission

  @invitation_system
  Scenario: Resend an expired invitation
    Given I am authenticated as user "alice"
    And I have sent an invitation to user "bob" that expired 7 days ago
    When I resend the invitation
    Then a new invitation should be created
    And the new invitation should have a new expiration date
    And user "bob" should receive the new invitation

  # ============================================================================
  # Conflict Resolution
  # ============================================================================

  @conflict_resolution
  Scenario: Handle concurrent edits with optimistic locking
    Given I am authenticated as user "alice"
    And user "bob" is authenticated
    And we both have access to the same todo "Fix critical bug"
    And the todo has version "1"
    When I load the todo and get version "1"
    And user "bob" loads the todo and gets version "1"
    And user "bob" updates the todo title to "Fix critical bug - urgent" and submits with version "1"
    And the update is successful with new version "2"
    And I update the todo description and submit with version "1"
    Then my update should fail with a conflict error
    And the error should indicate that the todo has been modified by another user
    And the current version should be "2"

  @conflict_resolution
  Scenario: Resolve conflict by merging changes
    Given I am authenticated as user "alice"
    And user "bob" is authenticated
    And we both have access to the same todo "Document API"
    And the todo has version "1"
    When I load the todo and get version "1"
    And user "bob" loads the todo and gets version "1"
    And user "bob" updates the todo title to "Document API v2" and submits with version "1"
    And the update is successful with new version "2"
    And I receive a conflict error when trying to update
    And I fetch the latest version of the todo
    And I merge my changes (adding description) with the latest version
    And I submit the merged changes with version "2"
    Then my update should succeed
    And the todo should have the new title "Document API v2"
    And the todo should have my added description
    And the new version should be "3"

  @conflict_resolution
  Scenario: Use last-write-wins for non-critical conflicts
    Given I am authenticated as user "alice"
    And user "bob" is authenticated
    And we both have access to the same todo "Low priority task"
    And the todo has version "1"
    And the conflict resolution strategy is set to "last_write_wins"
    When I load the todo and get version "1"
    And user "bob" loads the todo and gets version "1"
    And user "bob" updates the todo and submits with version "1"
    And the update is successful with new version "2"
    And I update the todo and submit with version "1"
    Then my update should succeed with last-write-wins strategy
    And my changes should overwrite user "bob"'s changes
    And the new version should be "3"

  @conflict_resolution
  Scenario: Lock a todo for exclusive editing
    Given I am authenticated as user "alice"
    And user "bob" is authenticated
    And we both have access to the same todo "Critical task"
    When I lock the todo for editing
    Then the todo should be marked as locked
    And I should be the locker
    And user "bob" should not be able to edit the todo
    And user "bob" should receive a locked error when trying to edit

  @conflict_resolution
  Scenario: Release a lock on a todo
    Given I am authenticated as user "alice"
    And I have locked the todo "Critical task" for editing
    And user "bob" cannot edit the todo
    When I release the lock on the todo
    Then the todo should be unlocked
    And user "bob" should be able to edit the todo

  @conflict_resolution
  Scenario: Automatic lock expiration
    Given I am authenticated as user "alice"
    And I have locked the todo "Critical task" for editing
    And the lock has a timeout of 30 minutes
    And 31 minutes have passed since the lock was acquired
    When user "bob" tries to edit the todo
    Then the lock should have expired automatically
    And user "bob" should be able to edit the todo
    And a new lock should be acquired by user "bob"

  # ============================================================================
  # Avatar Display
  # ============================================================================

  @avatar_display
  Scenario: Display assignee avatar on todo
    Given I am authenticated as user "alice"
    And I have a todo titled "Review code" assigned to user "bob"
    And user "bob" has an avatar URL "https://example.com/avatars/bob.jpg"
    When I view the todo "Review code"
    Then the todo should display the assignee information
    And the assignee should be "bob"
    And the assignee avatar URL should be "https://example.com/avatars/bob.jpg"

  @avatar_display
  Scenario: Display multiple assignee avatars on todo
    Given I am authenticated as user "alice"
    And I have a todo titled "Team task" assigned to users "bob" and "charlie"
    And user "bob" has avatar URL "https://example.com/avatars/bob.jpg"
    And user "charlie" has avatar URL "https://example.com/avatars/charlie.jpg"
    When I view the todo "Team task"
    Then the todo should display 2 assignees
    And the first assignee should be "bob" with avatar "https://example.com/avatars/bob.jpg"
    And the second assignee should be "charlie" with avatar "https://example.com/avatars/charlie.jpg"

  @avatar_display
  Scenario: Display default avatar for users without custom avatar
    Given I am authenticated as user "alice"
    And I have a todo titled "New user task" assigned to user "diana"
    And user "diana" does not have a custom avatar
    When I view the todo "New user task"
    Then the todo should display the assignee information
    And the assignee should be "diana"
    And the assignee should have a default avatar based on their username

  @avatar_display
  Scenario: Display owner avatar on shared list
    Given I am authenticated as user "bob"
    And user "alice" has shared a list "Team Projects" with me
    And user "alice" has avatar URL "https://example.com/avatars/alice.jpg"
    When I view the "Team Projects" list
    Then the list should display the owner information
    And the owner should be "alice"
    And the owner avatar URL should be "https://example.com/avatars/alice.jpg"
