# GUI Tests Documentation

## Overview

This directory contains comprehensive unit tests for the FreeTimer GUI implementation using Tkinter. The test suite ensures reliability and maintainability of all GUI components.

## Test Structure

### Test Files

- **`conftest.py`**: Pytest fixtures for GUI testing, including Tkinter root window and service mocks
- **`test_dialogs.py`**: Tests for dialog windows (CreateTimerDialog, AddTimeDialog)
- **`test_timer_widget.py`**: Tests for individual timer widget components
- **`test_main_window.py`**: Tests for the main application window

### Test Coverage

Total: **58 unit tests** covering the GUI implementation

#### Dialog Tests (11 tests)
- Dialog initialization and setup
- Input validation (name and duration)
- Error handling and user feedback
- Dialog result handling and cancellation

#### Timer Widget Tests (25 tests)
- Widget initialization with various configurations
- Display updates (time formatting, status labels)
- Button state management (idle, running, paused states)
- Action handlers (start, pause, reset, delete)
- Notification system integration
- Cleanup and destruction

#### Main Window Tests (22 tests)
- Window initialization and layout
- Timer creation workflow
- Timer widget management (add, remove, multiple)
- Notification toggle functionality
- About and README dialogs
- Main loop execution

## Running Tests

### Run all GUI tests
```bash
python -m pytest tests/gui/ -v
```

### Run specific test file
```bash
python -m pytest tests/gui/test_timer_widget.py -v
```

### Run specific test class
```bash
python -m pytest tests/gui/test_main_window.py::TestMainWindowInitialization -v
```

### Run with coverage
```bash
python -m pytest tests/gui/ --cov=src/interfaces/gui --cov-report=html
```

## Test Patterns

### Fixtures Used
- `tk_root`: Creates and cleans up Tkinter root window
- `timer_service`: Fresh TimerService instance
- `timer_service_with_timers`: Pre-populated service with test timers
- `mock_callback`: Mock function for callback testing

### Mocking Strategy
- Use `unittest.mock.patch` for external dependencies
- Mock system notifications and sound playback
- Use `wraps` for Tkinter components that need real behavior

### Assertions
- Verify widget creation and attributes
- Check button states based on timer status
- Validate callback invocations
- Ensure proper cleanup of resources

## Key Testing Considerations

### Tkinter-Specific
1. **Widget Visibility**: Use `grid_info()` and `winfo_ismapped()` to verify layout
2. **Update Idletasks**: Call `update_idletasks()` to process pending GUI events
3. **Window Cleanup**: Always destroy created windows in fixtures
4. **Hidden Windows**: Use `withdraw()` on root window to avoid displaying during tests

### Timer Integration
1. Short durations for test timers (1-2 seconds)
2. Proper cleanup of running timers
3. Mock sound and notification systems

### Error Handling
1. Validate user input before processing
2. Show appropriate error/warning messages
3. Handle edge cases (empty inputs, duplicates, etc.)

## Best Practices

1. **Isolation**: Each test is independent and doesn't affect others
2. **Cleanup**: Fixtures ensure proper resource cleanup
3. **Descriptive Names**: Test names clearly describe what is being tested
4. **Documentation**: Each test has a docstring explaining its purpose
5. **Organization**: Tests grouped by functionality in classes

## Future Enhancements

Potential areas for additional test coverage:
- Integration tests for complete user workflows
- Performance tests for multiple simultaneous timers
- Accessibility testing for keyboard navigation
- Visual regression testing for UI consistency
- Cross-platform compatibility tests (Windows, macOS, Linux)

## Contributing

When adding new GUI features:
1. Write tests first (TDD approach)
2. Follow existing test patterns and conventions
3. Ensure all tests pass before committing
4. Update this documentation as needed
5. Maintain test coverage above 80%
