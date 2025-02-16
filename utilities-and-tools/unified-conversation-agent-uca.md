---
description: WORK IN PROGRESS
---

# Unified Conversation Agent (UCA)

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





