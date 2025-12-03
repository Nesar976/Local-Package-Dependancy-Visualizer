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
    def add_node(self, file_path: str, metadata: Optional[Dict] = None):
        """
        Add a node to the graph.
        
        Args:
            file_path: Path to the file (normalized)
            metadata: Optional metadata about the node
        """
        normalized = self._normalize_path(file_path)        #clean the path
        self.nodes.add(normalized)      #add files to set of nodes
        if metadata:                            #add extra data if provided
            self.node_metadata[normalized] = metadata
        elif normalized not in self.node_metadata:
            self.node_metadata[normalized] = {}
    def add_edge(self, from_file: str, to_file: str, metadata: Optional[Dict] = None):
        """
        Add an edge to the graph.
        
        Args:
            from_file: Source file path
            to_file: Target file path
            metadata: Optional metadata about the edge
        """
        from_normalized = self._normalize_path(from_file)
        to_normalized = self._normalize_path(to_file)
        
        # Only add edges between project files
        if from_normalized not in self.nodes:
            self.add_node(from_normalized)
        if to_normalized not in self.nodes:
            self.add_node(to_normalized)
        
        edge_metadata = metadata or {}
        self.edges.append((from_normalized, to_normalized, edge_metadata))
        self.incoming[to_normalized].add(from_normalized)       #record who imports the file 
        self.outgoing[from_normalized].add(to_normalized)       #store in list
    def _normalize_path(self, file_path: str) -> str:
        """Normalize a file path to a consistent format."""
        try:
            return str(Path(file_path).resolve())
        except (OSError, ValueError):
            return str(file_path)       # is something error happens return orignal string 
    
    def get_dependencies(self, file_path: str) -> Set[str]:             #what all the file needs 
        """Get all files that the given file depends on."""
        normalized = self._normalize_path(file_path)
        return self.outgoing.get(normalized, set())
    
    def get_dependents(self, file_path: str) -> Set[str]:       
        """Get all files that depend on the given file."""
        normalized = self._normalize_path(file_path)
        return self.incoming.get(normalized, set())
    
    def get_all_nodes(self) -> Set[str]:
        """Get all nodes in the graph."""
        return self.nodes.copy()
    
    def get_all_edges(self) -> List[Tuple[str, str, Dict]]:
        """Get all edges in the graph."""
        return self.edges.copy()
    def get_node_count(self) -> int:
        """Get the number of nodes in the graph."""
        return len(self.nodes)
    
    def get_edge_count(self) -> int:
        """Get the number of edges in the graph."""
        return len(self.edges)
    
    def get_isolated_nodes(self) -> Set[str]:
        """Get nodes with no incoming or outgoing edges."""
        isolated = set()
        for node in self.nodes:
            if not self.incoming.get(node) and not self.outgoing.get(node):
                isolated.add(node)
        return isolated
    
    def get_leaf_nodes(self) -> Set[str]:
        """Get nodes with no outgoing edges (leaf nodes)."""
        return {node for node in self.nodes if not self.outgoing.get(node)}
    
    def get_root_nodes(self) -> Set[str]:
        """Get nodes with no incoming edges (root nodes)."""
        return {node for node in self.nodes if not self.incoming.get(node)}
    
    def get_metadata(self, file_path: str) -> Dict:
        """Get metadata for a node."""
        normalized = self._normalize_path(file_path)
        return self.node_metadata.get(normalized, {})
    
    def update_metadata(self, file_path: str, metadata: Dict):
        """Update metadata for a node."""
        normalized = self._normalize_path(file_path)
        if normalized in self.nodes:
            if normalized not in self.node_metadata:            #if file does not have meta data make an empty dict
                self.node_metadata[normalized] = {}
            self.node_metadata[normalized].update(metadata)
    
    def build_from_parser(self, parser, resolver):
        """
        Build graph from AST parser and import resolver.
        
        Args:
            parser: ASTParser instance
            resolver: ImportResolver instance
        """
        for file_path in parser.get_all_files():
            # Add node with metadata
            metadata = {
                'line_count': parser.get_line_count(file_path),
                'exports': list(parser.get_exports(file_path)),
                'export_count': len(parser.get_exports(file_path)),
            }
            self.add_node(file_path, metadata)
            
            # Add edges for imports
            for import_name, line_no, import_type in parser.get_imports(file_path):
                resolved = resolver.resolve_import(import_name, file_path)
                if resolved and not resolver.is_external_import(import_name):
                    edge_metadata = {
                        'line': line_no,
                        'import_type': import_type,
                        'import_name': import_name,
                    }
                    self.add_edge(file_path, resolved, edge_metadata)

