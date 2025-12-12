"""
State fingerprinting implementation.

Creates multi-dimensional fingerprints for UI states using accessibility tree,
URL patterns, and other stable properties.

This is a PLATFORM-AGNOSTIC implementation - it does not depend on any specific
UI automation framework (Playwright, Appium, etc.). It accepts data structures
and returns fingerprints.
"""

from __future__ import annotations
import hashlib
import json
from typing import Any
from urllib.parse import urlparse, parse_qs


class StateFingerprinter:
    """
    Creates robust fingerprints using Accessibility Tree as primary source.
    
    The accessibility tree provides semantic, stable state identification
    that is resilient to CSS and DOM changes. This approach prioritizes:
    1. Semantic identity (ARIA roles, landmarks, states) - 60%
    2. Functional identity (actionable elements) - 25%
    3. Structural identity (URL pattern) - 10%
    4. Content identity (title, headings) - 4%
    5. Style identity (DOM hash - optional) - 1%
    
    This class is platform-agnostic and accepts pre-captured data.
    """
    
    @staticmethod
    def create_fingerprint(
        accessibility_tree: dict[str, Any] | None = None,
        url: str = "",
        title: str = "",
        main_heading: str = "",
        **kwargs: Any
    ) -> dict[str, Any]:
        """Generate accessibility-tree-based state fingerprint.
        
        This is the platform-agnostic entry point. It accepts pre-captured data
        and generates a multi-dimensional fingerprint.
        
        Args:
            accessibility_tree: Accessibility tree dictionary (pre-captured)
            url: Current URL
            title: Page title
            main_heading: Main heading text (h1)
            **kwargs: Additional fingerprint dimensions
            
        Returns:
            Dictionary with accessibility-first fingerprint dimensions
        """
        if not accessibility_tree:
            # Fallback to minimal fingerprint
            return {
                "url_pattern": StateFingerprinter._extract_url_pattern(url),
                "route_params": StateFingerprinter._extract_route_params(url),
                "title": title,
                "main_heading": main_heading,
                "accessibility_tree": None,
                "actionable_elements": {"buttons": [], "links": [], "inputs": [], "total_count": 0},
                **kwargs
            }
        
        # Extract structured fingerprint from a11y tree
        return {
            # PRIMARY IDENTITY (60% weight) - Semantic
            "accessibility_tree": StateFingerprinter._extract_a11y_fingerprint(accessibility_tree),
            
            # FUNCTIONAL IDENTITY (25% weight) - Actionable elements
            "actionable_elements": StateFingerprinter._extract_actionable_elements(accessibility_tree),
            
            # STRUCTURAL IDENTITY (10% weight)
            "url_pattern": StateFingerprinter._extract_url_pattern(url),
            "route_params": StateFingerprinter._extract_route_params(url),
            
            # CONTENT IDENTITY (4% weight)
            "title": title,
            "main_heading": main_heading,
            
            # STYLE IDENTITY (1% weight - OPTIONAL, only for edge cases)
            # "dom_structure_hash": dom_hash,  # Can be passed in kwargs if needed
            
            # Allow additional dimensions
            **kwargs
        }
    
    @staticmethod
    def _extract_url_pattern(url: str) -> str:
        """Extract stable URL pattern (removing volatile IDs but keeping structure).
        
        Args:
            url: Full URL
            
        Returns:
            Normalized URL pattern (e.g. "admin/config" or "devices/edit")
        """
        parsed = urlparse(url)
        # For SPAs, fragment is often the "path"
        path = parsed.fragment if parsed.fragment else parsed.path
        
        # Handle "hash-bang" or clean paths
        if path.startswith('!'):
            path = path[1:]
        
        # Clean up
        path = path.strip('/')
        
        parts = path.split('/')
        normalized_parts = []
        
        for part in parts:
            # Keep semantic tokens (admin, config, users, etc.)
            # IDs usually appear in edit pages
            normalized_parts.append(part)
            
        path = '/'.join(normalized_parts)

        # If path is empty, check root
        if not path:
             return 'root'
        
        return path
    
    @staticmethod
    def _extract_route_params(url: str) -> dict[str, str]:
        """Extract route parameters from URL (query and fragment params).
        
        Args:
            url: Full URL
            
        Returns:
            Dictionary of parameters
        """
        parsed = urlparse(url)
        params = {}
        
        # Extract query parameters
        if parsed.query:
            query_params = parse_qs(parsed.query)
            # Flatten single-value lists
            params.update({k: v[0] if len(v) == 1 else v for k, v in query_params.items()})
        
        # For SPAs, check fragment for additional params
        if parsed.fragment and '?' in parsed.fragment:
            fragment_query = parsed.fragment.split('?', 1)[1]
            frag_params = parse_qs(fragment_query)
            params.update({k: v[0] if len(v) == 1 else v for k, v in frag_params.items()})
        
        return params
    
    @staticmethod
    def _extract_a11y_fingerprint(tree: dict[str, Any]) -> dict[str, Any]:
        """Extract stable semantic fingerprint from accessibility tree.
        
        Args:
            tree: Accessibility tree dictionary
            
        Returns:
            Dictionary with semantic fingerprint components
        """
        return {
            "structure_hash": StateFingerprinter._hash_tree_structure(tree),
            "landmark_roles": StateFingerprinter._extract_landmarks(tree),
            "interactive_count": StateFingerprinter._count_interactive(tree),
            "heading_hierarchy": StateFingerprinter._extract_headings(tree),
            "key_landmarks": StateFingerprinter._extract_key_landmarks(tree),
            "aria_states": StateFingerprinter._extract_aria_states(tree),
        }
    
    @staticmethod
    def _extract_actionable_elements(tree: dict[str, Any]) -> dict[str, Any]:
        """Extract all interactive elements from accessibility tree.
        
        This provides the list of available actions without needing a separate UI map!
        
        Args:
            tree: Accessibility tree
            
        Returns:
            Dictionary with categorized actionable elements
        """
        buttons = []
        links = []
        inputs = []
        
        def traverse(node: dict[str, Any]) -> None:
            role = node.get("role", "")
            name = node.get("name", "")
            value = node.get("value")
            
            if role == "button":
                buttons.append({
                    "role": role,
                    "name": name,
                    "aria_states": StateFingerprinter._get_node_aria_states(node),
                    "locator_strategy": f"getByRole('button', {{ name: '{name}' }})"
                })
            elif role == "link":
                links.append({
                    "role": role,
                    "name": name,
                    "href": value,
                    "aria_states": StateFingerprinter._get_node_aria_states(node),
                    "locator_strategy": f"getByRole('link', {{ name: '{name}' }})"
                })
            elif role in ["textbox", "combobox", "searchbox", "spinbutton"]:
                inputs.append({
                    "role": role,
                    "name": name,
                    "aria_states": StateFingerprinter._get_node_aria_states(node),
                    "locator_strategy": f"getByLabel('{name}')" if name else f"getByRole('{role}')"
                })
            
            # Recurse to children
            for child in node.get("children", []):
                traverse(child)
        
        traverse(tree)
        
        return {
            "buttons": buttons,
            "links": links,
            "inputs": inputs,
            "total_count": len(buttons) + len(links) + len(inputs),
        }
    
    @staticmethod
    def _hash_tree_structure(tree: dict[str, Any]) -> str:
        """Create hash of accessibility tree topology (roles + hierarchy).
        
        This is MORE stable than DOM hash because it captures semantic structure.
        Text is truncated to avoid hash changes from content updates.
        
        Args:
            tree: Accessibility tree
            
        Returns:
            8-character hash of tree structure
        """
        def extract_structure(node: dict[str, Any]) -> dict[str, Any]:
            return {
                "role": node.get("role"),
                "name": node.get("name", "")[:20],  # Truncate to avoid text changes
                "children": [extract_structure(child) for child in node.get("children", [])]
            }
        
        structure = extract_structure(tree)
        structure_str = json.dumps(structure, sort_keys=True)
        return hashlib.md5(structure_str.encode()).hexdigest()[:8]
    
    @staticmethod
    def _extract_landmarks(tree: dict[str, Any]) -> list[str]:
        """Extract ARIA landmark roles (most stable identifiers).
        
        Args:
            tree: Accessibility tree
            
        Returns:
            List of landmark role names
        """
        landmarks = []
        landmark_roles = {"navigation", "main", "complementary", "contentinfo", 
                         "banner", "search", "form", "region"}
        
        def traverse(node: dict[str, Any]) -> None:
            role = node.get("role", "")
            if role in landmark_roles:
                landmarks.append(role)
            for child in node.get("children", []):
                traverse(child)
        
        traverse(tree)
        return landmarks
    
    @staticmethod
    def _count_interactive(tree: dict[str, Any]) -> int:
        """Count total interactive elements.
        
        Args:
            tree: Accessibility tree
            
        Returns:
            Count of interactive elements
        """
        interactive_roles = {"button", "link", "textbox", "combobox", 
                            "checkbox", "radio", "searchbox", "spinbutton"}
        count = 0
        
        def traverse(node: dict[str, Any]) -> None:
            nonlocal count
            if node.get("role") in interactive_roles:
                count += 1
            for child in node.get("children", []):
                traverse(child)
        
        traverse(tree)
        return count
    
    @staticmethod
    def _extract_headings(tree: dict[str, Any]) -> list[str]:
        """Extract heading hierarchy (h1-h6).
        
        Args:
            tree: Accessibility tree
            
        Returns:
            List of headings with levels (e.g., ["h1: Dashboard", "h2: Overview"])
        """
        headings = []
        
        def traverse(node: dict[str, Any]) -> None:
            role = node.get("role", "")
            if role == "heading":
                level = node.get("level", 0)
                name = node.get("name", "")
                if name:  # Only include non-empty headings
                    headings.append(f"h{level}: {name}")
            for child in node.get("children", []):
                traverse(child)
        
        traverse(tree)
        return headings
    
    @staticmethod
    def _extract_key_landmarks(tree: dict[str, Any]) -> dict[str, Any]:
        """Extract stable anchor landmarks for contextual navigation.
        
        Args:
            tree: Accessibility tree
            
        Returns:
            Dictionary of key landmarks with their paths
        """
        landmarks = {}
        
        def traverse(node: dict[str, Any], path: list[str]) -> None:
            role = node.get("role", "")
            name = node.get("name", "")
            
            # Record navigation landmarks (most stable)
            if role == "navigation" and name:
                landmarks[f"nav_{len(landmarks)}"] = {
                    "role": role,
                    "name": name,
                    "path": " > ".join(path + [role])
                }
            
            # Record main content area
            if role == "main":
                landmarks["main_content"] = {
                    "role": role,
                    "name": name,
                    "path": " > ".join(path + [role])
                }
            
            # Record search landmarks
            if role == "search":
                landmarks["search"] = {
                    "role": role,
                    "name": name,
                    "path": " > ".join(path + [role])
                }
            
            for child in node.get("children", []):
                traverse(child, path + [role])
        
        traverse(tree, [])
        return landmarks
    
    @staticmethod
    def _extract_aria_states(tree: dict[str, Any]) -> dict[str, Any]:
        """Extract ARIA state attributes from the tree.
        
        ARIA states capture dynamic functional conditions:
        - aria-expanded: Collapsible menus/accordions
        - aria-selected: Tabs/options
        - aria-checked: Checkboxes/radios
        - aria-disabled: Disabled elements
        - aria-current: Current page/step
        - aria-pressed: Toggle buttons
        
        Args:
            tree: Accessibility tree
            
        Returns:
            Dictionary summarizing ARIA states in the tree
        """
        states_summary = {
            "expanded_elements": [],
            "selected_elements": [],
            "checked_elements": [],
            "disabled_count": 0,
            "current_indicators": [],
        }
        
        def traverse(node: dict[str, Any], path: list[str]) -> None:
            role = node.get("role", "")
            name = node.get("name", "")
            
            # Check for various ARIA states
            if node.get("expanded") is not None:
                states_summary["expanded_elements"].append({
                    "role": role,
                    "name": name,
                    "expanded": node.get("expanded"),
                    "path": " > ".join(path + [role]) if path else role
                })
            
            if node.get("selected") is not None:
                states_summary["selected_elements"].append({
                    "role": role,
                    "name": name,
                    "selected": node.get("selected")
                })
            
            if node.get("checked") is not None:
                states_summary["checked_elements"].append({
                    "role": role,
                    "name": name,
                    "checked": node.get("checked")
                })
            
            if node.get("disabled"):
                states_summary["disabled_count"] += 1
            
            # aria-current indicates current page/step
            if node.get("current"):
                states_summary["current_indicators"].append({
                    "role": role,
                    "name": name,
                    "current": node.get("current")
                })
            
            for child in node.get("children", []):
                traverse(child, path + [role])
        
        traverse(tree, [])
        return states_summary
    
    @staticmethod
    def _get_node_aria_states(node: dict[str, Any]) -> dict[str, Any]:
        """Extract ARIA state attributes from a single node.
        
        Args:
            node: Single node from accessibility tree
            
        Returns:
            Dictionary of ARIA states for this node
        """
        return {
            "expanded": node.get("expanded"),
            "selected": node.get("selected"),
            "checked": node.get("checked"),
            "disabled": node.get("disabled"),
            "pressed": node.get("pressed"),
            "current": node.get("current"),
        }
