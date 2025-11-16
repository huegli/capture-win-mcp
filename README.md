# capture-win-mcp

MCP (Model Context Protocol) server for capturing macOS windows and tracking Spaces. This server provides tools for AI assistants to interact with macOS windows through yabai and the built-in `screencapture` utility.

**📖 [Quick Start Guide](QUICK_START.md)** | **📦 [Distribution Guide](DISTRIBUTION.md)** | **👨‍💻 [Developer Docs](CLAUDE.md)**

## Features

- **List Windows**: Get detailed information about all windows organized by macOS Space (virtual desktop)
- **Capture Window**: Take screenshots of specific windows by their ID

## Prerequisites

- macOS (tested on macOS 15+)
- Python 3.12 or higher
- [yabai](https://github.com/koekeishiya/yabai) window manager

### Installing yabai

```bash
brew install koekeishiya/formulae/yabai
yabai --start-service
```

## Installation

### Method 1: Install from GitHub (Recommended)

Using `uv`:
```bash
uv pip install git+https://github.com/yourusername/capture-win-mcp.git
```

Using `pip`:
```bash
pip install git+https://github.com/yourusername/capture-win-mcp.git
```

### Method 2: Install from PyPI

Once published to PyPI:
```bash
# Using uv
uv pip install capture-win-mcp

# Using pip
pip install capture-win-mcp
```

### Method 3: Install from Source (For Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/capture-win-mcp.git
cd capture-win-mcp

# Create virtual environment
uv venv  # or: python3 -m venv venv
source .venv/bin/activate

# Install in editable mode
uv pip install -e .  # or: pip install -e .
```

## Usage

### As an MCP Server

#### Claude Desktop Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

**If installed via pip/uv (recommended):**
```json
{
  "mcpServers": {
    "capture-win": {
      "command": "capture-win-mcp"
    }
  }
}
```

**If running from source directory:**
```json
{
  "mcpServers": {
    "capture-win": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/capture-win-mcp",
        "run",
        "capture-win-mcp"
      ]
    }
  }
}
```

**If using a specific Python environment:**
```json
{
  "mcpServers": {
    "capture-win": {
      "command": "/path/to/venv/bin/capture-win-mcp"
    }
  }
}
```

After adding the configuration, restart Claude Desktop for the changes to take effect.

### Available Tools

#### `list_windows`

Lists all windows organized by macOS Space.

**Parameters:**
- `format` (optional): Output format - `"json"` (default) or `"summary"`

**Example:**
```json
{
  "format": "summary"
}
```

**Returns:** Window and Space information including:
- Space index, label, visibility status
- Window ID, title, app name, position, size
- Window counts per Space

#### `capture_window`

Captures a screenshot of a specific window.

**Parameters:**
- `window_id` (required): The window ID to capture (get this from `list_windows`)
- `include_shadow` (optional): Include window shadow in capture (default: `true`)

**Example:**
```json
{
  "window_id": 12345,
  "include_shadow": false
}
```

**Returns:** Base64-encoded PNG image of the window

### Standalone Usage

You can also use the original window tracking functionality:

```bash
# Show windows by space
python main.py

# Show spaces summary
python main.py --spaces

# Export to JSON
python main.py --export output.json
```

## Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Run the MCP server
python -m capture_win_mcp.server
```

## Architecture

- `capture_win_mcp/tracker.py`: EnhancedSpaceTracker class that interfaces with yabai
- `capture_win_mcp/server.py`: MCP server implementation with tools
- `main.py`: Standalone CLI tool for window tracking

## Troubleshooting

### "yabai not found" error

Make sure yabai is installed and running:

```bash
brew install koekeishiya/formulae/yabai
yabai --start-service
```

### Window capture fails

- Ensure the window ID is valid (use `list_windows` first)
- Check that macOS Screen Recording permissions are granted
- Some system windows may not be capturable

## License

MIT
