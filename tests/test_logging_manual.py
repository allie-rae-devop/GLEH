#!/usr/bin/env python3
"""
Manual test script for structured logging.

This script tests the logging configuration without requiring
the full Flask application to be running.

Author: InfrastructureEngineer
Date: 2025-11-14
"""

import os
import sys
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Set up a test Flask app
from flask import Flask, g
from datetime import datetime
import uuid
import time

# Mock config for testing
class TestConfig:
    DEBUG = True
    SECRET_KEY = 'test-secret-key'

def test_logging_config():
    """Test logging configuration without full app context."""
    print("=" * 80)
    print("LOGGING CONFIGURATION TEST")
    print("=" * 80)
    print()

    # Create test Flask app
    app = Flask(__name__)
    app.config.from_object(TestConfig)

    print("1. Testing structlog import...")
    try:
        import structlog
        print("   ✓ structlog imported successfully")
    except ImportError as e:
        print(f"   ✗ structlog import failed: {e}")
        print()
        print("   SOLUTION: Install structlog with:")
        print("   pip install structlog")
        return False

    print()
    print("2. Testing logging_config module...")
    try:
        from src.logging_config import configure_logging
        print("   ✓ logging_config module loaded successfully")
    except ImportError as e:
        print(f"   ✗ logging_config import failed: {e}")
        return False

    print()
    print("3. Configuring structured logging...")
    try:
        log = configure_logging(app)
        print("   ✓ Logging configured successfully")
    except Exception as e:
        print(f"   ✗ Configuration failed: {e}")
        return False

    print()
    print("4. Testing log output...")
    try:
        # Test basic logging
        log.info("test_event", test_field="test_value", timestamp=datetime.utcnow().isoformat())
        print("   ✓ Basic log entry created")

        # Test with request context simulation
        request_id = str(uuid.uuid4())
        bound_log = log.bind(
            request_id=request_id,
            method="GET",
            path="/test",
            ip="127.0.0.1"
        )
        bound_log.info("request_received")
        print("   ✓ Context-bound log entry created")

        # Test error logging
        try:
            raise ValueError("Test error for logging")
        except Exception as e:
            bound_log.error("error_occurred", error_type=type(e).__name__, error_message=str(e))
            print("   ✓ Error log entry created")

    except Exception as e:
        print(f"   ✗ Logging failed: {e}")
        return False

    print()
    print("5. Testing performance...")
    try:
        start_time = time.time()
        for i in range(100):
            log.info("performance_test", iteration=i)
        elapsed_ms = (time.time() - start_time) * 1000
        avg_ms = elapsed_ms / 100

        print(f"   100 log entries in {elapsed_ms:.2f}ms (avg: {avg_ms:.3f}ms per entry)")

        if avg_ms < 1.0:
            print(f"   ✓ Performance target met (<1ms per entry)")
        else:
            print(f"   ⚠ Performance slower than target (>{avg_ms:.3f}ms per entry)")

    except Exception as e:
        print(f"   ✗ Performance test failed: {e}")
        return False

    print()
    print("=" * 80)
    print("LOGGING CONFIGURATION TEST: PASSED")
    print("=" * 80)
    print()
    print("NEXT STEPS:")
    print("1. Run the Flask application to generate real logs")
    print("2. Make some test requests (login, logout, etc.)")
    print("3. Check logs/app.log for JSON output (production mode)")
    print("4. Run log_analyzer.py to analyze logs:")
    print("   python log_analyzer.py --since 1h")
    print()

    return True


def test_log_analyzer():
    """Test log analyzer with sample data."""
    print("=" * 80)
    print("LOG ANALYZER TEST")
    print("=" * 80)
    print()

    print("1. Testing log_analyzer import...")
    try:
        from log_analyzer import LogAnalyzer
        print("   ✓ log_analyzer imported successfully")
    except ImportError as e:
        print(f"   ✗ log_analyzer import failed: {e}")
        return False

    print()
    print("2. Creating test log file...")
    try:
        # Create temporary test log file
        test_logs = [
            {
                "timestamp": "2025-11-14T08:30:45.123456Z",
                "level": "info",
                "event": "request_received",
                "request_id": "test-request-1",
                "method": "GET",
                "path": "/api/content",
                "ip": "127.0.0.1"
            },
            {
                "timestamp": "2025-11-14T08:30:45.234567Z",
                "level": "info",
                "event": "request_completed",
                "request_id": "test-request-1",
                "status": 200,
                "latency_ms": 45.23
            },
            {
                "timestamp": "2025-11-14T08:31:00.123456Z",
                "level": "info",
                "event": "user_login_attempt",
                "username": "testuser"
            },
            {
                "timestamp": "2025-11-14T08:31:00.234567Z",
                "level": "info",
                "event": "user_login_success",
                "user_id": 1,
                "username": "testuser"
            }
        ]

        import tempfile
        import json

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            for log_entry in test_logs:
                f.write(json.dumps(log_entry) + '\n')
            test_log_file = f.name

        print(f"   ✓ Test log file created: {test_log_file}")

    except Exception as e:
        print(f"   ✗ Test log creation failed: {e}")
        return False

    print()
    print("3. Testing log analyzer...")
    try:
        analyzer = LogAnalyzer(test_log_file)
        num_logs = analyzer.load_logs()
        print(f"   ✓ Loaded {num_logs} log entries")

        # Test error rate calculation
        error_stats = analyzer.calculate_error_rate()
        print(f"   ✓ Error rate: {error_stats['overall_error_rate']}%")

        # Test latency calculation
        latency_stats = analyzer.calculate_latency_percentiles()
        print(f"   ✓ p50 latency: {latency_stats['p50']}ms")

        # Test authentication analysis
        auth_stats = analyzer.analyze_authentication()
        print(f"   ✓ Login attempts: {auth_stats['login_attempts']}")

        # Clean up
        os.unlink(test_log_file)

    except Exception as e:
        print(f"   ✗ Log analyzer test failed: {e}")
        if 'test_log_file' in locals():
            os.unlink(test_log_file)
        return False

    print()
    print("=" * 80)
    print("LOG ANALYZER TEST: PASSED")
    print("=" * 80)
    print()

    return True


if __name__ == '__main__':
    print()
    print("GLEH STRUCTURED LOGGING - MANUAL TEST SUITE")
    print("=" * 80)
    print()

    success = True

    # Test 1: Logging configuration
    if not test_logging_config():
        success = False

    print()

    # Test 2: Log analyzer
    if not test_log_analyzer():
        success = False

    print()

    if success:
        print("✓ ALL TESTS PASSED")
        print()
        print("Structured logging is ready for production use.")
        print("See docs/architecture/LOGGING_ARCHITECTURE.md for details.")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        print()
        print("Please fix the issues above before deploying.")
        sys.exit(1)
