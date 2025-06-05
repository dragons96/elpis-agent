from .i18n.en import WELCOME_INFO
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

USAGE = f"""Elpis Agent - Ultra-lightweight AI Coding Assistant

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

{WELCOME_INFO}
"""
