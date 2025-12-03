#!/usr/bin/env python3
"""
CLI Interface for Local Package Dependency Visualizer

This is the main entry point for the dependency visualizer tool.
"""

import argparse
import sys
from pathlib import Path

from parser import ASTParser, ImportResolver, GraphBuilder, DynamicImportDetector
from analyzer import CycleDetector, DeadCodeDetector, ModuleAnalyzer, SplitSuggester, Visualizer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Local Package Dependency Visualizer - Analyze Python project dependencies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s . --ascii
  %(prog)s /path/to/project --graphviz output.dot
  %(prog)s . --cycles --dead-code
  %(prog)s . --suggest-splits
        """
    )
    
    parser.add_argument(
        'project_path',
        type=str,
        help='Path to the Python project root directory'
    )
    
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=['__pycache__', '.git', '.venv', 'venv', 'env', '.env', 'node_modules'],
        help='Directories to exclude from analysis (default: __pycache__, .git, .venv, etc.)'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '--ascii',
        action='store_true',
        help='Print ASCII dependency map'
    )
    output_group.add_argument(
        '--graphviz',
        type=str,
        metavar='FILE',
        help='Export dependency graph to Graphviz DOT format (or PNG/SVG/PDF if dot is installed)'
    )
    output_group.add_argument(
        '--format',
        type=str,
        choices=['dot', 'png', 'svg', 'pdf'],
        default='dot',
        help='Graphviz output format (default: dot)'
    )
    output_group.add_argument(
        '--summary',
        action='store_true',
        help='Print summary statistics'
    )
    
    # Analysis options
    analysis_group = parser.add_argument_group('Analysis Options')
    analysis_group.add_argument(
        '--cycles',
        action='store_true',
        help='Detect and report circular dependencies'
    )
    analysis_group.add_argument(
        '--dead-code',
        action='store_true',
        help='Detect unused modules and dead code'
    )
    analysis_group.add_argument(
        '--oversized',
        type=int,
        metavar='LINES',
        default=500,
        help='Report modules exceeding this line count (default: 500)'
    )
    analysis_group.add_argument(
        '--suggest-splits',
        action='store_true',
        help='Suggest module splits based on heuristics'
    )
    analysis_group.add_argument(
        '--dynamic-imports',
        action='store_true',
        help='Warn about risky dynamic imports'
    )
    
    # Visualization options
    viz_group = parser.add_argument_group('Visualization Options')
    viz_group.add_argument(
        '--highlight-cycles',
        action='store_true',
        default=True,
        help='Highlight cycles in Graphviz output (default: True)'
    )
    viz_group.add_argument(
        '--highlight-oversized',
        action='store_true',
        default=True,
        help='Highlight oversized modules in Graphviz output (default: True)'
    )
    viz_group.add_argument(
        '--max-depth',
        type=int,
        default=3,
        help='Maximum depth for ASCII map (default: 3)'
    )
    
    args = parser.parse_args()
    
    # Validate project path
    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)
    
    if not project_path.is_dir():
        print(f"Error: Project path is not a directory: {project_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Analyzing project: {project_path}")
    print("=" * 60)
    
    # Initialize components
    print("\n[1/4] Parsing Python files...")
    ast_parser = ASTParser(str(project_path))
    exclude_dirs = set(args.exclude)
    file_count = ast_parser.parse_directory(exclude_dirs=exclude_dirs)
    print(f"  Parsed {file_count} Python files")
    
    print("\n[2/4] Resolving imports...")
    resolver = ImportResolver(str(project_path))
    print(f"  Found {len(resolver.get_project_modules())} project modules")
    
    print("\n[3/4] Building dependency graph...")
    graph_builder = GraphBuilder(str(project_path))
    graph_builder.build_from_parser(ast_parser, resolver)
    print(f"  Graph: {graph_builder.get_node_count()} nodes, {graph_builder.get_edge_count()} edges")
    
    # Detect dynamic imports
    dynamic_detector = DynamicImportDetector()
    if args.dynamic_imports:
        print("\n[3.5/4] Detecting dynamic imports...")
        for file_path in ast_parser.get_all_files():
            tree = ast_parser.parsed_files.get(file_path)
            if tree:
                dynamic_detector.detect_dynamic_imports(file_path, tree)
        dynamic_imports = dynamic_detector.get_all_dynamic_imports()
        if dynamic_imports:
            print(f"  Warning: Found dynamic imports in {len(dynamic_imports)} files")
            for file_path, issues in list(dynamic_imports.items())[:5]:
                rel_path = Path(file_path).relative_to(project_path)
                print(f"    - {rel_path}: {len(issues)} dynamic import(s)")
    
    print("\n[4/4] Running analysis...")
    
    # Cycle detection
    if args.cycles:
        cycle_detector = CycleDetector(graph_builder)
        cycles = cycle_detector.detect_cycles()
        if cycles:
            print(f"\n⚠️  CIRCULAR DEPENDENCIES DETECTED: {len(cycles)} cycle(s)")
            for i, cycle in enumerate(cycles[:10], 1):
                cycle_str = cycle_detector.format_cycle(cycle, str(project_path))
                print(f"  Cycle {i}: {cycle_str}")
            if len(cycles) > 10:
                print(f"  ... and {len(cycles) - 10} more cycles")
        else:
            print("\n✓ No circular dependencies found")
    
    # Dead code detection
    if args.dead_code:
        dead_code_detector = DeadCodeDetector(graph_builder, ast_parser)
        dead_code = dead_code_detector.detect_dead_code()
        unused_modules = dead_code['unused_modules']
        unused_exports = dead_code['unused_exports']
        
        if unused_modules:
            print(f"\n⚠️  UNUSED MODULES: {len(unused_modules)} module(s)")
            for module in sorted(list(unused_modules)[:10]):
                rel_path = Path(module).relative_to(project_path)
                print(f"  - {rel_path}")
            if len(unused_modules) > 10:
                print(f"  ... and {len(unused_modules) - 10} more")
        else:
            print("\n✓ No unused modules found")
    
    # Oversized modules
    module_analyzer = ModuleAnalyzer(graph_builder, ast_parser)
    module_analyzer.analyze_all_modules()
    oversized = module_analyzer.get_oversized_modules(args.oversized)
    if oversized:
        print(f"\n⚠️  OVERSIZED MODULES (> {args.oversized} lines): {len(oversized)} module(s)")
        for file_path, line_count in oversized[:10]:
            rel_path = Path(file_path).relative_to(project_path)
            print(f"  - {rel_path}: {line_count} lines")
        if len(oversized) > 10:
            print(f"  ... and {len(oversized) - 10} more")
    
    # Split suggestions
    if args.suggest_splits:
        split_suggester = SplitSuggester(graph_builder, ast_parser)
        suggestions = split_suggester.suggest_splits()
        if suggestions:
            print(f"\n💡 MODULE SPLIT SUGGESTIONS: {len(suggestions)} module(s)")
            for file_path, file_suggestions in list(suggestions.items())[:5]:
                rel_path = Path(file_path).relative_to(project_path)
                print(f"\n  {rel_path}:")
                for suggestion in file_suggestions:
                    print(f"    - {suggestion['recommendation']}")
                    print(f"      Reason: {suggestion['reason']}")
        else:
            print("\n✓ No split suggestions")
    
    # Visualization
    visualizer = Visualizer(graph_builder, str(project_path))
    
    if args.ascii:
        print("\n" + "=" * 60)
        print("ASCII DEPENDENCY MAP")
        print("=" * 60)
        ascii_map = visualizer.generate_ascii_map(max_depth=args.max_depth)
        print(ascii_map)
    
    if args.graphviz:
        print(f"\nExporting Graphviz graph to: {args.graphviz}")
        output_file = visualizer.export_graphviz(
            args.graphviz,
            format=args.format,
            highlight_cycles=args.highlight_cycles,
            highlight_oversized=args.highlight_oversized,
            oversized_threshold=args.oversized
        )
        print(f"  ✓ Graph exported to: {output_file}")
    
    if args.summary:
        print("\n" + "=" * 60)
        summary = visualizer.generate_summary()
        print(summary)
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()

    

