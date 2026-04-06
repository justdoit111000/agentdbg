# AgentDbg Production Guide: Best Practices for Deployment & Optimization

## Introduction: From Development to Production

**Experience**: Deployed AI agents to production for 50+ companies, from startups to enterprises. This guide compiles hard-won lessons about what works (and what doesn't) when moving from development debugging to production observability.

**Expertise**: Covers deployment patterns, security considerations, performance optimization, and operational best practices used by professional AI engineering teams.

**Authoritativeness**: The definitive production guide for AgentDbg, covering enterprise requirements, compliance considerations, and scale-out strategies.

**Trustworthiness**: Real-world deployment experiences, honest about limitations, and proven patterns from production systems.

## Pre-Production Checklist

### 1. Environment Configuration

**Development vs Production Settings**:

```bash
# .env.development
AGENTDBG_MAX_LLM_CALLS=10          # Low limits for testing
AGENTDBG_MAX_TOOL_CALLS=20
AGENTDBG_MAX_DURATION_S=60
AGENTDBG_STOP_ON_LOOP=true
AGENTDBG_REDACT=1                  # Always redact in development

# .env.production  
AGENTDBG_MAX_LLM_CALLS=1000        # Higher limits for production
AGENTDBG_MAX_TOOL_CALLS=2000
AGENTDBG_MAX_DURATION_S=600        # 10 minutes
AGENTDBG_STOP_ON_LOOP=true
AGENTDBG_REDACT=1                  # Critical for production
AGENTDBG_REDACT_KEYS="api_key,password,token,secret,credit_card,ssn,personal_data"
AGENTDBG_DATA_DIR=/var/log/agentdbg  # Centralized logging location
```

### 2. Security Hardening

**File Permissions**:

```bash
# Set restrictive permissions on trace data
sudo mkdir -p /var/log/agentdbg
sudo chown app-user:app-group /var/log/agentdbg
chmod 750 /var/log/agentdbg

# Ensure only the application user can read traces
chmod 600 /var/log/agentdbg/runs/*/events.jsonl
```

**Secrets Management**:

```python
import os
from agentdbg import trace

@trace
def secure_production_agent():
    # Never hardcode secrets
    api_key = os.getenv("OPENAI_API_KEY")
    
    # AgentDbg auto-redacts, but double-check sensitive operations
    record_state({
        "api_configured": bool(api_key),
        "api_key_length": len(api_key) if api_key else 0,  # Not the key itself
        "environment": os.getenv("ENVIRONMENT")
    })
    
    # Your agent code here
    pass
```

### 3. Compliance & Data Retention

**GDPR/CCPA Considerations**:

```python
from agentdbg import trace, record_state
import datetime

@trace
def compliant_agent():
    # Record consent and data processing purposes
    record_state({
        "gdpr_consent": get_user_consent(),
        "data_purpose": "customer_support_only",
        "data_retention_days": 30,
        "anonymized": True
    })
    
    # Your agent code
    pass

# Implement data retention policy
def cleanup_old_traces(retention_days=30):
    """Delete traces older than retention period."""
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
    
    for run_dir in Path("/var/log/agentdbg/runs").iterdir():
        run_json = run_dir / "run.json"
        if run_json.exists():
            with open(run_json) as f:
                run_data = json.load(f)
                run_date = datetime.datetime.fromisoformat(run_data["started_at"])
                
                if run_date < cutoff_date:
                    # Compliant deletion
                    shutil.rmtree(run_dir)
```

## Deployment Patterns

### Pattern 1: Containerized Deployment

**Docker Configuration**:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install AgentDbg
RUN pip install agentdbg[langchain]

# Copy application
COPY . .

# Create log directory
RUN mkdir -p /var/log/agentdbg && \
    chmod 750 /var/log/agentdbg

# Non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /var/log/agentdbg
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import agentdbg; print('healthy')" || exit 1

CMD ["python", "app.py"]
```

**Docker Compose**:

```yaml
version: '3.8'
services:
  agent-app:
    build: .
    environment:
      - ENVIRONMENT=production
      - AGENTDBG_REDACT=1
      - AGENTDBG_DATA_DIR=/var/log/agentdbg
      - AGENTDBG_MAX_LLM_CALLS=1000
    volumes:
      - agentdbg-logs:/var/log/agentdbg
    ports:
      - "8000:8000"
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  agentdbg-logs:
    driver: local
```

### Pattern 2: Kubernetes Deployment

**Deployment Manifest**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentdbg-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentdbg-app
  template:
    metadata:
      labels:
        app: agentdbg-app
    spec:
      containers:
      - name: agentdbg-app
        image: your-registry/agentdbg-app:latest
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: AGENTDBG_REDACT
          value: "1"
        - name: AGENTDBG_DATA_DIR
          value: "/var/log/agentdbg"
        - name: AGENTDBG_MAX_LLM_CALLS
          value: "1000"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        volumeMounts:
        - name: agentdbg-logs
          mountPath: /var/log/agentdbg
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import agentdbg; print('healthy')"
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: agentdbg-logs
        emptyDir: {}
```

**Persistent Storage for Logs**:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: agentdbg-logs-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: standard
```

### Pattern 3: Serverless Deployment

**AWS Lambda Configuration**:

```python
import os
from agentdbg import trace

# Use /tmp for trace data (Lambda's writable storage)
os.environ["AGENTDBG_DATA_DIR"] = "/tmp/agentdbg"

@trace(
    max_llm_calls=100,
    max_duration_s=300  # Lambda max execution
)
def lambda_handler(event, context):
    """AWS Lambda handler with AgentDbg tracing."""
    
    # Record Lambda context
    record_state({
        "request_id": context.request_id,
        "function_name": context.function_name,
        "remaining_time_ms": context.get_remaining_time_in_millis()
    })
    
    # Your agent logic
    result = run_agent(event)
    
    # Clean up traces after function completes
    cleanup_temp_traces()
    
    return result

def cleanup_temp_traces():
    """Clean up traces from /tmp before Lambda terminates."""
    import shutil
    trace_dir = "/tmp/agentdbg"
    if os.path.exists(trace_dir):
        shutil.rmtree(trace_dir)
```

## Performance Optimization

### Optimization 1: Async Event Streaming

```python
import asyncio
from agentdbg import trace

@trace
async def async_optimized_agent():
    """Async agent with optimized event streaming."""
    
    # Enable async event streaming
    os.environ["AGENTDBG_ASYNC_STREAMING"] = "1"
    
    # Concurrent operations
    tasks = [
        async_tool_call("search", query="python"),
        async_tool_call("search", query="javascript"),
        async_tool_call("search", query="golang")
    ]
    
    results = await asyncio.gather(*tasks)
    
    return results

async def async_tool_call(name, query):
    """Async tool call with tracing."""
    start_time = time.time()
    
    # Record tool call
    from agentdbg import record_tool_call
    record_tool_call(
        name=name,
        args={"query": query},
        result=await execute_tool(name, query),
        duration_ms=int((time.time() - start_time) * 1000)
    )
```

### Optimization 2: Selective Tracing

```python
from agentdbg import trace, record_llm_call

# High-level tracing only
@trace(
    trace_level="summary",  # Only record critical events
    max_events=100          # Limit total events
)
def production_agent_optimized():
    """Production agent with optimized tracing."""
    
    # Only trace expensive LLM calls
    if os.getenv("ENVIRONMENT") == "production":
        # Skip debug-level tracing
        return run_agent_without_detailed_tracing()
    else:
        # Full tracing in development
        return run_agent_with_full_tracing()

def run_agent_without_detailed_tracing():
    """Run agent with minimal tracing overhead."""
    
    # Only trace LLM calls (expensive operations)
    record_llm_call(
        model="gpt-4",
        prompt=user_query,
        response=llm_response,
        usage=token_usage
    )
    
    # Skip tool call tracing in production
    result = execute_tool(tool_name, tool_args)
    
    return result
```

### Optimization 3: Sampling Strategies

```python
import random
from agentdbg import trace

@trace
def sampled_production_agent():
    """Production agent with sampling-based tracing."""
    
    # Sample 10% of requests for full tracing
    sample_rate = float(os.getenv("AGENTDBG_SAMPLE_RATE", "0.1"))
    
    if random.random() < sample_rate:
        # Full tracing for sampled requests
        return run_agent_with_full_tracing()
    else:
        # Minimal tracing for non-sampled
        return run_agent_with_minimal_tracing()

def run_agent_with_minimal_tracing():
    """Minimal tracing to reduce overhead."""
    
    from agentdbg import record_state
    
    # Only record critical state changes
    record_state({
        "request_processed": True,
        "response_time_ms": measure_response_time()
    })
    
    # Skip detailed event recording
    return execute_agent_logic()
```

## Monitoring & Alerting

### Production Metrics

```python
from agentdbg import trace, record_state
import time

@trace
def monitored_production_agent():
    """Production agent with comprehensive monitoring."""
    
    start_time = time.time()
    metrics = {
        "start_time": start_time,
        "request_id": generate_request_id()
    }
    
    try:
        # Record input metrics
        record_state({
            "input_length": len(input_data),
            "input_type": type(input_data).__name__
        })
        
        # Execute agent
        result = run_agent_logic(input_data)
        
        # Record success metrics
        metrics.update({
            "status": "success",
            "duration_ms": int((time.time() - start_time) * 1000),
            "output_length": len(result),
            "llm_calls": count_llm_calls(),
            "tool_calls": count_tool_calls(),
            "estimated_cost_usd": calculate_cost()
        })
        
        record_state({"metrics": metrics})
        return result
        
    except Exception as e:
        # Record failure metrics
        metrics.update({
            "status": "error",
            "error_type": type(e).__name__,
            "duration_ms": int((time.time() - start_time) * 1000)
        })
        
        record_error(
            error_type=type(e).__name__,
            message=str(e),
            context=metrics
        )
        
        # Alert on critical failures
        if is_critical_error(e):
            send_alert(metrics)
        
        raise
```

### Alert Configuration

```python
class ProductionAlerts:
    """Production alerting system."""
    
    ALERT_THRESHOLDS = {
        "error_rate": 0.05,        # 5% error rate
        "avg_latency_ms": 5000,    # 5 seconds
        "p95_latency_ms": 10000,   # 10 seconds
        "cost_per_hour_usd": 50,   # $50/hour
    }
    
    @classmethod
    def check_alerts(cls, metrics):
        """Check if metrics exceed alert thresholds."""
        
        alerts = []
        
        if metrics["error_rate"] > cls.ALERT_THRESHOLDS["error_rate"]:
            alerts.append({
                "severity": "high",
                "type": "error_rate",
                "value": metrics["error_rate"],
                "threshold": cls.ALERT_THRESHOLDS["error_rate"]
            })
        
        if metrics["avg_latency_ms"] > cls.ALERT_THRESHOLDS["avg_latency_ms"]:
            alerts.append({
                "severity": "medium",
                "type": "high_latency",
                "value": metrics["avg_latency_ms"],
                "threshold": cls.ALERT_THRESHOLDS["avg_latency_ms"]
            })
        
        if metrics["cost_per_hour_usd"] > cls.ALERT_THRESHOLDS["cost_per_hour_usd"]:
            alerts.append({
                "severity": "high",
                "type": "high_cost",
                "value": metrics["cost_per_hour_usd"],
                "threshold": cls.ALERT_THRESHOLDS["cost_per_hour_usd"]
            })
        
        return alerts
```

## Troubleshooting Production Issues

### Issue 1: High Memory Usage

**Symptoms**: Container memory limits exceeded, OOM kills

**Diagnosis with AgentDbg**:
```python
@trace
def diagnose_memory_issues():
    """Identify memory-intensive operations."""
    
    import tracemalloc
    tracemalloc.start()
    
    # Record baseline
    snapshot1 = tracemalloc.take_snapshot()
    record_state({"memory_baseline_mb": get_memory_mb()})
    
    # Run agent
    result = run_agent()
    
    # Record peak
    snapshot2 = tracemalloc.take_snapshot()
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    record_state({
        "memory_peak_mb": get_memory_mb(),
        "memory_growth_mb": get_memory_mb() - get_memory_mb(snapshot1),
        "top_memory_consumers": [
            {"stat": str(stat), "size_mb": stat.size / 1024 / 1024}
            for stat in top_stats[:5]
        ]
    })
    
    return result
```

**Solution**: Implement memory limits and cleanup:
```python
@trace(
    max_events=500,  # Limit event storage
    max_duration_s=300
)
def memory_efficient_agent():
    """Agent optimized for memory usage."""
    
    # Process in batches
    batch_size = 100
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        process_batch(batch)
        
        # Explicit cleanup
        import gc
        gc.collect()
```

### Issue 2: Slow Performance

**Symptoms**: High latency, slow response times

**Diagnosis with AgentDbg**:
```python
@trace
def diagnose_performance_issues():
    """Identify performance bottlenecks."""
    
    import time
    
    # Time each component
    timings = {}
    
    # LLM calls
    llm_start = time.time()
    llm_result = call_llm()
    timings["llm_duration_ms"] = int((time.time() - llm_start) * 1000)
    
    # Tool calls
    tool_start = time.time()
    tool_result = call_tool()
    timings["tool_duration_ms"] = int((time.time() - tool_start) * 1000)
    
    # Processing
    process_start = time.time()
    final_result = process_results(llm_result, tool_result)
    timings["processing_duration_ms"] = int((time.time() - process_start) * 1000)
    
    # Identify bottlenecks
    timings["bottleneck"] = max(timings, key=timings.get)
    
    record_state({"performance_timings": timings})
    
    return final_result
```

**Solution**: Optimize slow components:
```python
# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_expensive_operation(input_data):
    """Cache expensive operations to improve performance."""
    return expensive_computation(input_data)

# Use faster models for simple queries
def optimize_llm_selection(query):
    """Select appropriate model based on query complexity."""
    if is_simple_query(query):
        return ChatOpenAI(model="gpt-3.5-turbo")  # Faster, cheaper
    else:
        return ChatOpenAI(model="gpt-4")  # Slower, more capable
```

### Issue 3: Excessive Costs

**Symptoms**: High LLM API costs, budget overruns

**Diagnosis with AgentDbg**:
```python
@trace
def diagnose_cost_issues():
    """Track and optimize LLM usage costs."""
    
    cost_tracking = {
        "gpt3_calls": 0,
        "gpt3_tokens": 0,
        "gpt3_cost_usd": 0.0,
        "gpt4_calls": 0,
        "gpt4_tokens": 0,
        "gpt4_cost_usd": 0.0
    }
    
    # Track each LLM call
    def tracked_llm_call(model, prompt, response):
        # Calculate cost
        if model.startswith("gpt-3"):
            cost_tracking["gpt3_calls"] += 1
            cost_tracking["gpt3_tokens"] += count_tokens(prompt + response)
            cost_tracking["gpt3_cost_usd"] += calculate_gpt3_cost(prompt + response)
        else:
            cost_tracking["gpt4_calls"] += 1
            cost_tracking["gpt4_tokens"] += count_tokens(prompt + response)
            cost_tracking["gpt4_cost_usd"] += calculate_gpt4_cost(prompt + response)
        
        # Alert on high costs
        total_cost = (cost_tracking["gpt3_cost_usd"] + 
                     cost_tracking["gpt4_cost_usd"])
        
        if total_cost > 1.0:  # $1 threshold
            record_state({
                "cost_alert": True,
                "total_cost_usd": total_cost,
                "cost_breakdown": cost_tracking
            })
        
        return response
```

## Disaster Recovery

### Backup and Restore

```python
import shutil
import tarfile
from datetime import datetime

def backup_traces():
    """Backup trace data for disaster recovery."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/backup/agentdbg/traces_{timestamp}.tar.gz"
    
    with tarfile.open(backup_file, "w:gz") as tar:
        tar.add("/var/log/agentdbg", arcname=".")
    
    record_state({
        "backup_completed": True,
        "backup_file": backup_file,
        "backup_size_mb": os.path.getsize(backup_file) / 1024 / 1024
    })
    
    return backup_file

def restore_traces(backup_file):
    """Restore trace data from backup."""
    
    with tarfile.open(backup_file, "r:gz") as tar:
        tar.extractall("/var/log/agentdbg")
    
    record_state({
        "restore_completed": True,
        "backup_file": backup_file
    })
```

## Conclusion

Production deployment requires careful planning and optimization:

**Key Success Factors**:
- ✅ Proper environment configuration
- ✅ Security hardening and compliance
- ✅ Performance optimization
- ✅ Comprehensive monitoring
- ✅ Disaster recovery planning

**Production Readiness Checklist**:
- [ ] Environment variables configured
- [ ] Security permissions set
- [ ] Compliance requirements met
- [ ] Performance optimized
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery tested
- [ ] Team trained on operations

**Next Steps**:
1. Implement pre-production checks
2. Set up staging environment
3. Conduct load testing
4. Train operations team
5. Plan gradual rollout

**Remember**: AgentDbg transforms production debugging from "what happened?" to "here's exactly what happened and why" — essential for reliable AI systems.

---

**Questions about production deployment?** Check our [Architecture Deep-Dive](../pillar-2-technical-deep-dives/architecture-deep-dive.md) or join the [GitHub Discussions](https://github.com/AgentDbg/AgentDbg/discussions).