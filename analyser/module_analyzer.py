"""
Module Analyzer - Analyzes module size and complexity.
"""

from typing import Dict, List, Tuple
from pathlib import Path


class ModuleAnalyzer:
    """Analyzes modules for size, complexity, and other metrics."""
    
    def __init__(self, graph, parser):
        """
        Initialize the module analyzer.
        
        Args:
            graph: GraphBuilder instance
            parser: ASTParser instance
        """
        self.graph = graph
        self.parser = parser
        self.metrics: Dict[str, Dict] = {}
    
    def analyze_all_modules(self) -> Dict[str, Dict]:
        """
        Analyze all modules and compute metrics.
        
        Returns:
            Dictionary mapping file paths to metrics
        """
        self.metrics = {}
        
        for file_path in self.graph.get_all_nodes():
            metrics = self._analyze_module(file_path)
            self.metrics[file_path] = metrics
        
        return self.metrics.copy()
    
    def _analyze_module(self, file_path: str) -> Dict:
        """Analyze a single module and return metrics."""
        line_count = self.parser.get_line_count(file_path)
        exports = self.parser.get_exports(file_path)
        dependencies = self.graph.get_dependencies(file_path)
        dependents = self.graph.get_dependents(file_path)
        
        metadata = self.graph.get_metadata(file_path)
        
        return {
            'line_count': line_count,
            'export_count': len(exports),
            'dependency_count': len(dependencies),
            'dependent_count': len(dependents),
            'fan_in': len(dependents),
            'fan_out': len(dependencies),
            'complexity_score': self._calculate_complexity(
                line_count, len(dependencies), len(dependents)
            ),
        }
    
    def _calculate_complexity(self, lines: int, deps: int, dependents: int) -> float:
        """
        Calculate a complexity score for a module.
        
        Args:
            lines: Number of lines
            deps: Number of dependencies
            dependents: Number of dependents
            
        Returns:
            Complexity score
        """
        # Simple heuristic: combine size and coupling
        size_factor = min(lines / 1000, 1.0)  # Normalize to 0-1
        coupling_factor = min((deps + dependents) / 20, 1.0)  # Normalize to 0-1
        return (size_factor * 0.6 + coupling_factor * 0.4) * 100
    
    def get_oversized_modules(self, threshold: int = 500) -> List[Tuple[str, int]]:
        """
        Get modules that exceed the line count threshold.
        
        Args:
            threshold: Line count threshold (default: 500)
            
        Returns:
            List of (file_path, line_count) tuples, sorted by line count
        """
        oversized = []
        
        for file_path, metrics in self.metrics.items():
            if metrics['line_count'] > threshold:
                oversized.append((file_path, metrics['line_count']))
        
        return sorted(oversized, key=lambda x: x[1], reverse=True)
    
    def get_highly_coupled_modules(self, threshold: int = 10) -> List[Tuple[str, int]]:
        """
        Get modules with high coupling (many dependencies or dependents).
        
        Args:
            threshold: Total coupling threshold (deps + dependents)
            
        Returns:
            List of (file_path, coupling_count) tuples, sorted by coupling
        """
        highly_coupled = []
        
        for file_path, metrics in self.metrics.items():
            total_coupling = metrics['dependency_count'] + metrics['dependent_count']
            if total_coupling > threshold:
                highly_coupled.append((file_path, total_coupling))
        
        return sorted(highly_coupled, key=lambda x: x[1], reverse=True)
    
    def get_metrics(self, file_path: str) -> Dict:
        """Get metrics for a specific module."""
        return self.metrics.get(file_path, {})
    
    def get_all_metrics(self) -> Dict[str, Dict]:
        """Get all computed metrics."""
        return self.metrics.copy()

