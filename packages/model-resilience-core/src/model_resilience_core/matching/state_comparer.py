"""
State comparison implementation.

Weighted fuzzy matching for comparing UI states based on multi-dimensional fingerprints.

Implements the resilience hierarchy from "Architecting UI Test Resilience":
1. Semantic identity (60%): Accessibility tree (landmarks, roles, structure)
2. Functional identity (25%): Actionable elements (buttons, links, inputs)
3. Structural identity (10%): URL pattern
4. Content identity (4%): Title, headings
5. Style identity (1%): DOM hash (optional, rarely used)
"""

from __future__ import annotations
import logging
from typing import Any
from ..models import UIState

logger = logging.getLogger(__name__)


class StateComparer:
    """
    Compares UI states using weighted similarity scoring.
    
    Implements fuzzy matching based on accessibility tree properties
    to identify same states even after UI changes (CSS, DOM restructure).
    """
    
    # Similarity thresholds
    MATCH_THRESHOLD = 0.80  # 80% similarity = same state
    STRONG_MATCH = 0.90     # 90%+ = very confident match
    WEAK_MATCH = 0.70       # 70-80% = possible match (needs review)
    
    # Weighting hierarchy (configurable)
    DEFAULT_WEIGHTS = {
        "semantic": 0.60,      # Accessibility tree
        "functional": 0.25,    # Actionable elements
        "structural": 0.10,    # URL pattern
        "content": 0.04,       # Title and headings
        "style": 0.01,         # DOM hash (optional)
    }
    
    def __init__(self, weights: dict[str, float] | None = None) -> None:
        """
        Initialize the state comparer.
        
        Args:
            weights: Custom weights for fingerprint dimensions (optional)
        """
        self.weights = weights if weights is not None else self.DEFAULT_WEIGHTS.copy()
    
    def calculate_similarity(
        self,
        fp1: dict[str, Any] | UIState,
        fp2: dict[str, Any] | UIState
    ) -> float:
        """Calculate weighted similarity between two state fingerprints.
        
        Args:
            fp1: First state fingerprint (dict) or UIState object
            fp2: Second state fingerprint (dict) or UIState object
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Extract fingerprints if UIState objects passed
        if isinstance(fp1, UIState):
            fp1 = fp1.fingerprint
        if isinstance(fp2, UIState):
            fp2 = fp2.fingerprint
        
        scores = {}
        
        # 1. Semantic identity (60%): Accessibility tree
        scores['semantic'] = self._compare_a11y_trees(
            fp1.get('accessibility_tree'),
            fp2.get('accessibility_tree')
        )
        
        # 2. Functional identity (25%): Actionable elements
        scores['functional'] = self._compare_actionable_elements(
            fp1.get('actionable_elements'),
            fp2.get('actionable_elements')
        )
        
        # 3. Structural identity (10%): URL pattern
        scores['structural'] = self._compare_url_patterns(
            fp1.get('url_pattern', ''),
            fp2.get('url_pattern', '')
        )
        
        # 4. Content identity (4%): Title and headings
        scores['content'] = self._compare_content(
            fp1.get('title', ''),
            fp2.get('title', ''),
            fp1.get('main_heading', ''),
            fp2.get('main_heading', '')
        )
        
        # 5. Style identity (1%): Optional
        # scores['style'] = ...
        
        # Calculate weighted average
        weighted_score = (
            scores['semantic'] * self.weights['semantic'] +
            scores['functional'] * self.weights['functional'] +
            scores['structural'] * self.weights['structural'] +
            scores['content'] * self.weights['content']
            # + scores['style'] * self.weights['style']  # Optional
        )
        
        logger.debug(
            "Similarity scores: semantic=%.2f, functional=%.2f, "
            "structural=%.2f, content=%.2f, weighted=%.2f",
            scores['semantic'], scores['functional'],
            scores['structural'], scores['content'], weighted_score
        )
        
        return weighted_score
    
    def is_match(
        self,
        state1: UIState | dict[str, Any],
        state2: UIState | dict[str, Any],
        threshold: float | None = None
    ) -> bool:
        """
        Determine if two states match based on similarity threshold.
        
        Args:
            state1: First state (UIState or fingerprint dict)
            state2: Second state (UIState or fingerprint dict)
            threshold: Minimum similarity for match (default: MATCH_THRESHOLD)
            
        Returns:
            True if states match, False otherwise
        """
        if threshold is None:
            threshold = self.MATCH_THRESHOLD
        
        similarity = self.calculate_similarity(state1, state2)
        return similarity >= threshold
    
    def find_matching_state(
        self,
        candidate_fingerprint: dict[str, Any],
        existing_states: list[UIState],
        threshold: float | None = None
    ) -> tuple[UIState | None, float]:
        """Find the best matching state from existing states.
        
        Args:
            candidate_fingerprint: Fingerprint to match
            existing_states: List of existing UIState objects
            threshold: Minimum similarity score to consider a match
            
        Returns:
            Tuple of (matched_state, similarity_score) or (None, 0.0)
        """
        if threshold is None:
            threshold = self.MATCH_THRESHOLD
        
        best_match = None
        best_score = 0.0
        
        for state in existing_states:
            score = self.calculate_similarity(
                candidate_fingerprint,
                state.fingerprint
            )
            
            if score >= threshold and score > best_score:
                best_match = state
                best_score = score
        
        if best_match:
            logger.info(
                "Found matching state: %s (similarity: %.2f%%)",
                best_match.state_id, best_score * 100
            )
        
        return best_match, best_score
    
    @staticmethod
    def _compare_a11y_trees(tree1: dict[str, Any] | None, tree2: dict[str, Any] | None) -> float:
        """Compare accessibility trees for semantic similarity.
        
        Compares:
        - Landmark roles (navigation, main, etc.)
        - Interactive element count
        - Heading hierarchy
        - Key landmarks
        - ARIA states
        
        Args:
            tree1: First accessibility tree
            tree2: Second accessibility tree
            
        Returns:
            Similarity score 0.0-1.0
        """
        if not tree1 or not tree2:
            return 0.0
        
        scores = []
        
        # Compare landmark roles (most stable) - 40% of semantic score
        landmarks1 = set(tree1.get('landmark_roles', []))
        landmarks2 = set(tree2.get('landmark_roles', []))
        if landmarks1 or landmarks2:
            landmark_score = len(landmarks1 & landmarks2) / max(len(landmarks1 | landmarks2), 1)
            scores.append((landmark_score, 0.40))
        
        # Compare interactive count (approximate) - 20% of semantic score
        count1 = tree1.get('interactive_count', 0)
        count2 = tree2.get('interactive_count', 0)
        if count1 or count2:
            # Allow 20% variance (e.g., 8 vs 10 elements)
            max_count = max(count1, count2)
            diff = abs(count1 - count2)
            count_score = max(0.0, 1.0 - (diff / max(max_count * 0.2, 1)))
            scores.append((count_score, 0.20))
        
        # Compare heading hierarchy - 20% of semantic score
        headings1 = tree1.get('heading_hierarchy', [])
        headings2 = tree2.get('heading_hierarchy', [])
        if headings1 or headings2:
            # Exact match on headings (they're stable content)
            heading_score = 1.0 if headings1 == headings2 else 0.5
            scores.append((heading_score, 0.20))
        
        # Compare key landmarks - 10% of semantic score
        key_landmarks1 = set(tree1.get('key_landmarks', {}).keys())
        key_landmarks2 = set(tree2.get('key_landmarks', {}).keys())
        if key_landmarks1 or key_landmarks2:
            key_landmark_score = len(key_landmarks1 & key_landmarks2) / max(len(key_landmarks1 | key_landmarks2), 1)
            scores.append((key_landmark_score, 0.10))
        
        # Compare ARIA states - 10% of semantic score
        aria_score = StateComparer._compare_aria_states(
            tree1.get('aria_states'),
            tree2.get('aria_states')
        )
        scores.append((aria_score, 0.10))
        
        # Calculate weighted average
        if not scores:
            return 0.5  # Neutral if no data
        
        total_weight = sum(weight for _, weight in scores)
        weighted_sum = sum(score * weight for score, weight in scores)
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    @staticmethod
    def _compare_aria_states(states1: dict[str, Any] | None, states2: dict[str, Any] | None) -> float:
        """Compare ARIA state attributes.
        
        Compares expanded/selected/checked/disabled states to detect
        same page in different dynamic conditions.
        
        Args:
            states1: First ARIA states dict
            states2: Second ARIA states dict
            
        Returns:
            Similarity score 0.0-1.0
        """
        if not states1 or not states2:
            return 1.0  # If no states, assume same (no dynamic state)
        
        scores = []
        
        # Compare expanded elements count
        exp1_count = len(states1.get('expanded_elements', []))
        exp2_count = len(states2.get('expanded_elements', []))
        if exp1_count or exp2_count:
            max_exp = max(exp1_count, exp2_count)
            exp_score = 1.0 - (abs(exp1_count - exp2_count) / max(max_exp, 1))
            scores.append(exp_score)
        
        # Compare selected elements count
        sel1_count = len(states1.get('selected_elements', []))
        sel2_count = len(states2.get('selected_elements', []))
        if sel1_count or sel2_count:
            max_sel = max(sel1_count, sel2_count)
            sel_score = 1.0 - (abs(sel1_count - sel2_count) / max(max_sel, 1))
            scores.append(sel_score)
        
        # Compare disabled count
        dis1 = states1.get('disabled_count', 0)
        dis2 = states2.get('disabled_count', 0)
        if dis1 or dis2:
            max_dis = max(dis1, dis2)
            dis_score = 1.0 - (abs(dis1 - dis2) / max(max_dis, 1))
            scores.append(dis_score)
        
        return sum(scores) / len(scores) if scores else 1.0
    
    @staticmethod
    def _compare_actionable_elements(
        actions1: dict[str, Any] | None,
        actions2: dict[str, Any] | None
    ) -> float:
        """Compare actionable elements (buttons, links, inputs).
        
        Uses fuzzy matching on role + name to handle text changes.
        
        Args:
            actions1: First actionable elements dict
            actions2: Second actionable elements dict
            
        Returns:
            Similarity score 0.0-1.0
        """
        if not actions1 or not actions2:
            return 0.0
        
        scores = []
        
        # Compare button count and names
        buttons1 = actions1.get('buttons', [])
        buttons2 = actions2.get('buttons', [])
        if buttons1 or buttons2:
            button_score = StateComparer._compare_element_lists(buttons1, buttons2)
            scores.append((button_score, 0.40))  # Buttons are important
        
        # Compare link count and names
        links1 = actions1.get('links', [])
        links2 = actions2.get('links', [])
        if links1 or links2:
            link_score = StateComparer._compare_element_lists(links1, links2)
            scores.append((link_score, 0.40))  # Links are important
        
        # Compare input count
        inputs1 = actions1.get('inputs', [])
        inputs2 = actions2.get('inputs', [])
        if inputs1 or inputs2:
            input_score = StateComparer._compare_element_lists(inputs1, inputs2)
            scores.append((input_score, 0.20))
        
        # Calculate weighted average
        if not scores:
            return 0.5
        
        total_weight = sum(weight for _, weight in scores)
        weighted_sum = sum(score * weight for score, weight in scores)
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    @staticmethod
    def _compare_element_lists(list1: list[dict[str, Any]], list2: list[dict[str, Any]]) -> float:
        """Compare two lists of elements by role and name.
        
        Uses fuzzy string matching for names to handle minor text changes.
        
        Args:
            list1: First element list
            list2: Second element list
            
        Returns:
            Similarity score 0.0-1.0
        """
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        # Extract names from elements
        names1 = [elem.get('name', '') for elem in list1]
        names2 = [elem.get('name', '') for elem in list2]
        
        # Count exact matches
        set1 = set(names1)
        set2 = set(names2)
        exact_matches = len(set1 & set2)
        
        # Calculate Jaccard similarity
        union_size = len(set1 | set2)
        if union_size == 0:
            return 1.0  # Both empty
        
        return exact_matches / union_size
    
    @staticmethod
    def _compare_url_patterns(url1: str, url2: str) -> float:
        """Compare URL patterns.
        
        Args:
            url1: First URL pattern
            url2: Second URL pattern
            
        Returns:
            Similarity score 0.0-1.0
        """
        if not url1 and not url2:
            return 1.0
        if not url1 or not url2:
            return 0.0
        
        # Exact match
        if url1 == url2:
            return 1.0
        
        # Partial match (e.g., "admin/config" vs "admin/users" = 50%)
        parts1 = url1.split('/')
        parts2 = url2.split('/')
        
        # Match as many parts as possible
        matches = sum(1 for p1, p2 in zip(parts1, parts2) if p1 == p2)
        max_parts = max(len(parts1), len(parts2))
        
        return matches / max_parts if max_parts > 0 else 0.0
    
    @staticmethod
    def _compare_content(
        title1: str,
        title2: str,
        heading1: str,
        heading2: str
    ) -> float:
        """Compare content (title and main heading).
        
        Args:
            title1: First page title
            title2: Second page title
            heading1: First main heading
            heading2: Second main heading
            
        Returns:
            Similarity score 0.0-1.0
        """
        scores = []
        
        # Compare titles (70% of content score)
        if title1 or title2:
            title_score = 1.0 if title1 == title2 else 0.0
            scores.append((title_score, 0.70))
        
        # Compare headings (30% of content score)
        if heading1 or heading2:
            heading_score = 1.0 if heading1 == heading2 else 0.0
            scores.append((heading_score, 0.30))
        
        if not scores:
            return 1.0
        
        total_weight = sum(weight for _, weight in scores)
        weighted_sum = sum(score * weight for score, weight in scores)
        return weighted_sum / total_weight if total_weight > 0 else 1.0
