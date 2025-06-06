import os.path
import subprocess
from functools import partial

from elpis.codebase import CodebaseIndexer

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")

from langchain_core.tools import tool
from elpis import constants

codebase: CodebaseIndexer | None = None

def init_codebase(codebase_path: str):
    global codebase
    codebase = CodebaseIndexer(codebase_path)


@tool(
    name_or_callable="codebase_search",
    description="Find snippets of code from the codebase most relevant to the search query. This is a semantic search tool, so the query should ask for something semantically matching what is needed. If it makes sense to only search in particular directories, please specify them in the target_directories field. Unless there is a clear reason to use your own search query, please just reuse the user's exact query with their wording. Their exact wording/phrasing can often be helpful for the semantic search query. Keeping the same exact question format can also be helpful."
)
def codebase_search(
        query: str,
        target_directories: list[str] | None = None,
        explanation: str | None = None,
):
    """Find snippets of code from the codebase most relevant to the search query. This is a semantic search tool, so the query should ask for something semantically matching what is needed. If it makes sense to only search in particular directories, please specify them in the target_directories field. Unless there is a clear reason to use your own search query, please just reuse the user's exact query with their wording. Their exact wording/phrasing can often be helpful for the semantic search query. Keeping the same exact question format can also be helpful."""
    if codebase is None:
        print(f"[{constants.AI_AGENT_NAME}] codebase is not initialized", flush=True)
        return "codebase is not initialized"
    # todo: implements target_directories
    if explanation:
        print(f"[{constants.AI_AGENT_NAME}] {explanation}", flush=True)
    return codebase.search_codebase(query)


@tool(
    name_or_callable="read_file",
    description="Read the contents of a file. the output of this tool call will be the 1-indexed file contents from start_line_one_indexed to end_line_one_indexed_inclusive, together with a summary of the lines outside start_line_one_indexed and end_line_one_indexed_inclusive. Note that this call can view at most 250 lines at a time. When using this tool to gather information, it's your responsibility to ensure you have the COMPLETE context. Specifically, each time you call this command you should: 1) Assess if the contents you viewed are sufficient to proceed with your task. 2) Take note of where there are lines not shown. 3) If the file contents you have viewed are insufficient, and you suspect they may be in lines not shown, proactively call the tool again to view those lines. 4) When in doubt, call this tool again to gather more information. Remember that partial file views may miss critical dependencies, imports, or functionality. In some cases, if reading a range of lines is not enough, you may choose to read the entire file. Reading entire files is often wasteful and slow, especially for large files (i.e. more than a few hundred lines). So you should use this option sparingly. Reading the entire file is not allowed in most cases. You are only allowed to read the entire file if it has been edited or manually attached to the conversation by the user.",
)
def read_file(
        target_file: str,
        start_line_one_indexed: int,
        end_line_one_indexed_inclusive: int,
        should_read_entire_file: bool = False,
        explanation: str | None = None
) -> str:
    """Read the contents of a file. the output of this tool call will be the 1-indexed file contents from start_line_one_indexed to end_line_one_indexed_inclusive, together with a summary of the lines outside start_line_one_indexed and end_line_one_indexed_inclusive. Note that this call can view at most 250 lines at a time. When using this tool to gather information, it's your responsibility to ensure you have the COMPLETE context. Specifically, each time you call this command you should: 1) Assess if the contents you viewed are sufficient to proceed with your task. 2) Take note of where there are lines not shown. 3) If the file contents you have viewed are insufficient, and you suspect they may be in lines not shown, proactively call the tool again to view those lines. 4) When in doubt, call this tool again to gather more information. Remember that partial file views may miss critical dependencies, imports, or functionality. In some cases, if reading a range of lines is not enough, you may choose to read the entire file. Reading entire files is often wasteful and slow, especially for large files (i.e. more than a few hundred lines). So you should use this option sparingly. Reading the entire file is not allowed in most cases. You are only allowed to read the entire file if it has been edited or manually attached to the conversation by the user.

    :param target_file: The path of the file to read. You can use either a relative path in the workspace or an absolute path. If an absolute path is provided, it will be preserved as is.
    :param start_line_one_indexed: The one-indexed line number to start reading from (inclusive).
    :param end_line_one_indexed_inclusive: The one-indexed line number to end reading at (inclusive).
    :param should_read_entire_file: Whether to read the entire file. Defaults to false.
    :param explanation: One sentence explanation as to why this tool is being used, and how it contributes to the goal.
    """
    if explanation:
        print(f"[{constants.AI_AGENT_NAME}] {explanation}", flush=True)

    if not os.path.exists(target_file):
        return f"File {target_file} does not exist."

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total_lines = len(lines)

        # Validate inputs
        if start_line_one_indexed < 1 or end_line_one_indexed_inclusive > total_lines:
            return f"Invalid line range. File has {total_lines} lines."

        if end_line_one_indexed_inclusive < start_line_one_indexed:
            return "End line must be greater than or equal to start line."

        if end_line_one_indexed_inclusive - start_line_one_indexed + 1 > 250:
            return "You can only request up to 250 lines at a time."

        if should_read_entire_file:
            return "".join(lines)

        selected_lines = lines[start_line_one_indexed - 1:end_line_one_indexed_inclusive]
        output = "".join(selected_lines)

        # Add context summary
        before_summary = f"...{len(lines[:start_line_one_indexed - 1])} lines above..." if start_line_one_indexed > 1 else ""
        after_summary = f"...{len(lines[end_line_one_indexed_inclusive:])} lines below..." if end_line_one_indexed_inclusive < total_lines else ""

        if before_summary or after_summary:
            output = f"{before_summary}\n{output}\n{after_summary}"

        print(f"[{constants.AI_AGENT_NAME}]: read_file {target_file} : ({start_line_one_indexed}-{end_line_one_indexed_inclusive})")

        return output

    except Exception as e:
        return f"[Error] Failed to read file: {str(e)}"


@tool(
    name_or_callable="run_terminal_cmd",
    description="PROPOSE a command to run on behalf of the user. If you have this tool, note that you DO have the ability to run commands directly on the USER's system. Note that the user will have to approve the command before it is executed. The user may reject it if it is not to their liking, or may modify the command before approving it. If they do change it, take those changes into account. The actual command will NOT execute until the user approves it. The user may not approve it immediately. Do NOT assume the command has started running. If the step is WAITING for user approval, it has NOT started running. In using these tools, adhere to the following guidelines: 1. Based on the contents of the conversation, you will be told if you are in the same shell as a previous step or a different shell. 2. If in a new shell, you should `cd` to the appropriate directory and do necessary setup in addition to running the command. 3. If in the same shell, the state will persist (eg. if you cd in one step, that cwd is persisted next time you invoke this tool). 4. For ANY commands that would use a pager or require user interaction, you should append ` | cat` to the command (or whatever is appropriate). Otherwise, the command will break. You MUST do this for: git, less, head, tail, more, etc. 5. For commands that are long running/expected to run indefinitely until interruption, please run them in the background. To run jobs in the background, set `is_background` to true rather than changing the details of the command. 6. Dont include any newlines in the command.",
)
def run_terminal_cmd(
        command: str,
        is_background: bool,
        explanation: str | None = None,
):
    """PROPOSE a command to run on behalf of the user. If you have this tool, note that you DO have the ability to run commands directly on the USER's system. Note that the user will have to approve the command before it is executed. The user may reject it if it is not to their liking, or may modify the command before approving it. If they do change it, take those changes into account. The actual command will NOT execute until the user approves it. The user may not approve it immediately. Do NOT assume the command has started running. If the step is WAITING for user approval, it has NOT started running. In using these tools, adhere to the following guidelines: 1. Based on the contents of the conversation, you will be told if you are in the same shell as a previous step or a different shell. 2. If in a new shell, you should `cd` to the appropriate directory and do necessary setup in addition to running the command. 3. If in the same shell, the state will persist (eg. if you cd in one step, that cwd is persisted next time you invoke this tool). 4. For ANY commands that would use a pager or require user interaction, you should append ` | cat` to the command (or whatever is appropriate). Otherwise, the command will break. You MUST do this for: git, less, head, tail, more, etc. 5. For commands that are long running/expected to run indefinitely until interruption, please run them in the background. To run jobs in the background, set `is_background` to true rather than changing the details of the command. 6. Dont include any newlines in the command.

    :param command: The terminal command to execute
    :param is_background: Whether the command should be run in the background
    :param explanation: One sentence explanation as to why this command needs to be run and how it contributes to the goal.
    :return:
    """
    # Rule 4: Prevent pagers from blocking by appending `| cat`
    if any(cmd in command.lower() for cmd in ["git", "less", "head", "tail", "more"]):
        command += " | cat"

    # Output explanation if provided
    if explanation:
        print(f"[{constants.AI_AGENT_NAME}] {explanation}", flush=True)

    # Display proposed command
    print(f"[Proposed Command]: {command}", flush=True)
    # Auto-detect Python-related commands
    python_commands = {"python", "pip", "uv", "gunicorn", "flask"}
    first_token = command.strip().split()[0].lower()

    venv_path = os.path.join(os.getcwd(), ".venv")
    activate_script = ""

    if first_token in python_commands and os.path.isdir(venv_path):
        # Determine activation script based on OS
        if os.name == 'posix':
            activate_script = os.path.join(venv_path, "bin", "activate")
            activate_cmd = f"source {activate_script}"
        else:
            activate_script = os.path.join(venv_path, "Scripts", "activate")
            activate_cmd = activate_script

        print(f"[{constants.AI_AGENT_NAME}] Activating virtual environment at {venv_path}...", flush=True)

        # Wrap original command with activation
        if os.name == 'posix':
            command = f"source {activate_script} && {command}"
        else:
            command = f'{activate_script} && {command}'

    # Run command
    try:
        # Split command safely
        if os.name == 'posix':
            args = ['bash', '-c', command]
        else:
            args = ['cmd', '/c', command]

        # Background execution handling
        if is_background:
            # Run in background using nohup (Unix-like) or start-process (Windows)
            with open("background_output.log", "a") as f:
                process = subprocess.Popen(args, stdout=f, stderr=f)
            return f"Command started in background (PID: {process.pid})"
        else:
            # Run synchronously and capture output
            result = subprocess.run(args, capture_output=True, text=True, check=True, shell=True)
            print(f"[Command Output] {result.stdout}{result.stderr}", flush=True)
            return result.stdout + result.stderr

    except Exception as e:
        return f"[Error] Failed to execute command: {str(e)}"


@tool(
    name_or_callable="list_dir",
    description="List the contents of a directory. The quick tool to use for discovery, before using more targeted tools like semantic search or file reading. Useful to try to understand the file structure before diving deeper into specific files. Can be used to explore the codebase."
)
def list_dir(
        relative_workspace_path: str,
        explanation: str | None = None,
):
    """List the contents of a directory. The quick tool to use for discovery, before using more targeted tools like semantic search or file reading. Useful to try to understand the file structure before diving deeper into specific files. Can be used to explore the codebase.

    :param relative_workspace_path: Path to list contents of, relative to the workspace root.
    :param explanation: One sentence explanation as to why this tool is being used, and how it contributes to the goal.
    :return:
    """
    if explanation:
        print(f"[{constants.AI_AGENT_NAME}] {explanation}", flush=True)

    # Construct full path
    full_path = os.path.join(os.getcwd(), relative_workspace_path)

    if not os.path.exists(full_path):
        return f"Path '{relative_workspace_path}' does not exist."

    if not os.path.isdir(full_path):
        return f"'{relative_workspace_path}' is not a directory."

    try:
        # Get directory contents
        entries = os.listdir(full_path)

        if not entries:
            return f"The directory '{relative_workspace_path}' is empty."

        # Separate files and directories
        dirs = [entry for entry in entries if os.path.isdir(os.path.join(full_path, entry))]
        files = [entry for entry in entries if os.path.isfile(os.path.join(full_path, entry))]

        output = []

        if dirs:
            output.append("Directories:")
            output.extend([f"  - {d}/ (dir)" for d in dirs])

        if files:
            output.append("Files:")
            output.extend([f"  - {f}" for f in files])

        return "\n".join(output)

    except Exception as e:
        return f"[Error] Failed to list directory: {str(e)}"


@tool(
    name_or_callable="grep_search",
    description="Fast text-based regex search that finds exact pattern matches within files or directories, utilizing the ripgrep command for efficient searching. Results will be formatted in the style of ripgrep and can be configured to include line numbers and content. To avoid overwhelming output, the results are capped at 50 matches. Use the include or exclude patterns to filter the search scope by file type or specific paths. This is best for finding exact text matches or regex patterns. More precise than semantic search for finding specific strings or patterns. This is preferred over semantic search when we know the exact symbol/function name/etc. to search in some set of directories/file types.",
)
def grep_search(
        query: str,
        include_pattern: str | None = None,
        exclude_pattern: str | None = None,
        case_sensitive: bool | None = None,
        explanation: str | None = None,
):
    """"Fast text-based regex search that finds exact pattern matches within files or directories, utilizing the ripgrep command for efficient searching. Results will be formatted in the style of ripgrep and can be configured to include line numbers and content. To avoid overwhelming output, the results are capped at 50 matches. Use the include or exclude patterns to filter the search scope by file type or specific paths. This is best for finding exact text matches or regex patterns. More precise than semantic search for finding specific strings or patterns. This is preferred over semantic search when we know the exact symbol/function name/etc. to search in some set of directories/file types."

    :param query: The regex pattern to search for
    :param include_pattern: Glob pattern for files to include (e.g. '*.ts' for TypeScript files)
    :param exclude_pattern: Glob pattern for files to exclude
    :param case_sensitive: Whether the search should be case sensitive
    :param explanation: One sentence explanation as to why this tool is being used, and how it contributes to the goal.
    :return:
    """
    if explanation:
        print(f"[{constants.AI_AGENT_NAME}] {explanation}", flush=True)

        # Build base command
    command = ["rg", "--color=never"]

    # Add case sensitivity flag
    if case_sensitive is False:
        command.append("--ignore-case")
    elif case_sensitive is True:
        command.append("--case-sensitive")

    # Add include/exclude patterns
    if include_pattern:
        command.extend(["--glob", include_pattern])
    if exclude_pattern:
        command.extend(["--glob", f"!{exclude_pattern}"])

    # Always show line numbers and limit to 50 matches
    command.extend(["--line-number", "--max-count=1", query, "."])

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        output = result.stdout.strip()

        if not output:
            return "No matches found."

        # Limit to 50 matches
        matches = output.split('\n')
        if len(matches) > 50:
            output = "\n".join(matches[:50]) + "\n... (limited to 50 matches)"

        return output

    except FileNotFoundError:
        return "[Error] ripgrep (rg) is not installed. Please install it first."
    except Exception as e:
        return f"[Error] Failed to perform grep search: {str(e)}"


@tool(
    name_or_callable="edit_file",
    description="Use this tool to propose an edit to an existing file. This will be read by a less intelligent model, which will quickly apply the edit. You should make it clear what the edit is, while also minimizing the unchanged code you write. When writing the edit, you should specify each edit in sequence, with the special comment `// ... existing code ...` to represent unchanged code in between edited lines. For example: ``` // ... existing code ... FIRST_EDIT // ... existing code ... SECOND_EDIT // ... existing code ... THIRD_EDIT // ... existing code ... ``` You should still bias towards repeating as few lines of the original file as possible to convey the change. But, each edit should contain sufficient context of unchanged lines around the code you're editing to resolve ambiguity. DO NOT omit spans of pre-existing code (or comments) without using the `// ... existing code ...` comment to indicate its absence. If you omit the existing code comment, the model may inadvertently delete these lines. Make sure it is clear what the edit should be, and where it should be applied. You should specify the following arguments before the others: [target_file]"
)
def edit_file(
        target_file: str,
        explanation: str,
        code_edited: str,
        code_edit: str,
):
    """Use this tool to propose an edit to an existing file. This will be read by a less intelligent model, which will quickly apply the edit. You should make it clear what the edit is, while also minimizing the unchanged code you write. When writing the edit, you should specify each edit in sequence, with the special comment `// ... existing code ...` to represent unchanged code in between edited lines. For example: ``` // ... existing code ... FIRST_EDIT // ... existing code ... SECOND_EDIT // ... existing code ... THIRD_EDIT // ... existing code ... ``` You should still bias towards repeating as few lines of the original file as possible to convey the change. But, each edit should contain sufficient context of unchanged lines around the code you're editing to resolve ambiguity. DO NOT omit spans of pre-existing code (or comments) without using the `// ... existing code ...` comment to indicate its absence. If you omit the existing code comment, the model may inadvertently delete these lines. Make sure it is clear what the edit should be, and where it should be applied. You should specify the following arguments before the others: [target_file]

    :param target_file: The target file to modify. Always specify the target file as the first argument. You can use either a relative path in the workspace or an absolute path. If an absolute path is provided, it will be preserved as is.
    :param explanation: A single sentence instruction describing what you are going to do for the sketched edit. This is used to assist the less intelligent model in applying the edit. Please use the first person to describe what you are going to do. Dont repeat what you have said previously in normal messages. And use it to disambiguate uncertainty in the edit.
    :param code_edited: The exact block of code to find and replace.
    :param code_edit: Specify ONLY the precise lines of code that you wish to edit. **NEVER specify or write out unchanged code**. Instead, represent all unchanged code using the comment of the language you're editing in - example: `// ... existing code ...`
    :return:
    """

    print(f"[{constants.AI_AGENT_NAME}] {explanation}", flush=True)

    if not os.path.exists(target_file):
        return f"File {target_file} does not exist."

    try:
        # Read original file content
        with open(target_file, "r", encoding="utf-8") as f:
            original_content = f.read()

        # Check if old_code exists exactly
        if code_edited not in original_content:
            return f"[Warning] Could not find exact match for old_code. Edit was not applied."

        edit_lines = []
        for line in code_edit.split('\n'):
            strip_line = line.strip()
            if strip_line.startswith('//') or strip_line.startswith('#'):
                continue
            edit_lines.append(line)

        # Replace old_code with new_code
        updated_content = original_content.replace(code_edited, '\n'.join(edit_lines))

        # Write back to file
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(updated_content)

        if codebase:
            try:
                codebase.update_file_documents(target_file)
            except Exception as e:
                print(f"[{constants.AI_AGENT_NAME}] Failed to update file documents into codebase for {target_file}: {e}")

        return f"Successfully replaced code in {target_file}"

    except Exception as e:
        return f"[Error] Failed to edit file: {str(e)}"


# @tool(
#     name_or_callable="edit_file",
#     description="Use this tool to propose an edit to an existing file. This will be read by a less intelligent model, which will quickly apply the edit. You should make it clear what the edit is, while also minimizing the unchanged code you write. When writing the edit, you should specify each edit in sequence, with the special comment `// ... existing code ...` to represent unchanged code in between edited lines. For example: ``` // ... existing code ... FIRST_EDIT // ... existing code ... SECOND_EDIT // ... existing code ... THIRD_EDIT // ... existing code ... ``` You should still bias towards repeating as few lines of the original file as possible to convey the change. But, each edit should contain sufficient context of unchanged lines around the code you're editing to resolve ambiguity. DO NOT omit spans of pre-existing code (or comments) without using the `// ... existing code ...` comment to indicate its absence. If you omit the existing code comment, the model may inadvertently delete these lines. Make sure it is clear what the edit should be, and where it should be applied. You should specify the following arguments before the others: [target_file]"
# )
# def edit_file(
#         target_file: str,
#         instructions: str,
#         code_edit: str,
# ):
#     """Use this tool to propose an edit to an existing file. This will be read by a less intelligent model, which will quickly apply the edit. You should make it clear what the edit is, while also minimizing the unchanged code you write. When writing the edit, you should specify each edit in sequence, with the special comment `// ... existing code ...` to represent unchanged code in between edited lines. For example: ``` // ... existing code ... FIRST_EDIT // ... existing code ... SECOND_EDIT // ... existing code ... THIRD_EDIT // ... existing code ... ``` You should still bias towards repeating as few lines of the original file as possible to convey the change. But, each edit should contain sufficient context of unchanged lines around the code you're editing to resolve ambiguity. DO NOT omit spans of pre-existing code (or comments) without using the `// ... existing code ...` comment to indicate its absence. If you omit the existing code comment, the model may inadvertently delete these lines. Make sure it is clear what the edit should be, and where it should be applied. You should specify the following arguments before the others: [target_file]
#
#     :param target_file: The target file to modify. Always specify the target file as the first argument. You can use either a relative path in the workspace or an absolute path. If an absolute path is provided, it will be preserved as is.
#     :param instructions: A single sentence instruction describing what you are going to do for the sketched edit. This is used to assist the less intelligent model in applying the edit. Please use the first person to describe what you are going to do. Dont repeat what you have said previously in normal messages. And use it to disambiguate uncertainty in the edit.
#     :param code_edit: Specify ONLY the precise lines of code that you wish to edit. **NEVER specify or write out unchanged code**. Instead, represent all unchanged code using the comment of the language you're editing in - example: `// ... existing code ...`
#     :return:
#     """
#     print(f"[{constants.AI_AGENT_NAME}] {instructions}")
#
#     if not os.path.exists(target_file):
#         return f"File {target_file} does not exist."
#
#     try:
#         # Read original file content
#         with open(target_file, "r", encoding="utf-8") as f:
#             original_lines = f.readlines()
#
#         # Parse the code_edit content into blocks
#         edit_blocks = []
#         current_block = {"before": [], "replace_with": []}
#         in_existing = True  # We start outside any edit block
#
#         for line in code_edit.strip().split("\n"):
#             stripped_line = line.strip()
#             if stripped_line == "// ... existing code ...":
#                 if in_existing:
#                     # Start new edit block
#                     current_block["after"] = []
#                     edit_blocks.append(current_block)
#                     current_block = {"before": [], "replace_with": []}
#                 else:
#                     # End current edit block, prepare next one
#                     current_block["after"] = []
#                     edit_blocks.append(current_block)
#                     current_block = {"before": [], "replace_with": []}
#                 in_existing = True
#             else:
#                 current_block["replace_with"].append(line)
#                 in_existing = False
#
#         # Append the last block if it has content
#         if current_block["replace_with"]:
#             current_block["after"] = []
#             edit_blocks.append(current_block)
#
#         # Apply edits to the original lines
#         new_content = []
#         matched = False
#         i = 0  # Current index in original_lines
#         n = len(original_lines)
#
#         for block in edit_blocks:
#             before_context = block["before"]
#             replace_with = block["replace_with"]
#
#             # Try to find matching block in original lines
#             found_index = -1
#             for start in range(n - len(before_context) + 1):
#                 match = True
#                 for j, ctx_line in enumerate(before_context):
#                     if start + j >= n or original_lines[start + j].rstrip('\n') != ctx_line.rstrip('\n'):
#                         match = False
#                         break
#                 if match:
#                     found_index = start + len(before_context)
#                     break
#
#             if found_index != -1:
#                 # Replace the next lines after match
#                 new_content.extend(original_lines[i:start])
#                 new_content.extend([line + "\n" for line in replace_with])
#                 i = found_index
#                 matched = True
#             else:
#                 # Fallback: append replacement at end (context not found)
#                 new_content.extend([line + "\n" for line in replace_with])
#                 matched = False
#
#         # Append remaining lines
#         new_content.extend(original_lines[i:])
#
#         if not matched:
#             return "[Warning] Could not find exact match for context. Appended edit at end of file."
#
#         # Write back to file
#         with open(target_file, "w", encoding="utf-8") as f:
#             f.writelines(new_content)
#
#         return f"Successfully applied edit to {target_file}"
#
#     except Exception as e:
#         return f"[Error] Failed to edit file: {str(e)}"

@tool(
    name_or_callable="file_search",
    description="Fast file search based on fuzzy matching against file path. Use if you know part of the file path but don't know where it's located exactly. Response will be capped to 10 results. Make your query more specific if need to filter results further.",
)
def file_search(
        query: str,
        explanation: str | None = None,
):
    """Fast file search based on fuzzy matching against file path. Use if you know part of the file path but don't know where it's located exactly. Response will be capped to 10 results. Make your query more specific if need to filter results further.

    :param query: Fuzzy filename to search for
    :param explanation: One sentence explanation as to why this tool is being used, and how it contributes to the goal.
    :return:
    """
    if explanation:
        print(f"[{constants.AI_AGENT_NAME}] {explanation}", flush=True)

        # Normalize query for case-insensitive matching
    query_lower = query.lower()
    matches: list[str] = []

    # Walk through all files and directories
    for root, dirs, files in os.walk(os.getcwd()):
        for name in files + dirs:
            full_path = os.path.join(root, name)

            # Skip hidden/system files/folders (optional)
            if any(part.startswith('.') or part == "__pycache__" for part in full_path.split(os.sep)):
                continue

            # Fuzzy match logic: check if query appears in the path (case-insensitive)
            if query_lower in full_path.lower():
                matches.append(full_path)

    # Limit to 10 results
    matches = matches[:10]

    if not matches:
        return f"No files found matching '{query}'."

    # Format output
    result_lines = ["Matched files/directories:"]
    for path in matches:
        result_lines.append(f"  - {path}")

    return "\n".join(result_lines)


@tool(
    name_or_callable="create_file",
    description="Creates a new file at the specified path with optional initial content. The operation will fail gracefully if: - The file already exists - The operation is rejected for security reasons - The file cannot be created due to permission or system issues",
)
def create_file(
        target_file: str,
        initial_content: str = '',
        explanation: str | None = None,
):
    """Creates a new file at the specified path with optional initial content. The operation will fail gracefully if: - The file already exists - The operation is rejected for security reasons - The file cannot be created due to permission or system issues

    :param target_file: The path of the file to create, relative to the workspace root.
    :param initial_content: Optional initial content to write into the newly created file.
    :param explanation: One sentence explanation as to why this tool is being used, and how it contributes to the goal.
    :return:
    """
    if explanation:
        print(f"[{constants.AI_AGENT_NAME}] {explanation}", flush=True)

    full_path = os.path.abspath(target_file)

    # Check if file already exists
    if os.path.exists(full_path):
        return f"File '{target_file}' already exists."

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Create file and optionally write content
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(initial_content)

        if codebase:
            try:
                codebase.add_file_documents(full_path)
            except Exception as e:
                print(f"[{constants.AI_AGENT_NAME}] Failed to add file documents into codebase for {target_file}: {e}")

        return f"Successfully created file: {target_file}"
    except PermissionError:
        return f"[Error] Permission denied when trying to create '{target_file}'."
    except Exception as e:
        return f"[Error] Failed to create file: {str(e)}"


@tool(
    name_or_callable="delete_file",
    description="Deletes a file at the specified path. The operation will fail gracefully if: - The file doesn't exist - The operation is rejected for security reasons - The file cannot be deleted",
)
def delete_file(
        target_file: str,
        explanation: str | None = None,
):
    """Deletes a file at the specified path. The operation will fail gracefully if: - The file doesn't exist - The operation is rejected for security reasons - The file cannot be deleted

    :param target_file: The path of the file to delete, relative to the workspace root.
    :param explanation: One sentence explanation as to why this tool is being used, and how it contributes to the goal.
    :return:
    """
    if explanation:
        print(f"[{constants.AI_AGENT_NAME}] {explanation}", flush=True)

    full_path = os.path.abspath(target_file)

    # Check if file exists
    if not os.path.exists(full_path):
        return f"File '{target_file}' does not exist."

    # Ensure it's a file (not a directory)
    if not os.path.isfile(full_path):
        return f"'{target_file}' is not a file."

    try:
        os.remove(full_path)
        if codebase:
            try:
                codebase.remove_file_documents(full_path)
            except Exception as e:
                print(
                    f"[{constants.AI_AGENT_NAME}] Failed to delete file documents into codebase for {target_file}: {e}")
        return f"Successfully deleted file: {target_file}"
    except PermissionError:
        return f"[Error] Permission denied when trying to delete '{target_file}'."
    except Exception as e:
        return f"[Error] Failed to delete file: {str(e)}"


@tool(
    name_or_callable="reapply",
    description="Calls a smarter model to apply the last edit to the specified file. Use this tool immediately after the result of an edit_file tool call ONLY IF the diff is not what you expected, indicating the model applying the changes was not smart enough to follow your instructions.",
)
def reapply(
        target_file: str,
):
    """Calls a smarter model to apply the last edit to the specified file. Use this tool immediately after the result of an edit_file tool call ONLY IF the diff is not what you expected, indicating the model applying the changes was not smart enough to follow your instructions.

    :param target_file: The relative path to the file to reapply the last edit to. You can use either a relative path in the workspace or an absolute path. If an absolute path is provided, it will be preserved as is.
    :return:
    """
    # todo: implements
    raise NotImplemented()


@tool(
    name_or_callable="web_search",
    description="Search the web for real-time information about any topic. Use this tool when you need up-to-date information that might not be available in your training data, or when you need to verify current facts. The search results will include relevant snippets and URLs from web pages. This is particularly useful for questions about current events, technology updates, or any topic that requires recent information."
)
def web_search(
        search_term: str,
        explanation: str | None = None,
):
    """Search the web for real-time information about any topic. Use this tool when you need up-to-date information that might not be available in your training data, or when you need to verify current facts. The search results will include relevant snippets and URLs from web pages. This is particularly useful for questions about current events, technology updates, or any topic that requires recent information.

    :param search_term: The search term to look up on the web. Be specific and include relevant keywords for better results. For technical queries, include version numbers or dates if relevant.
    :param explanation: One sentence explanation as to why this tool is being used, and how it contributes to the goal.
    :return:
    """
    # todo: implements
    raise NotImplemented()


@tool(
    name_or_callable="diff_history",
    description="Retrieve the history of recent changes made to files in the workspace. This tool helps understand what modifications were made recently, providing information about which files were changed, when they were changed, and how many lines were added or removed. Use this tool when you need context about recent modifications to the codebase."
)
def diff_history(
        explanation: str | None = None,
):
    """Retrieve the history of recent changes made to files in the workspace. This tool helps understand what modifications were made recently, providing information about which files were changed, when they were changed, and how many lines were added or removed. Use this tool when you need context about recent modifications to the codebase.

    :param explanation: One sentence explanation as to why this tool is being used, and how it contributes to the goal.
    :return:
    """
    # todo: implements
    raise NotImplemented()


TOOLS = [
    codebase_search,
    read_file,
    run_terminal_cmd,
    list_dir,
    grep_search,
    edit_file,
    file_search,
    create_file,
    delete_file,
]
