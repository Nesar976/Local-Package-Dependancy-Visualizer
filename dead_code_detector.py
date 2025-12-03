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

