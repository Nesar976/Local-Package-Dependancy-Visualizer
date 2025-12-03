"""
Cycle Detector - Detects circular dependencies in the dependency graph.
"""

from typing import List, Set, Dict, Tuple
from collections import defaultdict


class CycleDetector:
    """Detects cycles (circular dependencies) in a dependency graph."""
    
    def __init__(self, graph):
        """
        Initialize the cycle detector.
        
        Args:
            graph: GraphBuilder instance
        """
        self.graph = graph
        self.cycles: List[List[str]] = []
        self._visited: Set[str] = set()
        self._recursion_stack: Set[str] = set()
        self._cycle_paths: List[List[str]] = []
    
    def detect_cycles(self) -> List[List[str]]:
        """
        Detect all cycles in the dependency graph.
        
        Returns:
            List of cycles, where each cycle is a list of file paths
        """
        self.cycles = []
        self._visited = set()
        self._recursion_stack = set()
        self._cycle_paths = []
        
        for node in self.graph.get_all_nodes():
            if node not in self._visited:
                self._dfs(node, [])
        
        return self.cycles.copy()
    
    def _dfs(self, node: str, path: List[str]):
        """
        Depth-first search to detect cycles.
        
        Args:
            node: Current node
            path: Current path in the DFS
        """
        if node in self._recursion_stack:
            # Found a cycle
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            # Normalize cycle (start from lexicographically smallest node)
            if cycle:
                min_idx = min(range(len(cycle)), key=lambda i: cycle[i])
                cycle = cycle[min_idx:] + cycle[:min_idx]
            # Check if we've seen this cycle before
            cycle_tuple = tuple(sorted(set(cycle)))
            if cycle_tuple not in {tuple(sorted(set(c))) for c in self.cycles}:
                self.cycles.append(cycle)
            return
        
        if node in self._visited:
            return
        
        self._visited.add(node)
        self._recursion_stack.add(node)
        path.append(node)
        
        # Visit all neighbors
        for neighbor in self.graph.get_dependencies(node):
            self._dfs(neighbor, path.copy())
        
        self._recursion_stack.remove(node)
        path.pop()
    
    def has_cycles(self) -> bool:
        """Check if the graph has any cycles."""
        if not self.cycles:
            self.detect_cycles()
        return len(self.cycles) > 0
    
    def get_cycle_count(self) -> int:
        """Get the number of cycles detected."""
        if not self.cycles:
            self.detect_cycles()
        return len(self.cycles)
    
    def get_cycles(self) -> List[List[str]]:
        """Get all detected cycles."""
        if not self.cycles:
            self.detect_cycles()
        return self.cycles.copy()
    
    def get_nodes_in_cycles(self) -> Set[str]:
        """Get all nodes that are part of at least one cycle."""
        if not self.cycles:
            self.detect_cycles()
        
        nodes_in_cycles = set()
        for cycle in self.cycles:
            nodes_in_cycles.update(cycle)
        return nodes_in_cycles
    
    def format_cycle(self, cycle: List[str], project_root: str = None) -> str:
        """
        Format a cycle for display.
        
        Args:
            cycle: List of file paths in the cycle
            project_root: Optional project root to make paths relative
            
        Returns:
            Formatted cycle string
        """
        from pathlib import Path
        
        if project_root:
            project_root = Path(project_root)
            cycle_paths = [Path(f).relative_to(project_root) for f in cycle]
        else:
            cycle_paths = [Path(f).name for f in cycle]
        
        return ' -> '.join(str(p) for p in cycle_paths) + ' -> ...'

