# Model Context Protocol (MCP) Implementation in UCA

## Model Context Protocol (MCP) Implementation in UCA system.

### Introduction

This document outlines our implementation of Model Context Protocol (MCP) principles in the Social Benefits Assistant system. Unlike a full standardized MCP architecture, our implementation focuses on applying the core principles of structured context management, intelligent tool orchestration, and flow control to create a more effective conversational assistant.

### Why We Needed This

#### The Problem with Simple Message Appending

In our earlier implementation, we used a simple approach of appending every user message and LLM response to a growing conversation history. This method created several significant challenges:

```python
# Previous approach (simplified)
conversation_history = []

def process_query(query):
    # Add user message to history
    conversation_history.append({"role": "user", "content": query})
    
    # Generate response with entire conversation history as context
    response = llm.generate(system_prompt, conversation_history)
    
    # Add response to history
    conversation_history.append({"role": "assistant", "content": response})
    
    return response
```

This approach led to several critical issues:

1.  **Context Window Saturation**

    As conversations grew longer, we eventually hit the token limit of our LLM. Once this happened, we either had to truncate older messages (losing potentially valuable context) or face errors.

    ```python
    # Example of the problem
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        # Lose oldest messages and potentially important context
        conversation_history = conversation_history[-MAX_HISTORY_LENGTH:]
    ```
2.  **Unstructured Information**

    All information existed only as unstructured text within the conversation history. User demographic details, program information, and conversation state were mixed together, making it difficult to track specific pieces of information.
3.  **Redundant Information Retrieval**

    Without tracking what information we'd already retrieved, we often queried databases or external tools repeatedly for the same information, wasting resources and adding latency.

    ```python
    # For every query about a program, we would query the database again
    # even if we'd already retrieved that program's information
    program_details = database.get_program(program_id)
    ```
4.  **Inefficient Context Usage**

    When sending the entire conversation history to the LLM, we included everything, regardless of relevance to the current query.
5.  **Limited Flow Control**

    Complex multi-turn flows like grievance handling were difficult to manage without explicit state tracking.

#### How Our MCP Implementation Solves These Problems

Our MCP-inspired implementation addresses these challenges through:

1. **Structured Context Management**: Instead of a flat conversation history, we maintain a rich, structured context with separate components for different types of information.
2. **Intelligent Tool Orchestration**: We include decision logic to determine when to use existing context versus calling tools for new information.
3. **Flow Management**: We explicitly track the state of complex conversational flows, making it easier to handle multi-turn processes.
4. **Selective Context Utilization**: We selectively include only relevant portions of the context when generating responses.

### Core Components of Our Implementation

#### 1. MCPServer Class

The `MCPServer` class is the core of our implementation, responsible for managing thread contexts and providing access to various context components:

```python
class MCPServer:
    """Model Context Protocol (MCP) server for managing context in conversations."""
    
    def __init__(self):
        """Initialize the MCP Server."""
        # Thread contexts store
        self.thread_contexts = {}
    
    def get_thread_context(self, thread_id: str) -> Dict:
        """Get or initialize a thread context."""
        if thread_id not in self.thread_contexts:
            # Initialize a new thread context with the persona
            self.thread_contexts[thread_id] = {
                "conversation_history": [],
                "retrieved_programs": [],
                "user_profile": {},
                "tool_execution_history": [],
                "persona": {
                    "tone": "friendly and supportive",
                    "speech_patterns": ["uses contractions", "asks occasional questions", "expresses empathy"],
                    "personality_traits": ["helpful", "encouraging", "warm"]
                },
                # Add grievance context
                "grievance_context": {
                    "active": False,
                    "stage": None,
                    "user_id": None,
                    "user_details": None,
                    "program_details": None,
                    "complaint_parts": [],
                    "ticket_id": None,
                    "enough_detail": False
                }
            }
        return self.thread_contexts[thread_id]
```

#### 2. Tools Class

The `Tools` class provides specialized functions for accessing and processing information:

```python
class Tools:
    """Collection of tools for the social benefits assistant."""
    
    def __init__(self, db_tool, ollama, faiss_index_path, grievance_db_tool=None, embeddings_model="all-MiniLM-L6-v2"):
        """Initialize the tools with shared dependencies."""
        self.db_tool = db_tool
        self.ollama = ollama
        # Store grievance_db_tool if provided, otherwise use main db_tool
        self.grievance_db_tool = grievance_db_tool if grievance_db_tool else db_tool
        
        # Initialize embeddings and FAISS components
        # ...
```

#### 3. SocialBenefitsMCP Class

The `SocialBenefitsMCP` class ties everything together, coordinating between the MCP server, tools, and LLM:

```python
class SocialBenefitsMCP:
    """MCP-based social benefits assistant with tool-based architecture."""
    
    def __init__(
        self,
        db_path: str,
        grievance_db_path: str,
        faiss_index_path: str,
        model: str = "deepseek-r1:8b",
        temperature: float = 0.1,
        ollama_url: str = "http://localhost:11434"
    ):
        """Initialize the MCP-based assistant."""
        # Initialize shared components
        self.ollama = OllamaClient(base_url=ollama_url, model=model, temperature=temperature)
        self.db_tool = SQLDatabaseTool(db_path)
        
        # Initialize grievance components
        self.grievance_agent = GrievanceAgent(db_path=grievance_db_path)
        self.grievance_db_tool = SQLDatabaseTool(grievance_db_path, validate_tables=False)
        
        # Initialize the MCP server
        self.mcp_server = MCPServer()
        
        # Initialize tools
        self.tools = Tools(
            db_tool=self.db_tool,
            ollama=self.ollama,
            faiss_index_path=faiss_index_path
        )
        
        # Define system prompts
        self.system_prompt = """You are a Social Benefits Assistant that helps users find and understand benefit programs they may be eligible for.
        # ...
        """
```

### How Our Implementation Works

#### 1. Query Processing Flow

The core of our implementation is the `process_query` method:

```python
def process_query(self, query: str, thread_id: str = "default") -> str:
    """Process a user query using the MCP framework with enhanced classification."""
    try:
        # Add user message to conversation history
        self.mcp_server.update_conversation_history(thread_id, "user", query)
        
        # Get current context
        context = self.mcp_server.get_thread_context(thread_id)
        
        # Check if we're in active grievance handling mode
        grievance_active = context["grievance_context"]["active"]
        
        if grievance_active:
            return self._process_grievance_query(query, thread_id, context)
        
        # Determine if we need to call tools or can use existing context
        tool_decision = self.mcp_server.should_call_tools(thread_id, query, self.ollama)
        
        # Handle different decision paths
        if tool_decision == "CLARIFICATION":
            # Handle clarification...
        elif tool_decision == "GRIEVANCE":
            # Handle grievance...
        elif tool_decision == "COLLECT_INFO":
            # Handle information collection...
        elif tool_decision == "TOOLS":
            # Execute the full tool chain
            user_details = self.tools.extract_user_details_tool(query, context["conversation_history"])
            self.mcp_server.update_user_profile(thread_id, user_details)
            
            vector_results = self.tools.vector_search_tool(query)
            program_ids = [result["id"] for result in vector_results]
            program_details = self.tools.program_details_tool(program_ids)
            
            self.mcp_server.update_retrieved_programs(thread_id, program_details)
            
            eligibility_analysis = self.tools.analyze_eligibility_tool(
                program_details,
                context["user_profile"]
            )
            
            response = self.tools.conversation_formatter_tool(
                query,
                program_details,
                eligibility_analysis,
                context["user_profile"],
                context["persona"]
            )
        else:  # tool_decision == "CONTEXT"
            # Use existing context to answer follow-up question
            relevant_context = self.mcp_server.get_relevant_context(thread_id)
            
            # Create a prompt that includes existing information
            context_prompt = f"""
            USER QUERY: {query}
            
            USER PROFILE:
            {json.dumps(relevant_context["user_profile"], indent=2)}
            
            PREVIOUSLY RETRIEVED PROGRAMS:
            {json.dumps(relevant_context["retrieved_programs"], indent=2)}
            
            RECENT CONVERSATION:
            {json.dumps([{msg["role"]: msg["content"]} for msg in relevant_context["conversation_history"]], indent=2)}
            
            # Additional instructions...
            """
            
            response = self.ollama.generate(self.system_prompt, context_prompt, thread_id)
        
        # Add assistant message to conversation history
        self.mcp_server.update_conversation_history(thread_id, "assistant", response)
        
        return response
    except Exception as e:
        # Error handling...
```

#### 2. Decision Logic for Tool Usage

One of the key innovations in our implementation is the decision logic for determining when to use tools versus existing context:

```python
def should_call_tools(self, thread_id: str, query: str, ollama_client) -> str:
    """Determine if tools should be called for a given query.
    
    Returns:
        str: "TOOLS", "CONTEXT", "CLARIFICATION", "COLLECT_INFO", or "GRIEVANCE"
    """
    context = self.get_thread_context(thread_id)
    
    # If active grievance context, we should call tools
    if context["grievance_context"]["active"]:
        return "GRIEVANCE"
    
    # Use intent analysis to classify the query
    intent_data = self.identify_query_intent(query, thread_id, ollama_client)
    
    # Extract user ID if present and activate grievance flow
    user_id = intent_data.get("entities", {}).get("user_id")
    if user_id:
        self.update_grievance_context(thread_id, {
            "active": True, 
            "stage": "identification",
            "user_id": user_id
        })
        return "GRIEVANCE"
    
    # Handle based on primary intent and confidence
    primary_intent = intent_data.get("primary_intent", "unclear")
    confidence = intent_data.get("confidence", 0.0)
    
    if confidence < 0.6 or primary_intent == "unclear":
        # Handle low confidence or unclear intent
        return "CLARIFICATION"
    elif primary_intent == "grievance" or primary_intent == "status_check":
        # Activate grievance context
        return "GRIEVANCE"
    elif primary_intent == "program_info":
        # Check if we should collect more user information
        if suggested_flow == "program_info_collection" or len(context["user_profile"]) < 3:
            return "COLLECT_INFO"
        
        # If no programs have been retrieved yet, call tools
        if not context["retrieved_programs"]:
            return "TOOLS"
        
        # Use LLM to decide if this query needs tools
        decision_prompt = f"""
        USER QUERY: "{query}"
        
        CONTEXT:
        - Programs already in context: {[p.get('name') for p in context['retrieved_programs']]}
        - User profile: {json.dumps(context['user_profile'])}
        
        QUESTION: Should I call tools to get new information, or use existing context?
        """
        
        decision = ollama_client.generate(
            decision_system_prompt, 
            decision_prompt,
            f"{thread_id}_decision"
        ).strip().upper()
        
        if "CONTEXT" in decision:
            return "CONTEXT"
        else:
            return "TOOLS"
    # Additional logic...
```

#### 3. Multi-turn Grievance Flow

Our implementation includes a structured approach to handling multi-turn grievance flows:

```python
def _process_grievance_query(self, query: str, thread_id: str, context: Dict) -> str:
    """Process a query in the grievance flow."""
    # Determine current stage and next stage
    current_stage = context["grievance_context"]["stage"]
    
    # Special handling for USER ID in identification stage
    if current_stage == "identification":
        user_id_result = self.tools.identify_user_id_tool(query)
        
        if user_id_result["found"]:
            # Found a USER ID, save it and set stage to verification
            user_id = user_id_result["user_id"]
            self.mcp_server.update_grievance_context(thread_id, {"user_id": user_id, "stage": "verification"})
            return self._process_verification(user_id, thread_id, context)
        else:
            # No USER ID found, ask for it
            # ...
    
    # For non-special cases, use the normal stage determination
    next_stage = self.mcp_server.determine_grievance_stage(thread_id, query)
    
    # Update grievance stage
    self.mcp_server.update_grievance_context(thread_id, {"stage": next_stage})
    
    # Handle each stage appropriately
    if next_stage == "verification":
        # Get the user ID from context
        user_id = context["grievance_context"]["user_id"]
        return self._process_verification(user_id, thread_id, context)
    elif next_stage == "complaint":
        return self._process_complaint(query, thread_id, context)
    elif next_stage == "status_check":
        return self._process_status_check(thread_id, context)
    elif next_stage == "ticket_creation":
        return self._process_ticket_creation(thread_id, context)
    elif next_stage == "follow_up":
        return self._process_follow_up(query, thread_id, context)
```

### Benefits of Our Approach

Our MCP-inspired implementation offers several significant advantages over the previous simple approach:

#### 1. Enhanced Conversational Capability

By maintaining structured context and making intelligent decisions about tool usage, our system can handle much more complex conversations, including:

* Multi-turn grievance processes
* Follow-up questions about previously discussed programs
* Contextual understanding of user needs based on their profile

#### 2. Improved Efficiency

Our approach significantly improves efficiency in several ways:

* **Reduced Database Queries**: We only retrieve program information when needed, instead of for every query
* **Context Window Optimization**: We selectively include relevant context rather than the entire conversation history
* **Tool Usage Decisions**: We use existing information when appropriate, avoiding unnecessary tool calls

#### 3. Better Information Organization

The structured context allows us to:

* Track user profile information separately from conversation history
* Maintain a database of retrieved programs
* Record the execution history of tools
* Track the stages of complex flows like grievance handling

#### 4. Increased Robustness

Our implementation is more robust against common issues:

* **Context Window Limitations**: By organizing information efficiently, we can handle much longer conversations
* **State Management**: Explicit tracking of grievance states prevents confusion in complex flows
* **Error Handling**: Structured approach makes it easier to recover from errors

### Future Extensions

While our current implementation focuses on the core principles of MCP rather than the full standardized architecture, there are several ways we could extend it in the future:

#### 1. Formalized Capability Exchange

We could implement a more standardized capability discovery mechanism:

```python
def register_capability(self, capability_name, capability_details, handler_function):
    """Register a tool, resource, or prompt as a capability."""
    self.registered_capabilities[capability_name] = {
        "details": capability_details,
        "handler": handler_function
    }

def get_capabilities(self):
    """Return all available capabilities for discovery."""
    return {name: details["details"] for name, details 
            in self.registered_capabilities.items()}
```

#### 2. Database API Adapters

We could create adapters for each database or external API:

```python
class DatabaseAPIAdapter:
    def __init__(self, connection_string):
        self.connection = self.establish_connection(connection_string)
        self.capabilities = {
            "query_data": {
                "description": "Query data from the database",
                "parameters": {
                    "query": "SQL query or search parameters",
                    "limit": "Optional result limit"
                }
            }
        }
    
    def get_capabilities(self):
        return self.capabilities
    
    def handle_request(self, capability, parameters):
        if capability == "query_data":
            return self.execute_query(parameters["query"], parameters.get("limit"))
```

#### 3. Separate Client-Server Architecture

We could evolve toward a more formal client-server architecture with clear separation of concerns:

```python
class MCPClient:
    def __init__(self):
        self.servers = {}
        
    def connect_to_server(self, server_id, server_url):
        # Establish connection and request capabilities
        # ...
        
    def invoke_capability(self, server_id, capability_name, parameters):
        # Send request to appropriate server
        # ...
```

### Conclusion

Our implementation of MCP principles in the Social Benefits Assistant addresses the critical limitations of simple message appending approaches without requiring the full complexity of a standardized MCP architecture. By focusing on structured context management, intelligent tool orchestration, and flow control, we've created a system that can handle complex conversations more effectively while making efficient use of resources.

This approach provides a solid foundation that can be extended in the future to incorporate more aspects of the standardized MCP architecture as our needs evolve. The key insight is that even a partial implementation of MCP principles can provide substantial benefits over traditional approaches to building conversational AI systems.
