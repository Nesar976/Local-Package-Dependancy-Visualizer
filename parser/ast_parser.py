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
    def parse_file(self, file_path: str) -> Optional[ast.Module]:
        """
        Parse a Python file and extract its AST.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            AST module node or None if parsing fails
        """
        file_path = Path(file_path).resolve()
        
        if file_path in self.parsed_files:                #check file path is already parsed
            return self.parsed_files[str(file_path)]            #if yes return stord parsed file 
        
        try:                                                        #to catch error
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))
                self.parsed_files[str(file_path)] = tree                #save the tree
                self._extract_imports(str(file_path), tree)
                self._extract_exports(str(file_path), tree)
                self.file_lines[str(file_path)] = len(content.splitlines())
                return tree
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return None
    
    def _extract_imports(self, file_path: str, tree: ast.Module):
        """Extract all imports from an AST node."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name, node.lineno, 'import'))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                imports.append((module, node.lineno, 'from_import'))
                for alias in node.names:
                    imports.append((f"{module}.{alias.name}", node.lineno, 'from_import'))
        
        self.file_imports[file_path] = imports
    
    def _extract_exports(self, file_path: str, tree: ast.Module):
        """Extract exported names (functions, classes, constants) from AST."""
        exports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):
                    exports.add(node.name)
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith('_'):
                    exports.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and not target.id.startswith('_'):
                        exports.add(target.id)
        
        self.file_exports[file_path] = exports
    def parse_directory(self, directory: Optional[str] = None, exclude_dirs: Optional[Set[str]] = None) -> int:
        """
        Recursively parse all Python files in a directory.
        
        Args:
            directory: Directory to parse (defaults to project_root)
            exclude_dirs: Set of directory names to exclude (e.g., {'__pycache__', '.git'})
            
        Returns:
            Number of files parsed
        """
        if directory is None:
            directory = self.project_root
        else:
            directory = Path(directory).resolve()
        
        if exclude_dirs is None:
            exclude_dirs = {'__pycache__', '.git', '.venv', 'venv', 'env', '.env', 'node_modules', '.pytest_cache'}
        
        count = 0
        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if self.parse_file(str(file_path)) is not None:
                        count += 1
        
        return count
    def get_imports(self, file_path: str) -> List[Tuple[str, int, str]]:
        """Get all imports for a file."""
        return self.file_imports.get(file_path, [])
    
    def get_exports(self, file_path: str) -> Set[str]:
        """Get all exports for a file."""
        return self.file_exports.get(file_path, set())
    
    def get_line_count(self, file_path: str) -> int:
        """Get line count for a file."""
        return self.file_lines.get(file_path, 0)
    
    def get_all_files(self) -> List[str]:
        """Get list of all parsed files."""
        return list(self.parsed_files.keys())
