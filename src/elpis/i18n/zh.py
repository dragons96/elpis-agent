WELCOME_INFO = """欢迎来到 Elpis AI Agent.
交互命令:

    在对话中，你可以:

    - 询问编程问题和请求代码帮助

    - 要求读取和修改文件

    - 请求执行终端命令

    - 进行项目结构分析

    - 获取开发指导
    
    输入 'i' 或 'index' 索引代码

    输入 'q' 或 'quit' 退出程序
"""

USAGE_ZH = f"""Elpis Agent - 超轻量级 AI 编码助手

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

{WELCOME_INFO}
"""

CODEBASE_START_INDEX = '开始索引: '

CODEBASE_FINISH_INDEX = '索引完成! 共处理 {} 个代码块.'
