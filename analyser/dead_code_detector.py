"""
Dead Code Detector - Detects unused modules and dead code.
"""

from typing import Set, Dict, List
from pathlib import Path


class DeadCodeDetector:
    """Detects dead code and unused modules in the project."""
    
    def __init__(self, graph, parser):
        """
        Initialize the dead code detector.
        
        Args:
            graph: GraphBuilder instance
            parser: ASTParser instance
        """
        self.graph = graph
        self.parser = parser
        self.unused_modules: Set[str] = set()
        self.unused_exports: Dict[str, Set[str]] = {}  # file -> {unused_export, ...}
    
    def detect_dead_code(self, entry_points: List[str] = None) -> Dict[str, Set[str]]:
        """
        Detect dead code starting from entry points.
        
        Args:
            entry_points: List of entry point files (e.g., main.py, __main__.py)
                          If None, uses root nodes and files with 'main' in name
        
        Returns:
            Dictionary with 'unused_modules' and 'unused_exports' keys
        """
        if entry_points is None:
            entry_points = self._find_entry_points()
        
        # Find all reachable nodes from entry points
        reachable = set()
        to_visit = list(entry_points)
        
        while to_visit:
            current = to_visit.pop()
            if current in reachable:
                continue
            
            reachable.add(current)
            # Add all dependencies
            for dep in self.graph.get_dependencies(current):
                if dep not in reachable:
                    to_visit.append(dep)
            # Add all dependents (reverse direction)
            for dependent in self.graph.get_dependents(current):
                if dependent not in reachable:
                    to_visit.append(dependent)
        
        # Find unused modules (not reachable from entry points)
        all_nodes = self.graph.get_all_nodes()
        self.unused_modules = all_nodes - reachable
        
        # Find unused exports
        self.unused_exports = {}
        for file_path in all_nodes:
            exports = self.parser.get_exports(file_path)
            if not exports:
                continue
            
            # Check if exports are used (heuristic: check if file is imported)
            # This is a simplified check - in reality, we'd need to check if
            # specific names are imported
            dependents = self.graph.get_dependents(file_path)
            if not dependents and file_path not in entry_points:
                # File is not imported anywhere and not an entry point
                self.unused_exports[file_path] = exports
        
        return {
            'unused_modules': self.unused_modules,
            'unused_exports': self.unused_exports,
        }
    
    def _find_entry_points(self) -> List[str]:
        """Find potential entry points in the project."""
        entry_points = []
        
        # Look for common entry point patterns
        for file_path in self.graph.get_all_nodes():
            path_obj = Path(file_path)
            name = path_obj.name.lower()
            
            if name in ('__main__.py', 'main.py', 'app.py', 'run.py', 'cli.py'):
                entry_points.append(file_path)
            elif 'main' in name or 'entry' in name or 'start' in name:
                entry_points.append(file_path)
        
        # If no entry points found, use root nodes
        if not entry_points:
            root_nodes = self.graph.get_root_nodes()
            if root_nodes:
                entry_points = list(root_nodes)
            else:
                # Fallback: use all nodes (conservative approach)
                entry_points = list(self.graph.get_all_nodes())
        
        return entry_points
    
    def get_unused_modules(self) -> Set[str]:
        """Get set of unused modules."""
        return self.unused_modules.copy()
    
    def get_unused_exports(self) -> Dict[str, Set[str]]:
        """Get dictionary of unused exports per file."""
        return self.unused_exports.copy()
    
    def format_unused_module(self, file_path: str, project_root: str = None) -> str:
        """Format an unused module path for display."""
        if project_root:
            return str(Path(file_path).relative_to(Path(project_root)))
        return Path(file_path).name

