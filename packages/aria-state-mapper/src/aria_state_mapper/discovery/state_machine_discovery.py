"""
UI State Machine Discovery.

Main discovery engine for exploring web applications and building FSM graphs.
Uses Playwright for browser automation and ModelResilienceCore for state identification.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections import deque
from pathlib import Path
from typing import Any

from playwright.async_api import (
    async_playwright,
    Page,
    Locator,
    TimeoutError as PlaywrightTimeoutError,
)

from model_resilience_core import (
    UIState,
    StateTransition,
    ActionType,
    StateComparer,
)
from aria_state_mapper.playwright_integration import PlaywrightStateFingerprinter
from aria_state_mapper.discovery.state_classifier import StateClassifier

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class UIStateMachineDiscovery:
    """Main discovery tool using FSM/MBT approach with Playwright.
    
    This tool builds a Finite State Machine representation of the UI by:
    1. Discovering verifiable states (vertices)
    2. Recording transitions between states (edges)
    3. Capturing resilient locators for each actionable element
    """
    
    def __init__(
        self,
        base_url: str,
        headless: bool = True,
        timeout: int = 10000,
        max_states: int = 100,
        safe_button_patterns: str = "New,Add,Edit,View,Show,Cancel,Close,Search,Filter,Create,Upload,Refresh,Submit,Save,Update,Confirm,OK,Yes",
        use_dfs: bool = True,
    ):
        """Initialize the state machine discovery tool.
        
        Args:
            base_url: Base URL of the application
            headless: Run browser in headless mode
            timeout: Default timeout in milliseconds
            max_states: Maximum number of states to discover (safety limit, default: 100)
            safe_button_patterns: Comma-separated button text patterns safe to click
            use_dfs: Use Depth-First Search (recommended) vs Breadth-First Search
        """
        self.base_url = base_url.rstrip('/')
        self.headless = headless
        self.timeout = timeout
        self.max_states = max_states
        self.safe_button_patterns = [p.strip().lower() for p in safe_button_patterns.split(',')]
        self.use_dfs = use_dfs
        
        self.states: dict[str, UIState] = {}
        self.transitions: list[StateTransition] = []
        self.visited_states: set[str] = set()
        self.state_queue: deque[str] = deque()  # For BFS mode
        
        # Track transition signatures to avoid duplicates
        self.transition_signatures: set[tuple[str, str, str]] = set()  # (from_state, action_type, to_state)
        
        # Store credentials for re-login if needed
        self.username: str | None = None
        self.password: str | None = None
        
        # Track seeded states for verification
        self.seeded_states: set[str] = set()
        self.seeded_state_status: dict[str, str] = {}  # state_id → "unchanged"|"modified"|"removed"|"unreachable"
        
        # Create fingerprinter and comparer instances
        self.fingerprinter = PlaywrightStateFingerprinter()
        self.comparer = StateComparer()

    def seed_from_fsm_graph(self, graph_path: str):
        """Seed the FSM with states and transitions from existing FSM graph JSON.
        
        This enables incremental discovery, allowing you to:
        1. Start from a manually captured graph and expand it automatically
        2. Refresh an existing graph as the UI evolves
        3. Build graphs iteratively over time
        
        Args:
            graph_path: Path to FSM graph JSON file
            
        Example:
            # Load manually captured graph and expand it
            tool = UIStateMachineDiscovery("http://localhost:3000")
            tool.seed_from_fsm_graph("fsm_graph_augmented.json")
            await tool.discover()  # Continues from 21 existing states
        """
        graph_path_obj = Path(graph_path)
        if not graph_path_obj.exists():
            logger.error("Graph file not found: %s", graph_path)
            return
        
        try:
            with graph_path_obj.open("r") as f:
                graph_data = json.load(f)
            
            # Validate basic structure
            if "nodes" not in graph_data or "edges" not in graph_data:
                logger.error("Invalid FSM graph format: missing 'nodes' or 'edges'")
                return
            
            # Load states from nodes
            nodes = graph_data.get("nodes", [])
            for node in nodes:
                if node.get("node_type") != "state":
                    continue
                
                # Reconstruct UIState object
                state = UIState(
                    state_id=node["id"],
                    state_type=node.get("state_type", "unknown"),
                    fingerprint=node.get("fingerprint", {}),
                    verification_logic=node.get("verification_logic", {}),
                    element_descriptors=node.get("element_descriptors", {}),
                    discovered_at=node.get("discovered_at", "")
                )
                
                # Add to states dictionary
                self.states[state.state_id] = state
                
                # Track as seeded (needs verification)
                self.seeded_states.add(state.state_id)
                
                # DON'T add to visited_states yet - will be added after verification
                # DON'T add to queue - verification phase will handle this
            
            # Load transitions from edges
            edges = graph_data.get("edges", [])
            for edge in edges:
                if edge.get("edge_type") != "transition":
                    continue
                
                # Reconstruct StateTransition object
                transition = StateTransition(
                    transition_id=edge.get("transition_id", ""),
                    from_state_id=edge.get("source", ""),
                    to_state_id=edge.get("target", ""),
                    action_type=edge.get("action_type", ActionType.NAVIGATE),
                    trigger_locators=edge.get("trigger_locators", {}),
                    action_data=edge.get("action_data", {}),
                    success_rate=edge.get("success_rate", 1.0)
                )
                
                # Add to transitions list
                self.transitions.append(transition)
                
                # Add to signature set to prevent duplicates
                signature = (
                    transition.from_state_id,
                    transition.action_type,
                    transition.to_state_id
                )
                self.transition_signatures.add(signature)
            
            logger.info("Seeded FSM from graph: %d states, %d transitions loaded from %s", 
                       len(self.states), len(self.transitions), graph_path)
            logger.info("Incremental discovery will continue from these states")
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse FSM graph JSON: %s", e)
        except Exception as e:
            logger.error("Failed to load FSM graph: %s", e)

        
    async def discover(
        self,
        username: str | None = None,
        password: str | None = None,
        discover_login_flow: bool = True,
    ) -> dict[str, Any]:
        """Main discovery flow.
        
        Args:
            username: Login username (optional)
            password: Login password (optional)
            discover_login_flow: Whether to discover login states
            
        Returns:
            Dictionary with FSM graph data
        """
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=self.headless)
            page = await browser.new_page()
            page.set_default_timeout(self.timeout)
            
            try:
                exploration_method = "DFS (Depth-First)" if self.use_dfs else "BFS (Breadth-First)"
                logger.info("Starting FSM/MBT discovery for %s using %s", 
                           self.base_url, exploration_method)
                
                # Store credentials for potential re-login
                self.username = username
                self.password = password
                
                # Navigate to base URL
                await page.goto(self.base_url)
                await page.wait_for_load_state('networkidle')
                
                # Discover initial state (likely login page)
                initial_state = await self._discover_current_state(page)
                self.states[initial_state.state_id] = initial_state
                
                logger.info("Initial state: %s (%s)", initial_state.state_id, initial_state.state_type)
                
                # If login required, perform login
                if username and password and discover_login_flow:
                    await self._discover_login_flow(page, username, password)
                
                # After login (or if no login), discover the current state
                # This is our starting point for exploration
                current_state = await self._discover_current_state(page)
                if current_state.state_id not in self.states:
                    self.states[current_state.state_id] = current_state
                
                # Start exploration from current state (post-login or initial)
                logger.info("Starting exploration from: %s (%s)", 
                           current_state.state_id, current_state.state_type)
                self.state_queue.append(current_state.state_id)
                
                # Verify seeded states first (if seed graph was loaded)
                if self.seeded_states:
                    logger.info("Verifying %d seeded states before exploration...", len(self.seeded_states))
                    await self._verify_seeded_states(page)
                
                # Choose exploration strategy
                if self.use_dfs:
                    # DFS: Explore each branch completely before moving to next
                    await self._explore_states_dfs(page)
                else:
                    # BFS: Explore level by level
                    await self._explore_states_simple_bfs(page)
                
                # Export to graph
                graph_data = self._export_to_graph()
                
                logger.info("Discovery complete: %d states, %d transitions", 
                           len(self.states), len(self.transitions))
                
                return graph_data
                
            finally:
                await browser.close()
    
    async def _discover_current_state(self, page: Page) -> UIState:
        """Discover and classify the current UI state with fuzzy matching.
        
        Uses StateComparer to find matching states before creating new ones.
        This enables resilience to CSS changes, DOM restructuring, and minor
        UI updates by recognizing "same state" based on semantic similarity.
        
        Args:
            page: Playwright Page object
            
        Returns:
            UIState object (existing match or newly created)
        """
        # Wait for state to stabilize (e.g. loading spinners to disappear)
        await self._wait_for_stable_state(page)

        # Create fingerprint using PlaywrightStateFingerprinter
        fingerprint = await self.fingerprinter.create_fingerprint(page)
        
        # Try to find matching existing state (fuzzy matching)
        existing_states = list(self.states.values())
        matched_state, similarity = self.comparer.find_matching_state(
            fingerprint,
            existing_states,
            threshold=StateComparer.MATCH_THRESHOLD  # 80% threshold
        )
        
        if matched_state:
            # Found a match! Reuse existing state
            logger.info(
                "Matched existing state: %s (%.1f%% similar)",
                matched_state.state_id, similarity * 100
            )
            
            # Update element descriptors if new fingerprint has more/different elements
            actionable = fingerprint.get("actionable_elements", {})
            new_descriptors = (
                actionable.get("buttons", []) + 
                actionable.get("links", []) + 
                actionable.get("inputs", [])
            )
            
            # Merge descriptors (keep union of old + new)
            existing_names = {d.get('name') for d in matched_state.element_descriptors}
            for desc in new_descriptors:
                if desc.get('name') not in existing_names:
                    matched_state.element_descriptors.append(desc)
                    logger.debug(
                        "Added new element to matched state: %s",
                        desc.get('name')
                    )
            
            return matched_state
        
        # No match found - create new state
        state_type, state_id = StateClassifier.classify_state(fingerprint)
        
        # Create verification logic
        verification = self._create_verification_logic(fingerprint)
        
        # Extract actionable elements for state transitions
        actionable = fingerprint.get("actionable_elements", {})
        element_descriptors = (
            actionable.get("buttons", []) + 
            actionable.get("links", []) + 
            actionable.get("inputs", [])
        )
        
        state = UIState(
            state_id=state_id,
            state_type=state_type,
            fingerprint=fingerprint,
            verification_logic=verification,
            element_descriptors=element_descriptors
        )
        
        # Log discovery with a11y info
        a11y_tree = fingerprint.get("accessibility_tree", {})
        landmarks = a11y_tree.get("landmark_roles", []) if a11y_tree else []
        logger.info(
            "Created NEW state: %s (landmarks: %s, actions: %d)", 
            state_id, landmarks, actionable.get("total_count", 0)
        )
        
        return state

    async def _wait_for_stable_state(self, page: Page, timeout: int = 2000) -> None:
        """Wait for the UI to stabilize (loading indicators to clear).

        Args:
            page: Playwright Page object
            timeout: Max time to wait for stability in ms
        """
        start_time = time.time()
        check_interval = 0.2
        
        # Already waited for networkidle in navigation, but give a small buffer for UI rendering
        await asyncio.sleep(0.2)

        while (time.time() - start_time) * 1000 < timeout:
            try:
                # Check for loading indicators
                page_state = await self.fingerprinter._get_page_state(page)
                
                if not page_state["is_loading"]:
                    # Stable!
                    return
                
                logger.debug("Waiting for state to stabilize (loading detected)...")
                await asyncio.sleep(check_interval)
            except Exception:
                # If check fails, assume stable enough or error will be caught later
                return
        
        logger.debug("State verification timed out waiting for stability, proceeding anyway")
    
    def _create_verification_logic(self, fingerprint: dict[str, Any]) -> dict[str, Any]:
        """Create assertions to verify this state.
        
        Args:
            fingerprint: State fingerprint (accessibility tree-based)
            
        Returns:
            Dictionary of verification checks
        """
        a11y_tree = fingerprint.get("accessibility_tree", {})
        
        return {
            "url_pattern": fingerprint.get("url_pattern", ""),
            "required_landmarks": a11y_tree.get("landmark_roles", []) if a11y_tree else [],
            "min_interactive_count": a11y_tree.get("interactive_count", 0) if a11y_tree else 0,
            "structure_hash": a11y_tree.get("structure_hash") if a11y_tree else None,
            "title": fingerprint.get("title", ""),
        }
    
    async def _navigate_to_state(
        self, 
        page: Page, 
        target_state_id: str,
        _visited_in_recursion: set[str] | None = None
    ) -> bool:
        """Navigate to a specific state.
        
        Strategy:
        1. Check if already in target state
        2. Find a transition that leads to target state
        3. Execute that transition
        4. Verify arrival
        
        Args:
            page: Playwright Page object
            target_state_id: State ID to navigate to
            _visited_in_recursion: Internal recursion tracking
            
        Returns:
            True if navigation successful, False otherwise
        """
        # Initialize recursion tracking
        if _visited_in_recursion is None:
            _visited_in_recursion = set()
        
        # Prevent infinite recursion
        if target_state_id in _visited_in_recursion:
            logger.warning("Circular navigation detected for %s", target_state_id)
            return False
        _visited_in_recursion.add(target_state_id)
        
        # Check if already in target state
        try:
            current_state = await self._discover_current_state(page)
            if current_state.state_id == target_state_id:
                logger.debug("Already in target state %s", target_state_id)
                return True
        except Exception as e:
            logger.error("Error checking current state: %s", e)
            return False
        
        # Find a transition to the target state
        transition_to_target = None
        for transition in self.transitions:
            if transition.to_state_id == target_state_id:
                transition_to_target = transition
                break
        
        if not transition_to_target:
            logger.warning("No known transition to state %s", target_state_id)
            return False
        
        # Check if we're in the source state of this transition
        if current_state.state_id != transition_to_target.from_state_id:
            # Need to navigate to source state first (recursive)
            logger.debug("Need to navigate to %s before going to %s", 
                        transition_to_target.from_state_id, target_state_id)
            if not await self._navigate_to_state(
                page, 
                transition_to_target.from_state_id,
                _visited_in_recursion
            ):
                return False
        
        # Execute the transition
        try:
            success = await self._execute_transition(page, transition_to_target)
            
            if success:
                logger.debug("Successfully navigated to %s", target_state_id)
                return True
            else:
                logger.warning("Failed to execute transition to %s", target_state_id)
                return False
        except Exception as e:
            logger.error("Error executing transition to %s: %s", target_state_id, e)
            return False
    
    async def _execute_transition(self, page: Page, transition: StateTransition) -> bool:
        """Execute a known transition.
        
        Args:
            page: Playwright Page object
            transition: StateTransition to execute
            
        Returns:
            True if successful, False otherwise
        """
        try:
            trigger_locators = transition.trigger_locators
            action_type = transition.action_type
            
            if action_type == "submit_login":
                # Special case: re-execute login with stored credentials
                if not self.username or not self.password:
                    logger.debug("No credentials available for login")
                    return False
                
                try:
                    # Find and fill login form
                    username_field = page.get_by_label("Username", exact=False).or_(
                        page.get_by_placeholder("Username")
                    ).or_(page.locator('input[name="username"]')).first
                    
                    password_field = page.get_by_label("Password", exact=False).or_(
                        page.get_by_placeholder("Password")  
                    ).or_(page.locator('input[type="password"]')).first
                    
                    submit_button = page.get_by_role("button", name="Login").or_(
                        page.get_by_role("button", name="Submit")
                    ).or_(page.locator('button[type="submit"]')).first
                    
                    await username_field.fill(self.username)
                    await password_field.fill(self.password)
                    await submit_button.click()
                    
                    await page.wait_for_load_state('networkidle', timeout=self.timeout)
                    
                    # Verify we reached the target state
                    new_state = await self._discover_current_state(page)
                    return new_state.state_id == transition.to_state_id
                    
                except Exception as e:
                    logger.debug("Error re-executing login: %s", e)
                    return False
            
            elif action_type == "navigate":
                # For navigation links, try URL-based navigation first (faster for SPAs)
                href = trigger_locators.get("locators", {}).get("href")
                
                if href:
                    # Direct URL navigation for SPAs
                    try:
                        target_url = href if href.startswith('http') else self.base_url + '/' + href.lstrip('/')
                        await page.goto(target_url)
                        await page.wait_for_load_state('networkidle', timeout=3000)
                        
                        # Verify we reached the target state
                        new_state = await self._discover_current_state(page)
                        if new_state.state_id == transition.to_state_id:
                            return True
                    except Exception as e:
                        logger.debug("URL navigation failed: %s, trying click", e)
                
                # Fallback: locate and click the trigger element
                element = await self._locate_element_from_descriptor(page, trigger_locators)
                
                if not element:
                    logger.debug("Could not locate trigger element for transition")
                    return False
                
                await element.click()
                
                # Wait for navigation
                try:
                    await page.wait_for_load_state('networkidle', timeout=3000)
                except PlaywrightTimeoutError:
                    await asyncio.sleep(0.5)
                
                # Verify we reached the target state
                new_state = await self._discover_current_state(page)
                return new_state.state_id == transition.to_state_id
            
            elif action_type == "click":
                # Locate and click the trigger element
                element = await self._locate_element_from_descriptor(page, trigger_locators)
                
                if not element:
                    logger.debug("Could not locate trigger element for transition")
                    return False
                
                await element.click()
                
                # Wait for potential state change
                try:
                    await page.wait_for_load_state('networkidle', timeout=3000)
                except PlaywrightTimeoutError:
                    await asyncio.sleep(0.5)
                
                # Verify we reached the target state
                new_state = await self._discover_current_state(page)
                return new_state.state_id == transition.to_state_id
            
            else:
                logger.warning("Unknown action type: %s", action_type)
                return False
                
        except Exception as e:
            logger.debug("Error executing transition: %s", e)
            return False
    
    async def _discover_login_flow(self, page: Page, username: str, password: str) -> None:
        """Discover login flow states and transitions WITH intermediate states.
        
        This method captures the COMPLETE login cycle with all intermediate states:
        1. Empty login form state (V_LOGIN_FORM_EMPTY)
        2. Username filled state (V_LOGIN_FORM_USERNAME_FILLED)
        3. Both credentials filled state (V_LOGIN_FORM_READY)
        4. Post-submit result state (V_OVERVIEW_PAGE or V_LOGIN_FORM_ERROR)
        
        This granular approach aligns with FSM/MBT philosophy of capturing
        all verifiable states in the user journey.
        
        Args:
            page: Playwright Page object
            username: Username to use
            password: Password to use
        """
        logger.info("Discovering granular login flow with intermediate states...")
        
        try:
            # Find login elements using resilient locators
            username_field = page.get_by_label("Username", exact=False).or_(
                page.get_by_placeholder("Username")
            ).or_(page.locator('input[name="username"]')).first
            
            password_field = page.get_by_label("Password", exact=False).or_(
                page.get_by_placeholder("Password")  
            ).or_(page.locator('input[type="password"]')).first
            
            submit_button = page.get_by_role("button", name="Login").or_(
                page.get_by_role("button", name="Submit")
            ).or_(page.locator('button[type="submit"]')).first
            
            # Capture element descriptors for transitions
            username_field_desc = await self._get_element_descriptor(username_field)
            password_field_desc = await self._get_element_descriptor(password_field)
            submit_button_desc = await self._get_element_descriptor(submit_button)
            
            # STATE 1: Empty/Initial login form
            state1_empty = await self._discover_current_state(page)
            if state1_empty.state_id not in self.states:
                self.states[state1_empty.state_id] = state1_empty
            logger.info("State 1 - Empty form: %s", state1_empty.state_id)
            
            # TRANSITION 1: Fill username field
            await username_field.fill(username)
            await asyncio.sleep(0.3)  # Let UI update
            
            # STATE 2: Username filled, password empty
            state2_username = await self._discover_current_state(page)
            if state2_username.state_id not in self.states:
                self.states[state2_username.state_id] = state2_username
            
            # Record transition 1
            if state2_username.state_id != state1_empty.state_id:
                transition1 = StateTransition(
                    transition_id=f"T_{state1_empty.state_id}_TO_{state2_username.state_id}_FILL_USERNAME",
                    from_state_id=state1_empty.state_id,
                    to_state_id=state2_username.state_id,
                    action_type="fill",
                    trigger_locators=username_field_desc,
                    action_data={"field": "username", "value": "***"}
                )
                self.transitions.append(transition1)
                logger.info("Transition 1: %s -> %s (username filled)", 
                           state1_empty.state_id, state2_username.state_id)
            else:
                logger.debug("Username fill didn't change state, continuing...")
                state2_username = state1_empty  # Use same state
            
            # TRANSITION 2: Fill password field
            await password_field.fill(password)
            await asyncio.sleep(0.3)  # Let UI update
            
            # STATE 3: Both username and password filled (ready to submit)
            state3_ready = await self._discover_current_state(page)
            if state3_ready.state_id not in self.states:
                self.states[state3_ready.state_id] = state3_ready
            
            # Record transition 2
            if state3_ready.state_id != state2_username.state_id:
                transition2 = StateTransition(
                    transition_id=f"T_{state2_username.state_id}_TO_{state3_ready.state_id}_FILL_PASSWORD",
                    from_state_id=state2_username.state_id,
                    to_state_id=state3_ready.state_id,
                    action_type="fill",
                    trigger_locators=password_field_desc,
                    action_data={"field": "password", "value": "***"}
                )
                self.transitions.append(transition2)
                logger.info("Transition 2: %s -> %s (password filled)", 
                           state2_username.state_id, state3_ready.state_id)
            else:
                logger.debug("Password fill didn't change state, continuing...")
                state3_ready = state2_username  # Use same state
            
            # TRANSITION 3: Click submit button
            await submit_button.click()
            
            # Wait for navigation/state change
            try:
                await page.wait_for_load_state('networkidle', timeout=self.timeout)
            except PlaywrightTimeoutError:
                logger.warning("Networkidle timeout after login, continuing...")
                await asyncio.sleep(1)
            
            # Additional wait for SPA to update
            await asyncio.sleep(0.5)
            
            # Log current URL for debugging
            current_url = page.url
            logger.debug("After login submit, current URL: %s", current_url)
            
            # STATE 4: After login (success -> overview, or failure -> error)
            state4_result = await self._discover_current_state(page)
            if state4_result.state_id not in self.states:
                self.states[state4_result.state_id] = state4_result
            
            # Record transition 3
            transition3 = StateTransition(
                transition_id=f"T_{state3_ready.state_id}_TO_{state4_result.state_id}_SUBMIT",
                from_state_id=state3_ready.state_id,
                to_state_id=state4_result.state_id,
                action_type="submit",
                trigger_locators=submit_button_desc,
                action_data={"requires_credentials": True}
            )
            self.transitions.append(transition3)
            
            logger.info("Transition 3: %s -> %s (login submitted)", 
                       state3_ready.state_id, state4_result.state_id)
            logger.info("Login flow complete: 4 states, 3 transitions discovered")
            
        except Exception as e:
            logger.error("Error discovering granular login flow: %s", e)
            raise
    
    async def _get_element_descriptor(self, locator: Locator) -> dict[str, Any]:
        """Extract resilient locator strategies for element.
        
        Args:
            locator: Playwright Locator object
            
        Returns:
            Element descriptor with multiple locator strategies
        """
        try:
            # Get element type
            tag_name = await locator.evaluate("el => el.tagName.toLowerCase()")
            elem_type = "button" if tag_name == "button" else "input" if tag_name == "input" else "link"
            
            descriptor = await self.fingerprinter._create_element_descriptor(locator, elem_type)
            return descriptor if descriptor else {}
        except Exception as e:
            logger.debug("Error getting element descriptor: %s", e)
            return {}
    
    def _detect_conditional_transition(self, new_transition: StateTransition) -> None:
        """
        Detect if a new transition creates a conditional scenario.
        
        A conditional transition occurs when the same trigger (locator/button) from
        the same source state can lead to different target states. This typically
        happens when the outcome depends on system conditions (e.g., CPE online/offline).
        
        Args:
            new_transition: The newly discovered transition to check
        """
        # Find existing transitions with same source and similar trigger
        from_state = new_transition.from_state_id
        new_trigger_str = str(new_transition.trigger_locators.get("locator_strategy", ""))
        
        for existing in self.transitions:
            if existing.from_state_id != from_state:
                continue
            
            # Check if triggers are similar
            existing_trigger_str = str(existing.trigger_locators.get("locator_strategy", ""))
            
            # Simple heuristic: same button/link name
            if new_trigger_str and existing_trigger_str and new_trigger_str == existing_trigger_str:
                # Same trigger, different target → conditional!
                if existing.to_state_id != new_transition.to_state_id:
                    logger.warning(
                        "Conditional transition detected: %s → [%s OR %s] (same trigger)",
                        from_state,
                        existing.to_state_id,
                        new_transition.to_state_id
                    )
                    logger.info(
                        "  This transition depends on system conditions outside UI control."
                    )
                    logger.info(
                        "  Consider adding guard conditions to document the requirements."
                    )
                    
                    # Mark both transitions as conditional if not already marked
                    if not existing.is_conditional:
                        if "metadata" not in existing.metadata:
                            existing.metadata["note"] = "Conditional transition detected during discovery"
                    
                    if "metadata" not in new_transition.metadata:
                        new_transition.metadata = {}
                    new_transition.metadata["note"] = "Conditional transition detected during discovery"
                    
                    break
    
    async def _verify_seeded_states(self, page: Page):
        """Verify all seeded states by navigating to them and comparing fingerprints.
        
        This is critical for manual recording: manually captured states (dropdowns,
        overlays, forms) must be verified against the live UI to ensure they still
        exist and haven't changed.
        
        Args:
            page: Playwright Page object
        """
        logger.info("=" * 70)
        logger.info("SEED VERIFICATION PHASE")
        logger.info("=" * 70)
        logger.info("Verifying %d seeded states...", len(self.seeded_states))
        
        verified_count = 0
        unchanged_count = 0
        modified_count = 0
        removed_count = 0
        unreachable_count = 0
        
        for state_id in self.seeded_states:
            state = self.states[state_id]
            logger.info("Verifying state: %s (%s)", state_id, state.state_type)
            
            # Try to navigate to this state using URL pattern
            try:
                url_pattern = state.fingerprint.get("url_pattern", "")
                if url_pattern and url_pattern != "root":
                    # Try direct URL navigation
                    target_url = f"{self.base_url}/#{url_pattern}"
                    logger.debug("  Navigating to: %s", target_url)
                    await page.goto(target_url, wait_until='networkidle', timeout=5000)
                    await self._wait_for_stable_state(page)
                elif url_pattern == "root":
                    # Navigate to base URL
                    await page.goto(self.base_url, wait_until='networkidle', timeout=5000)
                    await self._wait_for_stable_state(page)
                else:
                    # No URL pattern - try to find transition to this state
                    logger.debug("  No URL pattern, checking transitions...")
                    incoming_transitions = [t for t in self.transitions if t.to_state_id == state_id]
                    if not incoming_transitions:
                        logger.warning("  ⚠️  No way to reach %s - marking as unreachable", state_id)
                        self.seeded_state_status[state_id] = "unreachable"
                        unreachable_count += 1
                        # Keep in states but don't mark as visited
                        continue
                
                # Read current UI state
                current_fingerprint = await self.fingerprinter.create_fingerprint(page)
                
                # Compare with seeded fingerprint
                seed_fingerprint = state.fingerprint
                similarity = self.comparer.calculate_similarity(
                    current_fingerprint,
                    seed_fingerprint
                )
                
                # Determine status based on similarity
                if similarity >= 0.95:
                    # Unchanged - very high similarity
                    self.seeded_state_status[state_id] = "unchanged"
                    logger.info("  ✓ UNCHANGED: %s (%.1f%% similar)", state_id, similarity * 100)
                    unchanged_count += 1
                    verified_count += 1
                    # Mark as visited
                    self.visited_states.add(state_id)
                    
                elif similarity >= 0.75:
                    # Modified - structure changed but still recognizable
                    self.seeded_state_status[state_id] = "modified"
                    logger.warning("  ⚠️  MODIFIED: %s (%.1f%% similar) - Updating fingerprint", 
                                 state_id, similarity * 100)
                    modified_count += 1
                    verified_count += 1
                    
                    # Update fingerprint with current UI
                    state.fingerprint = current_fingerprint
                    
                    # Update element descriptors
                    actionable = current_fingerprint.get("actionable_elements", {})
                    state.element_descriptors = (
                        actionable.get("buttons", []) + 
                        actionable.get("links", []) + 
                        actionable.get("inputs", [])
                    )
                    
                    # Mark as visited
                    self.visited_states.add(state_id)
                    
                else:
                    # Removed - similarity too low, state no longer exists
                    self.seeded_state_status[state_id] = "removed"
                    logger.error("  ✗ REMOVED: %s (%.1f%% similar) - State no longer exists or drastically changed", 
                               state_id, similarity * 100)
                    removed_count += 1
                    # Don't mark as visited - will be excluded from exploration
                    
            except Exception as e:
                logger.error("  ✗ ERROR verifying %s: %s", state_id, str(e))
                self.seeded_state_status[state_id] = "unreachable"
                unreachable_count += 1
        
        # Summary
        logger.info("=" * 70)
        logger.info("SEED VERIFICATION SUMMARY")
        logger.info("=" * 70)
        logger.info("Total seeded states: %d", len(self.seeded_states))
        logger.info("  ✓ Unchanged: %d", unchanged_count)
        logger.info("  ⚠️  Modified: %d (fingerprints updated)", modified_count)
        logger.info("  ✗ Removed: %d (marked for review)", removed_count)
        logger.info("  ⚠️  Unreachable: %d (no navigation path)", unreachable_count)
        logger.info("  Total verified: %d", verified_count)
        logger.info("=" * 70)
        
        if removed_count > 0 or unreachable_count > 0:
            logger.warning("Some seeded states could not be verified. Review the output for details.")
    
    async def _explore_states_dfs(self, page: Page):
        """Depth-First Search exploration - explore deeply before broadly.
        
        This is much more natural for UI exploration:
        1. Click a link
        2. Immediately explore that new state (recursive)
        3. When done, come back and try the next link
        4. This way we're always on the page we want to explore!
        
        Args:
            page: Playwright Page object
        """
        logger.info("Starting DFS (depth-first) state exploration...")
        
        # Track which states we've explored
        explored_states: set[str] = set()
        
        async def explore_state_recursive(state_id: str, depth: int = 0):
            """Recursively explore a state and all states reachable from it."""
            # Check limits
            if depth > 10:  # Prevent too deep recursion
                logger.warning("Max depth reached at %s", state_id)
                return
            
            if len(explored_states) >= self.max_states:
                logger.warning("Max states limit reached")
                return
            
            if state_id in explored_states:
                return
            
            # Get the state
            state = self.states.get(state_id)
            if not state:
                logger.warning("State %s not found in states dict", state_id)
                return
            
            # Skip ephemeral/non-explorable states (error, form, loading)
            if state.state_type in ["error", "form", "loading"]:
                logger.info("Skipping exploration of ephemeral %s state: %s",
                           state.state_type, state_id)
                explored_states.add(state_id)
                return
            
            indent = "  " * depth
            logger.info("%sExploring state [depth %d]: %s (%d/%d)",
                       indent, depth, state_id, len(explored_states), self.max_states)
            
            # Mark as explored
            explored_states.add(state_id)
            
            # Verify we're in this state (or can navigate to it)
            try:
                actual_state = await self._discover_current_state(page)
                
                if actual_state.state_id != state_id:
                    logger.debug("%sNot in expected state %s, currently in %s",
                                indent, state_id, actual_state.state_id)
                    
                    # Try to navigate
                    target_pattern = state.fingerprint.get("url_pattern", "")
                    if target_pattern and target_pattern != "root":
                        target_url = f"{self.base_url}/#{target_pattern}"
                        logger.debug("%sNavigating to %s", indent, target_url)
                        await page.goto(target_url)
                        await page.wait_for_load_state('networkidle', timeout=3000)
                        
                        # Verify again
                        actual_state = await self._discover_current_state(page)
                        if actual_state.state_id != state_id:
                            logger.warning("%sCan't navigate to %s, skipping", indent, state_id)
                            return
            
            except Exception as e:
                logger.error("%sError navigating to state: %s", indent, e)
                return
            
            # Discover transitions from this state
            try:
                # Find all safe links, buttons, and forms
                forms = await self._identify_forms(page)
                safe_links = await self._find_safe_links(page)
                safe_buttons = await self._find_safe_buttons(page)
                
                logger.info("%sFound %d forms, %d links, %d buttons to explore",
                           indent, len(forms), len(safe_links[:10]), len(safe_buttons[:5]))

                # Explore forms depth-first (Priority)
                for form_info in forms:
                    try:
                        logger.debug("%sExecuting form fill", indent)
                        new_state_id = await self._execute_form_fill(page, state, form_info, navigate_back=False)
                        
                        if new_state_id and new_state_id != state_id:
                            # Recursively explore!
                            await explore_state_recursive(new_state_id, depth + 1)
                            
                            # Navigate back using browser back (preserves SPA state better than goto)
                            logger.debug("%sReturning to %s after form fill in %s",
                                       indent, state_id, new_state_id)
                            try:
                                await page.go_back()
                                await page.wait_for_load_state('networkidle', timeout=3000)
                                await asyncio.sleep(0.5)  # Extra wait for SPA to stabilize
                            except Exception as e:
                                logger.debug("%sError navigating back: %s, trying goto as fallback", indent, e)
                                # Fallback to goto if back fails
                                target_pattern = state.fingerprint.get("url_pattern", "")
                                if target_pattern and target_pattern != "root":
                                    await page.goto(f"{self.base_url}/#{target_pattern}")
                                    await page.wait_for_load_state('networkidle', timeout=3000)
                    
                    except Exception as e:
                        logger.debug("%sError with form: %s", indent, e)
                
                # Explore each link depth-first
                for link_info in safe_links[:10]:
                    try:
                        link_text = link_info.get("locators", {}).get("text", "unknown")
                        logger.debug("%sClicking link: %s", indent, link_text)
                        
                        # Click and discover new state (DON'T navigate back)
                        new_state_id = await self._execute_link_click(page, state, link_info, navigate_back=False)
                        
                        if new_state_id and new_state_id != state_id:
                            # Recursively explore the new state immediately!
                            await explore_state_recursive(new_state_id, depth + 1)
                            
                            # After exploring the new state, navigate back using browser back
                            logger.debug("%sReturning to %s after exploring %s",
                                       indent, state_id, new_state_id)
                            try:
                                await page.go_back()
                                await page.wait_for_load_state('networkidle', timeout=3000)
                                await asyncio.sleep(0.5)  # Extra wait for SPA to stabilize
                            except Exception as e:
                                logger.debug("%sError navigating back: %s, trying goto as fallback", indent, e)
                                # Fallback to goto if back fails
                                target_pattern = state.fingerprint.get("url_pattern", "")
                                if target_pattern and target_pattern != "root":
                                    await page.goto(f"{self.base_url}/#{target_pattern}")
                                    await page.wait_for_load_state('networkidle', timeout=3000)
                    
                    except Exception as e:
                        logger.debug("%sError with link: %s", indent, e)
                
                # Explore buttons depth-first
                for button_info in safe_buttons[:5]:
                    try:
                        button_text = button_info.get("locators", {}).get("text", "unknown")
                        logger.debug("%sClicking button: %s", indent, button_text)
                        
                        new_state_id = await self._execute_button_click(page, state, button_info, navigate_back=False)
                        
                        if new_state_id and new_state_id != state_id:
                            # Recursively explore!
                            await explore_state_recursive(new_state_id, depth + 1)
                            
                            # Navigate back using browser back (preserves SPA state)
                            logger.debug("%sReturning to %s after exploring %s",
                                       indent, state_id, new_state_id)
                            try:
                                await page.go_back()
                                await page.wait_for_load_state('networkidle', timeout=3000)
                                await asyncio.sleep(0.5)  # Extra wait for SPA to stabilize
                            except Exception as e:
                                logger.debug("%sError navigating back: %s, trying goto as fallback", indent, e)
                                # Fallback to goto if back fails
                                target_pattern = state.fingerprint.get("url_pattern", "")
                                if target_pattern and target_pattern != "root":
                                    await page.goto(f"{self.base_url}/#{target_pattern}")
                                    await page.wait_for_load_state('networkidle', timeout=3000)
                    
                    except Exception as e:
                        logger.debug("%sError with button: %s", indent, e)
            
            except Exception as e:
                logger.error("%sError discovering transitions: %s", indent, e)
        
        # Start DFS from the initial state in the queue
        if self.state_queue:
            initial_state_id = self.state_queue.popleft()
            await explore_state_recursive(initial_state_id, depth=0)
        
        logger.info("DFS exploration complete: %d states explored", len(explored_states))
        self.visited_states = explored_states
    
    async def _explore_states_simple_bfs(self, page: Page):
        """Simple BFS exploration without complex state navigation.
        
        Like the original ui_discovery.py, we:
        1. Start from current page (post-login)
        2. Discover elements and links on current page
        3. Click links to discover new states
        4. Don't navigate back - just explore forward
        
        Args:
            page: Playwright Page object
        """
        logger.info("Starting simple BFS state exploration...")
        
        # Track which states we've explored (not just visited)
        explored_states: set[str] = set()
        
        while self.state_queue and len(explored_states) < self.max_states:
            current_state_id = self.state_queue.popleft()
            
            if current_state_id in explored_states:
                continue
            
            # Skip ephemeral/non-explorable states
            current_state = self.states.get(current_state_id)
            if current_state and current_state.state_type in ["error", "form", "loading"]:
                logger.info("Skipping exploration of ephemeral %s state: %s",
                           current_state.state_type, current_state_id)
                explored_states.add(current_state_id)
                continue
            
            logger.info("Exploring state: %s (%d/%d)",
                       current_state_id, len(explored_states), self.max_states)
            
            # We're already in SOME state, verify which one
            try:
                actual_state = await self._discover_current_state(page)
                
                # If we're not in the expected state, navigate by URL if possible
                if actual_state.state_id != current_state_id:
                    logger.debug("Not in expected state %s, currently in %s",
                                current_state_id, actual_state.state_id)
                    
                    # Try to get the URL pattern and navigate directly
                    target_pattern = current_state.fingerprint.get("url_pattern", "")
                    if target_pattern and target_pattern != "root":
                        target_url = f"{self.base_url}/#{target_pattern}"
                        logger.debug("Navigating directly to %s", target_url)
                        await page.goto(target_url)
                        await page.wait_for_load_state('networkidle', timeout=3000)
                        
                        # Verify again
                        actual_state = await self._discover_current_state(page)
                        if actual_state.state_id != current_state_id:
                            # Can't navigate to target state
                            if actual_state.state_id in explored_states:
                                logger.warning("Can't navigate to %s, and current state %s already explored. Skipping.",
                                             current_state_id, actual_state.state_id)
                                explored_states.add(current_state_id)
                                continue
                            else:
                                logger.warning("Can't navigate to %s, will explore current state %s instead",
                                             current_state_id, actual_state.state_id)
                                # Switch to exploring the actual state
                                current_state_id = actual_state.state_id
                                current_state = actual_state
                                if current_state_id not in self.states:
                                    self.states[current_state_id] = actual_state
            
            except Exception as e:
                logger.error("Error verifying/navigating to state: %s", e)
                explored_states.add(current_state_id)
                continue
            
            # Mark as explored
            explored_states.add(current_state_id)
            
            # Discover transitions from this state (will click links and discover new states)
            try:
                new_states = await self._discover_transitions_from_state(page, current_state)
                
                logger.info("Found %d new states from %s", len(new_states), current_state_id)
                
                # Add new states to queue (if not already explored or queued)
                queue_list = list(self.state_queue)
                added_count = 0
                for new_state_id in new_states:
                    if new_state_id not in explored_states and new_state_id not in queue_list:
                        self.state_queue.append(new_state_id)
                        queue_list.append(new_state_id)  # Update our copy too
                        added_count += 1
                        logger.info("Added %s to exploration queue (queue size: %d)", 
                                   new_state_id, len(self.state_queue))
                    else:
                        logger.debug("Skipping %s (already explored or in queue)", new_state_id)
                
                logger.info("Added %d states to queue, queue now has %d states", 
                           added_count, len(self.state_queue))
            
            except Exception as e:
                logger.error("Error discovering transitions: %s", e)
        
        logger.info("Exploration complete: %d states explored", len(explored_states))
        self.visited_states = explored_states
    
    async def _discover_transitions_from_state(
        self, 
        page: Page, 
        state: UIState
    ) -> list[str]:
        """Discover possible transitions from a given state.
        
        Args:
            page: Playwright Page object
            state: Current UIState
            
        Returns:
            List of new state IDs discovered (that haven't been explored yet)
        """
        new_states = []
        
        # Strategy 1: Fill and submit forms (High Priority)
        forms = await self._identify_forms(page)
        logger.debug("Found %d forms to try", len(forms))
        
        for form_info in forms:
            try:
                # Execute form fill
                # For BFS, we always navigate back to source to continue discovery
                new_state_id = await self._execute_form_fill(page, state, form_info, navigate_back=True)
                if new_state_id and new_state_id != state.state_id:
                    new_states.append(new_state_id)
            except Exception as e:
                logger.debug("Error executing form fill: %s", e)

        # Strategy 2: Click safe navigation links (most common transition)
        safe_links = await self._find_safe_links(page)
        logger.debug("Found %d safe navigation links to try", len(safe_links))
        
        for i, link_info in enumerate(safe_links[:10]):  # Try up to 10 links
            try:
                # Don't navigate back on the last link - stay there to explore it next
                is_last = (i == len(safe_links[:10]) - 1) and len(safe_links[:10]) > 0
                new_state_id = await self._execute_link_click(page, state, link_info, navigate_back=not is_last)
                if new_state_id and new_state_id != state.state_id:
                    new_states.append(new_state_id)
                    logger.debug("Link click produced state: %s", new_state_id)
            except Exception as e:
                logger.debug("Error executing link click: %s", e)
        
        # Strategy 3: Click safe buttons
        safe_buttons = await self._find_safe_buttons(page)
        logger.debug("Found %d safe buttons to try", len(safe_buttons))
        
        for i, button_info in enumerate(safe_buttons[:5]):  # Limit to first 5 buttons
            try:
                # Don't navigate back on the last button - stay there to explore it next
                is_last = (i == len(safe_buttons[:5]) - 1) and len(safe_buttons[:5]) > 0
                new_state_id = await self._execute_button_click(page, state, button_info, navigate_back=not is_last)
                if new_state_id and new_state_id != state.state_id:
                    new_states.append(new_state_id)
                    logger.debug("Button click produced state: %s", new_state_id)
            except Exception as e:
                logger.debug("Error executing button click: %s", e)
        
        return new_states
    
    async def _find_safe_links(self, page: Page) -> list[dict[str, Any]]:
        """Find navigation links that are safe to click.
        
        Args:
            page: Playwright Page object
            
        Returns:
            List of safe link descriptors
        """
        safe_links = []
        seen_hashes = set()  # To avoid duplicates
        
        # Safe navigation patterns (menu items, not data links)
        safe_nav_patterns = [
            "overview", "dashboard", "devices", "faults", "admin",
            "config", "presets", "provisions", "files", "tasks",
            "users", "permissions", "virtualparameters"
        ]
        
        try:
            # 1. Standard Navigation Links
            nav_locators = [
                page.locator('nav a'),
                page.locator('[role="navigation"] a'),
                page.locator('.wrapper .sidebar a'),
                page.locator('header a')
            ]

            # 2. Tab Links
            tab_locators = [
                page.locator('.tabs a'),
                page.locator('ul.tabs a'),
                page.locator('[role="tablist"] a'),
                page.locator('[role="tab"]')
            ]
            
            all_locators = nav_locators + tab_locators
            
            # Iterate through all locator strategies
            candidates = []
            for loc in all_locators:
                try:
                    count = await loc.count()
                    logger.debug("Locator found %d candidates", count)
                    for i in range(count):
                        candidates.append(loc.nth(i))
                except Exception as e:
                    logger.debug("Error counting locator: %s", e)
                    continue
            
            logger.debug("Total candidates found: %d", len(candidates))
            
            # Process candidates (limit to unique ones)
            for link in candidates:
                try:
                    # Deduplication check
                    if len(safe_links) >= 30:
                        break

                    text = await link.text_content()
                    text_lower = text.strip().lower() if text else ""
                    href = await link.get_attribute('href')
                    
                    logger.debug("Checking link: text='%s', href='%s'", text_lower, href)
                    
                    # Dedupe based on href + text
                    link_hash = f"{href}|{text_lower}"
                    if link_hash in seen_hashes:
                        logger.debug("Skipping duplicate")
                        continue
                    seen_hashes.add(link_hash)

                    # Skip external links
                    if href and href.startswith('http') and self.base_url not in href:
                         logger.debug("Skipping external link")
                         continue
                    
                    # Check if matches safe navigation patterns
                    is_known_safe_term = any(pattern in text_lower or (href and pattern in href.lower()) 
                                 for pattern in safe_nav_patterns)
                    
                    # Heuristic: If it's in a tab/nav container and DOESN'T look like "delete" or "remove"
                    is_likely_safe_nav = True
                    unsafe_terms = ["delete", "remove", "destroy", "drop"]
                    if any(term in text_lower for term in unsafe_terms):
                        is_likely_safe_nav = False
                        
                    if is_known_safe_term or is_likely_safe_nav:
                        logger.debug("Link accepted as safe")
                        descriptor = await self._get_element_descriptor(link)
                        if descriptor:
                            safe_links.append(descriptor)
                    else:
                        logger.debug("Link rejected as unsafe")
                
                except Exception as e:
                    logger.debug("Error processing link candidate: %s", e)
                    continue
        
        except Exception as e:
            logger.debug("Error finding safe links: %s", e)
        
        return safe_links
    
    async def _find_safe_buttons(self, page: Page) -> list[dict[str, Any]]:
        """Find buttons that are safe to click.
        
        Args:
            page: Playwright Page object
            
        Returns:
            List of safe button descriptors
        """
        safe_buttons = []
        
        try:
            # Include role="button" elements
            all_buttons = await page.locator('button:visible, [role="button"]:visible').all()
            
            for button in all_buttons[:20]:  # Limit scan
                try:
                    text = await button.text_content()
                    text_lower = text.strip().lower() if text else ""
                    
                    # Check if matches safe patterns
                    is_safe = any(pattern in text_lower for pattern in self.safe_button_patterns)
                    
                    if is_safe:
                        descriptor = await self._get_element_descriptor(button)
                        if descriptor:
                            safe_buttons.append(descriptor)
                
                except Exception:
                    continue
        
        except Exception as e:
            logger.debug("Error finding safe buttons: %s", e)
        
        return safe_buttons
    
    async def _identify_forms(self, page: Page) -> list[dict[str, Any]]:
        """Identify forms that can be filled and submitted.
        
        This looks for logical groupings of inputs and submit buttons,
        supporting the Compound Action model.
        
        Args:
            page: Playwright Page object
            
        Returns:
            List of form descriptors
        """
        forms = []
        try:
            # 1. Standard <form> elements
            form_elements = await page.locator("form:visible").all()
            
            for form in form_elements:
                try:
                    # Check if it has actionable elements
                    inputs = await form.locator("input:not([type='hidden']), select, textarea").all()
                    buttons = await form.locator("button, input[type='submit']").all()
                    
                    if not inputs and not buttons:
                        continue
                        
                    # Create descriptor
                    descriptor = {
                        "type": "standard_form",
                        "locator": await self._get_unique_selector(form),
                        "inputs": [await self._get_element_descriptor(i) for i in inputs],
                        "buttons": [await self._get_element_descriptor(b) for b in buttons if await b.is_visible()]
                    }
                    forms.append(descriptor)
                    
                except Exception as e:
                    logger.debug("Error processing form element: %s", e)
                    continue

        except Exception as e:
            logger.debug("Error identifying forms: %s", e)
            
        return forms

    async def _execute_form_fill(
        self,
        page: Page,
        from_state: UIState,
        form_info: dict[str, Any],
        navigate_back: bool = True
    ) -> str | None:
        """Execute a form fill compound action.
        
        Args:
            page: Playwright Page object
            from_state: State before action
            form_info: Form descriptor
            navigate_back: whether to return to source state
            
        Returns:
            New state ID or None
        """
        initial_url = page.url
        try:
            # Simple strategy: Fill text inputs with "test", check checkboxes
            inputs = form_info.get("inputs", [])
            submit_buttons = form_info.get("buttons", [])
            
            if not submit_buttons:
                logger.debug("No submit button found for form")
                return None
                
            # Use the first button as submit
            submit_btn_desc = submit_buttons[0]
            
            # Fill inputs
            filled_data = {}
            for inp in inputs:
                loc_dict = inp.get("locators", {})
                element_type = inp.get("element_type", "input")
                
                # Locate element
                try:
                    loc = await self._locate_element_from_descriptor(page, inp)
                    if not loc: continue
                    
                    if element_type == "input":
                        input_type = loc_dict.get("input_type", "text")
                        name = loc_dict.get("name", "unknown")
                        
                        if input_type in ["text", "email", "password", "search"]:
                            val = "test_value"
                            if input_type == "email": val = "test@example.com"
                            if input_type == "password": val = "password123"
                            
                            await loc.fill(val)
                            filled_data[name] = val
                            
                except Exception as e:
                    logger.debug("Error filling input: %s", e)

            # Submit
            loc_btn = await self._locate_element_from_descriptor(page, submit_btn_desc)
            if loc_btn:
                await loc_btn.click()
                
                # Wait for potential navigation
                try:
                    await page.wait_for_load_state('networkidle', timeout=3000)
                except PlaywrightTimeoutError:
                    await asyncio.sleep(1.0)
                
                # Discover new state
                new_state = await self._discover_current_state(page)
                
                # If changed state, record transition
                if new_state.state_id != from_state.state_id:
                     if new_state.state_id not in self.states:
                        self.states[new_state.state_id] = new_state
                     
                     # Check if this transition already exists (avoid duplicates)
                     transition_sig = (from_state.state_id, "fill_form", new_state.state_id)
                     if transition_sig not in self.transition_signatures:
                         transition = StateTransition(
                            transition_id=f"T_{from_state.state_id}_TO_{new_state.state_id}_FORM",
                            from_state_id=from_state.state_id,
                            to_state_id=new_state.state_id,
                            action_type=ActionType.FILL_FORM,
                            trigger_locators=submit_btn_desc,
                            action_data=filled_data
                         )
                         self.transitions.append(transition)
                         self.transition_signatures.add(transition_sig)
                         logger.info("Form transition: %s -> %s", from_state.state_id, new_state.state_id)
                     else:
                         logger.debug("Form transition %s -> %s already recorded, skipping duplicate",
                                    from_state.state_id, new_state.state_id)
                     
                     # Navigate back
                     if navigate_back and page.url != initial_url:
                        try:
                            # Use browser back to preserve SPA state
                            await page.go_back()
                            await page.wait_for_load_state('networkidle', timeout=3000)
                            await asyncio.sleep(0.3)  # Brief wait for SPA to stabilize
                        except Exception as e:
                            logger.debug("Browser back failed: %s, using goto as fallback", e)
                            await page.goto(initial_url)
                            await page.wait_for_load_state('networkidle')
                     
                     return new_state.state_id

        except Exception as e:
            logger.debug("Error executing form fill: %s", e)
            if navigate_back and page.url != initial_url:
                await page.goto(initial_url)

        return None
    
    async def _execute_link_click(
        self,
        page: Page,
        from_state: UIState,
        link_info: dict[str, Any],
        navigate_back: bool = True
    ) -> str | None:
        """Execute a link click and discover resulting state.
        
        Args:
            page: Playwright Page object
            from_state: State before clicking
            link_info: Link element descriptor
            navigate_back: Whether to navigate back after discovering new state
            
        Returns:
            New state ID, or None if no state change
        """
        initial_url = page.url
        
        try:
            # Try to locate link using descriptor
            link = await self._locate_element_from_descriptor(page, link_info)
            
            if not link:
                link_text = link_info.get("locators", {}).get("text", "unknown")
                logger.debug("Failed to locate link: %s", link_text)
                return None
            
            # Get link text for logging
            link_text = link_info.get("locators", {}).get("text", "unknown")
            
            # Click link
            await link.click()
            
            # Wait for navigation
            try:
                await page.wait_for_load_state('networkidle', timeout=3000)
            except PlaywrightTimeoutError:
                await asyncio.sleep(0.5)
            
            # Discover new state
            new_state = await self._discover_current_state(page)
            
            # Check if actually changed state
            if new_state.state_id == from_state.state_id:
                logger.debug("Link click didn't change state: %s", link_text)
                if navigate_back and page.url != initial_url:
                    await page.goto(initial_url)
                    await page.wait_for_load_state('networkidle')
                return None
            
            # Add new state
            if new_state.state_id not in self.states:
                self.states[new_state.state_id] = new_state
            
            # Check if this transition already exists (avoid duplicates)
            transition_sig = (from_state.state_id, "navigate", new_state.state_id)
            if transition_sig in self.transition_signatures:
                logger.debug("Transition %s -> %s already recorded, skipping duplicate", 
                           from_state.state_id, new_state.state_id)
            else:
                # Record transition
                transition = StateTransition(
                    transition_id=f"T_{from_state.state_id}_TO_{new_state.state_id}_NAV",
                    from_state_id=from_state.state_id,
                    to_state_id=new_state.state_id,
                    action_type="navigate",
                    trigger_locators=link_info,
                )
                
                # Check if this creates a conditional transition
                self._detect_conditional_transition(transition)
                
                self.transitions.append(transition)
                self.transition_signatures.add(transition_sig)
                
                logger.info("Navigation transition: %s -> %s (via '%s')", 
                           from_state.state_id, new_state.state_id, link_text)
            
            # Navigate back to source state so we can click other links
            if navigate_back and page.url != initial_url:
                logger.debug("Navigating back to %s to discover more transitions", from_state.state_id)
                try:
                    # Use browser back to preserve SPA state
                    await page.go_back()
                    await page.wait_for_load_state('networkidle', timeout=3000)
                    await asyncio.sleep(0.3)  # Brief wait for SPA to stabilize
                except Exception as e:
                    logger.debug("Browser back failed: %s, using goto as fallback", e)
                    await page.goto(initial_url)
                    await page.wait_for_load_state('networkidle')
            
            return new_state.state_id
            
        except Exception as e:
            link_text = link_info.get("locators", {}).get("text", "unknown")
            logger.debug("Error in link click execution for '%s': %s", link_text, str(e))
            if navigate_back:
                try:
                    if page.url != initial_url:
                        await page.goto(initial_url)
                        await page.wait_for_load_state('networkidle')
                except Exception:
                    pass
            return None
    
    async def _execute_button_click(
        self,
        page: Page,
        from_state: UIState,
        button_info: dict[str, Any],
        navigate_back: bool = True
    ) -> str | None:
        """Execute a button click and discover resulting state.
        
        Args:
            page: Playwright Page object
            from_state: State before clicking
            button_info: Button element descriptor
            navigate_back: Whether to navigate back after discovering new state
            
        Returns:
            New state ID, or None if no state change
        """
        initial_url = page.url
        
        try:
            # Try to locate button using descriptor
            button = await self._locate_element_from_descriptor(page, button_info)
            
            if not button:
                button_text = button_info.get("locators", {}).get("text", "unknown")
                logger.debug("Failed to locate button: %s", button_text)
                return None
            
            # Click button
            await button.click()
            
            # Wait for potential state change
            try:
                await page.wait_for_load_state('networkidle', timeout=2000)
            except PlaywrightTimeoutError:
                await asyncio.sleep(0.5)
            
            # Discover new state
            new_state = await self._discover_current_state(page)
            
            # Check if actually changed state
            if new_state.state_id == from_state.state_id:
                logger.debug("Button click didn't change state")
                if navigate_back and page.url != initial_url:
                    await page.goto(initial_url)
                    await page.wait_for_load_state('networkidle')
                return None
            
            # Add new state
            if new_state.state_id not in self.states:
                self.states[new_state.state_id] = new_state
            
            # Check if this transition already exists (avoid duplicates)
            transition_sig = (from_state.state_id, "click", new_state.state_id)
            if transition_sig in self.transition_signatures:
                logger.debug("Transition %s -> %s already recorded, skipping duplicate", 
                           from_state.state_id, new_state.state_id)
            else:
                # Record transition
                transition = StateTransition(
                    transition_id=f"T_{from_state.state_id}_TO_{new_state.state_id}_CLICK",
                    from_state_id=from_state.state_id,
                    to_state_id=new_state.state_id,
                    action_type="click",
                    trigger_locators=button_info,
                )
                self.transitions.append(transition)
                self.transition_signatures.add(transition_sig)
                
                logger.info("Button transition: %s -> %s", from_state.state_id, new_state.state_id)
            
            # Navigate back to source state
            if navigate_back and page.url != initial_url:
                logger.debug("Navigating back to %s to discover more transitions", from_state.state_id)
                try:
                    # Use browser back to preserve SPA state
                    await page.go_back()
                    await page.wait_for_load_state('networkidle', timeout=3000)
                    await asyncio.sleep(0.3)  # Brief wait for SPA to stabilize
                except Exception as e:
                    logger.debug("Browser back failed: %s, using goto as fallback", e)
                    await page.goto(initial_url)
                    await page.wait_for_load_state('networkidle')
            
            return new_state.state_id
            
        except Exception as e:
            button_text = button_info.get("locators", {}).get("text", "unknown")
            logger.debug("Error in button click execution for '%s': %s", button_text, str(e))
            if navigate_back:
                try:
                    if page.url != initial_url:
                        await page.goto(initial_url)
                        await page.wait_for_load_state('networkidle')
                except Exception:
                    pass
            return None
    
    async def _locate_element_from_descriptor(
        self,
        page: Page,
        descriptor: dict[str, Any]
    ) -> Locator | None:
        """Locate element using resilient descriptor.
        
        Args:
            page: Playwright Page object
            descriptor: Element descriptor with locator strategies
            
        Returns:
            Locator object, or None if not found
        """
        locators = descriptor.get("locators", {})
        element_type = descriptor.get("element_type", "")
        
        # Try locators in priority order
        # Priority 1: test_id
        if "test_id" in locators:
            try:
                loc = page.get_by_test_id(locators["test_id"])
                if await loc.count() > 0:
                    return loc.first
            except Exception:
                pass
        
        # Priority 2: role + aria_label
        if "role" in locators:
            try:
                if "aria_label" in locators:
                    loc = page.get_by_role(locators["role"], name=locators["aria_label"])
                else:
                    loc = page.get_by_role(locators["role"])
                if await loc.count() > 0:
                    return loc.first
            except Exception:
                pass
        
        # Priority 3: text (with element type context)
        if "text" in locators:
            try:
                text = locators["text"]
                if element_type == "link":
                    # For links, combine text with href if available
                    loc = page.locator(f'a:has-text("{text}")').first
                    if await loc.count() > 0:
                        return loc
                else:
                    loc = page.get_by_text(text, exact=False)
                    if await loc.count() > 0:
                        return loc.first
            except Exception:
                pass
        
        # Priority 4: href (for links)
        if "href" in locators and element_type == "link":
            try:
                href = locators["href"]
                loc = page.locator(f'a[href="{href}"]')
                if await loc.count() > 0:
                    return loc.first
            except Exception:
                pass
        
        # Priority 5: placeholder (for inputs)
        if "placeholder" in locators:
            try:
                loc = page.get_by_placeholder(locators["placeholder"])
                if await loc.count() > 0:
                    return loc.first
            except Exception:
                pass
        
        # Priority 6: name attribute (for inputs)
        if "name" in locators and element_type in ["input", "select"]:
            try:
                name = locators["name"]
                loc = page.locator(f'{element_type}[name="{name}"]')
                if await loc.count() > 0:
                    return loc.first
            except Exception:
                pass
        
        return None
    
    async def _get_unique_selector(self, locator: Locator) -> str:
        """Get a unique CSS selector for an element.
        
        Args:
            locator: Playwright Locator
            
        Returns:
            CSS selector string
        """
        try:
            # Try to get an ID-based selector
            element_id = await locator.get_attribute("id")
            if element_id:
                return f"#{element_id}"
            
            # Fallback to a generic selector
            tag_name = await locator.evaluate("el => el.tagName.toLowerCase()")
            return f"{tag_name}"
        except Exception:
            return "form"
    
    def _export_to_graph(self) -> dict[str, Any]:
        """Export FSM to graph format compatible with analysis tools.
        
        Returns:
            Dictionary containing nodes, edges, and metadata
        """
        nodes = []
        edges = []
        
        # Export states as nodes
        for state_id, state in self.states.items():
            nodes.append({
                "id": state_id,
                "node_type": "state",
                "state_type": state.state_type,
                "fingerprint": state.fingerprint,
                "verification_logic": state.verification_logic,
                "element_descriptors": state.element_descriptors,
                "discovered_at": state.discovered_at,
            })
        
        # Export transitions as edges
        for transition in self.transitions:
            edges.append({
                "source": transition.from_state_id,
                "target": transition.to_state_id,
                "edge_type": "transition",
                "transition_id": transition.transition_id,
                "action_type": transition.action_type,
                "trigger_locators": transition.trigger_locators,
                "action_data": transition.action_data,
                "success_rate": transition.success_rate,
            })
        
        graph_data = {
            "base_url": self.base_url,
            "graph_type": "fsm_mbt",
            "discovery_method": "playwright_state_machine_dfs" if self.use_dfs else "playwright_state_machine_bfs",
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "state_count": len(self.states),
                "transition_count": len(self.transitions),
                "visited_states": len(self.visited_states),
                "state_types": self._get_state_type_distribution(),
            }
        }
        
        # Add seed verification results if applicable
        if self.seeded_states:
            unchanged_count = sum(1 for s in self.seeded_state_status.values() if s == "unchanged")
            modified_count = sum(1 for s in self.seeded_state_status.values() if s == "modified")
            removed_count = sum(1 for s in self.seeded_state_status.values() if s == "removed")
            unreachable_count = sum(1 for s in self.seeded_state_status.values() if s == "unreachable")
            verified_count = unchanged_count + modified_count
            
            graph_data["seed_verification"] = {
                "seeded_state_count": len(self.seeded_states),
                "verified_count": verified_count,
                "unchanged_count": unchanged_count,
                "modified_count": modified_count,
                "removed_count": removed_count,
                "unreachable_count": unreachable_count,
                "state_status": self.seeded_state_status
            }
        
        return graph_data
    
    def _get_state_type_distribution(self) -> dict[str, int]:
        """Get distribution of state types.
        
        Returns:
            Dictionary mapping state_type to count
        """
        distribution: dict[str, int] = {}
        for state in self.states.values():
            distribution[state.state_type] = distribution.get(state.state_type, 0) + 1
        return distribution
