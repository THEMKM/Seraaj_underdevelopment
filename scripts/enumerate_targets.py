#!/usr/bin/env python3
"""
Path-tracing target enumeration for Seraaj project.
Scans backend Python files for FastAPI routes and other targetable symbols.
"""
import os
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Set


def find_backend_directories() -> List[Path]:
    """Find backend Python directories in the project."""
    candidates = [
        Path("apps/api"),
        Path("backend"),
        Path("src/backend"),
    ]
    return [p for p in candidates if p.exists() and p.is_dir()]


def find_frontend_directories() -> List[Path]:
    """Find frontend React/TSX directories in the project.""" 
    candidates = [
        Path("apps/web"),
        Path("frontend"), 
        Path("src/frontend"),
    ]
    return [p for p in candidates if p.exists() and p.is_dir()]


def should_skip_directory(path: Path) -> bool:
    """Check if directory should be skipped."""
    skip_dirs = {
        ".git", "node_modules", "dist", "build", ".venv", 
        "__pycache__", "tests", "docs", "ImplementationReports"
    }
    return any(part in skip_dirs for part in path.parts)


def extract_fastapi_routes(file_path: Path) -> List[Dict[str, str]]:
    """Extract FastAPI routes from a Python file."""
    targets = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return targets
    
    # Pattern for FastAPI route decorators
    # Matches: @app.get, @router.post, @app.api_route, etc.
    route_pattern = r'@(?:app|router)\.(?:get|post|put|delete|patch|head|options|api_route)\s*\('
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if re.search(route_pattern, line, re.IGNORECASE):
            # Look for the function definition on next lines
            func_name = None
            for j in range(i + 1, min(i + 5, len(lines))):
                func_match = re.match(r'(?:async\s+)?def\s+(\w+)', lines[j].strip())
                if func_match:
                    func_name = func_match.group(1)
                    break
            
            if func_name:
                # Extract HTTP method from decorator
                method_match = re.search(r'@(?:app|router)\.(\w+)', line)
                method = method_match.group(1).upper() if method_match else "UNKNOWN"
                
                # Create canonical symbol name
                file_stem = file_path.stem
                symbol = f"{file_stem}_{func_name}_{method}"
                
                targets.append({
                    "symbol": symbol,
                    "type": "route", 
                    "file": str(file_path.as_posix())
                })
    
    return targets


def extract_graphql_resolvers(file_path: Path) -> List[Dict[str, str]]:
    """Extract GraphQL resolvers from a Python file."""
    targets = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return targets
    
    # Pattern for GraphQL decorators and classes
    graphql_patterns = [
        r'@strawberry\.field',
        r'@graphene\.',
        r'class\s+\w*Query\w*',
        r'class\s+\w*Mutation\w*'
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        for pattern in graphql_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # For class definitions
                class_match = re.match(r'class\s+(\w+)', line.strip())
                if class_match:
                    class_name = class_match.group(1)
                    symbol = f"{file_path.stem}_{class_name}"
                    targets.append({
                        "symbol": symbol,
                        "type": "graphql",
                        "file": str(file_path.as_posix())
                    })
                    break
                
                # For method definitions after decorators
                func_name = None
                for j in range(i + 1, min(i + 3, len(lines))):
                    func_match = re.match(r'(?:async\s+)?def\s+(\w+)', lines[j].strip())
                    if func_match:
                        func_name = func_match.group(1)
                        break
                
                if func_name:
                    symbol = f"{file_path.stem}_{func_name}"
                    targets.append({
                        "symbol": symbol,
                        "type": "graphql",
                        "file": str(file_path.as_posix())
                    })
                break
    
    return targets


def extract_celery_tasks(file_path: Path) -> List[Dict[str, str]]:
    """Extract Celery tasks from a Python file."""
    targets = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return targets
    
    # Pattern for Celery task decorators
    task_patterns = [
        r'@celery\.task',
        r'@shared_task',
        r'@\w+\.task'
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        for pattern in task_patterns:
            if re.search(pattern, line):
                # Look for function definition
                func_name = None
                for j in range(i + 1, min(i + 3, len(lines))):
                    func_match = re.match(r'(?:async\s+)?def\s+(\w+)', lines[j].strip())
                    if func_match:
                        func_name = func_match.group(1)
                        break
                
                if func_name:
                    symbol = f"{file_path.stem}_{func_name}_TASK"
                    targets.append({
                        "symbol": symbol,
                        "type": "task",
                        "file": str(file_path.as_posix())
                    })
                break
    
    return targets


def scan_directory(directory: Path) -> List[Dict[str, str]]:
    """Recursively scan directory for targets."""
    targets = []
    
    for root, dirs, files in os.walk(directory):
        root_path = Path(root)
        
        # Skip unwanted directories
        if should_skip_directory(root_path):
            continue
            
        # Filter out skip directories from further traversal
        dirs[:] = [d for d in dirs if not should_skip_directory(root_path / d)]
        
        for file in files:
            file_path = root_path / file
            
            # Only scan Python files
            if file_path.suffix == '.py':
                targets.extend(extract_fastapi_routes(file_path))
                targets.extend(extract_graphql_resolvers(file_path))
                targets.extend(extract_celery_tasks(file_path))
    
    return targets


def main():
    """Main enumeration function."""
    # Find project directories
    backend_dirs = find_backend_directories()
    frontend_dirs = find_frontend_directories()
    
    all_targets = []
    
    # Scan backend directories
    for backend_dir in backend_dirs:
        all_targets.extend(scan_directory(backend_dir))
    
    # Deduplicate targets by symbol
    seen_symbols: Set[str] = set()
    unique_targets = []
    
    for target in all_targets:
        symbol = target["symbol"]
        if symbol not in seen_symbols:
            seen_symbols.add(symbol)
            unique_targets.append(target)
    
    # Sort by symbol name
    unique_targets.sort(key=lambda x: x["symbol"])
    
    # Write to scripts/targets.json
    output_path = Path("scripts/targets.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unique_targets, f, indent=2, ensure_ascii=False)
    
    print(f"Wrote {len(unique_targets)} targets to scripts/targets.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())