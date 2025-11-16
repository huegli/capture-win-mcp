# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`capture-win-mcp` is a Model Context Protocol (MCP) server that enables AI assistants to interact with macOS windows. It provides two primary capabilities:
1. Listing all windows organized by macOS Spaces (virtual desktops)
2. Capturing screenshots of specific windows by ID

The server leverages `yabai` (a tiling window manager) for accurate window tracking and macOS's built-in `screencapture` utility for screenshot capture.

## Architecture

### Module Structure

- **`capture_win_mcp/tracker.py`**: Core window tracking logic
  - `EnhancedSpaceTracker` class interfaces with yabai via subprocess calls
  - Queries spaces (`yabai -m query --spaces`) and windows (`yabai -m query --windows`)
  - Maintains cached `spaces_data` and `windows_data` as JSON lists
  - All yabai calls have 5-second timeouts for safety

- **`capture_win_mcp/server.py`**: MCP server implementation
  - Uses the official Python MCP SDK (`mcp` package)
  - Exposes two tools: `list_windows` and `capture_window`
  - Runs via stdio transport (stdin/stdout)
  - Returns images as base64-encoded PNG data

- **`main.py`**: Legacy standalone CLI tool (kept for backward compatibility)

### Data Flow

1. **List Windows**:
   - Tool called → `tracker.refresh()` queries yabai → data cached
   - Returns either structured JSON or human-readable summary
   - Organizes windows by Space with metadata (app, title, ID, position, visibility)

2. **Capture Window**:
   - Tool called with window_id → `tracker.refresh()` verifies window exists
   - `screencapture -x -l <window_id>` captures to `/tmp/capture_win_<id>.png`
   - Image read, base64-encoded, temporary file deleted
   - Returns text metadata + ImageContent with base64 data

## Development Commands

### Environment Setup

```bash
# Create virtual environment with uv
uv venv
source .venv/bin/activate  # or `. .venv/bin/activate`

# Install in editable mode
uv pip install -e .
```

### Running the MCP Server

```bash
# Direct execution
python -m capture_win_mcp.server

# Or using the installed script
capture-win-mcp
```

### Testing Tools Manually

The standalone CLI can verify yabai integration works:

```bash
# List windows by space (human-readable)
python main.py

# Show spaces summary
python main.py --spaces

# Export full data to JSON
python main.py --export test_output.json
```

### Installing yabai (Required Dependency)

```bash
brew install koekeishiya/formulae/yabai
yabai --start-service

# Verify it works
yabai -m query --spaces
yabai -m query --windows
```

## MCP Integration

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

After adding, restart Claude Desktop. The tools will appear automatically.

## Important Implementation Notes

### Error Handling Pattern

All subprocess calls use this pattern:
```python
try:
    result = subprocess.run([...], timeout=5, capture_output=True, text=True)
    # Process result
except Exception as e:
    # Log warning but don't crash
    return []  # or raise with user-friendly message
```

### Security Considerations

- Window IDs are validated before capture (must exist in tracker data)
- Screenshot files use temporary paths in `/tmp/` and are deleted immediately after encoding
- No arbitrary command execution - all subprocess calls use fixed command lists

### Platform Limitations

- **macOS only**: Uses macOS-specific tools (screencapture, yabai)
- **yabai required**: Without it, tracker will raise RuntimeError
- **Permissions needed**: macOS Screen Recording permissions must be granted to Terminal/IDE running the server

### Data Structures

**Space object** (from yabai):
```json
{
  "index": 1,
  "label": "Main",
  "is-visible": true,
  "is-native-fullscreen": false,
  "display": 1,
  "windows": [123, 456]
}
```

**Window object** (from yabai):
```json
{
  "id": 123,
  "app": "Chrome",
  "title": "Example Page",
  "space": 1,
  "frame": {"x": 0, "y": 0, "w": 1920, "h": 1080},
  "is-floating": false,
  "is-minimized": false
}
```

## Testing Changes

After modifying the server:
1. Reinstall: `uv pip install -e .`
2. Restart Claude Desktop (or MCP client)
3. Test both tools: first `list_windows`, then `capture_window` with a valid ID

## Common Issues

- **"yabai not found"**: Install yabai and ensure it's in PATH
- **"Window not found"**: Window may have closed between list and capture - refresh and retry
- **Empty screenshot**: Some system windows are not capturable by screencapture
- **MCP connection fails**: Check that the path in config is absolute and server script is executable
- **"coroutine 'main' was never awaited"**: The entry point must be a synchronous function that calls `asyncio.run()`. In `server.py`, `main()` is the sync entry point that calls `async_main()`
