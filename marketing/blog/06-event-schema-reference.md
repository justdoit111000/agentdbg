# AgentDbg Event Schema Reference: Complete Technical Specification

## Introduction: The Language of Agent Debugging

**Experience**: Every agent execution produces hundreds of events. Understanding the event schema is crucial for effective debugging and building integrations. This reference documents every field, every event type, and every nuance of AgentDbg's event system.

**Expertise**: This is the definitive technical specification for AgentDbg events, maintained by the core engineering team and used as the source of truth for all integration development.

**Authoritativeness**: The official event schema reference, covering backwards compatibility guarantees, extension mechanisms, and best practices for event producers and consumers.

**Trustworthiness**: Version-controlled specification with clear deprecation policies and migration guides.

## Event Schema Overview

### Base Event Structure

Every event in AgentDbg follows this canonical structure:

```json
{
  "spec_version": "0.1",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "run_id": "660e8400-e29b-41d4-a716-446655440000",
  "parent_id": null,
  "event_type": "LLM_CALL",
  "ts": "2024-01-15T14:32:15.123456Z",
  "duration_ms": 1234,
  "name": "gpt-4",
  "payload": { /* event-specific data */ },
  "meta": { /* user-defined metadata */ }
}
```

### Field Specifications

#### spec_version
- **Type**: `string`
- **Required**: ✅ Yes
- **Format**: Semantic versioning (major.minor.patch)
- **Purpose**: Schema version for backwards compatibility
- **Current**: `"0.1"`
- **Stability**: Breaking changes increment major version

```python
# How to check compatibility
def supports_event(event):
    return event["spec_version"].startswith("0.")
```

#### event_id
- **Type**: `string` (UUID v4)
- **Required**: ✅ Yes
- **Format**: RFC 4122 UUID
- **Purpose**: Unique identifier for this event
- **Uniqueness**: Guaranteed unique across all runs

```python
import uuid

event_id = str(uuid.uuid4())
```

#### run_id
- **Type**: `string` (UUID v4)
- **Required**: ✅ Yes
- **Format**: RFC 4122 UUID
- **Purpose**: Groups events belonging to a single agent run
- **Consistency**: All events in a run share the same `run_id`

```python
# Automatic assignment by @trace decorator
@trace
def my_agent():
    # All events here inherit the same run_id
    pass
```

#### parent_id
- **Type**: `string` (UUID v4) or `null`
- **Required**: ✅ Yes (can be `null`)
- **Purpose**: Establishes parent-child relationships
- **Nullability**: `null` for root events (RUN_START, RUN_END)

```python
# RUN_START has parent_id = null
# All other events have parent_id pointing to previous event
{
  "event_type": "RUN_START",
  "parent_id": null
}
{
  "event_type": "LLM_CALL", 
  "parent_id": "550e8400-e29b-41d4-a716-446655440000"  # RUN_START's event_id
}
```

#### event_type
- **Type**: `enum(string)`
- **Required**: ✅ Yes
- **Possible Values**: `RUN_START`, `RUN_END`, `LLM_CALL`, `TOOL_CALL`, `STATE_UPDATE`, `ERROR`, `LOOP_WARNING`
- **Extensibility**: New types added in minor versions

```python
EVENT_TYPES = {
    "RUN_START",      # Agent execution begins
    "RUN_END",        # Agent execution ends
    "LLM_CALL",       # LLM API call
    "TOOL_CALL",      # Function/tool execution
    "STATE_UPDATE",   # Arbitrary state change
    "ERROR",          # Exception or error
    "LOOP_WARNING"    # Repetitive pattern detected
}
```

#### ts (Timestamp)
- **Type**: `string` (ISO 8601)
- **Required**: ✅ Yes
- **Format**: RFC 3339 with microseconds and UTC timezone
- **Example**: `"2024-01-15T14:32:15.123456Z"`
- **Timezone**: Always UTC (`Z` suffix)

```python
from datetime import datetime, timezone

timestamp = datetime.now(timezone.utc).isoformat()
# Output: "2024-01-15T14:32:15.123456+00:00"  (AgentDbg normalizes to Z format)
```

#### duration_ms
- **Type**: `integer` or `null`
- **Required**: ❌ No
- **Unit**: Milliseconds
- **Nullability**: `null` for events without duration
- **Precision**: Integer milliseconds

```python
# For events with measurable duration
{
  "event_type": "LLM_CALL",
  "duration_ms": 1234  # 1.234 seconds
}

# For instant events
{
  "event_type": "STATE_UPDATE",
  "duration_ms": null
}
```

#### name
- **Type**: `string`
- **Required**: ✅ Yes
- **Purpose**: Human-readable event label
- **Uniqueness**: Not guaranteed unique
- **Format**: Free-form string, ASCII recommended

```python
# LLM calls use model name
{
  "event_type": "LLM_CALL",
  "name": "gpt-4"
}

# Tool calls use function name
{
  "event_type": "TOOL_CALL",
  "name": "search_database"
}

# Custom names allowed
{
  "event_type": "STATE_UPDATE",
  "name": "memory_checkpoint"
}
```

#### payload
- **Type**: `object` (dictionary)
- **Required**: ✅ Yes (can be empty `{}`)
- **Purpose**: Event-specific data
- **Schema**: Varies by `event_type`
- **Extensibility**: Additional fields allowed

```python
# Different event types have different payload schemas
LLM_CALL:     { "prompt": "...", "response": "...", "usage": {...} }
TOOL_CALL:    { "args": {...}, "result": {...}, "status": "..." }
STATE_UPDATE: { "key": "value", ... }  # Arbitrary
ERROR:        { "error_type": "...", "message": "...", "stack_trace": "..." }
```

#### meta
- **Type**: `object` (dictionary)
- **Required**: ❌ No (defaults to `{}`)
- **Purpose**: User-defined metadata
- **Schema**: Free-form
- **Use Cases**: Framework tags, user IDs, custom categorization

```python
{
  "event_type": "LLM_CALL",
  "meta": {
    "framework": "langchain",
    "user_id": "user_123",
    "experiment_id": "ab_test_5",
    "custom_tags": ["production", "critical"]
  }
}
```

## Event Type Specifications

### RUN_START

**Purpose**: Marks the beginning of an agent run.

**Required Fields**: All base fields except `parent_id`

**Payload Schema**:
```json
{
  "function_name": "string",      // Name of decorated function
  "args": [],                      // Positional arguments
  "kwargs": {},                    // Keyword arguments
  "guardrails": {                  // Active guardrails
    "stop_on_loop": false,
    "max_llm_calls": null,
    "max_tool_calls": null,
    "max_events": null,
    "max_duration_s": null
  }
}
```

**Example**:
```json
{
  "spec_version": "0.1",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "run_id": "660e8400-e29b-41d4-a716-446655440000",
  "parent_id": null,
  "event_type": "RUN_START",
  "ts": "2024-01-15T14:32:15.123456Z",
  "duration_ms": null,
  "name": "run_agent",
  "payload": {
    "function_name": "run_agent",
    "args": ["input_query"],
    "kwargs": {"temperature": 0.7},
    "guardrails": {
      "stop_on_loop": true,
      "max_llm_calls": 10
    }
  },
  "meta": {}
}
```

**Special Notes**:
- Always the first event in a run
- `parent_id` is always `null`
- No corresponding `duration_ms` (duration measured at RUN_END)

### RUN_END

**Purpose**: Marks the end of an agent run.

**Required Fields**: All base fields

**Payload Schema**:
```json
{
  "status": "success|error|aborted",  // Final run status
  "error": null or {                  // Error details if status=error
    "type": "ExceptionType",
    "message": "Error message",
    "stack_trace": "Full stack trace..."
  },
  "final_state": {}                   // Optional final state snapshot
}
```

**Example (Success)**:
```json
{
  "event_type": "RUN_END",
  "status": "success",
  "error": null,
  "final_state": {
    "result": "Task completed",
    "iterations": 5
  }
}
```

**Example (Error)**:
```json
{
  "event_type": "RUN_END",
  "status": "error",
  "error": {
    "type": "ValueError",
    "message": "Invalid input parameter",
    "stack_trace": "Traceback (most recent call last):\n  ..."
  },
  "final_state": null
}
```

**Special Notes**:
- Always the last event in a run
- Contains final status and error information
- `duration_ms` reflects total run time

### LLM_CALL

**Purpose**: Records a Large Language Model API call.

**Required Fields**: All base fields

**Payload Schema**:
```json
{
  "prompt": "string",           // Input prompt
  "response": "string",         // Model response
  "model": "string",            // Model identifier (often in name field)
  "usage": {                    // Token usage (if available)
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  },
  "finish_reason": "string",    // Why generation stopped
  "error": null or {            // Error details if call failed
    "type": "...",
    "message": "..."
  }
}
```

**Example (Successful Call)**:
```json
{
  "event_type": "LLM_CALL",
  "name": "gpt-4",
  "duration_ms": 1234,
  "payload": {
    "prompt": "Summarize the following text: ...",
    "response": "This is a summary of the text...",
    "model": "gpt-4",
    "usage": {
      "prompt_tokens": 100,
      "completion_tokens": 50,
      "total_tokens": 150
    },
    "finish_reason": "stop",
    "error": null
  }
}
```

**Example (Failed Call)**:
```json
{
  "event_type": "LLM_CALL",
  "name": "gpt-4",
  "duration_ms": 567,
  "payload": {
    "prompt": "...",
    "response": null,
    "error": {
      "type": "RateLimitError",
      "message": "Rate limit exceeded"
    }
  }
}
```

**Best Practices**:
- Include `usage` data whenever available for cost tracking
- Record full prompt/response for debugging (watch for size limits)
- Use `name` field for model identification
- Always record errors, even if call failed

### TOOL_CALL

**Purpose**: Records a function or tool execution.

**Required Fields**: All base fields

**Payload Schema**:
```json
{
  "args": {},                    // Function arguments
  "result": {},                  // Return value or null
  "status": "success|error",     // Execution status
  "error": null or {             // Error details if status=error
    "type": "...",
    "message": "...",
    "stack_trace": "..."
  }
}
```

**Example (Successful Tool Call)**:
```json
{
  "event_type": "TOOL_CALL",
  "name": "search_database",
  "duration_ms": 234,
  "payload": {
    "args": {
      "query": "SELECT * FROM users WHERE active = true",
      "limit": 10
    },
    "result": {
      "rows": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
      ],
      "count": 2
    },
    "status": "success",
    "error": null
  }
}
```

**Example (Failed Tool Call)**:
```json
{
  "event_type": "TOOL_CALL",
  "name": "external_api",
  "duration_ms": 5000,
  "payload": {
    "args": {"endpoint": "/users"},
    "result": null,
    "status": "error",
    "error": {
      "type": "ConnectionError",
      "message": "Connection timeout after 5 seconds",
      "stack_trace": "..."
    }
  }
}
```

**Best Practices**:
- Include full arguments for debugging
- Record both successful results and errors
- Use descriptive `name` values (function names)
- Include `duration_ms` for performance analysis

### STATE_UPDATE

**Purpose**: Records arbitrary state changes during execution.

**Required Fields**: All base fields

**Payload Schema**:
```json
{
  // Free-form key-value pairs
  "key": "value",
  "nested": {
    "data": "here"
  }
}
```

**Examples**:
```json
// Memory checkpoint
{
  "event_type": "STATE_UPDATE",
  "name": "memory_checkpoint",
  "payload": {
    "working_memory": ["user_request", "context"],
    "facts_extracted": 3,
    "current_step": "reasoning"
  }
}

// Progress update
{
  "event_type": "STATE_UPDATE",
  "name": "progress",
  "payload": {
    "percent_complete": 45,
    "current_phase": "data_processing",
    "items_processed": 450,
    "total_items": 1000
  }
}

// Custom metrics
{
  "event_type": "STATE_UPDATE",
  "name": "metrics",
  "payload": {
    "accuracy": 0.95,
    "latency_p95_ms": 234,
    "cache_hit_rate": 0.78
  }
}
```

**Best Practices**:
- Use descriptive `name` values
- Keep payload size reasonable (<1KB recommended)
- Use for debugging state, not production metrics
- Consider redaction for sensitive state data

### ERROR

**Purpose**: Records an exception or error condition.

**Required Fields**: All base fields

**Payload Schema**:
```json
{
  "error_type": "string",        // Exception class name
  "message": "string",            // Error message
  "stack_trace": "string",        // Full stack trace
  "context": {},                  // Additional error context
  "fatal": boolean                // Whether this caused run failure
}
```

**Example**:
```json
{
  "event_type": "ERROR",
  "name": "DatabaseConnectionError",
  "duration_ms": null,
  "payload": {
    "error_type": "DatabaseConnectionError",
    "message": "Failed to connect to database after 3 retries",
    "stack_trace": "Traceback (most recent call last):\n  File \"...\"\n...",
    "context": {
      "host": "db.example.com",
      "port": 5432,
      "retries": 3,
      "last_error": "Connection refused"
    },
    "fatal": true
  }
}
```

**Best Practices**:
- Always include stack traces for debugging
- Add context for better error understanding
- Set `fatal` appropriately for run status
- Use `error_type` for exception categorization

### LOOP_WARNING

**Purpose**: Indicates detection of repetitive patterns.

**Required Fields**: All base fields

**Payload Schema**:
```json
{
  "pattern": "string",           // Description of repetitive pattern
  "evidence": [],                // Examples of repeated events
  "repetition_count": 5,         // Number of repetitions detected
  "severity": "warning|critical" // Warning level
}
```

**Example**:
```json
{
  "event_type": "LOOP_WARNING",
  "name": "tool_loop_detected",
  "duration_ms": null,
  "payload": {
    "pattern": "TOOL_CALL: search_database with identical args",
    "evidence": [
      {
        "event_type": "TOOL_CALL",
        "name": "search_database",
        "args": {"query": "SELECT * FROM users"}
      },
      {
        "event_type": "TOOL_CALL",
        "name": "search_database",
        "args": {"query": "SELECT * FROM users"}
      }
    ],
    "repetition_count": 5,
    "severity": "critical"
  }
}
```

**Best Practices**:
- Include clear pattern descriptions
- Show concrete examples in evidence
- Use appropriate severity levels
- Trigger guardrails for critical loops

## Metadata Standards

### Recommended meta Fields

While `meta` is free-form, we recommend these conventions:

```json
{
  "meta": {
    "framework": "langchain|openai|crewai|custom",
    "environment": "development|staging|production",
    "user_id": "string",
    "session_id": "string",
    "experiment_id": "string",
    "version": "string",
    "tags": ["tag1", "tag2"]
  }
}
```

### Framework-Specific Meta

**LangChain**:
```json
{
  "meta": {
    "framework": "langchain",
    "chain_type": "SequentialChain",
    "agent_type": "ZERO_SHOT_REACT_DESCRIPTION"
  }
}
```

**OpenAI Agents SDK**:
```json
{
  "meta": {
    "framework": "openai_agents",
    "agent_name": "assistant",
    "generation_id": "gen_123"
  }
}
```

## Event Ordering & Relationships

### Chronological Order

Events are written in chronological order within a run:

```
RUN_START (parent_id = null)
├── LLM_CALL (parent_id = RUN_START.event_id)
│   └── TOOL_CALL (parent_id = LLM_CALL.event_id)
├── STATE_UPDATE (parent_id = LLM_CALL.event_id)
└── RUN_END (parent_id = RUN_START.event_id)
```

### Parent-Child Relationships

Establish the event hierarchy:

```python
# Finding all children of an event
def find_children(run_id, parent_event_id):
    return [
        event for event in load_events(run_id)
        if event.get("parent_id") == parent_event_id
    ]

# Finding the root event (RUN_START)
def find_root(event):
    while event.get("parent_id"):
        event = get_event(event["parent_id"])
    return event
```

### Event Siblings

Events with the same parent are siblings:

```python
# Find all LLM calls
def find_llm_calls(run_id):
    return [
        event for event in load_events(run_id)
        if event["event_type"] == "LLM_CALL"
    ]
```

## Backwards Compatibility

### Version Compatibility Matrix

| AgentDbg Version | spec_version | Compatible Reads |
|-----------------|--------------|------------------|
| 0.1.x           | 0.1          | 0.1 events       |
| 0.2.x           | 0.1          | 0.1, 0.2 events  |
| 1.0.x           | 1.0          | 0.1, 0.2, 1.0 events |

### Adding New Fields

New fields are added in non-breaking ways:

```json
// Old format (0.1)
{
  "event_type": "LLM_CALL",
  "payload": {
    "prompt": "...",
    "response": "..."
  }
}

// New format (0.2) - backwards compatible
{
  "event_type": "LLM_CALL",
  "payload": {
    "prompt": "...",
    "response": "...",
    "new_field": "..."  // Old readers ignore this
  }
}
```

### Deprecation Policy

- **Minor versions**: Add new fields, never remove existing fields
- **Major versions**: Can remove deprecated fields with 6-month notice
- **Migration guides**: Provided for breaking changes

## Validation & Testing

### Event Validation

```python
from jsonschema import validate, ValidationError

def validate_event(event):
    schema = load_schema(event["event_type"])
    try:
        validate(instance=event, schema=schema)
        return True
    except ValidationError as e:
        print(f"Invalid event: {e.message}")
        return False
```

### Schema Testing

```python
def test_event_schema():
    event = create_sample_event("LLM_CALL")
    assert validate_event(event)
    assert event["spec_version"] == "0.1"
    assert "event_id" in event
    assert "run_id" in event
```

## Performance Considerations

### Event Size Guidelines

| Event Type | Typical Size | Max Recommended |
|------------|--------------|-----------------|
| RUN_START  | ~500 bytes   | 1 KB            |
| RUN_END    | ~1 KB        | 5 KB            |
| LLM_CALL   | ~2 KB        | 20 KB           |
| TOOL_CALL  | ~1 KB        | 10 KB           |
| STATE_UPDATE| ~500 bytes   | 5 KB            |
| ERROR      | ~2 KB        | 10 KB           |
| LOOP_WARNING| ~1 KB        | 5 KB            |

### Optimization Tips

```python
# For large prompts, consider truncation
def record_large_llm_call(prompt, response):
    record_llm_call(
        prompt=prompt[:10000] + "...",  # Truncate large prompts
        response=response[:10000] + "...",
        meta={"original_sizes": {"prompt": len(prompt), "response": len(response)}}
    )
```

## Integration Examples

### Custom Event Producer

```python
def record_custom_event(event_type, name, payload):
    event = {
        "spec_version": "0.1",
        "event_id": str(uuid.uuid4()),
        "run_id": run_context.get().run_id,
        "parent_id": run_context.get().parent_id,
        "event_type": event_type,
        "ts": datetime.now(timezone.utc).isoformat(),
        "duration_ms": None,
        "name": name,
        "payload": payload,
        "meta": {"custom": True}
    }
    emit_event(event)
```

### Event Consumer

```python
def analyze_llm_usage(run_id):
    events = load_events(run_id)
    llm_calls = [e for e in events if e["event_type"] == "LLM_CALL"]
    
    total_tokens = sum(
        e["payload"]["usage"]["total_tokens"] 
        for e in llm_calls 
        if e["payload"].get("usage")
    )
    
    return {
        "total_llm_calls": len(llm_calls),
        "total_tokens": total_tokens,
        "estimated_cost": total_tokens * 0.00002  # $0.02 per 1K tokens
    }
```

---

**This specification is maintained by the AgentDbg core team. For questions or suggestions, please open a GitHub issue.**