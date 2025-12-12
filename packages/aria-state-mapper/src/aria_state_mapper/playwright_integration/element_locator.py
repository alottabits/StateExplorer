"""
Element locator with resilient strategies.

Priority-based element location using multiple Playwright locator strategies.
"""

from typing import Any


class ElementLocator:
    """
    Locates elements using priority-based fallback strategies.
    
    Tries multiple locator strategies in order of resilience:
    1. ARIA role + name (most resilient)
    2. Label text
    3. Visible text
    4. Name attribute
    5. Placeholder text
    6. Href attribute (for links)
    """
    
    # Priority order for locator strategies
    STRATEGY_PRIORITY = [
        "role",
        "label",
        "text",
        "name",
        "placeholder",
        "href",
    ]
    
    @staticmethod
    async def locate(page: Any, descriptor: dict[str, Any]) -> Any | None:
        """
        Locate element using descriptor with fallback strategies.
        
        Args:
            page: Playwright Page object
            descriptor: Element descriptor with multiple locator strategies
            
        Returns:
            Playwright Locator if found, None otherwise
        """
        for strategy in ElementLocator.STRATEGY_PRIORITY:
            if strategy in descriptor:
                locator = ElementLocator._try_strategy(
                    page, strategy, descriptor[strategy]
                )
                
                # Check if element exists
                try:
                    count = await locator.count()
                    if count > 0:
                        return locator
                except Exception:
                    continue
        
        return None
    
    @staticmethod
    def _try_strategy(page: Any, strategy: str, value: str) -> Any:
        """
        Try a specific locator strategy.
        
        Args:
            page: Playwright Page object
            strategy: Strategy name
            value: Value for the strategy
            
        Returns:
            Playwright Locator
        """
        if strategy == "role":
            # Parse role and name
            parts = value.split(":", 1)
            role = parts[0].strip()
            name = parts[1].strip() if len(parts) > 1 else None
            
            if name:
                return page.get_by_role(role, name=name)
            else:
                return page.get_by_role(role)
        
        elif strategy == "label":
            return page.get_by_label(value)
        
        elif strategy == "text":
            return page.get_by_text(value)
        
        elif strategy == "name":
            return page.locator(f"[name='{value}']")
        
        elif strategy == "placeholder":
            return page.get_by_placeholder(value)
        
        elif strategy == "href":
            return page.locator(f"a[href*='{value}']")
        
        else:
            # Unknown strategy, use CSS selector
            return page.locator(value)

