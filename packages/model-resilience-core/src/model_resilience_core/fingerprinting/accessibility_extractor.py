"""
Accessibility tree extraction utilities.

Platform-agnostic functions for extracting information from accessibility trees.
"""

import hashlib
from typing import Any


class AccessibilityExtractor:
    """
    Utilities for extracting information from accessibility trees.
    
    This class provides platform-agnostic methods for processing accessibility
    tree data structures.
    """
    
    @staticmethod
    def hash_tree_structure(tree: dict[str, Any]) -> str:
        """
        Generate a hash of the accessibility tree structure.
        
        Args:
            tree: Accessibility tree dictionary
            
        Returns:
            SHA256 hash of tree topology
        """
        structure = AccessibilityExtractor._get_tree_topology(tree)
        return hashlib.sha256(str(structure).encode()).hexdigest()[:16]
    
    @staticmethod
    def _get_tree_topology(node: dict[str, Any], depth: int = 0) -> list[Any]:
        """Recursively build tree topology."""
        if depth > 10:  # Prevent infinite recursion
            return []
        
        topology: list[Any] = [node.get("role", "")]
        
        children = node.get("children", [])
        for child in children:
            topology.append(AccessibilityExtractor._get_tree_topology(child, depth + 1))
        
        return topology
    
    @staticmethod
    def extract_landmarks(tree: dict[str, Any]) -> list[str]:
        """
        Extract ARIA landmark roles from tree.
        
        Args:
            tree: Accessibility tree dictionary
            
        Returns:
            List of landmark role names
        """
        landmarks: list[str] = []
        
        def traverse(node: dict[str, Any]) -> None:
            role = node.get("role", "")
            if role in ["banner", "navigation", "main", "contentinfo", "complementary", "search"]:
                landmarks.append(role)
            
            for child in node.get("children", []):
                traverse(child)
        
        traverse(tree)
        return landmarks
    
    @staticmethod
    def count_interactive(tree: dict[str, Any]) -> int:
        """
        Count interactive elements in tree.
        
        Args:
            tree: Accessibility tree dictionary
            
        Returns:
            Number of interactive elements
        """
        count = 0
        
        def traverse(node: dict[str, Any]) -> None:
            nonlocal count
            role = node.get("role", "")
            if role in ["button", "link", "textbox", "combobox", "checkbox", "radio", "menuitem"]:
                count += 1
            
            for child in node.get("children", []):
                traverse(child)
        
        traverse(tree)
        return count
    
    @staticmethod
    def extract_headings(tree: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract heading hierarchy from tree.
        
        Args:
            tree: Accessibility tree dictionary
            
        Returns:
            List of heading dictionaries with level and text
        """
        headings: list[dict[str, Any]] = []
        
        def traverse(node: dict[str, Any]) -> None:
            role = node.get("role", "")
            if role == "heading":
                level = node.get("level", 0)
                name = node.get("name", "")
                if name:
                    headings.append({"level": level, "text": name})
            
            for child in node.get("children", []):
                traverse(child)
        
        traverse(tree)
        return headings

