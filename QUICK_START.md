# Quick Start Guide

Get `capture-win-mcp` up and running in 5 minutes!

## 1. Install Prerequisites

```bash
# Install yabai (required for window tracking)
brew install koekeishiya/formulae/yabai
yabai --start-service
```

## 2. Install capture-win-mcp

### Option A: From GitHub (Recommended)

```bash
pip install git+https://github.com/yourusername/capture-win-mcp.git
```

### Option B: From Source

```bash
git clone https://github.com/yourusername/capture-win-mcp.git
cd capture-win-mcp
pip install -e .
```

### Option C: From PyPI (once published)

```bash
pip install capture-win-mcp
```

## 3. Verify Installation

```bash
# Check the command is available
capture-win-mcp --help

# Test window tracking (standalone mode)
python -m capture_win_mcp.tracker
```

## 4. Configure with Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "capture-win": {
      "command": "capture-win-mcp"
    }
  }
}
```

## 5. Restart Claude Desktop

After restarting, you'll have access to two new tools:

### List Windows
Ask Claude: "List all my windows organized by Space"

### Capture Window
Ask Claude: "Take a screenshot of my Safari window"

## Example Workflow

1. **List windows**: "Show me all windows across my Spaces"
2. **Find a window**: Claude will show you windows with their IDs
3. **Capture it**: "Capture window ID 12345" or "Capture my Chrome window"

## Troubleshooting

### yabai not found
```bash
brew install koekeishiya/formulae/yabai
yabai --start-service
```

### MCP server not connecting
- Verify installation: `which capture-win-mcp`
- Check config path is correct
- Restart Claude Desktop
- Check logs at `~/Library/Logs/Claude/`

### Permission issues
Grant Screen Recording permissions to your terminal/IDE in:
**System Settings → Privacy & Security → Screen Recording**

## Next Steps

- Read the full [README.md](README.md)
- Check [DISTRIBUTION.md](DISTRIBUTION.md) to share with others
- See [CLAUDE.md](CLAUDE.md) for developer documentation
