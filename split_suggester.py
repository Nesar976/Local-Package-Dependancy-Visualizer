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

