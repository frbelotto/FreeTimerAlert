# Integration Tests

## Overview

Integration tests verify how different FreeTimer components work together in real-world workflows. Unlike unit tests that test isolated components, integration tests validate the interaction between multiple modules.

## Structure

```
tests/integration/
├── __init__.py
├── test_integration.py     # Main integration tests
└── README.md               # This documentation
```

## Test Categories

### 1. TimerService Integration (2 tests)
Tests the integration between `TimerService` and `Timer`:
- **test_complete_timer_lifecycle_with_service**: Complete lifecycle (create → start → pause → resume → finish → reset → remove)
- **test_multiple_timers_concurrent_execution**: Multiple timers executing simultaneously

### 2. Timer With Callbacks (2 tests)
Verifies callbacks during timer lifecycle:
- **test_timer_callbacks_integration**: Callbacks are invoked at correct moments
- **test_timer_service_with_callbacks**: TimerService passes callbacks correctly

### 3. Parse Utils Integration (2 tests)
Integration of time parser with Timer:
- **test_parse_time_creates_valid_timer**: Parsed time creates valid timers
- **test_parse_time_with_timer_service**: Parser integrated with TimerService

### 4. Notifications Integration (2 tests)
Notification system:
- **test_sound_paths_are_valid**: Sound files exist and are valid
- **test_timer_notifications_integration**: Timer triggers sound and system notification

### 5. Complete User Workflow (3 tests)
Simulates complete user workflows:
- **test_complete_terminal_workflow**: Complete terminal workflow
- **test_multiple_timers_workflow**: Multiple timers management
- **test_timer_with_add_time**: Adding time to running timer

### 6. Stress Test (2 tests) - Marked as `slow`
Load and performance tests:
- **test_many_timers_sequential**: 50 sequential timers
- **test_timer_precision_under_load**: Precision with 10 concurrent timers

## Running Tests

### All integration tests
```bash
pytest tests/integration/ -v
```

### Only fast tests (exclude stress tests)
```bash
pytest tests/integration/ -v -m "not slow"
```

### Only tests marked as integration
```bash
pytest -m integration -v
```

### With coverage
```bash
pytest tests/integration/ --cov=src --cov-report=html
```

## Markers

Integration tests use pytest markers:

- `@pytest.mark.integration` - Marks all integration tests
- `@pytest.mark.slow` - Marks slow tests (stress tests)

## Features

### ✅ Real Scenarios
Tests workflows that users actually execute

### ✅ Multiple Components
Verifies interaction between 2+ modules

### ✅ Callbacks and Events
Validates notification and event system

### ✅ Concurrency
Tests multiple timers simultaneously

### ✅ Performance
Stress tests verify behavior under load

## Execution Time

- **Fast tests**: ~10-15 seconds
- **With stress tests**: ~20-25 seconds

Integration tests are slower than unit tests because:
- They wait for real timers to complete
- They test multiple components
- They include delays to simulate real usage

## Maintenance

When adding new features:

1. ✅ Write integration test if feature involves multiple modules
2. ✅ Use mocks only for external I/O (sound, system notifications)
3. ✅ Let real timers execute (do not mock)
4. ✅ Mark slow tests with `@pytest.mark.slow`
5. ✅ Document new workflows in README

## Best Practices

### ✅ DO
- Test complete workflows
- Use real timers (1-3 seconds)
- Verify final state of multiple components
- Clean up resources after tests

### ❌ DON'T
- Mock core components (Timer, TimerService)
- Create very long tests (>30s)
- Test implementation details
- Duplicate unit tests

## Contributing

To add new integration tests:

1. Identify the workflow to test
2. Create method in appropriate class
3. Use `@pytest.mark.integration`
4. If slow (>5s), add `@pytest.mark.slow`
5. Document the scenario in docstring
6. Update this README

## Coverage

Integration tests complement unit tests, focusing on:
- Integration between layers (core ↔ services ↔ interfaces)
- End-to-end workflows
- Behavior under load
- Synchronization and concurrency

**Total**: 13 integration tests (+ 162 unit tests)
