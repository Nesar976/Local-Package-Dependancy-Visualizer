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

