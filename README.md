# Local Package Dependency Visualizer

A Python tool to parse a project's imports and build a dependency graph of modules and packages. Detects cycles, dead code, and oversized modules. Provides ASCII maps and Graphviz exports. Warns about risky dynamic imports.

## Features

- **AST-based Parsing**: Walks Python ASTs to extract imports and module structure
- **Dependency Graph**: Builds a complete dependency graph of all modules
- **Cycle Detection**: Identifies circular dependencies
- **Dead Code Detection**: Finds unused modules and unreachable code
- **Oversized Module Detection**: Flags modules exceeding size thresholds
- **Module Split Suggestions**: Heuristic-based suggestions for refactoring large modules
- **Dynamic Import Detection**: Warns about risky dynamic imports
- **ASCII Visualization**: Prints human-readable dependency maps
- **Graphviz Export**: Exports graphs in DOT, PNG, SVG, or PDF formats
- **Fast Performance**: Optimized for medium-sized repositories, suitable for pre-commit hooks

## Project Structure

The project is split into two equal-weight components:

### Folder 1: `parser/` - Core Parsing and Graph Building
- `ast_parser.py`: AST walking and parsing
- `import_resolver.py`: Import resolution to file paths
- `graph_builder.py`: Dependency graph construction
- `dynamic_import_detector.py`: Dynamic import detection

### Folder 2: `analyzer/` - Analysis and Visualization
- `cycle_detector.py`: Cycle detection algorithms
- `dead_code_detector.py`: Dead code detection
- `module_analyzer.py`: Module size and complexity analysis
- `split_suggester.py`: Module split suggestions
- `visualizer.py`: ASCII maps and Graphviz export

## Installation

### Requirements

- Python 3.7+
- Standard library only (no external dependencies required)
- Optional: Graphviz (for PNG/SVG/PDF export)

### Setup

1. Clone or download this repository
2. No installation required - just run `python cli.py`

For Graphviz export to PNG/SVG/PDF:
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
# Download from https://graphviz.org/download/
```

## Usage

See [cli_description.md](cli_description.md) for detailed CLI documentation.

### Sample Test Project

A representative sample fixture lives under `tests/sample_project`. It includes circular imports, dynamic imports, oversized modules, dead code, and unused scripts so every analyzer feature has meaningful output. A helper script `tests/run_sample_demo.sh` runs the full suite.

```bash
# run manually
python cli.py tests/sample_project \
  --cycles \
  --dead-code \
  --oversized 150 \
  --suggest-splits \
  --dynamic-imports \
  --ascii \
  --summary

# or use the helper
bash tests/run_sample_demo.sh
```

### Quick Start

```bash
# Basic analysis
python cli.py .

# Detect cycles
python cli.py . --cycles

# Generate ASCII map
python cli.py . --ascii

# Export to Graphviz
python cli.py . --graphviz deps.dot

# Full analysis
python cli.py . --cycles --dead-code --oversized 500 --suggest-splits --ascii --graphviz deps.dot
```

## Examples

### Example 1: Detect Circular Dependencies

```bash
python cli.py /path/to/project --cycles
```

Output:
```
⚠️  CIRCULAR DEPENDENCIES DETECTED: 2 cycle(s)
  Cycle 1: module_a.py -> module_b.py -> module_c.py -> module_a.py -> ...
  Cycle 2: utils.py -> helpers.py -> utils.py -> ...
```

### Example 2: Find Oversized Modules

```bash
python cli.py . --oversized 300
```

Output:
```
⚠️  OVERSIZED MODULES (> 300 lines): 3 module(s)
  - parser/ast_parser.py: 450 lines
  - analyzer/visualizer.py: 380 lines
  - main.py: 320 lines
```

### Example 3: Get Split Suggestions

```bash
python cli.py . --suggest-splits
```

Output:
```
💡 MODULE SPLIT SUGGESTIONS: 2 module(s)

  parser/ast_parser.py:
    - Split into separate modules by class groups
      Reason: Module has 5 classes that could be grouped

  utils.py:
    - Consider splitting into domain-specific utility modules
      Reason: Large utility module with 25 functions
```

### Example 4: Generate Visualizations

```bash
# ASCII map
python cli.py . --ascii --max-depth 4

# Graphviz (DOT)
python cli.py . --graphviz deps.dot

# Graphviz (PNG - requires Graphviz)
python cli.py . --graphviz deps.png --format png
```

## Integration with Pre-commit

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: dependency-check
        name: Check for circular dependencies
        entry: python cli.py
        language: system
        args: ['.', '--cycles']
        pass_filenames: false
        always_run: true
```

## Technical Details

### Algorithms

- **Cycle Detection**: Uses DFS (Depth-First Search) with recursion stack tracking
- **Dead Code Detection**: BFS (Breadth-First Search) from entry points to find reachable nodes
- **Graph Building**: Constructs directed graph with nodes (files) and edges (imports)

### Performance

- Time Complexity: O(V + E) for most operations where V = vertices, E = edges
- Space Complexity: O(V + E) for graph storage
- Typically completes in seconds for projects with hundreds of files

### Limitations

- Only analyzes static imports (dynamic imports are detected but not fully resolved)
- Dead code detection uses heuristics (may have false positives)
- Split suggestions are heuristic-based
- External dependencies are not fully resolved

## Contributing

This is a student project. The codebase is split into two equal-weight components for two developers.

## License

This project is for educational purposes.

## Authors

- Sagar Veeresh Halladakeri - 251810700276
- Nesar Ravishankar Kavri - 251810700211

Group - 127

