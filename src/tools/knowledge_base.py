"""Knowledge base lookup tool for EUC Assessment Agent team.

This module provides a tool for agents to lookup information in the knowledge base.
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Define knowledge base path
DEFAULT_KB_PATH = Path(__file__).parent.parent.parent / "data" / "knowledge_base"


class KnowledgeBaseTool:
    """A tool for looking up information in the knowledge base."""

    def __init__(self, kb_path: Optional[Path] = None):
        """Initialize the knowledge base tool.
        
        Args:
            kb_path: Path to the knowledge base directory. Defaults to "data/knowledge_base".
        """
        self.kb_path = kb_path or DEFAULT_KB_PATH
        if not self.kb_path.exists():
            logger.warning(f"Knowledge base path does not exist: {self.kb_path}")
            self.kb_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created knowledge base directory: {self.kb_path}")
        
        # Cache for knowledge base entries
        self._kb_cache: Dict[str, Dict[str, Any]] = {}
        
        # Load knowledge base index if it exists
        self._load_kb_index()

    def _load_kb_index(self) -> None:
        """Load the knowledge base index if it exists."""
        index_path = self.kb_path / "index.json"
        if index_path.exists():
            try:
                with open(index_path, "r") as f:
                    self.kb_index = json.load(f)
                    logger.info(f"Loaded knowledge base index with {len(self.kb_index)} entries")
            except Exception as e:
                logger.error(f"Error loading knowledge base index: {e}")
                self.kb_index = {}
        else:
            logger.info("Knowledge base index not found, creating new index")
            self.kb_index = {}
            self._save_kb_index()

    def _save_kb_index(self) -> None:
        """Save the knowledge base index."""
        index_path = self.kb_path / "index.json"
        try:
            with open(index_path, "w") as f:
                json.dump(self.kb_index, f, indent=2)
                logger.info(f"Saved knowledge base index with {len(self.kb_index)} entries")
        except Exception as e:
            logger.error(f"Error saving knowledge base index: {e}")

    def lookup(self, category: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Lookup information in the knowledge base.
        
        Args:
            category: The category to search in (e.g., "licensing", "security")
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching entries
        """
        logger.info(f"Looking up '{query}' in category '{category}'")
        
        # Check if category exists
        category_path = self.kb_path / category
        if not category_path.exists():
            logger.warning(f"Category '{category}' not found in knowledge base")
            return []
        
        # Load cached entries for this category or read from disk
        if category not in self._kb_cache:
            self._load_category(category)
        
        # If still not in cache, return empty list
        if category not in self._kb_cache:
            return []
        
        # Simple search for matching entries
        results = []
        query_terms = query.lower().split()
        
        for entry_id, entry in self._kb_cache[category].items():
            # Check if any query term is in the entry text
            entry_text = entry.get("title", "") + " " + entry.get("content", "")
            entry_text = entry_text.lower()
            
            match_score = 0
            for term in query_terms:
                if term in entry_text:
                    match_score += 1
            
            if match_score > 0:
                results.append({
                    "id": entry_id,
                    "score": match_score,
                    **entry
                })
        
        # Sort by score (descending) and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _load_category(self, category: str) -> None:
        """Load all entries for a category into the cache."""
        category_path = self.kb_path / category
        if not category_path.exists():
            logger.warning(f"Category '{category}' not found in knowledge base")
            return
        
        self._kb_cache[category] = {}
        
        # Load each JSON file in the category directory
        for file_path in category_path.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    entry = json.load(f)
                    entry_id = file_path.stem
                    self._kb_cache[category][entry_id] = entry
            except Exception as e:
                logger.error(f"Error loading knowledge base entry {file_path}: {e}")

    def add_entry(self, category: str, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new entry to the knowledge base.
        
        Args:
            category: The category to add the entry to
            title: The title of the entry
            content: The content of the entry
            metadata: Additional metadata for the entry
            
        Returns:
            The ID of the new entry
        """
        logger.info(f"Adding new entry '{title}' to category '{category}'")
        
        # Create category directory if it doesn't exist
        category_path = self.kb_path / category
        if not category_path.exists():
            category_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created category directory: {category_path}")
        
        # Generate a unique ID for this entry
        import uuid
        entry_id = str(uuid.uuid4())[:8]
        
        # Create the entry
        entry = {
            "title": title,
            "content": content,
            "metadata": metadata or {},
            "created_at": __import__("datetime").datetime.now().isoformat()
        }
        
        # Save the entry
        entry_path = category_path / f"{entry_id}.json"
        with open(entry_path, "w") as f:
            json.dump(entry, f, indent=2)
        
        # Update cache
        if category not in self._kb_cache:
            self._kb_cache[category] = {}
        self._kb_cache[category][entry_id] = entry
        
        # Update index
        if category not in self.kb_index:
            self.kb_index[category] = []
        self.kb_index[category].append({
            "id": entry_id,
            "title": title,
            "created_at": entry["created_at"]
        })
        self._save_kb_index()
        
        return entry_id


# Singleton instance
_kb_tool = None


def get_knowledge_base() -> KnowledgeBaseTool:
    """Get the singleton knowledge base tool instance."""
    global _kb_tool
    if _kb_tool is None:
        _kb_tool = KnowledgeBaseTool()
    return _kb_tool 