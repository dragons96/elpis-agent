AI_AGENT_NAME = 'Elpis'

# 系统级别的提示词
SYSTEM_PROMPT = """"""

BANNER = """
          _____                    _____            _____                    _____                    _____          
         /\    \                  /\    \          /\    \                  /\    \                  /\    \         
        /::\    \                /::\____\        /::\    \                /::\    \                /::\    \        
       /::::\    \              /:::/    /       /::::\    \               \:::\    \              /::::\    \       
      /::::::\    \            /:::/    /       /::::::\    \               \:::\    \            /::::::\    \      
     /:::/\:::\    \          /:::/    /       /:::/\:::\    \               \:::\    \          /:::/\:::\    \     
    /:::/__\:::\    \        /:::/    /       /:::/__\:::\    \               \:::\    \        /:::/__\:::\    \    
   /::::\   \:::\    \      /:::/    /       /::::\   \:::\    \              /::::\    \       \:::\   \:::\    \   
  /::::::\   \:::\    \    /:::/    /       /::::::\   \:::\    \    ____    /::::::\    \    ___\:::\   \:::\    \  
 /:::/\:::\   \:::\    \  /:::/    /       /:::/\:::\   \:::\____\  /\   \  /:::/\:::\    \  /\   \:::\   \:::\    \ 
/:::/__\:::\   \:::\____\/:::/____/       /:::/  \:::\   \:::|    |/::\   \/:::/  \:::\____\/::\   \:::\   \:::\____\\
\:::\   \:::\   \::/    /\:::\    \       \::/    \:::\  /:::|____|\:::\  /:::/    \::/    /\:::\   \:::\   \::/    /
 \:::\   \:::\   \/____/  \:::\    \       \/_____/\:::\/:::/    /  \:::\/:::/    / \/____/  \:::\   \:::\   \/____/ 
  \:::\   \:::\    \       \:::\    \               \::::::/    /    \::::::/    /            \:::\   \:::\    \     
   \:::\   \:::\____\       \:::\    \               \::::/    /      \::::/____/              \:::\   \:::\____\    
    \:::\   \::/    /        \:::\    \               \::/____/        \:::\    \               \:::\  /:::/    /    
     \:::\   \/____/          \:::\    \               ~~               \:::\    \               \:::\/:::/    /     
      \:::\    \               \:::\    \                                \:::\    \               \::::::/    /      
       \:::\____\               \:::\____\                                \:::\____\               \::::/    /       
        \::/    /                \::/    /                                 \::/    /                \::/    /        
         \/____/                  \/____/                                   \/____/                  \/____/         
"""

WELCOME_INFO = """Welcome to Elpis AI Agent.

Interactive Commands:

    In conversation, you can:

    - Ask programming questions and request code help

    - Request file reading and modification

    - Ask for terminal command execution

    - Perform project structure analysis

    - Get development guidance

    Type 'q' or 'quit' to exit the program
"""

WELCOME_INFO_ZH = """欢迎来到 Elpis AI Agent.
交互命令:

    在对话中，你可以:
    
    - 询问编程问题和请求代码帮助
    
    - 要求读取和修改文件
    
    - 请求执行终端命令
    
    - 进行项目结构分析
    
    - 获取开发指导
    
    输入 'q' 或 'quit' 退出程序
"""

USAGE_ZH = """Elpis Agent - 超轻量级 AI 编码助手

用法:

    elpis [选项]
    
    python -m elpis.main [选项]
    
    uvx elpis-agent [选项]  # 推荐方式

环境变量配置:

    OPENAI_API_KEY     OpenAI API 密钥 (必需)
    
    OPENAI_BASE_URL    API 端点 URL (可选)
    
    CHAT_MODEL         对话模型 (默认: gpt-4o-mini)
    
    TOOL_MODEL         工具模型 (默认: gpt-4o)
    
    TEMPERATURE        默认温度 (默认: 0.3)
    
    TOOL_TEMPERATURE   工具模型温度 (默认: 0.1)
    
    SYSTEM_PROMPT      自定义系统提示词 (可选)
    
    MAX_MEMORY_MESSAGES 最大消息数 (默认: 20)

使用示例:

    # 基本使用
    
    elpis
    
    # 使用自定义配置文件
    
    elpis --env_file /path/to/custom.env
    
    # 直接运行（推荐）
    
    uvx elpis-agent --env_file .env.local

交互命令:

    在对话中，你可以:
    
    - 询问编程问题和请求代码帮助
    
    - 要求读取和修改文件
    
    - 请求执行终端命令
    
    - 进行项目结构分析
    
    - 获取开发指导
    
    输入 'q' 或 'quit' 退出程序
"""

USAGE = """Elpis Agent - Ultra-lightweight AI Coding Assistant

Usage:

    elpis [options]

    python -m elpis.main [options]

    uvx elpis-agent [options]  # Recommended

Environment Variables:

    OPENAI_API_KEY     OpenAI API key (required)

    OPENAI_BASE_URL    API endpoint URL (optional)

    CHAT_MODEL         Chat model (default: gpt-4o-mini)

    TOOL_MODEL         Tool model (default: gpt-4o)

    TEMPERATURE        Default temperature (default: 0.3)

    TOOL_TEMPERATURE   Tool model temperature (default: 0.1)

    SYSTEM_PROMPT      Custom system prompt (optional)

    MAX_MEMORY_MESSAGES Maximum message count (default: 20)

Examples:

    # Basic usage

    elpis

    # Use custom configuration file

    elpis --env_file /path/to/custom.env

    # Direct run (recommended)

    uvx elpis-agent --env_file .env.local

Interactive Commands:

    In conversation, you can:

    - Ask programming questions and request code help

    - Request file reading and modification

    - Ask for terminal command execution

    - Perform project structure analysis

    - Get development guidance

    Type 'q' or 'quit' to exit the program
"""
