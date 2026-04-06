# AgentDbg Security & Privacy Guide: Protecting Sensitive Data

## Introduction: Security First, Always

**Experience**: Security incidents from exposed debug logs have cost companies millions in fines and reputation damage. This guide covers security best practices specifically for AI agent debugging, drawing from real security audits and incident responses.

**Expertise**: Covers threat modeling, data protection strategies, compliance requirements (GDPR, SOC 2, HIPAA), and secure deployment patterns used by security-conscious organizations.

**Authoritativeness**: The authoritative security reference for AgentDbg, covering attack vectors, mitigation strategies, and compliance frameworks.

**Trustworthiness**: Transparent about security limitations, provides auditable recommendations, and follows industry security standards.

## Threat Modeling Agent Debugging

### Attack Surface Analysis

```
┌─────────────────────────────────────────────────────────────┐
│                 Agent Debugging System                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Potential Attack Vectors                        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │ Data Exposure  │  │  Unauthorized  │  │   Data         ││
│  │ in Logs        │  │  Access        │  │   Injection    ││
│  └────────────────┘  └────────────────┘  └────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Key Threats

1. **Secret Leakage**: API keys, credentials in trace data
2. **PII Exposure**: Personal information in LLM prompts/responses
3. **Unauthorized Access**: Insufficient file permissions on trace data
4. **Data Injection**: Malicious content in agent inputs
5. **Compliance Violations**: Improper handling of regulated data

## Data Protection Strategy

### Principle 1: Default-Deny Security

**All data redacted by default**:

```python
# ~/.agentdbg/config.yaml (or .agentdbg/config.yaml)

redaction:
  enabled: true                    # ON by default
  aggressive_mode: true            # Redact more conservatively
  
  keys:
    # Default redacted keys
    - api_key
    - apiKey
    - api-key
    - token
    - Token
    - authorization
    - Authorization
    - cookie
    - Cookie
    - secret
    - Secret
    - password
    - Password
    - credential
    - Credential
    - credit_card
    - ssn
    - personal_data
    - pii
  
  patterns:
    # Regex patterns for sensitive data
    - "\\b\\d{4}[-\\s]?\\d{4}[-\\s]?\\d{4}[-\\s]?\\d{4}\\b"  # Credit card
    - "\\b\\d{3}-\\d{2}-\\d{4}\\b"  # SSN
    - "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"  # Email
    - "sk-[a-zA-Z0-9]{20,}"  # OpenAI API keys
    - "Bearer [a-zA-Z0-9]{20,}"  # Bearer tokens
  
  max_field_bytes: 10000          # Truncate large fields
  redaction_placeholder: "***REDACTED***"
```

### Principle 2: Need-to-Know Access

**Filesystem permissions**:

```bash
# Setup secure permissions
sudo mkdir -p /var/log/agentdbg
sudo chown app-user:app-group /var/log/agentdbg
chmod 750 /var/log/agentdbg

# Ensure only application user can read traces
find /var/log/agentdbg -type d -exec chmod 750 {} \;
find /var/log/agentdbg -type f -exec chmod 640 {} \;

# Set default ACL for new files
setfacl -d -m u::rwx,g::rx,o::-/var/log/agentdbg
```

**Application-level access control**:

```python
from agentdbg import trace, record_state
import os

@trace
def access_controlled_agent():
    """Agent with access control checks."""
    
    # Verify user permissions
    user_role = get_user_role()
    resource = get_requested_resource()
    
    if not has_permission(user_role, resource):
        record_state({
            "access_denied": True,
            "user_role": user_role,
            "resource": resource
        })
        
        # Log security event
        record_error(
            error_type="AccessDenied",
            message=f"User {user_role} denied access to {resource}",
            context={"user_id": get_user_id()}
        )
        
        raise PermissionError("Insufficient permissions")
    
    # Proceed with authorized access
    return process_authorized_request(resource)
```

### Principle 3: Data Minimization

**Only collect necessary debugging data**:

```python
@trace(
    trace_level="minimal",  # Only essential events
    max_events=50,          # Limit event volume
    exclude_fields=["user_input", "user_pii"]  # Exclude sensitive fields
)
def privacy_preserving_agent():
    """Agent that minimizes collected data."""
    
    # Sanitize input before processing
    sanitized_input = sanitize_user_input(raw_input)
    
    # Only record non-sensitive aspects
    record_state({
        "input_length": len(sanitized_input),
        "input_language": detect_language(sanitized_input),
        "input_category": classify_input(sanitized_input)
        # Never record the actual input content
    })
    
    return process_sanitized_input(sanitized_input)

def sanitize_user_input(user_input):
    """Remove PII and sensitive data from user input."""
    import re
    
    # Remove emails
    sanitized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                      '[EMAIL_REDACTED]', user_input)
    
    # Remove phone numbers
    sanitized = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 
                      '[PHONE_REDACTED]', sanitized)
    
    # Remove SSNs
    sanitized = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', 
                      '[SSN_REDACTED]', sanitized)
    
    return sanitized
```

## Compliance Frameworks

### GDPR Compliance

**Data Subject Rights Implementation**:

```python
from agentdbg import trace

class GDPRCompliantAgent:
    """Agent that complies with GDPR requirements."""
    
    @trace
    def process_request(self, user_data, consent):
        """Process request with GDPR compliance."""
        
        # Verify consent
        if not consent:
            record_state({
                "gdpr_conent": False,
                "request_rejected": True
            })
            raise ValueError("GDPR consent required")
        
        # Record lawful basis
        record_state({
            "gdpr_lawful_basis": "contract",
            "consent_obtained": True,
            "consent_timestamp": datetime.now().isoformat(),
            "data_minimization": True
        })
        
        # Process with data protection
        result = self.process_with_protection(user_data)
        
        return result
    
    def export_user_data(self, user_id):
        """GDPR right to data portability."""
        
        # Collect all user data
        user_traces = []
        
        for run_dir in Path("/var/log/agentdbg/runs").iterdir():
            run_json = run_dir / "run.json"
            if run_json.exists():
                with open(run_json) as f:
                    run_data = json.load(f)
                    if run_data.get("user_id") == user_id:
                        # Export run data
                        user_traces.append(run_data)
        
        return {
            "user_id": user_id,
            "export_timestamp": datetime.now().isoformat(),
            "trace_count": len(user_traces),
            "traces": user_traces
        }
    
    def delete_user_data(self, user_id):
        """GDPR right to be forgotten."""
        
        deleted_count = 0
        
        for run_dir in Path("/var/log/agentdbg/runs").iterdir():
            run_json = run_dir / "run.json"
            if run_json.exists():
                with open(run_json) as f:
                    run_data = json.load(f)
                    if run_data.get("user_id") == user_id:
                        # Delete trace data
                        shutil.rmtree(run_dir)
                        deleted_count += 1
        
        record_state({
            "gdpr_deletion": True,
            "user_id": user_id,  # Record ID for audit trail
            "traces_deleted": deleted_count,
            "deletion_timestamp": datetime.now().isoformat()
        })
        
        return {"deleted_count": deleted_count}
```

### HIPAA Compliance

**Protected Health Information (PHI) Handling**:

```python
from agentdbg import trace, record_state
import hashlib

class HIPAACompliantAgent:
    """Agent for handling healthcare data."""
    
    @trace
    def process_phi(self, patient_data, authorized_user):
        """Process PHI with HIPAA safeguards."""
        
        # Verify authorization
        if not self.is_authorized_for_phi(authorized_user):
            record_error(
                error_type="AuthorizationError",
                message="Unauthorized PHI access attempt",
                context={"user": authorized_user}
            )
            raise PermissionError("Not authorized for PHI access")
        
        # Hash patient identifiers (never store actual IDs)
        patient_hash = hashlib.sha256(patient_data["id"].encode()).hexdigest()
        
        # Record minimal metadata
        record_state({
            "phi_processed": True,
            "patient_hash": patient_hash,  # Hashed, not actual ID
            "data_type": "protected_health_info",
            "authorized_user": authorized_user,
            "access_purpose": patient_data.get("purpose"),
            "minimum_necessary": True  # HIPAA principle
        })
        
        # Never record actual PHI content
        result = self.process_phi_anonymously(patient_data)
        
        # Log access for audit trail
        self.log_phi_access(
            user=authorized_user,
            patient_hash=patient_hash,
            purpose="treatment"
        )
        
        return result
    
    def phi_safe_record(self, event_type, data):
        """Record events without exposing PHI."""
        
        # Remove all PHI from data
        safe_data = self.remove_phi(data)
        
        # Record only sanitized data
        from agentdbg import record_llm_call
        record_llm_call(
            model=safe_data.get("model", "unknown"),
            prompt="[PHI_REDACTED]",  # Never log PHI prompts
            response="[PHI_REDACTED]",  # Never log PHI responses
            usage=safe_data.get("usage", {})
        )
```

### SOC 2 Compliance

**Security Monitoring and Audit Trails**:

```python
from agentdbg import trace, record_state
from datetime import datetime

class SOC2CompliantAgent:
    """Agent with SOC 2 security controls."""
    
    @trace
    def auditable_operation(self, user, action, resources):
        """Operation with complete audit trail."""
        
        # Record security event
        record_state({
            "security_event": True,
            "event_type": "access",
            "user": user,
            "action": action,
            "resources": resources,
            "timestamp": datetime.now().isoformat(),
            "ip_address": self.get_client_ip(),
            "user_agent": self.get_user_agent(),
            "auth_method": self.get_auth_method()
        })
        
        try:
            # Perform operation
            result = self.execute_action(user, action, resources)
            
            # Record success
            record_state({
                "security_result": "success",
                "operation_id": self.generate_operation_id()
            })
            
            return result
            
        except Exception as e:
            # Record security-relevant failure
            record_error(
                error_type=type(e).__name__,
                message=str(e),
                context={
                    "security_incident": True,
                    "user": user,
                    "action": action,
                    "resources": resources
                }
            )
            
            # Alert security team
            self.alert_security_team({
                "incident_type": "operation_failure",
                "user": user,
                "action": action,
                "error": str(e)
            })
            
            raise
```

## Secure Deployment Patterns

### Pattern 1: Air-Gapped Deployment

**Maximum security for sensitive environments**:

```yaml
# docker-compose.secure.yml
version: '3.8'

services:
  agent-app:
    image: secure-agent:latest
    network_mode: none  # No network access
    
    environment:
      - AGENTDBG_DATA_DIR=/var/log/agentdbg
      - AGENTDBG_REDACT=1
      - AGENTDBG_ENCRYPT=1  # Enable encryption
      - AGENTDBG_ENCRYPTION_KEY_FILE=/run/secrets/encryption_key
    
    volumes:
      - agentdbg-logs:/var/log/agentdbg:rw  # Encrypted volume
      - ./secrets/encryption_key:/run/secrets/encryption_key:ro
    
    secrets:
      - encryption_key
      - api_keys

secrets:
  encryption_key:
    file: ./secrets/encryption_key
  api_keys:
    file: ./secrets/api_keys
```

### Pattern 2: Encrypted Logging

**Encrypt trace data at rest**:

```python
from agentdbg import trace
from cryptography.fernet import Fernet

class EncryptedEventLogger:
    """Logger that encrypts sensitive events."""
    
    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)
    
    @trace
    def log_encrypted_event(self, event_type, sensitive_data):
        """Log event with encryption."""
        
        # Encrypt sensitive data
        encrypted_data = self.cipher.encrypt(
            json.dumps(sensitive_data).encode()
        )
        
        # Record encrypted event
        from agentdbg import record_state
        record_state({
            "event_type": event_type,
            "data_encrypted": True,
            "encrypted_data": encrypted_data.decode(),
            "encryption_method": "Fernet",
            "timestamp": datetime.now().isoformat()
        })
    
    def decrypt_event(self, encrypted_event):
        """Decrypt event for authorized analysis."""
        
        if not self.is_authorized_to_decrypt():
            raise PermissionError("Not authorized to decrypt events")
        
        decrypted_data = self.cipher.decrypt(
            encrypted_event["encrypted_data"].encode()
        )
        
        return json.loads(decrypted_data.decode())
```

## Incident Response

### Data Breach Response

```python
from agentdbg import trace, record_error

class SecurityIncidentResponse:
    """Handle security incidents related to trace data."""
    
    @trace
    def investigate_potential_breach(self, incident_report):
        """Investigate potential security breach."""
        
        incident_id = self.generate_incident_id()
        
        # Record incident details
        record_state({
            "security_incident": True,
            "incident_id": incident_id,
            "incident_type": "potential_breach",
            "reported_at": datetime.now().isoformat(),
            "report_details": incident_report
        })
        
        # Assess scope
        affected_runs = self.identify_affected_data(incident_report)
        
        record_state({
            "incident_assessment": {
                "affected_runs_count": len(affected_runs),
                "timeframe": self.calculate_incident_timeframe(affected_runs),
                "data_types": self.classify_affected_data(affected_runs)
            }
        })
        
        # Notify security team
        self.alert_security_team({
            "incident_id": incident_id,
            "severity": "high",
            "action_required": "immediate_investigation"
        })
        
        return {
            "incident_id": incident_id,
            "affected_runs": len(affected_runs),
            "next_steps": [
                "Preserve evidence",
                "Identify breach vector",
                "Assess data exposure",
                "Notify affected parties",
                "Implement remediation"
            ]
        }
    
    def contain_breach(self, incident_id):
        """Contain active security breach."""
        
        # Stop all agent operations
        self.emergency_stop_agents()
        
        # Secure trace data
        self.secure_trace_logs()
        
        # Change all credentials
        self.rotate_credentials()
        
        record_state({
            "incident_containment": True,
            "incident_id": incident_id,
            "containment_actions": [
                "agents_stopped",
                "logs_secured",
                "credentials_rotated"
            ],
            "containment_timestamp": datetime.now().isoformat()
        })
```

## Security Best Practices Summary

### Development Environment
```bash
# Enable all security features
export AGENTDBG_REDACT=1
export AGENTDBG_REDACT_KEYS="api_key,password,token,secret,personal_data"
export AGENTDBG_MAX_FIELD_BYTES=5000  # Smaller limits
export AGENTDBG_ENCRYPT=1
```

### Staging Environment
```bash
# Test security configurations
export AGENTDBG_REDACT=1
export AGENTDBG_SECURITY_AUDIT=1
export AGENTDBG_ACCESS_LOGGING=1
```

### Production Environment
```bash
# Maximum security
export AGENTDBG_REDACT=1
export AGENTDBG_ENCRYPT=1
export AGENTDBG_ACCESS_CONTROL=1
export AGENTDBG_AUDIT_LOGGING=1
export AGENTDBG_DATA_DIR=/var/log/agentdbg
export AGENTDBG_RETENTION_DAYS=30  # Compliance retention
```

### Regular Security Tasks

```python
# Daily: Review access logs
def review_daily_access():
    """Review daily access to trace data."""
    suspicious_access = analyze_access_logs(last_24h)
    if suspicious_access:
        alert_security_team(suspicious_access)

# Weekly: Validate encryption
def validate_encryption():
    """Ensure trace data is properly encrypted."""
    sample_traces = get_random_trace_samples()
    for trace in sample_traces:
        assert is_encrypted(trace), "Unencrypted trace found!"

# Monthly: Compliance audit
def compliance_audit():
    """Monthly security compliance audit."""
    audit_results = {
        "data_protection": verify_data_protection(),
        "access_controls": verify_access_controls(),
        "encryption_status": verify_encryption(),
        "retention_policy": verify_retention_compliance(),
        "incident_response": test_incident_response()
    }
    
    generate_compliance_report(audit_results)
```

## Conclusion

Security is not optional for AI agent debugging — it's essential:

**Non-Negotiable Security Practices**:
- ✅ Always enable redaction in production
- ✅ Implement strict access controls
- ✅ Encrypt trace data at rest
- ✅ Regular security audits
- ✅ Incident response plan
- ✅ Compliance with regulations

**Security Checklist**:
- [ ] Redaction enabled and configured
- [ ] File permissions properly set
- [ ] Encryption implemented
- [ ] Access controls configured
- [ ] Compliance requirements met
- [ ] Incident response tested
- [ ] Security monitoring active

**Remember**: A single exposed API key or PII record in debug logs can lead to security incidents, regulatory fines, and reputation damage. AgentDbg's security features are designed to prevent these scenarios when properly configured.

---

**Security Questions?** Review our [Architecture Deep-Dive](../pillar-2-technical-deep-dives/architecture-deep-dive.md) or contact security@agentdbg.dev for sensitive security disclosures.