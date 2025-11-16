#!/usr/bin/env python3
"""MCP server for capturing macOS windows and tracking Spaces."""

import asyncio
import base64
import json
import subprocess
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .tracker import EnhancedSpaceTracker


# Initialize the MCP server
app = Server("capture-win-mcp")

# Global tracker instance
tracker = EnhancedSpaceTracker()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_windows",
            description="List all windows organized by macOS Space. Returns detailed information about windows, spaces, and which windows belong to which Space.",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "Output format: 'json' (structured data) or 'summary' (human-readable)",
                        "enum": ["json", "summary"],
                        "default": "json"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="capture_window",
            description="Capture a screenshot of a specific window by its ID. Returns the image as base64-encoded PNG. Use list_windows first to get window IDs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "window_id": {
                        "type": "integer",
                        "description": "The window ID to capture (from list_windows)"
                    },
                    "include_shadow": {
                        "type": "boolean",
                        "description": "Include window shadow in the capture",
                        "default": True
                    }
                },
                "required": ["window_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""

    if name == "list_windows":
        return await handle_list_windows(arguments)
    elif name == "capture_window":
        return await handle_capture_window(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_list_windows(arguments: dict) -> list[TextContent]:
    """Handle list_windows tool call."""
    try:
        # Refresh tracker data
        tracker.refresh()

        format_type = arguments.get("format", "json")

        if format_type == "json":
            # Return structured JSON data
            data = tracker.get_all_data()
            return [
                TextContent(
                    type="text",
                    text=json.dumps(data, indent=2)
                )
            ]
        else:  # summary format
            # Return human-readable summary
            data = tracker.get_all_data()
            windows_by_space = tracker.get_windows_by_space()

            summary_lines = []
            summary_lines.append(f"Total Spaces: {data['summary']['total_spaces']}")
            summary_lines.append(f"Total Windows: {data['summary']['total_windows']}")
            summary_lines.append("")

            # Create space map for quick lookup
            space_map = {s.get('index'): s for s in data['spaces']}

            for space_index in sorted(windows_by_space.keys()):
                windows = windows_by_space[space_index]
                space_info = space_map.get(space_index, {})
                space_label = space_info.get('label', '(unlabeled)')
                is_visible = space_info.get('is-visible', False)
                visibility = "VISIBLE" if is_visible else "hidden"

                summary_lines.append(f"Space {space_index}: {space_label} ({visibility})")
                summary_lines.append(f"  {len(windows)} window(s)")

                for window in windows:
                    app_name = window.get('app', 'Unknown')
                    title = window.get('title', '(Untitled)')
                    win_id = window.get('id', 0)
                    summary_lines.append(f"    - [{app_name}] {title} (ID: {win_id})")

                summary_lines.append("")

            return [
                TextContent(
                    type="text",
                    text="\n".join(summary_lines)
                )
            ]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error listing windows: {str(e)}"
            )
        ]


async def handle_capture_window(arguments: dict) -> list[ImageContent | TextContent]:
    """Handle capture_window tool call."""
    try:
        window_id = arguments.get("window_id")
        include_shadow = arguments.get("include_shadow", True)

        if window_id is None:
            return [
                TextContent(
                    type="text",
                    text="Error: window_id is required"
                )
            ]

        # Refresh tracker to verify window exists
        tracker.refresh()
        window = tracker.get_window_by_id(window_id)

        if not window:
            return [
                TextContent(
                    type="text",
                    text=f"Error: Window with ID {window_id} not found"
                )
            ]

        # Create temporary file for screenshot
        temp_file = Path(f"/tmp/capture_win_{window_id}.png")

        # Build screencapture command
        cmd = ["screencapture", "-x"]  # -x: no sound

        if not include_shadow:
            cmd.append("-o")  # -o: no shadow

        cmd.extend(["-l", str(window_id)])  # -l: capture window by ID
        cmd.append(str(temp_file))

        # Capture the window
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return [
                TextContent(
                    type="text",
                    text=f"Error capturing window: {result.stderr}"
                )
            ]

        # Read and encode the image
        if not temp_file.exists():
            return [
                TextContent(
                    type="text",
                    text="Error: Screenshot file not created"
                )
            ]

        image_data = temp_file.read_bytes()
        base64_image = base64.b64encode(image_data).decode('utf-8')

        # Clean up temporary file
        temp_file.unlink()

        # Get window details for context
        app_name = window.get('app', 'Unknown')
        title = window.get('title', '(Untitled)')

        return [
            TextContent(
                type="text",
                text=f"Captured window: [{app_name}] {title} (ID: {window_id})"
            ),
            ImageContent(
                type="image",
                data=base64_image,
                mimeType="image/png"
            )
        ]

    except subprocess.TimeoutExpired:
        return [
            TextContent(
                type="text",
                text="Error: Screenshot capture timed out"
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error capturing window: {str(e)}"
            )
        ]


async def async_main():
    """Run the MCP server (async)."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Entry point for the MCP server."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
