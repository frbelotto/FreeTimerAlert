"""Script for manually testing and debugging the Timer class.

Run this script to observe timer behavior with detailed logging.
"""

import time
import logging
from datetime import timedelta
from pathlib import Path
from src.core.timer import Timer, TimerStatus

logging.basicConfig(level=logging.DEBUG)


def _play_sound(filename: str, block: bool = False) -> None:
    """Play sound file from Assets/Sounds directory."""
    try:
        from playsound3 import playsound

        base = Path(__file__).resolve().parent
        sound_path = str(base / "Assets" / "Sounds" / filename)
        playsound(sound_path, block=block)
    except Exception as e:
        print(f"⚠️  Could not play sound '{filename}': {e}")


def on_timer_start(timer: Timer) -> None:
    """Callback executed when timer starts."""
    print(f"🚀 Timer started! Duration: {timer.duration}")
    _play_sound("clock-start.mp3")


def on_timer_end(timer: Timer) -> None:
    """Callback executed when timer finishes."""
    print(f"✅ Timer finished! Final status: {timer.status}")
    _play_sound("timer-terminer.mp3", block=True)


def example_basic_timer() -> None:
    """Demonstrate basic timer usage."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Timer (20 seconds)")
    print("=" * 60)

    timer = Timer(duration=timedelta(seconds=20))
    timer.on_start.append(on_timer_start)
    timer.on_end.append(on_timer_end)

    print(f"Initial status: {timer.status}")
    print(f"Initial remaining: {timer.remaining}")

    timer.start()

    # Monitor timer progress printing only when whole second changes
    last_whole: int | None = None
    while timer.is_active:
        remaining_whole = int(timer.remaining.total_seconds())  # Floor to whole seconds
        if remaining_whole != last_whole:
            print(f"⏱️  Remaining: {remaining_whole:02d}s | Progress: {timer.get_progress():.1%} | Status: {timer.status}")
            last_whole = remaining_whole
        time.sleep(0.1)  # Fine-grained polling without spam

    print(f"\nFinal status: {timer.status}")


def example_pause_resume() -> None:
    """Demonstrate pause and resume functionality."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Pause and Resume (10 seconds)")
    print("=" * 60)

    timer = Timer(duration=timedelta(seconds=10))
    timer.start()

    print("Timer running...")
    time.sleep(3)

    print(f"⏸️  Pausing timer at {timer.remaining.total_seconds():.1f}s")
    timer.pause()
    remaining_at_pause = timer.remaining

    print("Paused for 2 seconds...")
    time.sleep(2)

    print(f"Remaining after pause: {timer.remaining.total_seconds():.1f}s (should be same: {remaining_at_pause.total_seconds():.1f}s)")

    print("▶️  Resuming timer...")
    timer.resume()

    time.sleep(2)

    print(f"🛑 Stopping timer at {timer.remaining.total_seconds():.1f}s")
    timer.stop()

    print(f"Final status: {timer.status}")


def example_add_time() -> None:
    """Demonstrate adding extra time to timer."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Add Extra Time (5 seconds + 3 seconds)")
    print("=" * 60)

    timer = Timer(duration=timedelta(seconds=5))
    timer.start()

    print("Timer running for 2 seconds...")
    time.sleep(2)

    print(f"Remaining before adding time: {timer.remaining.total_seconds():.1f}s")

    extra_time = timedelta(seconds=3)
    timer.add_time(extra_time)

    print(f"➕ Added {extra_time.total_seconds():.1f}s")
    print(f"Remaining after adding time: {timer.remaining.total_seconds():.1f}s")

    # Let it finish (print only integer second changes)
    last_whole: int | None = None
    while timer.is_active and timer.status == TimerStatus.RUNNING:
        remaining_whole = int(timer.remaining.total_seconds())
        if remaining_whole != last_whole:
            print(f"⏱️  Remaining: {remaining_whole:02d}s")
            last_whole = remaining_whole
        time.sleep(0.1)

    print(f"Final status: {timer.status}")


def example_reset() -> None:
    """Demonstrate timer reset functionality."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Reset Timer")
    print("=" * 60)

    duration = timedelta(seconds=8)
    timer = Timer(duration=duration)
    timer.start()

    print("Timer running for 3 seconds...")
    time.sleep(3)

    print(f"Remaining before reset: {timer.remaining.total_seconds():.1f}s")

    print("🔄 Resetting timer...")
    timer.reset()

    print(f"Status after reset: {timer.status}")
    print(f"Remaining after reset: {timer.remaining.total_seconds():.1f}s (should be {duration.total_seconds():.1f}s)")
    print(f"Is active: {timer.is_active}")


def example_multiple_callbacks() -> None:
    """Demonstrate multiple callbacks."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Multiple Callbacks")
    print("=" * 60)

    def callback_1(timer: Timer) -> None:
        print("  📢 Callback 1 executed!")

    def callback_2(timer: Timer) -> None:
        print("  📢 Callback 2 executed!")

    def callback_3(timer: Timer) -> None:
        print("  📢 Callback 3 executed!")

    timer = Timer(duration=timedelta(seconds=3))
    timer.on_start.extend([callback_1, callback_2])
    timer.on_end.append(callback_3)

    print("Starting timer with 2 on_start callbacks and 1 on_end callback...")
    timer.start()

    # Wait for completion
    while timer.is_active:
        time.sleep(0.5)

    print(f"Final status: {timer.status}")


def interactive_mode() -> None:
    """Interactive mode for manual testing."""
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE")
    print("=" * 60)
    print("\nCommands:")
    print("  start    - Start the timer")
    print("  pause    - Pause the timer")
    print("  resume   - Resume the timer")
    print("  stop     - Stop the timer")
    print("  reset    - Reset the timer")
    print("  add N    - Add N seconds to timer")
    print("  status   - Show timer status")
    print("  quit     - Exit interactive mode")
    print()

    duration = timedelta(seconds=30)
    timer = Timer(duration=duration)
    timer.on_start.append(on_timer_start)
    timer.on_end.append(on_timer_end)

    print(f"Timer created with duration: {duration.total_seconds():.0f}s\n")

    while True:
        try:
            command = input(">>> ").strip().lower()

            if command == "quit":
                if timer.is_active:
                    timer.stop()
                print("Exiting...")
                break

            elif command == "start":
                timer.start()
                print(f"Status: {timer.status}")

            elif command == "pause":
                timer.pause()
                print(f"Status: {timer.status}")

            elif command == "resume":
                timer.resume()
                print(f"Status: {timer.status}")

            elif command == "stop":
                timer.stop()
                print(f"Status: {timer.status}")

            elif command == "reset":
                timer.reset()
                print(f"Status: {timer.status}, Remaining: {timer.remaining}")

            elif command.startswith("add "):
                try:
                    seconds = int(command.split()[1])
                    timer.add_time(timedelta(seconds=seconds))
                    print(f"Added {seconds}s. Remaining: {timer.remaining}")
                except (ValueError, IndexError):
                    print("Usage: add N (where N is number of seconds)")

            elif command == "status":
                print(f"Status: {timer.status}")
                print(f"Remaining: {timer.remaining.total_seconds():.1f}s")
                print(f"Progress: {timer.get_progress():.1%}")
                print(f"Is active: {timer.is_active}")
                print(f"Running: {timer.running}")

            else:
                print("Unknown command. Type 'quit' to exit.")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Stopping timer...")
            if timer.is_active:
                timer.stop()
            break


def main() -> None:
    """Main entry point for timer debugging."""
    print("\n" + "=" * 60)
    print("TIMER DEBUG SCRIPT")
    print("=" * 60)
    print("\nSelect an option:")
    print("  1 - Basic timer (20s)")
    print("  2 - Pause and resume (10s)")
    print("  3 - Add extra time (5s + 3s)")
    print("  4 - Reset timer")
    print("  5 - Multiple callbacks")
    print("  6 - Interactive mode")
    print("  0 - Run all examples sequentially")
    print()

    try:
        choice = input("Enter option (0-6): ").strip()

        if choice == "1":
            example_basic_timer()
        elif choice == "2":
            example_pause_resume()
        elif choice == "3":
            example_add_time()
        elif choice == "4":
            example_reset()
        elif choice == "5":
            example_multiple_callbacks()
        elif choice == "6":
            interactive_mode()
        elif choice == "0":
            example_basic_timer()
            example_pause_resume()
            example_add_time()
            example_reset()
            example_multiple_callbacks()
        else:
            print("Invalid option.")

    except KeyboardInterrupt:
        print("\n\nExecution interrupted.")

    print("\n" + "=" * 60)
    print("DEBUG SESSION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
