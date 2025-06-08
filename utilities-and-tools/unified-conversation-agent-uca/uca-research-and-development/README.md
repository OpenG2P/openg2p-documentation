---
description: WORK IN PROGRESS
---

# UCA Research & Development

This is an exploration project to build an AI-based Unified Conversation Agent (UCA) to make the lives of end users better and deliver useful services. UCA will leverage AI technologies to support OpenG2P use cases for social benefit delivery across programs and departments. This intelligent agent will engage directly with callers via voice, providing real-time updates on program statuses and disbursements, informing them about eligibility for additional programs, and enabling seamless program application entirely through phone or voice interactions.

## 1.Speech-to-Text Implementation Using Vosk

### Overview

This documentation covers the implementation of a real-time speech-to-text system using the Vosk speech recognition toolkit. The system captures audio input from the microphone and converts it to text in real-time.

### Model Selection

After evaluating different speech recognition models, we selected Vosk for its offline capabilities and ease of implementation. Two models were tested:

* vosk-model-small-en-us-0.15 (smaller model)
* vosk-model-en-us-0.22 (larger model)

Based on empirical testing, the larger model (en-us-0.22) demonstrated better accuracy in speech recognition compared to the smaller model. While no formal metrics were used for evaluation, hands-on experience showed more reliable transcription results with the larger model.

### Implementation Details

#### Dependencies

* vosk: Speech recognition engine
* sounddevice: Audio input handling
* json: Processing recognition results
* queue: Managing audio data stream

#### Key Components

1. **Model Initialization**

```python
model = vosk.Model("models/vosk-model-small-en-us-0.15")
samplerate = 16000
```

The system initializes with a Vosk model and sets the audio sampling rate to 16kHz, which is the standard for speech recognition.

2. **Audio Capture** The implementation uses a queue-based system to handle audio input:

```python
def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))
```

This callback function captures audio data in real-time and places it in a queue for processing.

3. **Recognition Loop** The main recognition loop:

* Continuously processes audio data from the queue
* Converts speech to text in real-time
* Outputs recognized text when confidence is sufficient

### Usage

1. Ensure the appropriate Vosk model is downloaded and placed in the models directory
2. Run the script
3. Speak into the microphone
4. Press Ctrl+C to stop the recognition

### Performance Considerations

* The larger model (en-us-0.22) requires more computational resources but provides better accuracy
* The system processes audio in real-time with minimal latency
* Queue-based implementation ensures smooth audio capture without data loss

### Future Improvements

* Implement formal accuracy metrics for model comparison
* Add support for multiple languages
* Optimize memory usage for long-running sessions

### Technical Notes

* Audio is captured at 16kHz with 16-bit depth
* Processing occurs in blocks of 8000 samples
* Single channel (mono) audio input is used for optimal recognition\


## 2.Text to Speech using different models

### Text-to-Speech (TTS) Implementation

#### Model Evaluation and Selection

We evaluated three different TTS solutions:

1. **Coqui TTS (Jenny Model)**
   * GitHub: https://github.com/coqui-ai/TTS
   * Implementation used `tts_models/en/jenny/jenny`
   * Voice quality was not satisfactory - produced unexpected voice modulation
   * Resource-intensive and required significant setup
2. **Coqui Tacotron2-DDC**
   * Using `tts_models/en/ljspeech/tacotron2-DDC`
   * Produced good voice quality
   * Drawbacks:
     * Long loading times
     * Lower accuracy compared to alternatives
     * Resource-intensive
3. **pyttsx3**
   * GitHub: https://github.com/nateshmbhat/pyttsx3
   * Selected as final implementation
   * Advantages:
     * Fast response time
     * Simple implementation
     * Reliable performance
     * Minimal resource usage
     * Good voice quality
   * Implementation uses default speech rate of 150

#### Final Implementation Details

The system uses pyttsx3 with the following key components:

1. **Engine Initialization**

```python
def initialize_engine():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    return engine
```

2. **Main TTS Loop**

* Continuous text input processing
* Clean exit functionality
* Simple user interface&#x20;

#### Usage

1. Initialize the TTS engine
2. Enter text when prompted
3. System converts text to speech in real-time
4. Type 'quit' to exit
5. Supports keyboard interrupt (Ctrl+C)

#### Alternative Implementations (For Reference)

**Coqui TTS Implementation**

```python
from TTS.api import TTS
from IPython.display import Audio, display

def stream_tts(text, model_name="tts_models/en/jenny/jenny"):
    tts = TTS(model_name=model_name)
    wav = tts.tts(text)
    return Audio(wav, rate=22050, autoplay=True)
```

**Tacotron Implementation**

```python
def stream_tts(text, model_name="tts_models/en/ljspeech/tacotron2-DDC"):
    tts = TTS(model_name=model_name)
    wav = tts.tts(text)
    sd.play(wav, samplerate=22050)
    sd.wait()
```

### Performance Considerations

* pyttsx3 provides immediate response with minimal latency
* No internet connection required
* Lower resource usage compared to neural network-based solutions
* Suitable for continuous operation



## 3.Integrated Speech System Documentation

### System Overview

The system integrates speech-to-text (STT) and text-to-speech (TTS) capabilities with an API service, creating a complete voice interaction system. Key features include loopback prevention and thread-based conversation management.

### Core Components

#### 1. Audio Processing

* Uses Vosk for speech recognition (model: vosk-model-en-us-0.22)
* Implements pyttsx3 for text-to-speech
* Manages audio through sounddevice with 16kHz sampling rate

#### 2. API Integration

```python
def send_to_uca(text: str, thread_id: str) -> Optional[str]:
    """Send text to UCA API and receive response"""
    payload = {
        'query': text,
        'thread_id': thread_id
    }
    response = requests.post(
        'http://xxxxxx/chat',
        json=payload,
        timeout=10
    )
```

* Implements REST API communication
* Supports conversation threading
* Includes timeout handling (10 seconds)
* Response cleaning functionality

#### 3. Loopback Prevention System

The system implements multiple mechanisms to prevent audio loopback:

1. **Global Processing Flag**

```python
processing_output = False
```

* Tracks when system is outputting speech
* Prevents audio capture during TTS playback

2. **Audio Callback Control**

```python
def audio_callback(indata, frames, time, status):
    if not processing_output:
        q.put(bytes(indata))
```

* Only processes input when not outputting speech
* Uses global flag to control audio capture

3. **Silence Detection**

```python
last_speech_time = time.time()
silence_threshold = 2.0
if current_time - last_speech_time >= silence_threshold:
    # Process speech
```

* Implements 2-second silence threshold
* Prevents rapid-fire speech processing

4. **Queue Management**

```python
while not q.empty():
    q.get()
```

* Clears audio queue before processing new input
* Prevents backlog of audio data

### Error Handling

1. **API Communication**

* Timeout handling for API requests
* Response validation
* Error message feedback through TTS

2. **Audio Processing**

* Exception handling in main loop
* Graceful shutdown on interruption
* Recovery from processing errors

### Thread Management

* Unique thread IDs for conversation tracking
* Format: 'user01\_XX' where XX is the session number
* Maintains conversation context across interactions

### Response Processing

#### Clean Response Function

```python
def clean_response(response: str) -> str:
    """Clean the API response to get only the actual message content"""
    if '================================== Ai Message ==================================' in response:
        message = response.split('================================== Ai Message ==================================')[-1]
        message = message.replace('=', '')
        return message.strip()
    return response
```

* Removes formatting characters
* Extracts relevant message content
* Maintains original response if no cleaning needed

### Usage Flow

1. System initialization
   * Load speech recognition model
   * Initialize TTS engine
   * Configure audio settings
2. Continuous operation loop
   * Listen for speech input
   * Convert speech to text
   * Send to API
   * Process response
   * Convert response to speech
   * Reset for next interaction

### Technical Requirements

* Python 3.x
* vosk
* pyttsx3
* sounddevice
* requests

### Performance Considerations

* Audio processing runs at 16kHz with 16-bit depth
* 8000 sample blocksize for audio processing
* 2-second silence threshold for speech segmentation
* 150 WPM speech rate for TTS

### Future Improvements

1. Dynamic silence threshold adjustment
2. Multiple language support
3. Enhanced error recovery
4. Voice activity detection
5. Configurable audio parameters

### Troubleshooting

1. Audio Loopback Issues
   * Verify speakers aren't feeding into microphone
   * Check processing\_output flag status
   * Confirm silence threshold appropriateness
2. API Communication
   * Check network connectivity
   * Verify thread\_id format
   * Monitor API response times
   * Validate API endpoint status





## 4.Data Preparation and Embedding Creation

### Step 1: Data Preparation and Embedding Creation

#### Overview

The first step involves extracting data from SQL database and creating embeddings using FAISS. This process creates a searchable vector store for efficient similarity searches.

#### Components Used

* LangChain HuggingFace Embeddings
* FAISS Vector Store
* SQLite Database
* all-MiniLM-L6-v2 embedding model

#### Implementation Details

**1. Database Connection and Data Retrieval**

```python
def fetch_programs_from_db():
    conn = sqlite3.connect('pdb')
    cursor = conn.cursor()
    cursor.execute('SELECT pid, mneumonic, description FROM pinfo')
    programs = cursor.fetchall()
    conn.close()
    return programs
```

* Connects to SQLite database
* Retrieves specific fields: pid, mneumonic, description
* Returns data as tuples

**2. Document Creation**

```python
def create_program_documents(programs):
    documents = []
    for pid, mneumonic, description in programs:
        content = f"{mneumonic}: {description}" if description else mneumonic
        doc = Document(
            page_content=content,
            metadata={
                "pid": pid,
                "mneumonic": mneumonic
            }
        )
        documents.append(doc)
    return documents
```

Key features:

* Combines mneumonic and description for context
* Preserves metadata (pid and mneumonic)
* Creates LangChain Document objects
* Handles cases where description might be missing

**3. Embedding Creation and Storage**

```python
def create_and_save_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    programs = fetch_programs_from_db()
    documents = create_program_documents(programs)
    vector_store = FAISS.from_documents(documents, embeddings)
    vector_store.save_local("new_faiss/programs_index")
```

Important aspects:

* Uses all-MiniLM-L6-v2 for embedding generation
* Creates FAISS vector store
* Saves index locally for future use

#### Data Flow

1. SQL Data → Python Objects
2. Python Objects → LangChain Documents
3. Documents → Vector Embeddings
4. Embeddings → FAISS Index

### Technical Considerations

#### 1. Data Structure

* Content structure: `"{mneumonic}: {description}"`
*   Metadata structure:

    ```python
    {
        "pid": unique_identifier,
        "mneumonic": mneumonic_text
    }
    ```

### Error Handling

#### Database Errors

```python
try:
    conn = sqlite3.connect('pdb')
    # ... database operations
except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    conn.close()
```

#### Embedding Creation Errors

```python
try:
    vector_store = FAISS.from_documents(documents, embeddings)
except Exception as e:
    print(f"Embedding creation error: {e}")
```



## 5.Integrated AI Agent System&#x20;

### Architecture Overview

The CombinedProgramAgent creates a AI system that integrates vector search (FAISS), structured database queries (SQL), and language model reasoning through the ReAct architecture.&#x20;

### Core Components

#### 1. Agent Initialization

```python
def __init__(
    self,
    db_path: str,
    faiss_index_path: str,
    llm_model: str = "llama3.2",
    embeddings_model: str = "all-MiniLM-L6-v2",
    num_threads: int = 4
):
```

This initialization sets up three primary components:

* Language Model (LLM) configuration
* Tool initialization (FAISS and SQL)
* ReAct agent setup with system prompt

#### 2. LLM Configuration

```python
def _init_llm(self, model: str, num_threads: int):
    return ChatOllama(
        model=model,
        temperature=0,
        num_thread=num_threads
    )
```

The LLM configuration:

* Uses Ollama for local model deployment
* Sets temperature to 0 for consistent, deterministic responses
* Enables multi-threading for improved performance

#### 3. Tool Integration

**SQL Database Toolkit**

```python
db = SQLDatabase.from_uri(f'sqlite:///{db_path}')
sql_toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
sql_tools = sql_toolkit.get_tools()
```

The SQLDatabaseToolkit provides:

* Query generation from natural language
* Direct SQL execution
* Result summarization
* Schema inspection capabilities

**FAISS Vector Search**

```python
embeddings = HuggingFaceEmbeddings(model_name=embeddings_model)
vector_store = FAISS.load_local(faiss_index_path, embeddings)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
```

The FAISS integration enables:

* Semantic similarity search
* Efficient retrieval of relevant program information
* Configurable number of similar results (k=3)

### ReAct Agent Architecture

#### Understanding ReAct

ReAct (Reasoning and Action) is an agent architecture that combines:

1. Reasoning: Thinking about what to do next
2. Action: Executing tools based on reasoning
3. Observation: Processing tool outputs
4. Reflection: Using results to plan next steps

#### System Prompt Design

```python
system_prompt = """You are a program eligibility advisor that helps users find suitable social benefit programs. Follow these steps for each query:
1. Identify the intent...
2. First, use the program_info tool...
3. For each potentially relevant program...
4. Combine the information...
"""
```

The system prompt structures the agent's behavior by:

* Defining clear steps for processing queries
* Establishing tool usage priorities
* Setting response formatting guidelines
* Implementing error checking protocols

#### Memory Management

```python
memory = MemorySaver()
return create_react_agent(
    self.llm,
    self.tools,
    checkpointer=memory,
    state_modifier=SystemMessage(content=system_prompt)
)
```

The MemorySaver enables:

* Conversation state tracking
* Thread-based memory management
* Consistent context maintenance

### Query Processing Flow

1.  **Query Reception**

    ```python
    def get_response(self, query: str, thread_id: str) -> str:
    ```

    * Receives user query and thread ID
    * Prepares configuration for processing
2. **Tool Selection**
   * Agent decides between FAISS and SQL tools
   * FAISS for semantic search
   * SQL for specific criteria verification
3. **Response Generation**
   * Combines tool outputs
   * Formats according to system prompt
   * Returns structured response

### Understanding SQLDatabaseToolkit

The SQLDatabaseToolkit provides several tools:

1. **Query Generator**
   * Converts natural language to SQL
   * Handles complex query construction
   * Manages table relationships
2. **SQL Executor**
   * Runs generated queries
   * Handles error cases
   * Returns formatted results
3. **Schema Inspector**
   * Analyzes database structure
   * Provides table information
   * Helps in query construction

### Common Challenges and Solutions

#### 1. Library Dependency Conflicts

Solution approaches:

* Use virtual environments
* Pin specific package versions(requirements.txt)
* Document working configurations







## Date-Feb 21st 2025

## <mark style="color:red;">Improving AI Agent Accuracy and Reliability</mark>

### Initial Implementation and Challenges

#### Original Approach

The initial implementation used a combined agent system with:

* FAISS vector store for semantic search
* SQL database for detailed program information
* Basic system prompt for agent guidance

**Prompt Used:**

```
system_prompt = """You are a program eligibility advisor that helps users find suitable social benefit programs. Follow these steps for each query:

1. Identify the intent of the user,if it is greeting then respond naturally to greetings and casual conversation. If its related to Programs/eligibility/schemes then follow the next instructions.
2. First, use the program_info tool to find relevant programs based on the user's situation
3. For each potentially relevant program found, use the SQL tools to check detailed eligibility criteria
4. Combine the information from both sources to provide a complete response that includes:
   - Program name and brief description
   - Key eligibility criteria
   - Whether the user likely qualifies based on their stated situation
   
Keep responses concise but informative. If more information is needed from the user to determine eligibility, ask for specific details.

Remember: 
- Verify eligibility criteria in the database before making definitive statements
- Consider all relevant programs that might apply to the user's situation
- Be clear about what information you're basing your response on"""

```



#### Key Challenges Encountered

1. **Data Quality Issues**
   * Limited program descriptions in FAISS
   * Abstract information leading to ambiguous matches
   * Insufficient context for accurate recommendations
2. **LLM Hallucination**
   * Agent making assumptions beyond available data
   * Mixing up eligibility criteria
   * Providing inaccurate program recommendations
3. **Response Accuracy**
   * Inconsistent response structure
   * Unclear distinction between found and inferred information
   * Missing verification steps

### Evolution of Solutions

#### Attempt 1: Enhanced Prompt Engineering

**Detailed Structured Prompt**

```
system_prompt = """You are a program eligibility advisor that MUST follow these exact steps and ONLY use information from our tools. Never make up or hallucinate information from external sources.
EXACT SEARCH SEQUENCE:
1. FAISS Search (MANDATORY FIRST STEP):
   - Use the program_info tool to search for relevant programs
   - You will receive results in this format for each program:
     * content: "MNEUMONIC: Description of the program"
     * metadata: {"pid": number, "mneumonic": "code"}
   - You must explicitly state all programs found, showing both content and metadata
2. SQL Database Check (MANDATORY SECOND STEP):
   - For each program found in FAISS results, use the SQL tools to query the database
   - Use this exact query structure:
     SELECT * FROM pinfo WHERE pid = [pid_from_faiss] AND mneumonic = '[mneumonic_from_faiss]'
   - You must show the complete database results for each program
3. Response Formation (FINAL STEP):
   - Use ONLY the information retrieved from steps 1 and 2
   - Never add information from external sources or your general knowledge
   - Structure your response like this:
     a. Programs Found (from FAISS):
        - List each program with its exact description and metadata
     b. Eligibility Details (from SQL which is there in the form of sql query):
        - Show the exact eligibility criteria from database
     c. Analysis:
        - Compare user's stated situation against the exact criteria found
        - Only make conclusions based on the data we have
IMPORTANT RULES:
- Never make up program names or criteria
- Never suggest programs that weren't found in our search
- If no programs match in FAISS search, say so clearly
- If you need more information to determine eligibility, ask specific questions based on the criteria you found
- For greetings or non-program queries, respond naturally without using tools
Remember: You are working with a specific database of programs. Only provide information that was explicitly returned by our search tools. If you're unsure about any criteria, show the exact data you found and ask for clarification."""
```

**Improvements Attempted:**

* Strict step-by-step instructions
* Explicit search sequence
* Mandatory tool usage order
* Structured response format

**Results:**

* Some improvement in response structure
* Still faced Hallucination issues
* Didn't fully solve accuracy problems

#### Attempt 2: Data-Centric Approach

**1. Data Quality Enhancement**

* Replaced abstract descriptions with detailed program information
* Improved FAISS embeddings quality
* Better context preservation

**2. Simplified Yet Strict Prompt**

```
system prompt="""You are a program eligibility advisor that helps users find suitable social benefit programs. Follow these steps for each query:
Must follow:give the response only with respect to the content you retrieve from program_info tool and SQL tool,if the content is not there then say "I dont have any idea on that" , Do not hallucinate or give information other than the retrieved info[Highly mandatory]
1. Identify the intent of the user,if it is greeting then respond naturally to greetings and casual conversation. If its related to Programs/eligibility/schemes then follow the next instructions.
2. First, use the program_info tool to find relevant programs based on the user's situation,it will return ID and Mnuemonic, use the ID to retrive the complete details from SQL which in mentioned in next step.
3. For each potentially relevant program found, use the SQL tools to check detailed eligibility criteria
4. Combine the information from both sources to provide a complete response that includes:
   - Program name and brief description
   - Key eligibility criteria
   - Whether the user likely qualifies based on their stated situation
Keep responses concise but informative. If more information is needed from the user to determine eligibility, ask for specific details.
Remember:
- Verify eligibility criteria in the database before making definitive statements
- Consider all relevant programs that might apply to the user's situation
- Be clear about what information you're basing your response on"""
```

**Key Features:**

* Clear hallucination prohibition
* Explicit tool usage instructions
* Strong emphasis on retrieved data only

**3. Improved Data Flow**

1. FAISS returns program ID and Mneumonic
2. SQL lookup using returned IDs
3. Comprehensive information retrieval



## Speech System API Integration&#x20;

### FastAPI Service Implementation:

The system implements a FastAPI-based service that integrates the CombinedProgramAgent with speech capabilities, enabling HTTP-based communication for the speech interface.

#### Components

**1. API Configuration**

```python
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()
```

**2. Agent Initialization**

```python
agent = CombinedProgramAgent(
    db_path='pdb',
    faiss_index_path='/home/veerendra/faiss/programs_index',
    llm_model='llama3.2',
    embeddings_model='all-MiniLM-L6-v2'
)
```

**3. Request Model**

```python
class UserInput(BaseModel):
    query: str
    thread_id: str
```

#### API Endpoints

1. **Health Check**

```python
@app.get("/")
def respond():
    return 'All well'
```

2. **Chat Endpoint**

```python
@app.post("/chat")
def ai_respond(user_input: UserInput):
    query = user_input.query
    thread_id = user_input.thread_id
    response = agent.get_response(query, thread_id)
    return {'ai_message': response}
```

#### Server Configuration

```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

* Listens on all network interfaces
* Uses port 8000
* Enables remote access

### &#x20;TTS Challenges: Pyttsx3

#### Platform-Specific Speech Engines

1. **Windows Environment**
   * Uses SAPI5 (Microsoft Speech API)
   * Advantages:
     * High-quality voice synthesis
     * Natural-sounding output
     * Multiple voice options
     * Good control over speech parameters
   *   Implementation:

       ```python
       engine = pyttsx3.init('sapi5')
       ```
2. **Linux Environment**
   * Uses eSpeak by default
   * Limitations:
     * Robotic voice quality
     * Limited voice options
     * Less natural pronunciation
     * Reduced control over voice parameters



### Ollama Installation and CUDA Permission Issues

#### Error Overview

When I ran the combined\_agent.py, the following error was encountered: attempting to use Ollama with CUDA acceleration,&#x20;

```
ollama._types.ResponseError: llama runner process has terminated: error:status: Permission denied [/usr/local/lib/ollama/cuda_v11/libggml-blas.so]
```

This error indicates a permission issue with the CUDA libraries that Ollama needs to access.

#### Root Causes

1. **Permission Problems**: The Ollama service user doesn't have proper permissions to access CUDA libraries
2. **Ownership Issues**: CUDA library files have incorrect ownership
3. **Installation Conflicts**: Mismatched CUDA versions between system drivers and Ollama requirements

#### Resolution Steps

The issue was resolved through a complete reinstallation of Ollama and proper permission configuration:

1.  **Fix Immediate Permissions**

    ```bash
    sudo chown -R ollama:ollama /usr/local/lib/ollama/
    ```
2.  **Perform Clean Reinstallation**

    ```bash
    # Remove existing installation
    sudo apt purge ollama

    # Download latest version
    curl -fsSL https://ollama.com/install.sh | sh
    ```
3.  **Verify CUDA Compatibility**

    ```bash
    # Check CUDA version supported by current drivers
    nvidia-smi
    ```
4.  **Update NVIDIA Drivers (if needed)**

    ```bash
    sudo apt install nvidia-driver-535 nvidia-cuda-toolkit
    sudo reboot
    ```
5.  **Restart and Verify Service**

    ```bash
    sudo systemctl restart ollama
    sudo journalctl -u ollama.service -b  # Check for service er structure
    ```





### Transitioning from Llama3.2 to DeepSeek:&#x20;

#### Limitations of Llama3.2

When implementing the combined agent system with Llama3.2, we encountered several significant performance issues:

1. **Inconsistent Tool Utilization**
   * The model frequently failed to call the appropriate tools
   * Sometimes ignored the FAISS vector search tool (program\_info)
   * Other times skipped the SQL database tools
   * Resulted in incomplete information gathering
2. **Poor Intent Recognition**
   * Failed to properly identify user intents
   * Confused casual conversation with program inquiries
   * Responded inappropriately to queries
3. **Prompt Adherence Issues**
   * Did not consistently follow the structured approach defined in prompts
   * Skipped critical verification steps
   * Provided responses without gathering necessary information
4. **Reasoning Limitations**
   * Struggled with complex multi-step reasoning
   * Failed to integrate information from multiple sources
   * Made conclusions without proper verification

#### Motivation for DeepSeek Implementation

Due to these limitations, we explored the DeepSeek model (deepseek-r1:8b) for the following reasons:

1. **Advanced Capabilities**
   * Larger parameter count (8B vs Llama3.2)
   * Better reported performance on reasoning tasks
   * Improved instruction-following capabilities
   * Enhanced context understanding
2. **Quality Improvements**
   * More consistent reasoning patterns
   * Better adherence to structured prompts
   * Improved multi-step planning
   * Higher accuracy in understanding complex queries
3. **Integration Potential**
   * Compatible with Ollama deployment
   * Designed for assistant-like applications
   * Support for complex reasoning chains

### DeepSeek Model Compatibility Issues

#### Error Overview

When attempting to use the DeepSeek model with tools in the CombinedProgramAgent, the following error occurred:

```
ollama._types.ResponseError: registry.ollama.ai/library/deepseek-r1:8b does not support tools
```

This error indicates that the DeepSeek model, as implemented in Ollama, doesn't support the function calling/tools API that LangGraph and LangChain require for agent implementation.

#### Technical Background

1. **Tool-Using Capability**: Modern LLMs require specific capabilities to utilize tools/function calling:
   * Standardized input/output formats
   * Support for specific JSON schema interpretation
   * Built-in capability to generate structured tool-use requests
2. **DeepSeek Limitations**: The current DeepSeek implementation in Ollama:
   * Lacks the necessary function-calling API
   * Cannot parse or generate the required JSON structure
   * Is not fine-tuned for tool-using applications





## Enhanced Agent Architecture and Tool Control



This documentation analyzes the evolution of the CombinedProgramAgent system, focusing on architectural improvements that resolved critical limitations in the original implementation. The agent serves as a program eligibility advisor that utilizes vector search (FAISS) and structured database queries (SQL) to provide accurate program recommendations based on user inquiries.

### Original Implementation Analysis

#### Architecture Overview

The original implementation featured:

1. A standard LangChain ReAct agent architecture
2. Direct integration of SQL and FAISS tools
3. A basic system prompt guiding agent behavior



#### Critical Limitations

**1. Tool Sequencing Problems**

The original implementation allowed the agent to use tools in any order, resulting in:

```python
# Original tool initialization - no sequencing enforcement
sql_toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
sql_tools = sql_toolkit.get_tools()

# FAISS tool created but not prioritized
faiss_tool = create_retriever_tool(
    retriever,
    "program_info",
    "Search for program information and descriptions"
)

# Tools combined without hierarchy
return sql_tools + [faiss_tool]
```

This approach gave equal priority to all tools, allowing the agent to:

* Execute SQL queries without first identifying relevant programs through FAISS
* Misunderstand the dependent relationship between tools
* Produce incomplete or erroneous information

**2. Hallucination Issues**

The original system permitted hallucination through:

1. Lack of strict data validation
2. No explicit response verification
3. Basic prompt structure without enforced boundaries:

```python
pythonCopysystem_prompt = """You are a program eligibility advisor...
Must follow:give the response only with respect to the content you retrieve from program_info tool and SQL tool,
if the content is not there then say "I dont have any idea on that" , Do not hallucinate...
"""
```

Despite these instructions, the agent would often invent program details, combine real and fabricated information, or provide erroneous eligibility assessments.



### Enhanced Implementation Analysis

The updated implementation represents a significant architectural advancement with several sophisticated mechanisms:

**1. Enforced Tool Sequencing**

```python
faiss_tool = create_retriever_tool(
    retriever,
    "program_search",
    "MUST USE FIRST! Converts user needs to program IDs. Returns: [ID|Program Name|Brief Description]"
)

sql_tools = [
    Tool.from_function(
        func=self._wrap_sql_tool(tool),
        name=tool.name,
        description=f"REQUIRES PROGRAM ID FROM program_search. {tool.description} Input must include 'program_id:' followed by ID."
    ) for tool in sql_toolkit.get_tools()
]

# FAISS tool intentionally positioned first
return [faiss_tool] + sql_tools
```

This implementation enforces a strict tool hierarchy through:

1. Clear "MUST USE FIRST" directive in the FAISS tool description
2. SQL tools explicitly requiring input from the FAISS tool
3. Order-dependent tool list structure

**2. SQL Tool Wrapper Mechanism**

```python
def _wrap_sql_tool(self, tool: Tool):
    def wrapped_tool(
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        if "program_id:" not in query:
            return "Error: Missing program_id. First use program_search to get valid IDs."
        return tool._run(query, run_manager)
    return wrapped_tool
```

This wrapper operates through:

1. **Function Closure**: Creates a new function that encapsulates the original tool
2. **Input Validation**: Checks for the presence of "program\_id:" in the query
3. **Error Redirection**: Returns an explicit error message rather than executing the tool when validation fails
4. **Transparent Execution**: Passes valid requests to the original tool with all necessary context

The wrapper establishes a dependency chain that ensures:

* FAISS search must be used first to get program IDs
* SQL tools can only operate on previously identified programs
* The agent receives immediate feedback when attempting to bypass the workflow

**3. Response Validation System**

The enhanced implementation introduces a sophisticated response validation mechanism:

```python
pythonCopydef _get_known_programs(self) -> Dict[str, str]:
    try:
        return {row['id']: row['name'] 
                for row in self.db.run("SELECT id, name FROM programs")}
    except:
        return {}

def _validate_response(self, response: str) -> str:
    # Allow any response that doesn't mention programs (greetings/smalltalk)
    if not any(prog.lower() in response.lower() for prog in self.known_programs.values()):
        return response
        
    # Program-related responses must contain known program names
    if any(prog.lower() in response.lower() for prog in self.known_programs.values()):
        return response
        
    return "I need more details to properly check program eligibility. Please share your situation."
```

This validation system:

1. Builds a repository of known program names from the database
2. Applies different validation rules based on response content
3. Allows conversational responses without program references to pass unchanged
4. Verifies that program-related responses only mention known programs
5. Provides a fallback response for potential hallucinations

**4. Improved System Prompt**

The updated system prompt incorporates several advanced features:

```python
pythonCopysystem_prompt = """You are a program eligibility advisor. Follow these STRICT RULES:

1. INPUT CLASSIFICATION:
   - If the user message is a greeting or small talk (e.g., "hello", "hi", "how are you?"):
     * Respond politely but briefly
     * DO NOT USE ANY TOOLS
     * Keep response under 15 words
   - For program-related queries:
     * MUST follow the workflow below

2. PROGRAM WORKFLOW:
   a. Use program_search FIRST
   b. For each found ID: Use SQL tools with 'program_id:<ID>'
   c. Compare user details to SQL criteria

3. RESPONSE RULES:
   - Program responses MUST follow format:
     [Program Name] (ID: <id>)
     - Eligibility: <quoted criteria>
     - Match: <Yes/Partial/No> because <comparison>
   - No programs found: "No matching programs found"

PROHIBITIONS:
- Inventing programs/criteria
- Using SQL without program_search first
- Speculating beyond retrieved data"""
```

Key improvements include:

1. Explicit greeting identification with examples
2. Clear prohibition on tool usage for greetings
3. Mandatory response format for standardization
4. Specific prohibition clauses
