import json
import os
from typing import List, Dict, Optional


class LegalDataService:
    """
    Service for loading and querying legal data from JSON files.
    Provides access to consumer, employment, and tenant law information.
    """
    
    def __init__(self, data_dir: str = "backend/data"):
        """
        Initialize the legal data service.
        
        Args:
            data_dir: Directory containing the legal data JSON files
        """
        self.data_dir = data_dir
        self._consumer_laws: Optional[List[Dict]] = None
        self._employment_laws: Optional[List[Dict]] = None
        self._tenant_laws: Optional[List[Dict]] = None
    
    def _load_json_file(self, filename: str) -> List[Dict]:
        """
        Load and parse a JSON file from the data directory.
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            List of dictionaries containing law data
        """
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found at {file_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing {filename}: {e}")
            return []
    
    @property
    def consumer_laws(self) -> List[Dict]:
        """Lazy load consumer laws data."""
        if self._consumer_laws is None:
            self._consumer_laws = self._load_json_file("consumer_laws.json")
        return self._consumer_laws
    
    @property
    def employment_laws(self) -> List[Dict]:
        """Lazy load employment laws data."""
        if self._employment_laws is None:
            self._employment_laws = self._load_json_file("employment_laws.json")
        return self._employment_laws
    
    @property
    def tenant_laws(self) -> List[Dict]:
        """Lazy load tenant laws data."""
        if self._tenant_laws is None:
            self._tenant_laws = self._load_json_file("tenant_laws.json")
        return self._tenant_laws
    
    def get_all_laws(self) -> Dict[str, List[Dict]]:
        """
        Get all laws organized by category.
        
        Returns:
            Dictionary with keys 'consumer', 'employment', 'tenant'
        """
        return {
            "consumer": self.consumer_laws,
            "employment": self.employment_laws,
            "tenant": self.tenant_laws
        }
    
    def find_law_by_id(self, law_id: str) -> Optional[Dict]:
        """
        Find a specific law by its ID across all categories.
        
        Args:
            law_id: The law ID (e.g., "CON_IN_001", "EMP_IN_001", "TN_IN_002")
            
        Returns:
            Dictionary containing the law data or None if not found
        """
        all_laws = self.consumer_laws + self.employment_laws + self.tenant_laws
        for law in all_laws:
            if law.get("id") == law_id:
                return law
        return None
    
    def find_law_by_scenario(self, category: str, scenario: str) -> Optional[Dict]:
        """
        Find a law by category and scenario.
        
        Args:
            category: Category type ('consumer', 'employment', 'tenant')
            scenario: Scenario identifier (e.g., "defective_product_delivered")
            
        Returns:
            Dictionary containing the law data or None if not found
        """
        category_map = {
            "consumer": self.consumer_laws,
            "consumer_protection": self.consumer_laws,
            "employment": self.employment_laws,
            "tenant": self.tenant_laws,
            "tenant_rights": self.tenant_laws
        }
        
        laws = category_map.get(category.lower(), [])
        scenario_normalized = scenario.lower().replace(" ", "_")
        
        for law in laws:
            if law.get("scenario") == scenario_normalized:
                return law
        return None
    
    def search_by_keywords(self, keywords: List[str], category: Optional[str] = None) -> List[Dict]:
        """
        Search for laws matching any of the provided keywords.
        
        Args:
            keywords: List of keywords to search for
            category: Optional category filter ('consumer', 'employment', 'tenant')
            
        Returns:
            List of matching law dictionaries
        """
        if category:
            category_map = {
                "consumer": self.consumer_laws,
                "consumer_protection": self.consumer_laws,
                "employment": self.employment_laws,
                "tenant": self.tenant_laws,
                "tenant_rights": self.tenant_laws
            }
            laws_to_search = category_map.get(category.lower(), [])
        else:
            laws_to_search = self.consumer_laws + self.employment_laws + self.tenant_laws
        
        matching_laws = []
        keywords_lower = [k.lower() for k in keywords]
        
        for law in laws_to_search:
            law_keywords = [k.lower() for k in law.get("keywords", [])]
            if any(keyword in law_keywords for keyword in keywords_lower):
                matching_laws.append(law)
        
        return matching_laws
    
    def get_laws_by_category(self, category: str) -> List[Dict]:
        """
        Get all laws for a specific category.
        
        Args:
            category: Category type ('consumer', 'employment', 'tenant')
            
        Returns:
            List of law dictionaries for that category
        """
        category_map = {
            "consumer": self.consumer_laws,
            "consumer_protection": self.consumer_laws,
            "employment": self.employment_laws,
            "tenant": self.tenant_laws,
            "tenant_rights": self.tenant_laws
        }
        return category_map.get(category.lower(), [])


# Singleton instance
legal_data_service = LegalDataService()

# Made with Bob
