"""
Visualizer - Creates ASCII maps and Graphviz exports.
"""

from typing import Dict, List, Set, Optional
from pathlib import Path
from collections import defaultdict, deque


class Visualizer:
    """Creates visualizations of the dependency graph."""
    
    def __init__(self, graph, project_root: str):
        """
        Initialize the visualizer.
        
        Args:
            graph: GraphBuilder instance
            project_root: Root directory of the project
        """
        self.graph = graph
        self.project_root = Path(project_root).resolve()
    
    def generate_ascii_map(self, max_depth: int = 3, max_width: int = 80) -> str:
        """
        Generate an ASCII dependency map.
        
        Args:
            max_depth: Maximum depth to display
            max_width: Maximum width of the output
            
        Returns:
            ASCII string representation of the graph
        """
        lines = []
        lines.append("=" * max_width)
        lines.append("DEPENDENCY MAP")
        lines.append("=" * max_width)
        lines.append("")
        
        # Get root nodes (nodes with no incoming edges)
        root_nodes = self.graph.get_root_nodes()
        
        if not root_nodes:
            # If no root nodes, pick nodes with fewest dependencies
            all_nodes = list(self.graph.get_all_nodes())
            if all_nodes:
                root_nodes = {min(all_nodes, key=lambda n: len(self.graph.get_dependencies(n)))}
        
        visited = set()
        
        for root in sorted(root_nodes):
            if root not in visited:
                self._ascii_dfs(root, lines, visited, 0, max_depth, max_width)
        
        # Add isolated nodes
        isolated = self.graph.get_isolated_nodes() - visited
        if isolated:
            lines.append("")
            lines.append("ISOLATED MODULES:")
            for node in sorted(isolated):
                rel_path = self._get_relative_path(node)
                lines.append(f"  {rel_path}")
        
        return '\n'.join(lines)
    
    def _ascii_dfs(self, node: str, lines: List[str], visited: Set[str], 
                   depth: int, max_depth: int, max_width: int):
        """Recursive helper for ASCII map generation."""
        if depth > max_depth or node in visited:
            return
        
        visited.add(node)
        rel_path = self._get_relative_path(node)
        
        # Truncate if too long
        if len(rel_path) > max_width - (depth * 2) - 4:
            rel_path = rel_path[:max_width - (depth * 2) - 7] + "..."
        
        indent = "  " * depth
        lines.append(f"{indent}├─ {rel_path}")
        
        deps = sorted(self.graph.get_dependencies(node))
        for i, dep in enumerate(deps):
            is_last = (i == len(deps) - 1)
            if depth + 1 <= max_depth:
                if is_last:
                    prefix = "  " * (depth + 1) + "└─ "
                else:
                    prefix = "  " * (depth + 1) + "├─ "
                
                dep_rel = self._get_relative_path(dep)
                if len(dep_rel) > max_width - len(prefix) - 4:
                    dep_rel = dep_rel[:max_width - len(prefix) - 7] + "..."
                
                lines.append(f"{prefix}{dep_rel}")
                
                if dep not in visited and depth + 1 < max_depth:
                    self._ascii_dfs(dep, lines, visited, depth + 2, max_depth, max_width)
    
    def _get_relative_path(self, file_path: str) -> str:
        """Get relative path from project root."""
        try:
            return str(Path(file_path).relative_to(self.project_root))
        except ValueError:
            return Path(file_path).name
    
    def export_graphviz(self, output_file: str, format: str = 'dot',
                       show_external: bool = False, 
                       highlight_cycles: bool = True,
                       highlight_oversized: bool = True,
                       oversized_threshold: int = 500) -> str:
        """
        Export the dependency graph to Graphviz DOT format.
        
        Args:
            output_file: Output file path
            format: Graphviz format ('dot', 'png', 'svg', 'pdf')
            show_external: Whether to show external dependencies
            highlight_cycles: Whether to highlight nodes in cycles
            highlight_oversized: Whether to highlight oversized modules
            oversized_threshold: Line count threshold for oversized modules
            
        Returns:
            Path to the generated file
        """
        from .cycle_detector import CycleDetector
        
        # Detect cycles if needed
        nodes_in_cycles = set()
        if highlight_cycles:
            cycle_detector = CycleDetector(self.graph)
            nodes_in_cycles = cycle_detector.get_nodes_in_cycles()
        
        # Find oversized modules
        oversized_nodes = set()
        if highlight_oversized:
            for node in self.graph.get_all_nodes():
                metadata = self.graph.get_metadata(node)
                if metadata.get('line_count', 0) > oversized_threshold:
                    oversized_nodes.add(node)
        
        # Generate DOT content
        dot_lines = ['digraph Dependencies {']
        dot_lines.append('  rankdir=LR;')
        dot_lines.append('  node [shape=box, style=rounded];')
        dot_lines.append('')
        
        # Add nodes
        for node in sorted(self.graph.get_all_nodes()):
            rel_path = self._get_relative_path(node)
            node_id = self._sanitize_id(node)
            
            # Determine node style
            color = 'black'
            style = 'rounded'
            
            if node in nodes_in_cycles:
                color = 'red'
                style = 'rounded, bold'
            elif node in oversized_nodes:
                color = 'orange'
            
            metadata = self.graph.get_metadata(node)
            label = rel_path
            if metadata.get('line_count'):
                label += f'\\n({metadata["line_count"]} lines)'
            
            dot_lines.append(f'  "{node_id}" [label="{label}", color={color}, style={style}];')
        
        dot_lines.append('')
        
        # Add edges
        for from_node, to_node, edge_meta in self.graph.get_all_edges():
            from_id = self._sanitize_id(from_node)
            to_id = self._sanitize_id(to_node)
            
            # Determine edge style
            edge_style = 'solid'
            if from_node in nodes_in_cycles and to_node in nodes_in_cycles:
                edge_style = 'bold'
                color = 'red'
            else:
                color = 'gray'
            
            dot_lines.append(f'  "{from_id}" -> "{to_id}" [style={edge_style}, color={color}];')
        
        dot_lines.append('}')
        
        dot_content = '\n'.join(dot_lines)
        
        # Write DOT file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(dot_content)
        
        # If format is not 'dot', try to render it (requires graphviz)
        if format != 'dot':
            try:
                import subprocess
                rendered_path = output_path.with_suffix(f'.{format}')
                subprocess.run(
                    ['dot', f'-T{format}', str(output_path), '-o', str(rendered_path)],
                    check=True,
                    capture_output=True
                )
                return str(rendered_path)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Graphviz not available, just return DOT file
                print(f"Warning: Could not render {format}. DOT file saved: {output_path}")
                return str(output_path)
        
        return str(output_path)
    
    def _sanitize_id(self, file_path: str) -> str:
        """Create a sanitized ID for Graphviz nodes."""
        # Replace special characters with underscores
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', file_path)
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        return sanitized
    
    def generate_summary(self) -> str:
        """Generate a text summary of the dependency graph."""
        lines = []
        lines.append("DEPENDENCY GRAPH SUMMARY")
        lines.append("=" * 50)
        lines.append("")
        
        nodes = self.graph.get_all_nodes()
        edges = self.graph.get_all_edges()
        
        lines.append(f"Total modules: {len(nodes)}")
        lines.append(f"Total dependencies: {len(edges)}")
        lines.append("")
        
        # Root nodes
        root_nodes = self.graph.get_root_nodes()
        lines.append(f"Root modules (no dependencies): {len(root_nodes)}")
        for node in sorted(root_nodes)[:5]:
            lines.append(f"  - {self._get_relative_path(node)}")
        if len(root_nodes) > 5:
            lines.append(f"  ... and {len(root_nodes) - 5} more")
        lines.append("")
        
        # Leaf nodes
        leaf_nodes = self.graph.get_leaf_nodes()
        lines.append(f"Leaf modules (no dependents): {len(leaf_nodes)}")
        for node in sorted(leaf_nodes)[:5]:
            lines.append(f"  - {self._get_relative_path(node)}")
        if len(leaf_nodes) > 5:
            lines.append(f"  ... and {len(leaf_nodes) - 5} more")
        lines.append("")
        
        # Isolated nodes
        isolated = self.graph.get_isolated_nodes()
        if isolated:
            lines.append(f"Isolated modules: {len(isolated)}")
            for node in sorted(isolated)[:5]:
                lines.append(f"  - {self._get_relative_path(node)}")
            if len(isolated) > 5:
                lines.append(f"  ... and {len(isolated) - 5} more")
            lines.append("")
        
        return '\n'.join(lines)
