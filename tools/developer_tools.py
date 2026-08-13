"""
Developer Agent Tools - Code writing, execution, and technical tasks.
"""
import os
import re
import subprocess
import tempfile
from typing import Optional


def execute_python(code: str, timeout: int = 30) -> dict:
    """
    Execute Python code in a sandboxed environment.

    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds

    Returns:
        dict: Contains 'output', 'error', and 'return_code'
    """
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir()
        )

        os.unlink(temp_file)

        return {
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Execution timed out after {timeout} seconds", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def execute_shell(command: str, timeout: int = 30) -> dict:
    """
    Execute a shell command.

    Args:
        command: Shell command to execute
        timeout: Maximum execution time in seconds

    Returns:
        dict: Contains 'output', 'error', and 'return_code'
    """
    # Block dangerous commands
    dangerous_patterns = [
        r'\brm\s+-rf\s+[/~]',
        r'\bformat\b',
        r'\bdel\s+/[sq]',
        r'\bshutdown\b',
        r'>\s*/dev/sd',
        r'\bmkfs\b',
        r'\bdd\s+if=',
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return {"error": "Potentially dangerous command blocked", "success": False}

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {timeout} seconds", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def analyze_code(code: str, language: str = "python") -> dict:
    """
    Analyze code for potential issues, complexity, and style.

    Args:
        code: Source code to analyze
        language: Programming language (python, javascript, etc.)

    Returns:
        dict: Analysis results including metrics and suggestions
    """
    lines = code.split('\n')
    non_empty_lines = [l for l in lines if l.strip()]
    comment_lines = []

    if language == "python":
        comment_lines = [l for l in lines if l.strip().startswith('#')]
        function_pattern = r'def\s+(\w+)\s*\('
        class_pattern = r'class\s+(\w+)'
        import_pattern = r'^(?:from|import)\s+'
    elif language in ["javascript", "typescript"]:
        comment_lines = [l for l in lines if l.strip().startswith('//') or l.strip().startswith('/*')]
        function_pattern = r'(?:function\s+(\w+)|(\w+)\s*[=:]\s*(?:async\s*)?\([^)]*\)\s*=>)'
        class_pattern = r'class\s+(\w+)'
        import_pattern = r'^(?:import|require)\s*\(?'
    else:
        function_pattern = r'function\s+(\w+)'
        class_pattern = r'class\s+(\w+)'
        import_pattern = r'^(?:import|include|require)'

    functions = re.findall(function_pattern, code)
    classes = re.findall(class_pattern, code)
    imports = [l for l in lines if re.match(import_pattern, l.strip())]

    # Calculate complexity indicators
    nested_depth = 0
    max_depth = 0
    for line in lines:
        indent = len(line) - len(line.lstrip())
        if language == "python":
            depth = indent // 4
        else:
            depth = line.count('{') - line.count('}')
            nested_depth += depth
            depth = nested_depth
        max_depth = max(max_depth, depth)

    # Identify potential issues
    issues = []

    if language == "python":
        if re.search(r'except\s*:', code):
            issues.append("Bare 'except:' clause - consider catching specific exceptions")
        if re.search(r'eval\s*\(', code):
            issues.append("Use of eval() - potential security risk")
        if re.search(r'exec\s*\(', code):
            issues.append("Use of exec() - potential security risk")
        if any(len(l) > 100 for l in lines):
            issues.append("Lines exceeding 100 characters - consider breaking up")

    # Calculate comment ratio
    comment_ratio = len(comment_lines) / len(non_empty_lines) if non_empty_lines else 0

    return {
        "total_lines": len(lines),
        "code_lines": len(non_empty_lines),
        "comment_lines": len(comment_lines),
        "comment_ratio": round(comment_ratio, 2),
        "functions": functions if isinstance(functions[0], str) if functions else [] else [f[0] or f[1] for f in functions] if functions else [],
        "classes": classes,
        "imports": len(imports),
        "max_nesting_depth": max_depth,
        "issues": issues,
        "language": language
    }


def format_code(code: str, language: str = "python") -> dict:
    """
    Format/prettify code according to language standards.

    Args:
        code: Source code to format
        language: Programming language

    Returns:
        dict: Contains 'formatted' code or 'error'
    """
    if language == "python":
        try:
            import textwrap
            # Basic Python formatting
            lines = code.split('\n')
            formatted_lines = []
            indent_level = 0

            for line in lines:
                stripped = line.strip()

                # Decrease indent for these keywords
                if stripped.startswith(('else:', 'elif ', 'except:', 'except ', 'finally:', 'elif:', 'except ')):
                    indent_level = max(0, indent_level - 1)

                if stripped:
                    formatted_lines.append('    ' * indent_level + stripped)
                else:
                    formatted_lines.append('')

                # Increase indent after these
                if stripped.endswith(':') and not stripped.startswith('#'):
                    indent_level += 1
                # Decrease indent for return/break/continue/pass
                if stripped.startswith(('return ', 'return', 'break', 'continue', 'pass', 'raise ')):
                    indent_level = max(0, indent_level - 1)

            return {"formatted": '\n'.join(formatted_lines), "language": language}
        except Exception as e:
            return {"error": str(e)}

    elif language == "json":
        try:
            import json
            parsed = json.loads(code)
            return {"formatted": json.dumps(parsed, indent=2), "language": language}
        except Exception as e:
            return {"error": f"Invalid JSON: {e}"}

    else:
        return {"formatted": code, "language": language, "note": "No formatter available for this language"}


def search_documentation(query: str, language: str = "python") -> dict:
    """
    Search programming documentation and resources.

    Args:
        query: Search query
        language: Programming language context

    Returns:
        dict: Documentation search results
    """
    import urllib.request
    from urllib.parse import quote_plus

    # Map languages to documentation sites
    doc_sites = {
        "python": "docs.python.org",
        "javascript": "developer.mozilla.org",
        "typescript": "typescriptlang.org",
        "rust": "doc.rust-lang.org",
        "go": "pkg.go.dev",
    }

    site = doc_sites.get(language, "")
    site_filter = f"site:{site}" if site else ""

    search_query = f"{language} {query} {site_filter}".strip()
    search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(search_query)}"

    try:
        req = urllib.request.Request(
            search_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="replace")

        results = []
        result_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        links = re.findall(result_pattern, html)

        for url, title in links[:5]:
            if "uddg=" in url:
                url_match = re.search(r'uddg=([^&]+)', url)
                if url_match:
                    url = urllib.request.unquote(url_match.group(1))
            results.append({"title": title.strip(), "url": url})

        return {"query": query, "language": language, "results": results}

    except Exception as e:
        return {"error": str(e)}


def generate_gitignore(project_type: str) -> dict:
    """
    Generate a .gitignore file for common project types.

    Args:
        project_type: Type of project (python, node, java, etc.)

    Returns:
        dict: Contains 'content' with gitignore content
    """
    templates = {
        "python": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
.env
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/
""",
        "node": """# Node
node_modules/
npm-debug.log*
yarn-error.log*
.env
.env.local
dist/
build/
.cache/
coverage/
*.log
""",
        "java": """# Java
*.class
*.jar
*.war
*.ear
target/
.gradle/
build/
.idea/
*.iml
.settings/
.project
.classpath
""",
        "go": """# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
vendor/
go.sum
""",
        "rust": """# Rust
target/
Cargo.lock
**/*.rs.bk
""",
    }

    content = templates.get(project_type.lower())
    if content:
        return {"content": content.strip(), "project_type": project_type}
    else:
        available = list(templates.keys())
        return {"error": f"Unknown project type. Available: {', '.join(available)}"}


def create_dockerfile(language: str, framework: Optional[str] = None) -> dict:
    """
    Generate a Dockerfile for common project types.

    Args:
        language: Programming language (python, node, go, etc.)
        framework: Optional framework (flask, fastapi, express, etc.)

    Returns:
        dict: Contains 'content' with Dockerfile content
    """
    templates = {
        "python": """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
""",
        "python-fastapi": """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
        "python-flask": """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["flask", "run", "--host", "0.0.0.0"]
""",
        "node": """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000
CMD ["node", "index.js"]
""",
        "node-express": """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000
CMD ["node", "server.js"]
""",
        "go": """FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/main .

EXPOSE 8080
CMD ["./main"]
""",
    }

    key = f"{language}-{framework}" if framework else language
    content = templates.get(key.lower()) or templates.get(language.lower())

    if content:
        return {"content": content.strip(), "language": language, "framework": framework}
    else:
        available = list(set(k.split('-')[0] for k in templates.keys()))
        return {"error": f"Unknown language. Available: {', '.join(available)}"}


def git_status(repo_path: str = ".") -> dict:
    """
    Get git repository status.

    Args:
        repo_path: Path to the git repository

    Returns:
        dict: Git status information
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "-b"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return {"error": result.stderr or "Not a git repository"}

        lines = result.stdout.strip().split('\n')
        branch_line = lines[0] if lines else ""
        branch = branch_line.replace("## ", "").split("...")[0] if branch_line.startswith("##") else "unknown"

        # Parse file status
        staged = []
        modified = []
        untracked = []

        for line in lines[1:]:
            if not line:
                continue
            status = line[:2]
            filename = line[3:]

            if status[0] in "MADRC":
                staged.append({"file": filename, "status": status[0]})
            if status[1] in "MD":
                modified.append({"file": filename, "status": status[1]})
            if status == "??":
                untracked.append(filename)

        return {
            "branch": branch,
            "staged": staged,
            "modified": modified,
            "untracked": untracked,
            "clean": len(staged) == 0 and len(modified) == 0 and len(untracked) == 0
        }
    except Exception as e:
        return {"error": str(e)}


def git_log(repo_path: str = ".", count: int = 10) -> dict:
    """
    Get recent git commits.

    Args:
        repo_path: Path to the git repository
        count: Number of commits to retrieve

    Returns:
        dict: List of recent commits
    """
    try:
        result = subprocess.run(
            ["git", "log", f"-{count}", "--pretty=format:%H|%an|%ae|%s|%ci"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return {"error": result.stderr or "Failed to get git log"}

        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0][:8],
                        "full_hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "message": parts[3],
                        "date": parts[4]
                    })

        return {"commits": commits, "count": len(commits)}
    except Exception as e:
        return {"error": str(e)}


def git_diff(repo_path: str = ".", staged: bool = False, file_path: str = None) -> dict:
    """
    Get git diff for changes.

    Args:
        repo_path: Path to the git repository
        staged: If True, show staged changes; otherwise show unstaged
        file_path: Optional specific file to diff

    Returns:
        dict: Diff output
    """
    try:
        cmd = ["git", "diff"]
        if staged:
            cmd.append("--staged")
        if file_path:
            cmd.append(file_path)

        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return {"error": result.stderr or "Failed to get diff"}

        diff_output = result.stdout
        if len(diff_output) > 50000:
            diff_output = diff_output[:50000] + "\n... (truncated)"

        # Parse stats
        additions = len(re.findall(r'^\+[^+]', diff_output, re.MULTILINE))
        deletions = len(re.findall(r'^-[^-]', diff_output, re.MULTILINE))

        return {
            "diff": diff_output,
            "stats": {
                "additions": additions,
                "deletions": deletions
            },
            "staged": staged
        }
    except Exception as e:
        return {"error": str(e)}


def git_commit(message: str, repo_path: str = ".", add_all: bool = False) -> dict:
    """
    Create a git commit.

    Args:
        message: Commit message
        repo_path: Path to the git repository
        add_all: If True, stage all changes before committing

    Returns:
        dict: Commit result
    """
    try:
        if add_all:
            add_result = subprocess.run(
                ["git", "add", "-A"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if add_result.returncode != 0:
                return {"error": f"Failed to stage changes: {add_result.stderr}"}

        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            if "nothing to commit" in result.stdout:
                return {"message": "Nothing to commit", "success": True}
            return {"error": result.stderr or result.stdout}

        # Extract commit hash from output
        hash_match = re.search(r'\[[\w\-/]+\s+([a-f0-9]+)\]', result.stdout)
        commit_hash = hash_match.group(1) if hash_match else "unknown"

        return {
            "success": True,
            "message": message,
            "hash": commit_hash,
            "output": result.stdout
        }
    except Exception as e:
        return {"error": str(e)}


def git_branch(repo_path: str = ".", action: str = "list", branch_name: str = None) -> dict:
    """
    Manage git branches.

    Args:
        repo_path: Path to the git repository
        action: Action to perform (list, create, delete, current)
        branch_name: Branch name for create/delete actions

    Returns:
        dict: Branch operation result
    """
    try:
        if action == "list":
            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            branches = []
            current = None
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line.startswith('*'):
                    current = line[2:]
                    branches.append(current)
                elif line:
                    branches.append(line)
            return {"branches": branches, "current": current}

        elif action == "current":
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return {"current": result.stdout.strip()}

        elif action == "create":
            if not branch_name:
                return {"error": "Branch name required"}
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return {"error": result.stderr}
            return {"success": True, "branch": branch_name, "message": f"Created and switched to {branch_name}"}

        elif action == "delete":
            if not branch_name:
                return {"error": "Branch name required"}
            result = subprocess.run(
                ["git", "branch", "-d", branch_name],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return {"error": result.stderr}
            return {"success": True, "message": f"Deleted branch {branch_name}"}

        else:
            return {"error": f"Unknown action: {action}. Use: list, create, delete, current"}

    except Exception as e:
        return {"error": str(e)}


def git_checkout(target: str, repo_path: str = ".") -> dict:
    """
    Checkout a branch or file.

    Args:
        target: Branch name or file path to checkout
        repo_path: Path to the git repository

    Returns:
        dict: Checkout result
    """
    try:
        result = subprocess.run(
            ["git", "checkout", target],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return {"error": result.stderr}

        return {"success": True, "target": target, "output": result.stdout or result.stderr}
    except Exception as e:
        return {"error": str(e)}


def git_pull(repo_path: str = ".", remote: str = "origin", branch: str = None) -> dict:
    """
    Pull changes from remote.

    Args:
        repo_path: Path to the git repository
        remote: Remote name (default: origin)
        branch: Branch to pull (default: current branch)

    Returns:
        dict: Pull result
    """
    try:
        cmd = ["git", "pull", remote]
        if branch:
            cmd.append(branch)

        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            return {"error": result.stderr}

        return {
            "success": True,
            "output": result.stdout,
            "remote": remote,
            "branch": branch
        }
    except Exception as e:
        return {"error": str(e)}


def git_push(repo_path: str = ".", remote: str = "origin", branch: str = None, set_upstream: bool = False) -> dict:
    """
    Push changes to remote.

    Args:
        repo_path: Path to the git repository
        remote: Remote name (default: origin)
        branch: Branch to push (default: current branch)
        set_upstream: If True, set upstream tracking

    Returns:
        dict: Push result
    """
    try:
        cmd = ["git", "push"]
        if set_upstream:
            cmd.extend(["-u", remote])
            if branch:
                cmd.append(branch)
        else:
            cmd.append(remote)
            if branch:
                cmd.append(branch)

        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            return {"error": result.stderr}

        return {
            "success": True,
            "output": result.stdout or result.stderr,
            "remote": remote,
            "branch": branch
        }
    except Exception as e:
        return {"error": str(e)}


def git_stash(repo_path: str = ".", action: str = "save", message: str = None) -> dict:
    """
    Manage git stash.

    Args:
        repo_path: Path to the git repository
        action: Action (save, pop, list, drop, apply)
        message: Optional stash message for save action

    Returns:
        dict: Stash operation result
    """
    try:
        if action == "save":
            cmd = ["git", "stash", "push"]
            if message:
                cmd.extend(["-m", message])
        elif action == "pop":
            cmd = ["git", "stash", "pop"]
        elif action == "list":
            cmd = ["git", "stash", "list"]
        elif action == "drop":
            cmd = ["git", "stash", "drop"]
        elif action == "apply":
            cmd = ["git", "stash", "apply"]
        else:
            return {"error": f"Unknown action: {action}"}

        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0 and "No stash" not in result.stderr:
            return {"error": result.stderr}

        if action == "list":
            stashes = [s for s in result.stdout.strip().split('\n') if s]
            return {"stashes": stashes, "count": len(stashes)}

        return {"success": True, "action": action, "output": result.stdout or result.stderr}
    except Exception as e:
        return {"error": str(e)}


def generate_readme(project_name: str, description: str, language: str, features: list = None) -> dict:
    """
    Generate a README.md template for a project.

    Args:
        project_name: Name of the project
        description: Short description
        language: Primary programming language
        features: List of key features

    Returns:
        dict: Contains 'content' with README markdown
    """
    install_commands = {
        "python": "pip install -r requirements.txt",
        "node": "npm install",
        "go": "go mod download",
        "rust": "cargo build",
    }

    run_commands = {
        "python": "python main.py",
        "node": "npm start",
        "go": "go run .",
        "rust": "cargo run",
    }

    install_cmd = install_commands.get(language.lower(), "# Add install command")
    run_cmd = run_commands.get(language.lower(), "# Add run command")

    features_md = ""
    if features:
        features_md = "\n## Features\n\n" + "\n".join(f"- {f}" for f in features)

    content = f"""# {project_name}

{description}
{features_md}

## Installation

```bash
{install_cmd}
```

## Usage

```bash
{run_cmd}
```

## License

MIT
"""

    return {"content": content.strip()}