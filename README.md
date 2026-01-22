# 🔥 Sentry Test Application

A comprehensive test application for Sentry error tracking and performance monitoring. This app provides endpoints to trigger various error types and test all Sentry features for both frontend (JavaScript) and backend (Python/Flask).

## Features

### Backend (Python/Flask)
- **Error Types**: Unhandled exceptions, ZeroDivisionError, KeyError, TypeError, AttributeError, IndexError, ValueError, RecursionError, HTTP errors (4xx/5xx), custom exceptions, chained exceptions
- **Performance Monitoring**: Slow endpoints, nested spans, simulated database operations, HTTP client spans
- **Context & Tags**: User context, custom contexts, tags, extra data
- **Breadcrumbs**: Automatic and manual breadcrumb trails
- **Issue Grouping**: Custom fingerprinting for error grouping
- **Scopes**: Isolated scope demonstrations
- **Release Health**: Release and environment tracking
- **User Feedback**: Feedback submission endpoint

### Frontend (JavaScript)
- **Error Types**: TypeError, ReferenceError, RangeError, URIError, unhandled promise rejections, async errors
- **Performance Monitoring**: Transactions, nested spans, slow operations
- **Session Replay**: Automatic session replay integration
- **Context & Breadcrumbs**: User context, custom contexts, manual breadcrumbs
- **Beautiful Test UI**: Dark-themed dashboard with all test buttons

## Quick Start

### Option 1: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Sentry DSN
export SENTRY_DSN="https://your-key@your-org.ingest.sentry.io/your-project-id"

# Run the app
python hello.py
```

### Option 2: Docker

```bash
# Build the image
docker build -t sentry-test .

# Run with Sentry DSN
docker run -p 5000:5000 -e SENTRY_DSN="your-dsn-here" sentry-test
```

### Option 3: Docker Compose

```bash
# Start all services (includes CouchDB)
docker-compose up

# Or with your Sentry DSN
SENTRY_DSN="your-dsn-here" docker-compose up
```

Then open http://localhost:5000 in your browser.

## Configuration

Set these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SENTRY_DSN` | Your Sentry DSN | `""` (required for backend) |
| `SENTRY_ENVIRONMENT` | Environment name | `development` |
| `SENTRY_RELEASE` | Release version | `sentry-test@1.0.0` |
| `PORT` | Server port | `5000` |
| `COUCHDB_USER` | CouchDB username | (optional) |
| `COUCHDB_PASSWORD` | CouchDB password | (optional) |

## API Endpoints

### Error Triggers
| Endpoint | Description |
|----------|-------------|
| `GET /api/errors/unhandled` | Unhandled exception |
| `GET /api/errors/division` | ZeroDivisionError |
| `GET /api/errors/key` | KeyError |
| `GET /api/errors/type` | TypeError |
| `GET /api/errors/attribute` | AttributeError |
| `GET /api/errors/index` | IndexError |
| `GET /api/errors/value` | ValueError |
| `GET /api/errors/recursion` | RecursionError |
| `GET /api/errors/http/<code>` | HTTP error (e.g., 404, 500) |
| `GET /api/errors/custom` | Custom exception with context |
| `GET /api/errors/chained` | Chained exceptions |
| `GET /api/errors/logged` | Error via logging |

### Messages
| Endpoint | Description |
|----------|-------------|
| `GET /api/messages/capture?level=info&message=text` | Capture message |
| `GET /api/messages/event` | Capture custom event |

### Performance
| Endpoint | Description |
|----------|-------------|
| `GET /api/performance/slow` | 2-second slow endpoint |
| `GET /api/performance/nested` | Nested spans demo |
| `GET /api/performance/database` | Simulated DB operations |
| `GET /api/performance/http` | Simulated HTTP calls |

### Context & Breadcrumbs
| Endpoint | Description |
|----------|-------------|
| `GET /api/breadcrumbs/trail` | Error with breadcrumb trail |
| `GET /api/context/rich` | Error with rich context |

### Fingerprinting
| Endpoint | Description |
|----------|-------------|
| `GET /api/fingerprint/custom?group=X` | Custom fingerprinted error |
| `GET /api/fingerprint/transaction?type=X` | Transaction-based fingerprint |

### Other
| Endpoint | Description |
|----------|-------------|
| `GET /api/scope/isolated` | Isolated scope demo |
| `GET /api/async/thread` | Background thread error |
| `POST /api/sensitive/scrubbed` | Sensitive data scrubbing test |
| `GET /api/health` | Health check |
| `GET /api/sentry/test` | Quick Sentry test |
| `GET /api/release/info` | Current release info |
| `POST /api/feedback/submit` | Submit user feedback |

## Frontend Usage

1. Open http://localhost:5000 in your browser
2. Enter your Sentry DSN in the input field at the top
3. Click "Initialize Sentry" to connect
4. Click any button to trigger errors/events
5. Check your Sentry dashboard to see the captured events

## Testing Checklist

Use this app to verify:

- [ ] Basic error capture (unhandled exceptions)
- [ ] Different error types are captured correctly
- [ ] Stack traces are complete and useful
- [ ] Source maps work (for JS errors)
- [ ] Performance transactions appear
- [ ] Spans show nested relationships
- [ ] User context is attached
- [ ] Custom tags appear on events
- [ ] Breadcrumbs show event trail
- [ ] Custom contexts appear
- [ ] Fingerprinting groups issues correctly
- [ ] Session Replay captures user sessions
- [ ] Release health tracking works
- [ ] Sensitive data is scrubbed
- [ ] User feedback is captured

## Original Tasks

This repo was originally a screening exercise with these tasks:

1. ✅ Make the Dockerfile work
2. ✅ Set up Docker Compose
3. Write a smoke test
4. Set up CI/CD

## Resources

- [Sentry Python SDK Docs](https://docs.sentry.io/platforms/python/)
- [Sentry JavaScript SDK Docs](https://docs.sentry.io/platforms/javascript/)
- [Sentry Flask Integration](https://docs.sentry.io/platforms/python/integrations/flask/)

## Disclaimer

This repo is adapted from https://github.com/IBM-Cloud/get-started-python/
