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

