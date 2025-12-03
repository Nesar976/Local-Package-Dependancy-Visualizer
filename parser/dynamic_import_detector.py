"""
Dynamic Import Detector - Detects risky dynamic imports in Python code.
"""

import ast
from typing import List, Tuple, Dict
from pathlib import Path


class DynamicImportDetector:
    """Detects dynamic imports that may be risky or hard to analyze."""
    
    def __init__(self):
        """Initialize the dynamic import detector."""
        self.dynamic_imports: Dict[str, List[Tuple[int, str, str]]] = {}  # file -> [(line, pattern, reason), ...]
    def detect_dynamic_imports(self, file_path: str, tree: ast.Module) -> List[Tuple[int, str, str]]:
        """
        Detect dynamic imports in an AST.
        
        Args:
            file_path: Path to the file being analyzed
            tree: AST module node
            
        Returns:
            List of (line_number, pattern, reason) tuples
        """
        issues = []
        
        for node in ast.walk(tree):
            # Check for __import__() calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == '__import__':
                    issues.append((
                        node.lineno,
                        '__import__()',
                        'Direct __import__() call - dynamic import'
                    ))
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr == '__import__':
                        issues.append((
                            node.lineno,
                            'builtins.__import__()',
                            'Dynamic import via builtins.__import__()'
                        ))
            
            # Check for importlib usage
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ('import_module', 'import_module'):
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == 'importlib':
                            issues.append((
                                node.lineno,
                                'importlib.import_module()',
                                'Dynamic import via importlib.import_module()'
                            ))
                    elif node.func.attr == '__import__':
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == 'builtins':
                            issues.append((
                                node.lineno,
                                'builtins.__import__()',
                                'Dynamic import via builtins.__import__()'
                            ))
            
            # Check for exec/eval with import strings
            if isinstance(node, (ast.Exec, ast.Call)):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ('exec', 'eval', 'compile'):
                            # This is a heuristic - we can't statically analyze the string
                            issues.append((
                                node.lineno,
                                f'{node.func.id}()',
                                f'Potential dynamic import via {node.func.id}() - cannot statically analyze'
                            ))
        
        if issues:
            self.dynamic_imports[file_path] = issues
        
        return issues
    def get_dynamic_imports(self, file_path: str) -> List[Tuple[int, str, str]]:
        """Get dynamic imports detected for a file."""
        return self.dynamic_imports.get(file_path, [])
    
    def get_all_dynamic_imports(self) -> Dict[str, List[Tuple[int, str, str]]]:
        """Get all dynamic imports detected across all files."""
        return self.dynamic_imports.copy()
    
    def has_dynamic_imports(self, file_path: str) -> bool:
        """Check if a file has dynamic imports."""
        return file_path in self.dynamic_imports and len(self.dynamic_imports[file_path]) > 0