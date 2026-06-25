# Spec Driven Development

This directory contains specifications for the To-Do App using Spec Driven Development frameworks.

## 📋 Overview

This implementation uses **2 Spec Driven Development frameworks** to define and verify application behavior:

1. **Cucumber** - Behavior-Driven Development (BDD) framework for human-readable specifications
2. **Pact** - Contract Testing framework for API consumer-provider specifications

## 🎯 Selected Features

Two features have been chosen for spec-driven implementation:

### Feature 1: Reminder System 🔔
- Configure reminders on todos with deadlines
- Support for recurrence patterns (daily, weekly, monthly)
- Time window configuration for reminder delivery
- Multiple notification channels (email, webhook, in-app)
- Handling of overdue todos

### Feature 2: Multi-user Collaboration 👥
- Share todo lists with other users
- Assign todos to specific users
- Permission model (read, write, admin)
- Invitation system
- Conflict resolution for concurrent edits

## 📁 Structure

```
specs/
├── README.md                    # This file
├── cucumber/                    # Cucumber BDD specifications
│   ├── features/                # Feature files (.feature)
│   │   ├── reminder_system.feature
│   │   └── collaboration.feature
│   ├── step_definitions/        # Step definition implementations
│   │   ├── reminder_steps.py
│   │   └── collaboration_steps.py
│   ├── conftest.py              # Pytest fixtures for Cucumber
│   └── requirements.txt         # Cucumber dependencies
│
├── pact/                       # Pact contract specifications
│   ├── contracts/              # Contract definition files
│   │   ├── reminder_contract.py
│   │   └── collaboration_contract.py
│   ├── tests/                  # Contract verification tests
│   │   ├── test_reminder_contract.py
│   │   └── test_collaboration_contract.py
│   └── requirements.txt         # Pact dependencies
│
└── workflows/                  # GitHub Actions workflows
    └── spec-verification.yml    # Spec verification CI
```

## 🚀 Quick Start

### Install Dependencies

```bash
# Install Cucumber dependencies
pip install -r specs/cucumber/requirements.txt

# Install Pact dependencies
pip install -r specs/pact/requirements.txt

# Install all spec dependencies
pip install -r specs/requirements.txt
```

### Run Specifications

```bash
# Run Cucumber specs
cd specs/cucumber
behave features/

# Run Pact contract tests
cd specs/pact
python -m pytest tests/ -v

# Run all specs
cd specs
python -m pytest cucumber/ pact/tests/ -v
```

## 📝 Frameworks

### Cucumber (BDD)

**Purpose**: Define application behavior in human-readable language

**Feature Files**: `.feature` files in Gherkin syntax

**Example**:
```gherkin
Feature: Reminder System
  As a user
  I want to set reminders on my todos
  So that I don't forget important tasks

  Scenario: Set a deadline reminder
    Given I have a todo "Complete project"
    When I set a deadline of "2024-12-31"
    And I set a reminder for "1 day before"
    Then the reminder should be scheduled for "2024-12-30"
```

**Step Definitions**: Python code that implements the steps

### Pact (Contract Testing)

**Purpose**: Define and verify API contracts between consumer and provider

**Contract Files**: Define expected request/response patterns

**Example**:
```python
# Consumer side (what the frontend expects)
def test_reminder_contract(pact):
    expected = {
        "id": 1,
        "title": "Test Todo",
        "reminder": {
            "type": "deadline",
            "when": "1 day before",
            "channel": "email"
        }
    }
    
    pact.given("a todo with reminder")
        .upon_receiving("a request to get todo with reminder")
        .with_request("GET", "/api/todos/1")
        .will_respond_with(200, body=expected)
```

## 🎯 Feature Specifications

### Feature 1: Reminder System

**Spec Files**:
- `specs/cucumber/features/reminder_system.feature` - BDD scenarios
- `specs/cucumber/step_definitions/reminder_steps.py` - Step implementations
- `specs/pact/contracts/reminder_contract.py` - API contract
- `specs/pact/tests/test_reminder_contract.py` - Contract verification

**Implementation Files**:
- `api/models.py` - Reminder model extensions
- `api/schemas.py` - Reminder schema extensions
- `api/crud.py` - Reminder CRUD operations
- `api/main.py` - Reminder API endpoints

### Feature 2: Multi-user Collaboration

**Spec Files**:
- `specs/cucumber/features/collaboration.feature` - BDD scenarios
- `specs/cucumber/step_definitions/collaboration_steps.py` - Step implementations
- `specs/pact/contracts/collaboration_contract.py` - API contract
- `specs/pact/tests/test_collaboration_contract.py` - Contract verification

**Implementation Files**:
- `api/models.py` - User, Permission, Invitation models
- `api/schemas.py` - Collaboration schema extensions
- `api/crud.py` - Collaboration CRUD operations
- `api/main.py` - Collaboration API endpoints

## ✅ Agent-Based Verification

All specifications are verified by AI agents through:

1. **Spec Review**: Agents review spec files for completeness and correctness
2. **Implementation Verification**: Agents verify that implementation matches specs
3. **Test Execution**: Agents run spec tests and verify results
4. **CI Integration**: GitHub Actions workflow runs all spec verifications

## 🔍 Verification Process

1. **Spec Definition**: Write specs in Gherkin (Cucumber) or Python (Pact)
2. **Implementation**: Implement features to match specs
3. **Agent Review**: AI agent reviews specs and implementation
4. **Test Execution**: Run spec tests
5. **CI Verification**: GitHub Actions runs all verifications

## 📊 Coverage

| Feature | Cucumber | Pact | Implementation | Tests |
|---------|----------|------|----------------|-------|
| Reminder System | ✅ | ✅ | ✅ | ✅ |
| Multi-user Collaboration | ✅ | ✅ | ✅ | ✅ |

## 📚 Resources

- [Cucumber Documentation](https://cucumber.io/docs/)
- [Pact Documentation](https://docs.pact.io/)
- [Behavior-Driven Development](https://cucumber.io/docs/bdd/)
- [Contract Testing](https://docs.pact.io/getting_started/what_is_pact)

---

*Part of the To-Do App Spec Driven Development implementation*
