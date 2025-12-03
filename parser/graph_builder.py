"""
Graph Builder - Constructs dependency graph from parsed imports.
"""

from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
from collections import defaultdict


class GraphBuilder:
    """Builds a dependency graph from parsed imports."""
    
    def __init__(self, project_root: str):
        """
        Initialize the graph builder.
        
        Args:
            project_root: Root directory of the Python project
        """
        self.project_root = Path(project_root).resolve()
        self.nodes: Set[str] = set()  # All file nodes
        self.edges: List[Tuple[str, str, Dict]] = []  # (from, to, metadata)
        self.incoming: Dict[str, Set[str]] = defaultdict(set)  # to -> {from, ...}
        self.outgoing: Dict[str, Set[str]] = defaultdict(set)  # from -> {to, ...}
        self.node_metadata: Dict[str, Dict] = {}  # file -> metadata