"""
Analyzer Module - Part 2 of the Local Package Dependency Visualizer

This module handles:
- Cycle detection in dependency graphs
- Dead code detection
- Oversized module detection
- Module split suggestions
- ASCII visualization
- Graphviz export
"""

from .cycle_detector import CycleDetector
from .dead_code_detector import DeadCodeDetector
from .module_analyzer import ModuleAnalyzer
from .split_suggester import SplitSuggester
from .visualizer import Visualizer

__all__ = [
    'CycleDetector',
    'DeadCodeDetector',
    'ModuleAnalyzer',
    'SplitSuggester',
    'Visualizer',
]

