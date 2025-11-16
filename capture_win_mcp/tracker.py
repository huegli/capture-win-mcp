"""
Enhanced Space detection using macOS private APIs.
This provides better Space tracking by querying Mission Control directly.
"""

import subprocess
import json
from collections import defaultdict
from typing import Dict, List, Optional


class EnhancedSpaceTracker:
    """Enhanced tracker using yabai for accurate Space detection."""

    def __init__(self):
        self.has_yabai = self._check_yabai()
        self.spaces_data = None
        self.windows_data = None

    def _check_yabai(self) -> bool:
        """Check if yabai is installed."""
        try:
            subprocess.run(['which', 'yabai'],
                         capture_output=True,
                         check=True,
                         timeout=2)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _query_yabai_spaces(self) -> List[Dict]:
        """Query yabai for space information."""
        try:
            result = subprocess.run(
                ['yabai', '-m', 'query', '--spaces'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Warning: Could not query yabai spaces: {e}")
            return []

    def _query_yabai_windows(self) -> List[Dict]:
        """Query yabai for window information."""
        try:
            result = subprocess.run(
                ['yabai', '-m', 'query', '--windows'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Warning: Could not query yabai windows: {e}")
            return []

    def refresh(self):
        """Refresh space and window data."""
        if self.has_yabai:
            self.spaces_data = self._query_yabai_spaces()
            self.windows_data = self._query_yabai_windows()
        else:
            raise RuntimeError("yabai not found. Install with: brew install koekeishiya/formulae/yabai")

    def get_windows_by_space(self) -> Dict[int, List[Dict]]:
        """Get windows organized by space index."""
        if not self.windows_data:
            return {}

        windows_by_space = defaultdict(list)
        for window in self.windows_data:
            space_index = window.get('space', 0)
            windows_by_space[space_index].append(window)

        return dict(windows_by_space)

    def get_window_by_id(self, window_id: int) -> Optional[Dict]:
        """Get a specific window by its ID."""
        if not self.windows_data:
            return None

        for window in self.windows_data:
            if window.get('id') == window_id:
                return window

        return None

    def get_all_data(self) -> Dict:
        """Get all space and window data."""
        windows_by_space = self.get_windows_by_space()

        return {
            'spaces': self.spaces_data or [],
            'windows': self.windows_data or [],
            'summary': {
                'total_spaces': len(self.spaces_data) if self.spaces_data else 0,
                'total_windows': len(self.windows_data) if self.windows_data else 0,
                'windows_by_space': {
                    f"space_{k}": len(v) for k, v in windows_by_space.items()
                }
            }
        }
