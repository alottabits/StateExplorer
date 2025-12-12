"""
Similarity metrics for comparing values.

Collection of similarity functions for different data types.
"""

from difflib import SequenceMatcher


class SimilarityMetrics:
    """
    Collection of similarity metrics for comparing different types of values.
    """
    
    @staticmethod
    def jaccard_similarity(set1: set, set2: set) -> float:
        """
        Calculate Jaccard similarity between two sets.
        
        Args:
            set1: First set
            set2: Second set
            
        Returns:
            Jaccard similarity (0.0-1.0)
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def text_similarity(text1: str, text2: str) -> float:
        """
        Calculate text similarity using SequenceMatcher.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Text similarity (0.0-1.0)
        """
        if text1 == text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        return SequenceMatcher(None, text1, text2).ratio()
    
    @staticmethod
    def numeric_similarity(num1: int | float, num2: int | float, tolerance: float = 0.2) -> float:
        """
        Calculate numeric similarity with tolerance.
        
        Args:
            num1: First number
            num2: Second number
            tolerance: Acceptable relative difference (default: 20%)
            
        Returns:
            Numeric similarity (0.0-1.0)
        """
        if num1 == num2:
            return 1.0
        
        max_val = max(abs(num1), abs(num2))
        if max_val == 0:
            return 1.0
        
        relative_diff = abs(num1 - num2) / max_val
        
        if relative_diff <= tolerance:
            return 1.0 - (relative_diff / tolerance)
        else:
            return 0.0
    
    @staticmethod
    def list_similarity(list1: list, list2: list) -> float:
        """
        Calculate similarity between two lists.
        
        Args:
            list1: First list
            list2: Second list
            
        Returns:
            List similarity (0.0-1.0)
        """
        if list1 == list2:
            return 1.0
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        # Convert to sets and use Jaccard
        return SimilarityMetrics.jaccard_similarity(set(list1), set(list2))

