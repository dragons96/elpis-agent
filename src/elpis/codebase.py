import os
from typing import Type, Callable

from gitignore_parser import parse_gitignore, parse_gitignore_str
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore, VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

from elpis import i18n, model_factory


class CodebaseIndexer:
    """A simple codebase and index"""

    def __init__(self, workspace: str = os.getcwd(), embeddings: Embeddings = None,
                 vector_store_cls: Type[VectorStore] = InMemoryVectorStore,
                 text_chunk_size: int = 1000, text_chunk_overlap: int = 200,
                 code_chunk_size: int = 1000, code_chunk_overlap: int = 0):
        self._workspace = os.path.abspath(workspace)
        if embeddings:
            self._embeddings = embeddings
        else:
            self._embeddings = model_factory.new_model(
                os.getenv('EMBEDDING_MODEL_KEY_PREFIX')
            )
        self._vector_store_cls = vector_store_cls
        self._vectorstore = None
        self._lang = i18n.select_lang(os.getenv('LANG', default='zh'))
        self._text_loader = TextLoader(
            file_path='',
            encoding='utf-8',
            autodetect_encoding=True,
        )
        self._file_suffix_code_mapping = {
            'py': 'python',
            'pyi': 'python',
            'cpp': 'cpp',
            'go': 'go',
            'java': 'java',
            'kt': 'kotlin',
            'kts': 'kotlin',
            'js': 'js',
            'jsx': 'js',
            'mjs': 'js',
            'cjs': 'js',
            'ts': 'ts',
            'tsx': 'ts',
            'php': 'php',
            'proto': 'proto',
            'rst': 'rst',
            'rb': 'ruby',
            'rs': 'rust',
            'scala': 'scala',
            'swift': 'swift',
            'md': 'markdown',
            'markdown': 'markdown',
            'tex': 'latex',
            'latex': 'latex',
            'html': 'html',
            'htm': 'html',
            'sol': 'sol',
            'cs': 'csharp',
            'cobol': 'cobol',
            'c': 'c',
            'h': 'c',  # C header files
            'hh': 'cpp',  # C++ header files
            'hpp': 'cpp',  # C++ header files
            'lua': 'lua',
            'pl': 'perl',
            'pm': 'perl',
            'hs': 'haskell',
        }
        self._splitters = {}
        self._text_chunk_size = text_chunk_size
        self._text_chunk_overlap = text_chunk_overlap
        self._code_chunk_size = code_chunk_size
        self._code_chunk_overlap = code_chunk_overlap

    def _load_file_data(self, file_path: str) -> list[Document]:
        try:
            return TextLoader(file_path=file_path, encoding='utf-8', autodetect_encoding=True).load()
        except Exception:
            return []

    def _is_code_file(self, file_suffix: str):
        return file_suffix in self._file_suffix_code_mapping

    def get_current_gitignore_matchers(self) -> Callable[[str], bool] | None:
        default_gitignore_matchers = parse_gitignore_str(""".mypy_cache/
/.coverage
/.coverage.*
/.nox/
/.python-version
/.pytype/
/dist/
/docs/_build/
/src/*.egg-info/
__pycache__/
.idea/
.vscode/
build/
dist/
logs/
venv/
.venv/
node_modules/
""", base_dir=self._workspace)
        gitignore_path = os.path.join(self._workspace, '.gitignore')
        if os.path.exists(gitignore_path):
            return lambda f: default_gitignore_matchers(f) or parse_gitignore(gitignore_path, base_dir=self._workspace)(f)
        return default_gitignore_matchers

    def index_codebase(self):
        print(f'[codebase]: {self._lang.CODEBASE_START_INDEX} {self._workspace}', flush=True)

        gitignore_matchers = self.get_current_gitignore_matchers()

        documents = []

        for root, dirs, files in os.walk(self._workspace):
            # 构建当前目录相对于工作空间的路径
            relative_root = os.path.relpath(root, self._workspace)

            # 过滤掉被 .gitignore 忽略的目录（提前剪枝）
            filtered_dirs = []
            for d in dirs:
                dir_path = os.path.join(relative_root, d)
                # ignore .gitignore
                if gitignore_matchers and gitignore_matchers(dir_path):
                    continue
                filtered_dirs.append(d)
            dirs[:] = filtered_dirs  # 替换，实现剪枝

            for file in files:
                file_path = os.path.join(root, file)
                documents += self.add_file_documents(file_path, gitignore_matchers)

        print(self._lang.CODEBASE_FINISH_INDEX.format(len(documents)))

    def search_codebase(self, query: str, k: int = 5) -> list[Document]:
        if not self._vectorstore:
            return []

        return self._vectorstore.similarity_search(query, k=k)

    def add_file_documents(self, file_path: str,
                           gitignore_matchers: Callable[[str], bool] | None = None):

        file_suffix = file_path.split('.')[-1]
        relative_path = os.path.relpath(file_path, self._workspace)

        # ignore .gitignore
        if gitignore_matchers and gitignore_matchers(relative_path):
            return []

        current_mtime = os.path.getmtime(file_path)

        # load file as documents
        current_documents = self._load_file_data(file_path)

        if not current_documents:
            return []

        splitter_key = self._file_suffix_code_mapping[file_suffix] if file_suffix in self._file_suffix_code_mapping else 'text'
        splitter = self._splitters.get(file_suffix)
        if splitter is None:
            if splitter_key == 'text':
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self._text_chunk_size,
                    chunk_overlap=self._text_chunk_overlap,
                    length_function=len,
                    is_separator_regex=False,
                )
            else:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    Language(splitter_key),
                    chunk_size=self._code_chunk_size,
                    chunk_overlap=self._code_chunk_overlap,
                )
            self._splitters[splitter_key] = splitter

        current_documents = splitter.split_documents(current_documents)

        # 更新 mtime 记录
        if self._embeddings and not self._vectorstore:
            self._vectorstore = self._vector_store_cls.from_documents(current_documents, self._embeddings)
        else:
            self._vectorstore.add_documents(current_documents)
        return current_documents

    def remove_file_documents(self, file_path: str):
        if not self._vectorstore:
            return
        file_path = os.path.abspath(file_path)
        if hasattr(self._vectorstore, 'delete'):
            self._vectorstore.delete(filter={'source': file_path})

    def update_file_documents(self, file_path: str):
        self.remove_file_documents(file_path)
        self.add_file_documents(file_path)
