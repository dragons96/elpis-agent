# Elpis Agent

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
- 🧠 **Memory Management**: Configurable message history limit to prevent token overflow

## Installation

### Quick Start with uvx (Recommended)

You can also run Elpis Agent directly without installation using `uvx`:

```bash
uvx --from elpis-agent elpis --env_file /path/to/.env
```

This command will:

- Automatically download and run the latest version of elpis-agent
- Use your custom environment file for configuration
- No need for local installation or virtual environment setup

### Requirements

- Python >= 3.11
- OpenAI API Key

### Installation Steps

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

Edit the `.env` file and fill in the necessary configurations:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL=gpt-4o-mini
TEMPERATURE=0.7
MAX_MEMORY_MESSAGES=20
```

## Usage

### Command Line Interface

After installation, you can start Elpis Agent using:

```bash
elpis
```

Or run directly with Python:

```bash
python -m elpis.main
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

## Project Structure

```
elpis-agent/
├── src/elpis/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Main entry point
│   ├── agent.py             # Core agent implementation
│   ├── tools.py             # Tool definitions
│   ├── prompts.py           # Prompt templates
│   └── constants.py         # Constants and configurations
├── tests/                   # Test files
├── docs/                    # Documentation
├── .env.example             # Environment variables template
├── pyproject.toml           # Project configuration
├── README.md                # Project documentation (English)
├── README_zh.md             # Project documentation (Chinese)
└── LICENSE                  # License file
```

## Core Components

### ElpisAgent

The main agent class that handles:

- Message management with configurable history limits
- Tool integration and execution
- Model interaction and response generation
- Context preservation across conversations

### Tools

Built-in tools include:

- **read_file**: Read file contents
- **run_terminal_cmd**: Execute terminal commands with user confirmation

### Memory Management

The agent implements intelligent memory management:

- Configurable message history limit (default: 20 messages)
- Automatic truncation of old messages while preserving system context
- Prevention of token overflow and cost optimization

## Configuration

Environment variables can be configured in the `.env` file:

| Variable                | Description                                  | Default                       |
| ----------------------- | -------------------------------------------- | ----------------------------- |
| `OPENAI_API_KEY`      | OpenAI API key (required)                    | -                             |
| `OPENAI_BASE_URL`     | OpenAI API base URL                          | `https://api.openai.com/v1` |
| `MODEL`               | Model name to use                            | `gpt-4o-mini`               |
| `TEMPERATURE`         | Model temperature (0.0-2.0)                  | `0.7`                       |
| `SYSTEM_PROMPT`       | Custom system prompt                         | Default agent prompt          |
| `MAX_MEMORY_MESSAGES` | Maximum number of messages to keep in memory | `20`                        |

## Development

### Setting up Development Environment

1. Clone the repository
2. Create virtual environment: `uv venv`
3. Activate environment: `.venv\Scripts\activate`
4. Install in development mode: `uv pip install -e .`
5. Install development dependencies: `uv pip install pytest black flake8`

### Running Tests

```bash
pytest tests/
```

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

### 🎯 Core Features

- [ ] **Codebase & Indexing**: Implement codebase analysis and intelligent indexing for better context understanding
- [ ] **Enhanced Web Search**: Improve web search tools with better result filtering and integration
- [ ] **Message & Operation Memory**: Advanced message memorization and operation history tracking
- [ ] **IDE Plugin Development**: Create plugins for popular IDEs (VS Code, IntelliJ, etc.)

### 🔧 Additional Features

- [ ] **Multi-language Support**: Extend support for more programming languages
- [ ] **Code Review Assistant**: Automated code review and suggestion system
- [ ] **Project Template Generator**: Generate project templates based on requirements
- [ ] **Integration with Git**: Git operations and workflow assistance
- [ ] **Performance Monitoring**: Track and optimize agent performance
- [ ] **Custom Tool Development**: Framework for creating custom tools

### 📚 Documentation & Community

- [ ] **Comprehensive Documentation**: Detailed API documentation and tutorials
- [ ] **Example Projects**: Sample projects demonstrating various use cases
- [ ] **Community Contributions**: Guidelines and tools for community contributions

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Author

Developed with ❤️ by the Elpis team.

---

**Note**: This project is inspired by Cursor and aims to provide similar functionality in a command-line interface with extensible tool integration.
