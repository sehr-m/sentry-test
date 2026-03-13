"""
Sentry Test Application - Flask Backend
A comprehensive test application demonstrating all Sentry features and error types.
"""

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from flask import Flask, render_template, request, jsonify, abort
import atexit
import os
import json
import logging
import random
import time
import threading

# =============================================================================
# SENTRY CONFIGURATION
# =============================================================================
# Set your Sentry DSN as an environment variable: SENTRY_DSN
# Or replace the default value below with your actual DSN

SENTRY_DSN = os.getenv("SENTRY_DSN", "https://2749c2d817b29ffda63bc190e9294cc3@sehr.ngrok.io/4510755321085952")  # Add your DSN here or set env var

# Configure logging integration
logging_integration = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[
        FlaskIntegration(),
        logging_integration,
    ],
    # Performance Monitoring
    traces_sample_rate=1.0,  # Capture 100% of transactions for testing
    profiles_sample_rate=1.0,  # Profile 100% of sampled transactions
    
    # Release tracking
    release=os.getenv("SENTRY_RELEASE", "sentry-test@1.0.0"),
    environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
    
    # Additional options
    send_default_pii=True,  # Send user data (be careful in production)
    attach_stacktrace=True,  # Attach stack traces to messages
    
    # Before send hook for filtering/enriching events
    before_send=lambda event, hint: enrich_event(event, hint),
)

def enrich_event(event, hint):
    """Hook to enrich or filter events before sending to Sentry."""
    # Add custom context
    if "extra" not in event:
        event["extra"] = {}
    event["extra"]["custom_enrichment"] = "Added by before_send hook"
    return event

# =============================================================================
# FLASK APP SETUP
# =============================================================================

app = Flask(__name__, static_url_path="")
logger = logging.getLogger(__name__)

# Optional: CouchDB setup (if available)
db_name = "mydb"
client = None
db = None

try:
    from cloudant import Cloudant
    if os.getenv("COUCHDB_USER"):
        client = Cloudant(
            os.environ["COUCHDB_USER"],
            os.environ["COUCHDB_PASSWORD"],
            url=os.getenv(
                "COUCHDB_URL", "http://{}:5984".format(os.getenv("COUCHDB_HOST", "localhost")),
            ),
            connect=True,
        )
        db = client.create_database(db_name, throw_on_exists=False)
except Exception as e:
    logger.warning(f"CouchDB not configured: {e}")

port = int(os.getenv("PORT", 5000))


# =============================================================================
# HELPER: Set User Context
# =============================================================================

@app.before_request
def set_sentry_user():
    """Set user context for all requests."""
    # In a real app, this would come from authentication
    user_id = request.headers.get("X-User-ID", "anonymous")
    sentry_sdk.set_user({
        "id": user_id,
        "email": f"{user_id}@example.com",
        "username": user_id,
        "ip_address": request.remote_addr,
    })
    
    # Add breadcrumb for the request
    sentry_sdk.add_breadcrumb(
        category="http",
        message=f"Request to {request.path}",
        level="info",
        data={"method": request.method, "url": request.url}
    )


# =============================================================================
# BASIC ROUTES
# =============================================================================

@app.route("/")
def root():
    """Serve the main test page."""
    return app.send_static_file("index.html")

@app.route("/")
def hello_world():
    1/0  # raises an error
    return "<p>Hello, World!</p>"


@app.route("/api/visitors", methods=["GET"])
def get_visitor():
    """Get all visitors from database."""
    if client and db:
        return jsonify(list(map(lambda doc: doc["name"], db)))
    else:
        return jsonify([])


@app.route("/api/visitors", methods=["POST"])
def put_visitor():
    """Add a new visitor to database."""
    user = request.json["name"]
    data = {"name": user}
    if client and db:
        my_document = db.create_document(data)
        data["_id"] = my_document["_id"]
        return jsonify(data)
    else:
        return jsonify(data)


# =============================================================================
# ERROR TESTING ENDPOINTS
# =============================================================================

@app.route("/api/errors/unhandled")
def error_unhandled():
    """Trigger an unhandled exception - the most basic error type."""
    sentry_sdk.add_breadcrumb(
        category="test",
        message="About to trigger unhandled exception",
        level="warning"
    )
    raise Exception("This is an unhandled exception for Sentry testing!")


@app.route("/api/errors/division")
def error_division():
    """Trigger a ZeroDivisionError."""
    sentry_sdk.set_tag("error_type", "division_by_zero")
    result = 1 / 0
    return jsonify({"result": result})


@app.route("/api/errors/key")
def error_key():
    """Trigger a KeyError."""
    data = {"name": "test"}
    return jsonify({"value": data["nonexistent_key"]})


@app.route("/api/errors/type")
def error_type():
    """Trigger a TypeError."""
    result = "string" + 42
    return jsonify({"result": result})


@app.route("/api/errors/attribute")
def error_attribute():
    """Trigger an AttributeError."""
    obj = None
    return jsonify({"value": obj.nonexistent_method()})


@app.route("/api/errors/index")
def error_index():
    """Trigger an IndexError."""
    my_list = [1, 2, 3]
    return jsonify({"value": my_list[100]})


@app.route("/api/errors/value")
def error_value():
    """Trigger a ValueError."""
    return jsonify({"value": int("not_a_number")})


@app.route("/api/errors/recursion")
def error_recursion():
    """Trigger a RecursionError (stack overflow)."""
    def infinite_recursion():
        return infinite_recursion()
    return jsonify({"value": infinite_recursion()})


@app.route("/api/errors/memory")
def error_memory():
    """Trigger a MemoryError (be careful with this one!)."""
    # This creates a very large list - use with caution
    giant_list = [0] * (10 ** 10)
    return jsonify({"size": len(giant_list)})


@app.route("/api/errors/http/<int:status_code>")
def error_http(status_code):
    """Trigger HTTP errors (4xx, 5xx)."""
    sentry_sdk.set_context("http_error", {
        "requested_status": status_code,
        "description": f"Intentionally triggered HTTP {status_code}"
    })
    abort(status_code)


@app.route("/api/errors/custom")
def error_custom():
    """Trigger a custom exception with extra context."""
    class CustomSentryTestError(Exception):
        pass
    
    sentry_sdk.set_context("custom_error_context", {
        "component": "error_testing",
        "severity": "high",
        "test_id": random.randint(1000, 9999)
    })
    sentry_sdk.set_tag("custom_error", "true")
    sentry_sdk.set_extra("random_data", {"key": "value", "number": 42})
    
    raise CustomSentryTestError("This is a custom error with rich context!")


@app.route("/api/errors/chained")
def error_chained():
    """Trigger chained exceptions to test exception chains."""
    try:
        try:
            raise ValueError("Original error")
        except ValueError as e:
            raise RuntimeError("Second level error") from e
    except RuntimeError as e:
        raise Exception("Third level error - the final exception") from e


@app.route("/api/errors/logged")
def error_logged():
    """Trigger an error through logging (captured by LoggingIntegration)."""
    logger.info("This is an info message (breadcrumb)")
    logger.warning("This is a warning message (breadcrumb)")
    logger.error("This is an error message - should create a Sentry event!")
    return jsonify({"status": "logged"})


# =============================================================================
# CAPTURED MESSAGES & MANUAL REPORTING
# =============================================================================

@app.route("/api/messages/capture")
def message_capture():
    """Capture a message manually (not an error)."""
    level = request.args.get("level", "info")
    message = request.args.get("message", "Test message from Sentry test app")
    
    sentry_sdk.capture_message(message, level=level)
    return jsonify({"status": "captured", "level": level, "message": message})


@app.route("/api/messages/event")
def message_event():
    """Capture a fully customized event."""
    event_id = sentry_sdk.capture_event({
        "message": "Custom event with all the bells and whistles",
        "level": "warning",
        "tags": {
            "feature": "custom_events",
            "test_type": "manual"
        },
        "extra": {
            "custom_data": {
                "items": [1, 2, 3],
                "metadata": {"source": "test_endpoint"}
            }
        },
        "fingerprint": ["custom-event-fingerprint"]
    })
    return jsonify({"status": "captured", "event_id": str(event_id)})


# =============================================================================
# PERFORMANCE MONITORING
# =============================================================================

@app.route("/api/performance/slow")
def performance_slow():
    """A slow endpoint for performance monitoring."""
    with sentry_sdk.start_span(op="test", description="Simulated slow operation"):
        time.sleep(2)  # Simulate slow operation
    return jsonify({"status": "completed", "duration": "2 seconds"})


@app.route("/api/performance/nested")
def performance_nested():
    """Endpoint with nested spans for transaction tracing."""
    with sentry_sdk.start_span(op="task", description="Parent operation") as parent:
        parent.set_tag("level", "parent")
        time.sleep(0.1)
        
        with sentry_sdk.start_span(op="subtask", description="Child operation 1") as child1:
            child1.set_tag("level", "child")
            child1.set_data("child_number", 1)
            time.sleep(0.2)
            
        with sentry_sdk.start_span(op="subtask", description="Child operation 2") as child2:
            child2.set_tag("level", "child")
            child2.set_data("child_number", 2)
            time.sleep(0.15)
            
            with sentry_sdk.start_span(op="subtask", description="Grandchild operation") as grandchild:
                grandchild.set_tag("level", "grandchild")
                time.sleep(0.1)
    
    return jsonify({"status": "completed", "spans": "nested"})


@app.route("/api/performance/database")
def performance_database():
    """Simulate database operations with spans."""
    results = []
    
    with sentry_sdk.start_span(op="db.query", description="SELECT users"):
        time.sleep(0.1)
        results.append({"query": "SELECT", "rows": 100})
    
    with sentry_sdk.start_span(op="db.query", description="INSERT record"):
        time.sleep(0.05)
        results.append({"query": "INSERT", "affected": 1})
    
    with sentry_sdk.start_span(op="db.query", description="UPDATE records"):
        time.sleep(0.08)
        results.append({"query": "UPDATE", "affected": 5})
    
    return jsonify({"operations": results})


@app.route("/api/performance/http")
def performance_http():
    """Simulate HTTP calls with spans."""
    results = []
    
    with sentry_sdk.start_span(op="http.client", description="GET /api/users") as span:
        span.set_data("http.method", "GET")
        span.set_data("http.url", "https://api.example.com/users")
        time.sleep(0.3)
        span.set_data("http.status_code", 200)
        results.append({"endpoint": "/users", "status": 200})
    
    with sentry_sdk.start_span(op="http.client", description="POST /api/data") as span:
        span.set_data("http.method", "POST")
        span.set_data("http.url", "https://api.example.com/data")
        time.sleep(0.2)
        span.set_data("http.status_code", 201)
        results.append({"endpoint": "/data", "status": 201})
    
    return jsonify({"http_calls": results})


# =============================================================================
# BREADCRUMBS
# =============================================================================

@app.route("/api/breadcrumbs/trail")
def breadcrumbs_trail():
    """Create a trail of breadcrumbs then error."""
    sentry_sdk.add_breadcrumb(
        category="navigation",
        message="User started breadcrumb test",
        level="info"
    )
    
    sentry_sdk.add_breadcrumb(
        category="user",
        message="User clicked button",
        level="info",
        data={"button_id": "test-button", "page": "main"}
    )
    
    sentry_sdk.add_breadcrumb(
        category="api",
        message="API call initiated",
        level="info",
        data={"endpoint": "/api/data", "method": "GET"}
    )
    
    sentry_sdk.add_breadcrumb(
        category="api",
        message="API response received",
        level="info",
        data={"status": 200, "size": "1.2kb"}
    )
    
    sentry_sdk.add_breadcrumb(
        category="error",
        message="About to trigger error",
        level="warning"
    )
    
    raise Exception("Error with breadcrumb trail!")


# =============================================================================
# CONTEXT & TAGS
# =============================================================================

@app.route("/api/context/rich")
def context_rich():
    """Error with rich context information."""
    # Set various contexts
    sentry_sdk.set_context("user_preferences", {
        "theme": "dark",
        "language": "en",
        "notifications": True
    })
    
    sentry_sdk.set_context("session_info", {
        "session_id": "abc123xyz",
        "started_at": "2024-01-15T10:30:00Z",
        "page_views": 42
    })
    
    sentry_sdk.set_context("feature_flags", {
        "new_ui": True,
        "beta_features": False,
        "experiment_group": "A"
    })
    
    # Set tags
    sentry_sdk.set_tag("component", "context_testing")
    sentry_sdk.set_tag("version", "2.0.0")
    sentry_sdk.set_tag("region", "us-west-2")
    
    # Set extra data
    sentry_sdk.set_extra("debug_info", {
        "memory_usage": "256MB",
        "cpu_load": 0.45,
        "active_connections": 12
    })
    
    raise Exception("Error with rich context!")


# =============================================================================
# SCOPES
# =============================================================================

@app.route("/api/scope/isolated")
def scope_isolated():
    """Demonstrate isolated scope usage."""
    # This scope only affects this specific capture
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("isolated", "true")
        scope.set_extra("scope_type", "pushed")
        scope.set_level("warning")
        scope.set_context("isolated_context", {"data": "only in this scope"})
        
        sentry_sdk.capture_message("Message with isolated scope")
    
    # This capture won't have the isolated scope data
    sentry_sdk.capture_message("Message without isolated scope")
    
    return jsonify({"status": "both messages captured"})


# =============================================================================
# ISSUE GROUPING (FINGERPRINTING)
# =============================================================================

@app.route("/api/fingerprint/custom")
def fingerprint_custom():
    """Errors with custom fingerprint for grouping."""
    group = request.args.get("group", "default")
    
    with sentry_sdk.push_scope() as scope:
        # All errors with same fingerprint will be grouped together
        scope.fingerprint = ["custom-group", group]
        try:
            raise Exception(f"Error in group: {group}")
        except Exception as e:
            event_id = sentry_sdk.capture_exception(e)
            return jsonify({"status": "error_captured", "group": group, "event_id": str(event_id)})


@app.route("/api/fingerprint/transaction")
def fingerprint_transaction():
    """Custom fingerprint based on transaction type."""
    transaction_type = request.args.get("type", "payment")
    
    with sentry_sdk.push_scope() as scope:
        scope.fingerprint = ["transaction-error", transaction_type]
        scope.set_tag("transaction_type", transaction_type)
        try:
            raise Exception(f"Transaction failed: {transaction_type}")
        except Exception as e:
            event_id = sentry_sdk.capture_exception(e)
            return jsonify({"status": "error_captured", "transaction_type": transaction_type, "event_id": str(event_id)})


# =============================================================================
# ASYNC & THREADING
# =============================================================================

@app.route("/api/async/thread")
def async_thread():
    """Error in a separate thread."""
    def thread_function():
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("thread", "background")
            time.sleep(0.5)
            raise Exception("Error from background thread!")
    
    thread = threading.Thread(target=thread_function)
    thread.start()
    
    return jsonify({"status": "thread started", "note": "Error will be captured async"})


# =============================================================================
# SENSITIVE DATA HANDLING
# =============================================================================

@app.route("/api/sensitive/scrubbed", methods=["POST"])
def sensitive_scrubbed():
    """Test sensitive data scrubbing."""
    # Sentry should scrub sensitive fields by default
    data = request.json or {}
    
    sentry_sdk.set_context("sensitive_data_test", {
        "password": "secret123",  # Should be scrubbed
        "credit_card": "4111111111111111",  # Should be scrubbed
        "ssn": "123-45-6789",  # Should be scrubbed
        "api_key": "sk_live_abc123",  # Should be scrubbed
        "safe_data": "This should appear"
    })
    
    raise Exception("Error with potentially sensitive data")


# =============================================================================
# RELEASE HEALTH
# =============================================================================

@app.route("/api/release/info")
def release_info():
    """Get current release info."""
    return jsonify({
        "release": os.getenv("SENTRY_RELEASE", "sentry-test@1.0.0"),
        "environment": os.getenv("SENTRY_ENVIRONMENT", "development"),
        "dsn_configured": bool(SENTRY_DSN)
    })


# =============================================================================
# FEEDBACK
# =============================================================================

@app.route("/api/feedback/submit", methods=["POST"])
def feedback_submit():
    """Submit user feedback for the last event."""
    data = request.json or {}
    event_id = data.get("event_id")
    
    if event_id:
        sentry_sdk.capture_user_feedback({
            "event_id": event_id,
            "name": data.get("name", "Anonymous"),
            "email": data.get("email", "anonymous@example.com"),
            "comments": data.get("comments", "No comment provided")
        })
        return jsonify({"status": "feedback submitted"})
    
    return jsonify({"error": "event_id required"}), 400


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.route("/api/health")
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "sentry_configured": bool(SENTRY_DSN),
        "database_connected": client is not None
    })


@app.route("/api/sentry/test")
def sentry_test():
    """Quick test to verify Sentry is working."""
    try:
        sentry_sdk.capture_message("Sentry test message - if you see this, Sentry is working!")
        return jsonify({
            "status": "success",
            "message": "Test message sent to Sentry"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =============================================================================
# CLEANUP
# =============================================================================

@atexit.register
def shutdown():
    if client:
        client.disconnect()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║                    SENTRY TEST APPLICATION                        ║
╠═══════════════════════════════════════════════════════════════════╣
║  Server starting on http://0.0.0.0:{port}                          ║
║  Sentry DSN: {"Configured ✓" if SENTRY_DSN else "NOT SET - Set SENTRY_DSN env var"}                           
║                                                                   ║
║  Test Endpoints:                                                  ║
║  • GET  /api/errors/*        - Trigger various errors             ║
║  • GET  /api/messages/*      - Capture messages                   ║
║  • GET  /api/performance/*   - Performance monitoring             ║
║  • GET  /api/breadcrumbs/*   - Breadcrumb trails                  ║
║  • GET  /api/context/*       - Context & tags                     ║
║  • GET  /api/fingerprint/*   - Issue grouping                     ║
║  • GET  /api/sentry/test     - Quick Sentry test                  ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=port, debug=True)
