"""
State Classification Logic.

Classifies UI states based on fingerprints to generate human-readable state IDs.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class StateClassifier:
    """Classifies UI states based on fingerprint.
    
    This is application-specific logic that can be overridden for different UIs.
    """
    
    @staticmethod
    def classify_state(fingerprint: dict[str, Any]) -> tuple[str, str]:
        """Classify state and generate unique state_id.
        
        Args:
            fingerprint: State fingerprint dictionary
            
        Returns:
            Tuple of (state_type, state_id)
            
        Examples:
            - ("form", "V_LOGIN_FORM_EMPTY")
            - ("error", "V_LOGIN_FORM_ERROR")
            - ("dashboard", "V_DASHBOARD_LOADED")
        """
        url_pattern = fingerprint.get("url_pattern", "")
        title = fingerprint.get("title", "").lower()
        
        # Extract from accessibility tree
        a11y_tree = fingerprint.get("accessibility_tree", {})
        landmarks = a11y_tree.get("landmark_roles", []) if a11y_tree else []
        
        # Extract from actionable elements
        actionable = fingerprint.get("actionable_elements", {})
        buttons = actionable.get("buttons", [])
        links = actionable.get("links", [])
        
        # Check for logout button as indicator of logged-in state
        has_logout = any(
            btn.get("name", "").lower() in ["log out", "logout", "sign out"]
            for btn in buttons
        ) or any(
            link.get("name", "").lower() in ["log out", "logout", "sign out"]
            for link in links
        )
        
        # Check for login button (indicates we're on login page, not logged in)
        has_login_button = any(
            btn.get("name", "").lower() in ["login", "log in", "sign in"]
            for btn in buttons
        )
        
        # Check for form role (login forms)
        has_form = "form" in landmarks
        
        # Check for data table
        has_table = any(btn.get("role") == "table" for btn in buttons)
        
        # Priority 1: Error states
        has_actual_error = ("alert" in landmarks or 
                           "error" in url_pattern.lower() or 
                           "error" in title)
        if has_actual_error:
            # If it has form and login button, it's a login page (even with error banner)
            if has_form and has_login_button:
                # This is a login page, not an error page
                logger.debug("Login form detected with error banner, treating as login page")
                pass  # Fall through to login form handling
            elif "login" in url_pattern.lower() or "login" in title:
                return "error", "V_LOGIN_FORM_ERROR"
            else:
                state_id = f"V_ERROR_{StateClassifier._normalize_name(url_pattern)}"
                return "error", state_id
        
        # Priority 2: Modal states (dialog role)
        if "dialog" in [btn.get("role") for btn in buttons]:
            state_id = f"V_MODAL_{StateClassifier._normalize_name(url_pattern)}"
            return "modal", state_id
        
        # Priority 3: Loading states
        is_loading = any(
            btn.get("aria_states", {}).get("disabled") and "load" in btn.get("name", "").lower()
            for btn in buttons
        )
        if is_loading or "loading" in url_pattern.lower():
            state_id = f"V_LOADING_{StateClassifier._normalize_name(url_pattern)}"
            return "loading", state_id
        
        # Priority 4: Logged-in states (check BEFORE login form)
        if has_logout and "navigation" in landmarks:
            # DYNAMIC CLASSIFICATION: Use the URL pattern to define the state
            # Special case for root/dashboard
            if "overview" in url_pattern or "overview" in title:
                return "dashboard", "V_OVERVIEW_PAGE"
            
            # For everything else, derive ID from normalized URL
            state_id = f"V_{StateClassifier._normalize_name(url_pattern)}"
            
            # Determine type (heuristic)
            if "admin" in url_pattern:
                state_type = "admin"
            elif "list" in url_pattern or has_table:
                 state_type = "list"
            else:
                state_type = "page"
                
            return state_type, state_id
        
        # Priority 5: Login form states (empty/ready)
        if (has_form or "login" in url_pattern or "login" in title) and has_login_button:
            # Only classify as login form if we DON'T have logout button
            if not has_logout:
                return "form", "V_LOGIN_FORM_EMPTY"
        
        # Priority 6: Dashboard/main application states
        if "main" in landmarks and ("dashboard" in url_pattern or "dashboard" in title or "overview" in url_pattern):
            return "dashboard", "V_DASHBOARD_LOADED"
        
        if "navigation" in landmarks and has_table:
            # Likely a list/management page
            state_id = f"V_LIST_{StateClassifier._normalize_name(url_pattern)}"
            return "list", state_id
        
        # Priority 7: Success states (status role)
        if "status" in landmarks:
            state_id = f"V_SUCCESS_{StateClassifier._normalize_name(url_pattern)}"
            return "success", state_id
        
        # Default: use URL pattern
        state_type = "page"
        state_id = f"V_{StateClassifier._normalize_name(url_pattern)}"
        
        return state_type, state_id
    
    @staticmethod
    def _normalize_name(text: str) -> str:
        """Normalize text for use in state IDs.
        
        Args:
            text: Text to normalize
            
        Returns:
            Uppercase, underscored identifier
        """
        normalized = text.replace('/', '_').replace('#', '').replace('!', '')
        normalized = normalized.replace('-', '_').replace('.', '_')
        normalized = normalized.strip('_').upper()
        return normalized if normalized else "UNKNOWN"

