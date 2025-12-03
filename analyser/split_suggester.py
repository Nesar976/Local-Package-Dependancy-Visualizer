"""
Split Suggester - Suggests module splits based on heuristics.
"""

from typing import List, Dict, Tuple, Set
from pathlib import Path
import ast


class SplitSuggester:
    """Suggests how to split large modules into smaller ones."""
    
    def __init__(self, graph, parser):
        """
        Initialize the split suggester.
        
        Args:
            graph: GraphBuilder instance
            parser: ASTParser instance
        """
        self.graph = graph
        self.parser = parser
        self.suggestions: Dict[str, List[Dict]] = {}
    
    def suggest_splits(self, min_lines: int = 300, min_functions: int = 10) -> Dict[str, List[Dict]]:
        """
        Suggest module splits based on heuristics.
        
        Args:
            min_lines: Minimum lines to consider for splitting
            min_functions: Minimum functions/classes to consider for splitting
            
        Returns:
            Dictionary mapping file paths to split suggestions
        """
        self.suggestions = {}
        
        for file_path in self.graph.get_all_nodes():
            line_count = self.parser.get_line_count(file_path)
            
            if line_count < min_lines:
                continue
            
            tree = self.parser.parsed_files.get(file_path)
            if not tree:
                continue
            
            suggestions = self._analyze_for_splits(file_path, tree, min_functions)
            if suggestions:
                self.suggestions[file_path] = suggestions
        
        return self.suggestions.copy()
    
    def _analyze_for_splits(self, file_path: str, tree: ast.Module, min_functions: int) -> List[Dict]:
        """Analyze a module and suggest how to split it."""
        suggestions = []
        
        # Group top-level definitions by type
        classes = []
        functions = []
        constants = []
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(node)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node)
            elif isinstance(node, ast.Assign):
                constants.append(node)
        
        # Heuristic 1: Split by class groups (if many classes)
        if len(classes) >= 3:
            # Group classes by name similarity or relatedness
            class_groups = self._group_classes(classes)
            if len(class_groups) > 1:
                suggestions.append({
                    'type': 'class_grouping',
                    'reason': f'Module has {len(classes)} classes that could be grouped',
                    'groups': len(class_groups),
                    'recommendation': 'Split into separate modules by class groups',
                })
        
        # Heuristic 2: Split by function groups (if many functions)
        if len(functions) >= min_functions:
            # Check if functions can be grouped by name prefix or purpose
            function_groups = self._group_functions(functions)
            if len(function_groups) > 1:
                suggestions.append({
                    'type': 'function_grouping',
                    'reason': f'Module has {len(functions)} functions that could be grouped',
                    'groups': len(function_groups),
                    'recommendation': 'Split into separate modules by function groups',
                })
        
        # Heuristic 3: Split by import usage
        import_groups = self._group_by_imports(file_path, tree)
        if len(import_groups) > 1:
            suggestions.append({
                'type': 'import_grouping',
                'reason': 'Functions/classes use different import sets',
                'groups': len(import_groups),
                'recommendation': 'Split modules based on import dependencies',
            })
        
        # Heuristic 4: Split large single-purpose modules
        if len(classes) == 0 and len(functions) >= 15:
            suggestions.append({
                'type': 'utility_split',
                'reason': f'Large utility module with {len(functions)} functions',
                'recommendation': 'Consider splitting into domain-specific utility modules',
            })
        
        return suggestions
    
    def _group_classes(self, classes: List[ast.ClassDef]) -> List[List[ast.ClassDef]]:
        """Group classes by name similarity."""
        groups = []
        used = set()
        
        for i, cls in enumerate(classes):
            if i in used:
                continue
            
            group = [cls]
            used.add(i)
            
            # Find classes with similar names
            base_name = cls.name.lower()
            for j, other_cls in enumerate(classes[i+1:], start=i+1):
                if j in used:
                    continue
                
                other_name = other_cls.name.lower()
                # Check for common prefix
                if self._common_prefix(base_name, other_name) >= 3:
                    group.append(other_cls)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _group_functions(self, functions: List[ast.FunctionDef]) -> List[List[ast.FunctionDef]]:
        """Group functions by name prefix."""
        groups = []
        used = set()
        
        for i, func in enumerate(functions):
            if i in used:
                continue
            
            group = [func]
            used.add(i)
            
            # Find functions with similar prefixes
            base_name = func.name.lower()
            prefix = self._get_prefix(base_name)
            
            for j, other_func in enumerate(functions[i+1:], start=i+1):
                if j in used:
                    continue
                
                other_name = other_func.name.lower()
                other_prefix = self._get_prefix(other_name)
                
                if prefix and prefix == other_prefix and len(prefix) >= 3:
                    group.append(other_func)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _group_by_imports(self, file_path: str, tree: ast.Module) -> List[Set[str]]:
        """Group definitions by their import usage."""
        # This is a simplified version - in practice, you'd analyze
        # which imports each function/class uses
        return [set()]  # Placeholder
    
    def _common_prefix(self, s1: str, s2: str) -> int:
        """Find length of common prefix between two strings."""
        i = 0
        while i < min(len(s1), len(s2)) and s1[i] == s2[i]:
            i += 1
        return i
    
    def _get_prefix(self, name: str) -> str:
        """Extract prefix from a function name (e.g., 'get_user' -> 'get')."""
        parts = name.split('_')
        if len(parts) > 1:
            return parts[0]
        return ''
    
    def get_suggestions(self, file_path: str) -> List[Dict]:
        """Get split suggestions for a file."""
        return self.suggestions.get(file_path, [])
    
    def get_all_suggestions(self) -> Dict[str, List[Dict]]:
        """Get all split suggestions."""
        return self.suggestions.copy()
    
    def format_suggestion(self, file_path: str, suggestion: Dict, project_root: str = None) -> str:
        """Format a split suggestion for display."""
        rel_path = Path(file_path).relative_to(Path(project_root)) if project_root else Path(file_path).name
        
        lines = [
            f"File: {rel_path}",
            f"  Type: {suggestion['type']}",
            f"  Reason: {suggestion['reason']}",
            f"  Recommendation: {suggestion['recommendation']}",
        ]
        
        if 'groups' in suggestion:
            lines.append(f"  Suggested groups: {suggestion['groups']}")
        
        return '\n'.join(lines)
