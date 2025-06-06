**dragons96**

 - [521274311@qq.com](mailto:521274311@qq.com)# Elpis Agent

[中文文档](README_zh.md) | English

An ultra-lightweight command-line AI coding assistant tool that mimics Cursor implementation. Elpis is an intelligent code assistant based on LangChain and OpenAI API that helps developers with code writing, file operations, and project management through natural language interaction.

> 🎓 **Learning Project**: This is a minimalist project that is perfect for learning and understanding the working principles of AI coding assistants such as Cursor. Very suitable for developers who want to explore the basic principles of AI driven development tools.

## Features

- 🤖 **Intelligent Conversation**: Natural language interaction based on large language models
- 📁 **File Operations**: Support for reading and writing file contents
- 💻 **Command Execution**: Execute terminal commands (with user confirmation)
- 🔧 **Tool Integration**: Built-in various development tools and features
- 🎯 **Continuous Dialogue**: Support for multi-turn conversations with context preservation
- ⚙️ **Configurable**: Support for custom models, temperature, and other parameters
- 🧠 **Persistent Memory**: SQLite-based conversation history with automatic persistence across sessions
- 🔍 **Codebase Indexing**: Intelligent codebase analysis and semantic search capabilities
- 🌐 **Multi-language Support**: Built-in internationalization (i18n) support
- 🎛️ **Dual Model Architecture**: Separate models for chat and tool operations for optimized performance
- 🏭 **Model Factory**: Flexible model initialization supporting multiple providers and types
- 💾 **Session Management**: Automatic session isolation and memory persistence using LangGraph checkpoints
- ✅ **User Confirmation**: Interactive confirmation for dangerous operations (file creation/deletion, command execution)

## Quick Start (Recommended)

### Run with uvx (No Installation Required)

The easiest way to use Elpis Agent is with `uvx`, which requires no local installation:

```bash
# From PyPI
uvx --from elpis-agent elpis --env_file /path/to/.env --lang [en|zh]

# From GitHub
uvx --no-cache --from https://github.com/dragons96/elpis-agent.git elpis --env_file /path/to/.env --lang [en|zh]

# From Gitee
uvx --no-cache --from https://gitee.com/dragons96/elpis-agent.git elpis --env_file /path/to/.env --lang [en|zh]
```

This command will:

- Automatically download and run the latest version of elpis-agent
- Use your custom environment file for configuration
- No need for local installation or virtual environment setup
- Always get the latest features and bug fixes

You can also use 'uvx' to directly run the UI interface without the need for local installation:

```bash
# From PyPI
uvx --from elpis-agent[ui] elpis-ui --env_file /path/to/.env --lang [en|zh]
# From Github
uvx --no-cache --from https://github.com/dragons96/elpis-agent.git --with langgraph-cli[inmem] elpis-ui --env_file /path/to/.env --lang [en|zh]

# From Gitee
uvx --no-cache --from https://gitee.com/dragons96/elpis-agent.git --with langgraph-cli[inmem] elpis-ui --env_file /path/to/.env --lang [en|zh]
```

This will:

- Automatically download and run the latest version with UI interface
- Use your custom environment file for configuration
- No need for local installation or virtual environment setup
- Open a web interface in your browser for interactive use

### Requirements

- Python >= 3.11
- OpenAI API Key
- Create a `.env` file with your configuration (see Configuration section below)

## Development Setup

### For Secondary Development

If you want to modify the code or contribute to the project, follow these steps:

1. Clone the repository

```bash
git clone <repository-url>
cd elpis-agent
```

2. Create virtual environment

```bash
uv venv
.venv\Scripts\activate
```

3. Install dependencies

```bash
uv pip install -e .
```

4. Configure environment variables

```bash
cp .env.example .env
```

## Configuration

Create a `.env` file and fill in the necessary configurations:

```env
# Chat Model Configuration
CHAT_BASE_URL=https://api.openai.com/v1
CHAT_API_KEY=your_openai_api_key_here
CHAT_MODEL=gpt-4o-mini
CHAT_MODEL_PROVIDER=openai
CHAT_MODEL_TYPE=chat
CHAT_TEMPERATURE=0.3

# Embedding Model Configuration (Optional - for codebase indexing)
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=your_openai_api_key_here
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_MODEL_PROVIDER=openai
EMBEDDING_MODEL_TYPE=embedding
EMBEDDING_TEMPERATURE=0.3

# Model Key Prefixes
CHAT_MODEL_KEY_PREFIX=CHAT
EMBEDDING_MODEL_KEY_PREFIX=EMBEDDING

# General Settings
SYSTEM_PROMPT=                    # Custom system prompt (optional)
MAX_MEMORY_MESSAGES=20           # Maximum messages to keep in memory
LANG=zh                          # Interface language (zh/en)

# UI Configuration (for LangGraph UI mode)
LANGGRAPH_API_URL=http://localhost:8123  # LangGraph UI server URL
```

### Configuration Notes

- **Chat Model**: Required for all functionality
- **Embedding Model**: Optional, only needed for codebase indexing and semantic search
- **Language Settings**: Set `LANG=en` for English interface or `LANG=zh` for Chinese
- **UI Mode**: When using `elpis --ui`, the LangGraph UI will be available at the configured URL

## Usage

### Command Line Interface

You can start Elpis Agent using elpis (recommended) or after local installation:

```bash

elpis
```

Or run directly with uv:

```bash
uv run elpis
```

### UI Interface

Elpis Agent also provides a web-based UI interface for easier interaction:

#### Local Installation and Run

After installation, you can start the UI interface using:

```bash
elpis-ui
```

Or run directly with UV:

```bash
uv run elpis-ui
```

### Interactive Commands

- Type your questions or requests in natural language
- Use `exit` or `quit` to end the session
- The agent can help with:
  - Code writing and debugging
  - File reading and modification
  - Terminal command execution
  - Project structure analysis
  - Development guidance

### Example Usage

```
> Can you help me create a Python function to calculate fibonacci numbers?
> Read the contents of main.py file
> Run the test command to check if everything works
> Help me refactor this code to make it more efficient
```

### Memory Persistence Examples

```bash
# First session
> Hello, my name is Alice and I'm working on a Python project
> What's my name?  # Agent remembers: Alice

# After restarting the application with same session
> Do you remember my name?  # Agent still remembers: Alice
> What project was I working on?  # Agent remembers: Python project
```

```python
# Cross-session memory persistence example
agent1 = LangGraphElpisAgent(chat_model=chat_model, session_id="project_analysis")
agent1.ask("Please analyze the main.py file")
# ... conversation continues ...

# Later, resume the same session
agent2 = LangGraphElpisAgent(chat_model=chat_model, session_id="project_analysis")
agent2.ask("What did we discuss about main.py earlier?")  # Agent remembers previous context

# User confirmation for dangerous operations
agent = LangGraphElpisAgent(chat_model=chat_model)
agent.ask("Please create a new config file with database settings")
# Output:
# [Elpis] Detected dangerous operation requiring confirmation:
#   1. create_file
#      target_file: config.json
#      content: {"database": {"host": "localhost", "port": 5432}}
# 
# Please confirm whether to execute the above operation (y/n): y
# [Elpis] User confirmed, executing operation...
```

**Note**: The agent automatically creates a `.elpis/memory.db` file in your current working directory to store conversation history. Different projects will have separate memory databases.

## Project Structure

```
elpis-agent/
├── src/elpis/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Main entry point for CLI
│   ├── langgraph_agent.py   # LangGraph-based agent with SQLite memory
│   ├── tools.py             # Tool definitions and implementations
│   ├── prompts.py           # Prompt templates
│   ├── constants.py         # Constants and configurations
│   ├── codebase.py          # Codebase indexing and semantic search
│   ├── factories/           # Factory pattern implementations
│   │   ├── __init__.py
│   │   ├── model_factory.py      # Model factory for flexible initialization
│   │   └── checkpointer_factory.py # Checkpointer factory for memory management
│   ├── i18n/                # Internationalization support
│   │   ├── __init__.py
│   │   ├── en.py            # English language support
│   │   └── zh.py            # Chinese language support
│   └── ui/                  # Web UI components
│       ├── __init__.py
│       ├── graph.py         # LangGraph UI integration
│       ├── graph_main.py    # UI main entry point
│       └── langgraph.json   # LangGraph configuration
├── tests/                   # Test files
├── docs/                    # Documentation
├── .env.example             # Environment variables template
├── pyproject.toml           # Project configuration
├── README.md                # Project documentation (English)
├── README_zh.md             # Project documentation (Chinese)
└── LICENSE                  # License file
```

## Agent Workflow

```mermaid
flowchart TD
    %% Application Startup Phase
    A[Start Application] --> B{Select Interface Mode}
  
    %% CLI Mode Branch
    B -->|CLI Mode| C1[Load Environment Variables]
    C1 --> C2[Initialize Language Settings]
    C2 --> C3{Embedding Model Available?}
    C3 -->|Yes| C4[Initialize Codebase Index]
    C3 -->|No| C5[Skip Codebase Indexing]
    C4 --> C6[Create Agent Instance]
    C5 --> C6
    C6 --> C7[Wait for User Input]
  
    %% CLI User Interaction Loop
    C7 --> C8{Input Type Detection}
    C8 -->|Exit Command| END[Exit Application]
    C8 -->|Index Command| C9{Codebase Exists?}
    C8 -->|User Question| C10[Process User Message]
  
    C9 -->|Yes| C11[Execute Codebase Indexing]
    C9 -->|No| C12[Show Prompt Message]
    C11 --> C7
    C12 --> C7
  
    %% CLI Message Processing Flow
    C10 --> C13[Invoke Chat Model]
    C13 --> C14[Stream Response Output]
    C14 --> C15{Contains Tool Calls?}
    C15 -->|No| C16{Task Completed?}
    C15 -->|Yes| C17[Execute Tool Calls]
    C16 -->|Yes| C7
    C16 -->|No| C18[Add Continue Prompt]
    C17 --> C19[Process Tool Results]
    C18 --> C13
    C19 --> C18
  
    %% UI Mode Branch
    B -->|UI Mode| U1[Start LangGraph UI Service]
    U1 --> U2[Initialize Configuration]
    U2 --> U3[Load Agent Graph]
    U3 --> U4[Start Web Interface]
    U4 --> U5[Listen for Web Requests]
  
    %% UI Request Processing Loop
    U5 --> U6[Process Web Request]
    U6 --> U7[Execute Agent Graph]
    U7 --> U8[Return Response Result]
    U8 --> U5
  
    %% Style Definitions
    classDef startNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef endNode fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef processNode fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef toolNode fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef uiNode fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
  
    class A startNode
    class END endNode
    class C13,C14,U7 processNode
    class C17,C19 toolNode
    class U1,U4,U5 uiNode
```

## Core Components

### ElpisAgent

The core AI agent class responsible for:

- Managing interactions with large language models (supports dual-model architecture)
- Handling tool calls and message flows
- Maintaining conversation context
- Integrating codebase indexing and search capabilities
- **SQLite-based Persistent Memory**: Uses SQLite database for reliable memory storage
- **Session Isolation**: Each conversation session maintains separate memory context
- **Cross-session Memory Recovery**: Automatically restores conversation history when resuming sessions
- **Memory Management**: Automatic cleanup of old sessions and efficient memory usage
- **Thread Safety**: Safe for concurrent access across multiple sessions
- **Automatic Persistence**: All conversations are automatically saved without manual intervention
- **User Confirmation System**: Interactive confirmation for dangerous operations using LangGraph interrupt functionality
  - Automatic detection of risky operations (file creation/deletion, command execution)
  - Real-time user interaction through command-line interface
  - Graceful handling of user approval/rejection decisions
  - Detailed operation information display for informed decision-making

### CodebaseIndexer

Intelligent codebase analysis component:

- Semantic search across project files
- Support for multiple programming languages
- Automatic gitignore filtering
- Vector-based document indexing
- Configurable text chunking strategies

### Model Factory

Flexible model initialization system:

- Support for multiple model providers (OpenAI, etc.)
- Chat and embedding model types
- Environment-based configuration
- Prefix-based model selection

### Tools

Built-in tools include:

- **read_file**: Read file contents
- **run_terminal_cmd**: Execute terminal commands with user confirmation

### Memory Management

The agent implements persistent memory management using SQLite:

- **SQLite-based Storage**: Conversation history stored in `.elpis/memory.db`
- **Session Isolation**: Different session IDs maintain separate conversation histories
- **Automatic Persistence**: Memory survives application restarts
- **LangGraph Checkpoints**: Built on LangGraph's checkpoint system for reliability
- **Thread Safety**: Concurrent access support with built-in locking mechanisms
- **Auto-initialization**: Database and directory created automatically on first run

### Internationalization (i18n)

Multi-language support:

- Language detection and selection
- Localized user interface messages
- Extensible language pack system

## Configuration

Environment variables can be configured in the `.env` file:

### Chat Model Configuration

| Variable                | ion                                 | Default                   |
| ----------------------- | ----------------------------------- | ------------------------- |
| `CHAT_BASE_URL`       | Chat model API                      | `https://apenai.com/v1` |
| `CHAT_API_KEY`        | Chat model API                      | -                         |
| `CHAT_MODEL`          | Chat model name                 g1` |                           |
| `CHAT_MODEL_PROVIDER` | Chat model provr (openlama)         | `i`                     |
| `CHAT_MODEL_TYPE`     | Chat model type                     |                           |
| `CHAT_TEMPERATURE`    | Chat model temperature              | `0.3`                   |

### Embedd ing Model C onfiguration

| Variable                      | Description                                        | Default |
| ----------------------------- | -------------------------------------------------- | ------- |
| `EMBEDDING_BASE_URL`        | Embedding model APIe URL                           |         |
| `EMBEDDING_API_KEY `        | Embedding model API key                            |         |
| `EMBEDDING_MODEL `          | Embedding model name                               |         |
| `EMBEDDING_MODEL_PROVIDER ` | Embedding model provider (openai, ollama)          |         |
| `EMBEDDING_MODEL_TYPE`      | Embedding model type                      mbedding |         |
| `EMBEDDING_TEMPERATU`       | Embedding model    temperature                     | `0.3` |

### Model Key Prefixes

| Variable                       | Description                              | Defalut |
| ------------------------------ | ---------------------------------------- | ------- |
| `CHAT_MODEL_KEY_PREFIX`      | Prefix for chat model configuration      |         |
| `EMBEDDING_MODEL_KEY_PREFIX` | Prefix for embedding model configuration |         |

### General Settings

| Variable          | Description                | Default |
| ----------------- | -------------------------- | ------- |
| `SYSTEM_PROMPT` | Custom system prompt       | -       |
| `LANG`          | Interface language (zh/en) | `zh`  |

### Memory Configuration

The SQLite-based memory system automatically manages conversation history:

- **Database Location**: `.elpis/memory.db` in current working directory
- **Session Management**: Each session ID maintains separate conversation threads
- **Automatic Cleanup**: No manual configuration required
- **Persistence**: Conversations survive application restarts
- **Thread Safety**: Built-in support for concurrent access

### User Confirmation Configuration

The agent includes a safety system that requires user confirmation for potentially dangerous operations:

- **Dangerous Operations**: File creation, deletion, editing, and command execution
- **Interactive Confirmation**: Real-time prompts through command-line interface
- **Customizable**: Can be configured to include/exclude specific operations
- **Graceful Handling**: Proper cancellation and error handling for rejected operations

```python
# Customize dangerous operations list
agent.DANGEROUS_TOOLS = {
    'create_file',
    'delete_file', 
    'edit_file',
    'run_terminal_cmd'
}

# Disable confirmation for specific tools
agent.DANGEROUS_TOOLS.discard('create_file')

# Disable all confirmations
agent.DANGEROUS_TOOLS = set()
```

### Model Configurati

on Prefixes

The model factory supports flexible configuration using prefixes:

- `CHAT_MODEL_KEY_PRE FIX` - For chat model configuration
- `TOOL_MODEL_KEY_PREFIX` - For tool model configuration
- `EMBEDDING_MODEL_KEY_PREFIX` - For embedding model configuration

Each prefix supports:

- `{PREFIX}_MODEL` - Model name
- `{PREFIX}_MODEL_PROVIDER` - Provider (openai, anthropic, etc.)
- `{PREFIX}_MODEL_TYPE` - Type (chat, embedding)
- `{PREFIX}_API_KEY` - API key
- `{PREFIX}_BASE_URL` - Base URL
- `{PREFIX}_TEMPERATURE` - Temperature setting

## Development

### Setting up Development Environment

1. Clone the repository
2. Create virtual environment: `uv venv`
3. Activate environment: `.venv\Scripts\activate`
4. Install in development mode: `uv pip install -e .`
5. Install development dependencies: `uv pip install pytest black flake8`

### Code Formatting

```bash
black src/
flake8 src/
```

### Building Distribution

```bash
python -m build
```

## TODO - Feature Roadmap

X

### 🎯 Core Features

- [X] **Codebase & Indexing**: ✅ Implemented codebase analysis and intelligent indexing
- [X] **Multi-language Support**: ✅ Built-in internationalization (i18n) support
- [X] **Dual Model Architecture**: ✅ Separate models for chat and tool operations
- [X] **Persistent Memory System**: ✅ SQLite-based conversation history with session management
- [ ] **Enhanced Web Search**: Improve web search tools with better result filtering and integration
- [ ] **IDE Plugin Development**: Create plugins for popular IDEs (VS Code, IntelliJ, etc.)

### 🔧 Additional Features

- [ ] **Code Review Assistant**: Automated code review and suggestion system
- [ ] **Project Template Generator**: Generate project templates based on requirements
- [ ] **Integration with Git**: Git operations and workflow assistance
- [ ] **Performance Monitoring**: Track and optimize agent performance
- [ ] **Custom Tool Development**: Framework for creating custom tools
- [ ] **Advanced Codebase Features**: Code refactoring suggestions, dependency analysis
- [ ] **Multi-Provider Support**: Extend model factory to support more AI providers

### 📚 Documentation & Community

- [ ] **Comprehensive Documentation**: Detailed API documentation and tutorials
- [ ] **Example Projects**: Sample projects demonstrating various use cases
- [ ] **Community Contributions**: Guidelines and tools for community contributions
- [ ] **Codebase Indexing Guide**: Documentation for advanced codebase features

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Author

- **dragons96** - [521274311@qq.com](mailto:521274311@qq.com)

---

**Note**: This project is inspired by Cursor and aims to provide similar functionality in a command-line interface with extensible tool integration.
