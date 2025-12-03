"""
AST Parser - Walks Python AST to extract imports and module information.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


class ASTParser:
    """Parses Python files using AST to extract imports and module structure."""
    
    def __init__(self, project_root: str):
        """
        Initialize the AST parser.
        
        Args:
            project_root: Root directory of the Python project
        """
        self.project_root = Path(project_root).resolve()        #to clear the path
        self.parsed_files: Dict[str, ast.Module] = {}
        self.file_imports: Dict[str, List[Tuple[str, int, str]]] = {}  # file -> [(import_name, line, import_type), ...]
        self.file_exports: Dict[str, Set[str]] = {}  # file -> {exported_names}
        self.file_lines: Dict[str, int] = {}  # file -> line_count