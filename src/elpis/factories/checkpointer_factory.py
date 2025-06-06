from typing import Literal
from langgraph.checkpoint.base import BaseCheckpointSaver


def new_checkpointer(
        checkpointer_type: Literal['memory', 'sqlite'] | str = 'memory'
) -> BaseCheckpointSaver | None:
    if checkpointer_type == 'memory':
        from langgraph.checkpoint.memory import InMemorySaver
        return InMemorySaver()
    elif checkpointer_type == 'sqlite':
        import os
        from pathlib import Path
        import sqlite3
        from langgraph.checkpoint.sqlite import SqliteSaver
        elpis_dir = Path(os.getcwd()) / ".elpis"
        elpis_dir.mkdir(exist_ok=True)

        # Create SQLite database file path
        db_path = elpis_dir / "memory.db"

        # Create SQLite connection
        # check_same_thread=False is OK as SqliteSaver uses locks for thread safety
        conn = sqlite3.connect(str(db_path), check_same_thread=False)

        # Initialize and return SqliteSaver
        return SqliteSaver(conn)

    return None

