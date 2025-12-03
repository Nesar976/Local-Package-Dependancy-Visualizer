# CLI Description - Local Package Dependency Visualizer

## Overview

The Local Package Dependency Visualizer is a command-line tool that analyzes Python projects to build dependency graphs, detect issues, and provide actionable refactoring suggestions. The tool is designed to be fast enough for integration into pre-commit hooks and provides both human-readable and machine-readable output formats.

## Command Structure

```bash
python cli.py <project_path> [OPTIONS]
```

## Required Arguments

- **`project_path`**: Path to the Python project root directory to analyze

## Optional Arguments

### Output Options

- **`--ascii`**: Print an ASCII dependency map showing the module hierarchy
- **`--graphviz FILE`**: Export the dependency graph to a Graphviz DOT file (or PNG/SVG/PDF if Graphviz is installed)
- **`--format {dot,png,svg,pdf}`**: Specify the Graphviz output format (default: `dot`)
- **`--summary`**: Print summary statistics about the dependency graph

### Analysis Options

- **`--cycles`**: Detect and report circular dependencies (cycles in the dependency graph)
- **`--dead-code`**: Detect unused modules and dead code that is not reachable from entry points
- **`--oversized LINES`**: Report modules exceeding the specified line count (default: 500 lines)
- **`--suggest-splits`**: Suggest module splits based on heuristics (class grouping, function grouping, import usage)
- **`--dynamic-imports`**: Warn about risky dynamic imports (e.g., `__import__()`, `importlib.import_module()`)

### Visualization Options

- **`--highlight-cycles`**: Highlight nodes involved in cycles in Graphviz output (default: True)
- **`--highlight-oversized`**: Highlight oversized modules in Graphviz output (default: True)
- **`--max-depth DEPTH`**: Maximum depth for ASCII map visualization (default: 3)

### Filtering Options

- **`--exclude DIR [DIR ...]`**: Directories to exclude from analysis (default: `__pycache__`, `.git`, `.venv`, `venv`, `env`, `.env`, `node_modules`)

## Usage Examples

### Basic Analysis
```bash
# Analyze current directory with default checks
python cli.py .

# Analyze specific project
python cli.py /path/to/myproject
```

### Detect Issues
```bash
# Check for cycles and dead code
python cli.py . --cycles --dead-code

# Find oversized modules (over 300 lines)
python cli.py . --oversized 300

# Check for dynamic imports
python cli.py . --dynamic-imports
```

### Generate Visualizations
```bash
# Print ASCII dependency map
python cli.py . --ascii

# Export to Graphviz DOT format
python cli.py . --graphviz dependencies.dot

# Export to PNG (requires Graphviz)
python cli.py . --graphviz dependencies.png --format png

# Export to SVG
python cli.py . --graphviz dependencies.svg --format svg
```

### Get Refactoring Suggestions
```bash
# Get module split suggestions
python cli.py . --suggest-splits

# Full analysis with all checks
python cli.py . --cycles --dead-code --oversized 400 --suggest-splits --dynamic-imports
```

### Comprehensive Report
```bash
# Full analysis with all outputs
python cli.py . \
  --cycles \
  --dead-code \
  --oversized 500 \
  --suggest-splits \
  --dynamic-imports \
  --ascii \
  --graphviz deps.dot \
  --summary
```

## Output Description

### ASCII Map
The ASCII map shows a tree structure of module dependencies:
```
├─ main.py
  ├─ parser/ast_parser.py
  ├─ parser/import_resolver.py
  └─ analyzer/cycle_detector.py
```

### Graphviz Export
The Graphviz export creates a visual graph where:
- **Nodes** represent Python modules/files
- **Edges** represent import dependencies
- **Red nodes/edges** indicate cycles
- **Orange nodes** indicate oversized modules
- Node labels include file paths and line counts

### Cycle Detection
Reports circular dependencies in the format:
```
Cycle 1: module_a.py -> module_b.py -> module_c.py -> module_a.py -> ...
```

### Dead Code Detection
Lists modules that are not reachable from any entry point (main files, root nodes).

### Oversized Module Detection
Lists modules exceeding the specified line count threshold, sorted by size.

### Split Suggestions
Provides heuristic-based suggestions for splitting large modules:
- **Class grouping**: Suggests splitting modules with many classes into separate files
- **Function grouping**: Suggests splitting modules with many functions by name prefix
- **Import grouping**: Suggests splitting based on different import dependencies
- **Utility split**: Suggests splitting large utility modules into domain-specific modules

### Dynamic Import Warnings
Warns about potentially risky dynamic imports:
- Direct `__import__()` calls
- `importlib.import_module()` usage
- `exec()`/`eval()` calls that might contain imports

## Integration with Pre-commit

The tool is designed to be fast enough for pre-commit hooks. Example `.pre-commit-config.yaml`:

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

## Exit Codes

- **0**: Success
- **1**: Error (invalid arguments, file not found, etc.)

## Performance

The tool is optimized for medium-sized repositories:
- Parses files using AST (fast, no execution)
- Builds graph in-memory
- Analysis algorithms are O(V + E) where V = vertices, E = edges
- Typically completes in seconds for projects with hundreds of files

## Limitations

- Only analyzes static imports (dynamic imports are detected but not fully resolved)
- Dead code detection uses heuristics (may have false positives)
- Split suggestions are heuristic-based and may not always be optimal
- External dependencies are not fully resolved (only project-local dependencies are tracked)