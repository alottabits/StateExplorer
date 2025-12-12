"""
ARIA snapshot capture using Playwright.

Uses Playwright's native aria_snapshot() API to capture accessibility trees.
This module provides the Playwright-specific async methods that capture data
which is then processed by ModelResilienceCore's platform-agnostic algorithms.
"""

from __future__ import annotations
import re
import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Page

logger = logging.getLogger(__name__)


class AriaSnapshotCapture:
    """
    Captures and parses ARIA snapshots from web pages.
    
    Uses Playwright's native aria_snapshot() API which provides a YAML
    representation of the accessibility tree. This API is standardized
    and maintained by the Playwright team.
    """
    
    @staticmethod
    async def capture(page: Page) -> dict[str, Any] | None:
        """
        Capture ARIA snapshot from current page.
        
        Args:
            page: Playwright Page object
            
        Returns:
            Parsed accessibility tree as dictionary, or None if capture fails
        """
        try:
            # Use Playwright's native ariaSnapshot() API - returns YAML string
            locator = page.locator('body')
            yaml_snapshot = await locator.aria_snapshot()
            
            # Parse YAML to extract structured data
            tree = AriaSnapshotCapture._parse_yaml_snapshot(yaml_snapshot)
            return tree
        except Exception as e:
            logger.warning(f"Error capturing ARIA snapshot: {e}")
            return None
    
    @staticmethod
    async def capture_with_main_heading(page: Page) -> tuple[dict[str, Any] | None, str]:
        """
        Capture ARIA snapshot and main heading together.
        
        Args:
            page: Playwright Page object
            
        Returns:
            Tuple of (accessibility_tree, main_heading)
        """
        tree = await AriaSnapshotCapture.capture(page)
        heading = await AriaSnapshotCapture.get_main_heading(page)
        return tree, heading
    
    @staticmethod
    async def get_main_heading(page: Page) -> str:
        """Get the main heading (h1) from the page.
        
        Args:
            page: Playwright Page object
            
        Returns:
            Text content of first h1 element, or empty string
        """
        try:
            h1 = page.locator('h1').first
            if await h1.count() > 0:
                return await h1.text_content() or ""
        except Exception:
            pass
        return ""
    
    @staticmethod
    def _parse_yaml_snapshot(yaml_str: str) -> dict[str, Any]:
        """Parse ARIA snapshot YAML into structured tree.
        
        ARIA snapshot format (actual example):
            - navigation:
              - list:
                - listitem:
                  - link "Overview":
                    - /url: "#!/overview"
            - heading "Dashboard" [level=2]
            - button "Submit"
        
        Args:
            yaml_str: YAML string from ariaSnapshot()
            
        Returns:
            Parsed tree structure with role/name/children
        """
        lines = yaml_str.strip().split('\n')
        root = {'role': 'root', 'name': '', 'children': []}
        stack = [(-2, root)]  # (indent_level, node)
        
        for line in lines:
            # Calculate indent level (each indent is 2 spaces)
            indent = (len(line) - len(line.lstrip()))
            content = line.strip()
            
            if not content or content.startswith('#'):
                continue
            
            # Skip URL lines (they're metadata, not nodes)
            if content.startswith('- /url:') or content.startswith('/url:'):
                # Extract URL and add to parent node
                url_match = re.search(r'/url:\s*"([^"]+)"', content)
                if url_match and stack:
                    parent = stack[-1][1]
                    parent['value'] = url_match.group(1)
                continue
            
            # Remove leading '- '
            if content.startswith('- '):
                content = content[2:]
            
            # Skip if it's just a key: value pair (not a role)
            if not content or content.startswith('/'):
                continue
            
            # Parse node: role "name" [attributes]
            node: dict[str, Any] = {'children': []}
            
            # Check for attributes in brackets
            attr_match = re.search(r'\[([^\]]+)\]$', content)
            if attr_match:
                attrs_str = attr_match.group(1)
                content = content[:attr_match.start()].strip()
                
                # Parse attributes (level=1, pressed=true, etc.)
                for attr_pair in attrs_str.split(','):
                    if '=' in attr_pair:
                        key, val = attr_pair.split('=', 1)
                        key = key.strip()
                        val = val.strip()
                        
                        # Convert to appropriate type
                        if val.lower() == 'true':
                            node[key] = True
                        elif val.lower() == 'false':
                            node[key] = False
                        elif val.isdigit():
                            node[key] = int(val)
                        else:
                            node[key] = val
            
            # Check if ends with colon (container node)
            is_container = content.endswith(':')
            if is_container:
                content = content[:-1].strip()
            
            # Parse role and name
            # Format: role "name" or just role or text: "content"
            
            # Handle text: "content" specially
            if content.startswith('text:'):
                text_match = re.search(r'text:\s*"?([^"]*)"?', content)
                if text_match:
                    node['role'] = 'text'
                    node['name'] = text_match.group(1)
                else:
                    node['role'] = 'text'
                    node['name'] = content[5:].strip()
            else:
                # Try to match: role "name"
                name_match = re.search(r'^(\S+)\s+"([^"]+)"$', content)
                if name_match:
                    node['role'] = name_match.group(1)
                    node['name'] = name_match.group(2)
                else:
                    # Just role, no name
                    node['role'] = content if content else 'generic'
                    node['name'] = ''
            
            # Pop stack to correct parent level
            while len(stack) > 1 and stack[-1][0] >= indent:
                stack.pop()
            
            # Add to parent
            if stack:
                parent = stack[-1][1]
                if 'children' not in parent:
                    parent['children'] = []
                parent['children'].append(node)
            
            # Push current node onto stack (it might have children)
            stack.append((indent, node))
        
        return root

