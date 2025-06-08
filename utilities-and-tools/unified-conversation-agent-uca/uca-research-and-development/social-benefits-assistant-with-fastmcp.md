---
description: >-
  FastMCP is a higher-level, decorator-based Python framework that simplifies
  building Model Context Protocol (MCP) servers by providing an  interface for
  registering tools, resources, and prompts.
---

# Social Benefits Assistant with FastMCP

***

## Introduction

The Social Benefits Assistant is a sophisticated system designed to help users navigate social benefit programs and handle grievances. Built using the Model Context Protocol (MCP) framework with FastMCP implementation, it provides a modern, scalable architecture for AI-powered assistance.

### Key Features

* **Program Eligibility Assessment**: Helps users find relevant social programs and assess their eligibility
* **Grievance Management**: Handles user complaints, creates tickets, and tracks status
* **Natural Language Interface**: Powered by Ollama LLMs for conversational interactions
* **Modular Architecture**: Separate MCP servers for different subsystems
* **Standardized Communication**: Uses MCP protocol for all inter-component communication

### Why FastMCP?

FastMCP provides a cleaner, more ergonomic interface for building MCP servers. Key advantages include:

* Decorator-based tool registration
* Built-in support for resources and prompts
* Standard transport mechanisms (stdio, SSE, WebSocket)
* Proper context management
* Type-safe implementations

***

## Architecture Overview

The Social Benefits Assistant uses a distributed architecture based on the Model Context Protocol (MCP). The system consists of three main components:

### System Architecture:

<figure><img src="../../../.gitbook/assets/Screenshot 2025-05-14 085900.png" alt=""><figcaption></figcaption></figure>

### Key Architectural Decisions

1. **Separation of Concerns**: Each subsystem (eligibility, grievance) has its own MCP server
2. **Standard Protocol**: All communication uses the MCP protocol
3. **LLM Integration**: Ollama serves as the intelligent routing layer
4. **Tool-Based Interface**: Each server exposes functionality through MCP tools
5. **Resource Management**: Static data is exposed through MCP resources
6. **Prompt Templates**: Response formatting is handled through MCP prompts

### Communication Flow

1. User sends query to the MCP client
2. Client uses Ollama to analyze intent
3. Based on intent, client calls appropriate MCP server(s)
4. Server processes request using tools
5. Server returns results via MCP protocol
6. Client formats response using prompts and Ollama
7. Final response is presented to user

***

## FastMCP Integration

### What is FastMCP?

FastMCP is a higher-level interface for the Model Context Protocol that simplifies the creation of MCP servers. It provides a more ergonomic API compared to the low-level MCP implementation.

### Integration Approach

Our integration of FastMCP involved:

#### 1. Server Creation

Instead of using the low-level `Server` class, we use `FastMCP`:

```python
from mcp.server.fastmcp import FastMCPeligibility_server = FastMCP(    name="EligibilityServer",    instructions="Eligibility subsystem for Social Benefits Assistant...")
```

#### 2. Tool Registration

Tools are registered using decorators instead of manual registration:

```python
@eligibility_server.tool(description="Extract user profile details from query")async def extract_user_details(query: str, ctx: Context) -> UserProfile:    # Tool implementation    pass
```

#### 3. Resource Definition

Resources are defined with decorators for dynamic content:

```python
@eligibility_server.resource("program://{program_id}/eligibility")async def program_eligibility_resource(program_id: int) -> str:    # Resource implementation    pass
```

#### 4. Prompt Templates

Prompts are registered for response formatting:

```python
@eligibility_server.prompt()def eligibility_response(programs: List[Dict], analysis: List[Dict], user_profile: Dict) -> List:    # Prompt implementation    pass
```

#### 5. Context Management

FastMCP provides a `Context` object for accessing MCP features:

```python
async def my_tool(param: str, ctx: Context) -> str:    # Access session, logging, progress reporting    await ctx.report_progress(50, 100)    await ctx.info("Processing...")    return result
```

### Benefits of FastMCP Integration

1. **Cleaner Code**: Decorator-based registration is more intuitive
2. **Type Safety**: Better type hints and validation
3. **Built-in Features**: Automatic parameter validation, error handling
4. **Standard Patterns**: Follows Python conventions
5. **Easier Testing**: Better separation of concerns

***

## System Components

### Overview

The Social Benefits Assistant consists of three main components:

1. **Eligibility Server**: Handles program search and eligibility assessment
2. **Grievance Server**: Manages user complaints and ticket tracking
3. **MCP Client**: Orchestrates communication and provides user interface

Each component is built using FastMCP and follows standard MCP patterns.

### Component Interaction

```mermaid
A[User Query] --> B[MCP Client]    B --> C{Intent Analysis}    C -->|Eligibility Query| D[Eligibility Server]    C -->|Grievance Query| E[Grievance Server]    D --> F[Database]    E --> G[Database]    D --> H[FAISS Index]    B --> I[Ollama LLM]
```

### Database Architecture

The system uses two databases:

1. **Program Database** (`program_db`):
   * Stores program information
   * Used by Eligibility Server
   * Includes FAISS index for semantic search
2. **Grievance Database** (`grievance_db.sqlite`):
   * Stores user memberships
   * Tracks complaints and tickets
   * Used by Grievance Server

***

## Eligibility Server

The Eligibility Server is responsible for helping users find relevant social benefit programs and assess their eligibility.

### Architecture

```python
eligibility_server = FastMCP(    name="EligibilityServer",    instructions="Eligibility subsystem for Social Benefits Assistant...")
```

### Key Components

#### 1. Database Connection

Uses `aiosqlite` for async database operations:

```python
@asynccontextmanagerasync def get_db_connection(db_path: str):    conn = await aiosqlite.connect(db_path)    conn.row_factory = aiosqlite.Row    try:        yield conn    finally:        await conn.close()
```

#### 2. FAISS Integration

Semantic search using FAISS and HuggingFace embeddings:

```python
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")vector_store = FAISS.load_local(faiss_index_path, embeddings)retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
```

#### 3. Tools

**extract\_user\_details**

Extracts user profile information from queries:

```python
@eligibility_server.tool(description="Extract user profile details from query")async def extract_user_details(query: str, ctx: Context) -> UserProfile:    # Implementation using pattern matching and NLP
```

**search\_programs**

Finds relevant programs using semantic search:

```python
@eligibility_server.tool(description="Search for relevant programs based on query")async def search_programs(query: str, ctx: Context) -> List[int]:    # FAISS-based semantic search
```

**analyze\_eligibility**

Assesses eligibility for specific programs:

```python
@eligibility_server.tool(description="Analyze program eligibility based on user profile")async def analyze_eligibility(    program_ids: List[int],     user_profile: Optional[UserProfile] = None,    ctx: Context = None) -> EligibilityResult:    # Rule-based eligibility analysis
```

#### 4. Prompts

**eligibility\_response**

Formats eligibility results for user presentation:

```python
@eligibility_server.prompt()def eligibility_response(programs: List[Dict], analysis: List[Dict], user_profile: Dict) -> List:    # Response formatting logic
```

#### 5. Resources

**program\_eligibility\_resource**

Provides eligibility information for specific programs:

```python
@eligibility_server.resource("program://{program_id}/eligibility")async def program_eligibility_resource(program_id: int) -> str:    # Returns program eligibility criteria
```

### Data Models

#### UserProfile

```python
class UserProfile(BaseModel):    income_level: Optional[str] = None    family_size: Optional[int] = None    location: Optional[str] = None    housing_status: Optional[str] = None    employment_status: Optional[str] = None    age: Optional[int] = None    # ... other fields
```

#### ProgramInfo

```python
class ProgramInfo(BaseModel):    id: int    name: str    description: str    eligibility_criteria: str    benefits: str    application_process: str
```

#### EligibilityAnalysis

```python
class EligibilityAnalysis(BaseModel):    program_id: int    program_name: str    eligibility_likelihood: Literal["High", "Medium", "Low", "Unknown"]    matching_criteria: List[str]    missing_information: List[str]
```

***

## Grievance Server

The Grievance Server handles user complaints, ticket creation, and status tracking.

### Architecture

```python
grievance_server = FastMCP(    name="GrievanceServer",    instructions="Grievance subsystem for Social Benefits Assistant...")
```

### Key Components

#### 1. Tools

**identify\_user\_id**

Checks if query contains a valid USER ID:

```python
@grievance_server.tool(description="Identify if a user input contains a valid USER ID format")async def identify_user_id(query: str, ctx: Context) -> UserIdResult:    # Regex-based pattern matching for USER### format
```

**verify\_user**

Verifies user credentials and retrieves information:

```python
@grievance_server.tool(description="Verify if a user ID exists and retrieve user information")async def verify_user(user_id: str, ctx: Context) -> UserVerificationResult:    # Database lookup and verification
```

**process\_complaint**

Analyzes complaints for completeness:

```python
@grievance_server.tool(description="Process a complaint and determine if enough information has been collected")async def process_complaint(    complaint: str,     previous_parts: Optional[List[str]] = None,    is_follow_up: bool = False,    ctx: Context = None) -> ComplaintAnalysis:    # NLP-based complaint analysis
```

**create\_ticket**

Creates support tickets for complaints:

```python
@grievance_server.tool(description="Create a ticket in the database for a grievance")async def create_ticket(    user_id: str,     complaint: str,     program_id: Optional[int] = 0,    ctx: Context = None) -> TicketDetails:    # Ticket generation and database insertion
```

**check\_status**

Checks program enrollment or ticket status:

```python
@grievance_server.tool(description="Check status of a program enrollment or specific ticket")async def check_status(    user_id: str,     ticket_id: Optional[str] = None,    ctx: Context = None) -> StatusCheckResult:    # Status retrieval from database
```

#### 2. Prompts

* **user\_verification\_response**: Formats successful verification
* **verification\_failed\_response**: Handles failed verification
* **ticket\_creation\_response**: Confirms ticket creation
* **status\_check\_response**: Presents status information

#### 3. Resources

* **user\_status\_resource**: Provides user status information
* **ticket\_details\_resource**: Returns ticket details

### Data Models

#### UserDetails

```python
class UserDetails(BaseModel):    user_id: str    user_name: str    status: Optional[str] = None    enrollment_date: Optional[str] = None    program_id: Optional[int] = None
```

#### ComplaintAnalysis

```python
class ComplaintAnalysis(BaseModel):    complaint: str    enough_detail: bool = False    program_mentioned: str = "Unspecified"    issue_category: str = "Other"    missing_information: List[str] = Field(default_factory=list)
```

***

## MCP Client

The MCP Client serves as the central orchestrator, connecting to Ollama LLM and routing queries to appropriate MCP servers.

### Architecture

The client implements the MCP protocol to communicate with FastMCP servers:

```python
class MCPClientApp:    def __init__(        self,        eligibility_url: str = "http://localhost:8000/sse",        grievance_url: str = "http://localhost:8001/sse",        ollama_url: str = "http://localhost:11434",        model: str = "llama2:8b"    ):        # Initialize connections
```

### Key Features

#### 1. Ollama Integration

Direct integration with Ollama for LLM capabilities:

```python
class OllamaClient:    async def generate(self, prompt: str, system_prompt: str = None) -> str:        # Ollama API communication
```

#### 2. Intent Analysis

Determines which subsystem to use:

```python
async def analyze_intent(self, query: str) -> str:    # Rule-based intent classification    # Returns "eligibility" or "grievance"
```

#### 3. Server Connection

Establishes SSE connections to MCP servers:

```python
async def connect_to_servers(self):    eligibility_streams = await sse_client(self.eligibility_url)    self.eligibility_session = await self._create_session(eligibility_streams)        grievance_streams = await sse_client(self.grievance_url)    self.grievance_session = await self._create_session(grievance_streams)
```

#### 4. Query Processing

Routes queries based on intent:

```python
async def process_query(self, query: str) -> str:    intent = await self.analyze_intent(query)        if intent == "grievance":        return await self.process_grievance_query(query)    else:        return await self.process_eligibility_query(query)
```

#### 5. Tool Calling

Uses MCP protocol to call server tools:

```python
# Example: Calling eligibility tooluser_details = await self.eligibility_session.call_tool(    "extract_user_details",    {"query": query, "ctx": {}})
```

### Conversation Management

The client maintains conversation history with Ollama:

```python
# Conversation history is tracked in OllamaClientself.conversation_history = []# History is included in each requestmessages = [    {"role": "system", "content": system_prompt},    *self.conversation_history,    {"role": "user", "content": prompt}]
```
