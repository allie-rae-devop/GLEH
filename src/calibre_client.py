"""
Calibre-Web OPDS Client

Provides a Python interface to interact with Calibre-Web via OPDS feeds.
Used to fetch books, covers, and metadata for integration with GLEH.

OPDS (Open Publication Distribution System) is the standard protocol for ebook catalogs.
Documentation: https://specs.opds.io/opds-1.2
"""

import os
import requests
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from flask import current_app

logger = logging.getLogger(__name__)

# OPDS/Atom namespace
ATOM_NS = {'atom': 'http://www.w3.org/2005/Atom',
           'opds': 'http://opds-spec.org/2010/catalog',
           'dc': 'http://purl.org/dc/terms/'}


class CalibreWebClient:
    """Client for interacting with Calibre-Web via OPDS feeds."""

    def __init__(self, base_url: Optional[str] = None, external_url: Optional[str] = None,
                 username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Calibre-Web OPDS client.

        Args:
            base_url: Internal base URL of Calibre-Web (e.g., http://calibre-web:8083 for Docker)
                     If not provided, reads from CALIBRE_WEB_URL env var or Flask config
            external_url: External base URL for browser access (e.g., http://localhost:8083)
                         If not provided, reads from CALIBRE_WEB_EXTERNAL_URL or uses base_url
            username: Optional Calibre-Web username for authentication
                     If not provided, reads from CALIBRE_WEB_USERNAME env var
            password: Optional Calibre-Web password for authentication
                     If not provided, reads from CALIBRE_WEB_PASSWORD env var
        """
        self.base_url = base_url or self._get_base_url()
        if not self.base_url:
            raise ValueError(
                "Calibre-Web URL not configured. "
                "Set CALIBRE_WEB_URL in .env or pass base_url parameter"
            )

        # Remove trailing slash for consistent URL construction
        self.base_url = self.base_url.rstrip('/')

        # External URL for browser-facing links (covers, readers)
        self.external_url = external_url or self._get_external_url() or self.base_url
        self.external_url = self.external_url.rstrip('/')

        # Get authentication credentials from parameters or environment
        self.username = username or self._get_username()
        self.password = password or self._get_password()

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GLEH/1.0 Calibre-Web OPDS Client'
        })

        # Set up basic authentication if credentials are provided
        if self.username and self.password:
            self.session.auth = (self.username, self.password)
            logger.info(f"Calibre-Web authentication configured for user: {self.username}")

    def _get_base_url(self) -> Optional[str]:
        """Get Calibre-Web base URL from environment or Flask config."""
        # Try Flask config first (if in app context)
        try:
            return current_app.config.get('CALIBRE_WEB_URL')
        except RuntimeError:
            # Not in Flask app context, try environment variable
            return os.environ.get('CALIBRE_WEB_URL')

    def _get_external_url(self) -> Optional[str]:
        """Get Calibre-Web external URL from environment or Flask config."""
        # Try Flask config first (if in app context)
        try:
            return current_app.config.get('CALIBRE_WEB_EXTERNAL_URL')
        except RuntimeError:
            # Not in Flask app context, try environment variable
            return os.environ.get('CALIBRE_WEB_EXTERNAL_URL')

    def _get_username(self) -> Optional[str]:
        """Get Calibre-Web username from environment or Flask config."""
        try:
            return current_app.config.get('CALIBRE_WEB_USERNAME')
        except RuntimeError:
            return os.environ.get('CALIBRE_WEB_USERNAME')

    def _get_password(self) -> Optional[str]:
        """Get Calibre-Web password from environment or Flask config."""
        try:
            return current_app.config.get('CALIBRE_WEB_PASSWORD')
        except RuntimeError:
            return os.environ.get('CALIBRE_WEB_PASSWORD')

    def get_books(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Fetch books from Calibre-Web OPDS feed.

        Args:
            limit: Maximum number of books to return (default: 100)
            offset: Number of books to skip (for pagination)

        Returns:
            List of book dictionaries with keys: id, title, authors, cover_url, etc.
        """
        try:
            # Calibre-Web OPDS feeds: /opds for catalog, /opds/new for recent books
            url = f"{self.base_url}/opds/new"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Parse OPDS XML feed
            root = ET.fromstring(response.content)
            books = self._parse_opds_feed(root)

            # Apply limit and offset
            return books[offset:offset + limit]

        except requests.RequestException as e:
            logger.error(f"Failed to fetch books from Calibre-Web OPDS: {e}")
            return []
        except ET.ParseError as e:
            logger.error(f"Failed to parse OPDS feed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching books: {e}")
            return []

    def get_book(self, book_id: int) -> Optional[Dict]:
        """
        Fetch a single book by ID.

        Args:
            book_id: Calibre book ID

        Returns:
            Book dictionary or None if not found
        """
        # For single book, just search all books and filter
        # OPDS doesn't have a direct "get by ID" endpoint
        try:
            all_books = self.get_books(limit=1000)
            for book in all_books:
                if book.get('id') == book_id:
                    return book
            return None
        except Exception as e:
            logger.error(f"Failed to fetch book {book_id}: {e}")
            return None

    def get_featured_books(self, count: int = 6) -> List[Dict]:
        """
        Fetch featured/recent books for homepage display.

        Args:
            count: Number of featured books to return

        Returns:
            List of book dictionaries
        """
        return self.get_books(limit=count, offset=0)

    def search_books(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Search for books by title, author, or other metadata.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching book dictionaries
        """
        try:
            url = f"{self.base_url}/opds/search"
            params = {'query': query}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            books = self._parse_opds_feed(root)

            return books[:limit]

        except requests.RequestException as e:
            logger.error(f"Failed to search books: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching books: {e}")
            return []

    def get_cover_url(self, book_id: int) -> str:
        """
        Get the cover image URL for a book.

        Args:
            book_id: Calibre book ID

        Returns:
            URL to book cover image (proxied through Flask for authentication)
        """
        # Use Flask proxy endpoint to avoid cross-origin authentication issues
        try:
            from flask import url_for
            return url_for('proxy_calibre_cover', book_id=book_id, _external=False)
        except RuntimeError:
            # Not in Flask app context, return relative URL
            return f"/api/calibre/cover/{book_id}"

    def get_reader_url(self, book_id: int) -> str:
        """
        Get the reader URL for a book.

        Args:
            book_id: Calibre book ID

        Returns:
            URL to Calibre-Web reader (proxied through nginx for SSO/guest access)
        """
        # Use nginx proxy path for SSO and guest access support
        return f"/calibre-web/read/{book_id}/epub"

    def _parse_opds_feed(self, root: ET.Element) -> List[Dict]:
        """
        Parse OPDS Atom feed and extract book entries.

        Args:
            root: XML root element of OPDS feed

        Returns:
            List of book dictionaries
        """
        books = []

        # Find all entry elements in the feed
        for entry in root.findall('atom:entry', ATOM_NS):
            try:
                book = self._parse_opds_entry(entry)
                if book:
                    books.append(book)
            except Exception as e:
                logger.warning(f"Failed to parse OPDS entry: {e}")
                continue

        return books

    def _parse_opds_entry(self, entry: ET.Element) -> Optional[Dict]:
        """
        Parse a single OPDS entry element into a book dictionary.

        Args:
            entry: XML entry element from OPDS feed

        Returns:
            Book dictionary or None if parsing fails
        """
        try:
            # Extract book ID from link href (OPDS feeds may use UUIDs in entry IDs)
            # Look for numeric IDs in links like /opds/cover/4 or /opds/download/7/epub/
            book_id = None
            import re
            for link in entry.findall('atom:link', ATOM_NS):
                href = link.get('href', '')
                # Match patterns like /opds/cover/4 or /opds/download/7/epub/
                match = re.search(r'/opds/(?:cover|download)/(\d+)', href)
                if match:
                    book_id = int(match.group(1))
                    break

            if not book_id:
                return None

            # Extract title
            title = entry.findtext('atom:title', 'Unknown Title', ATOM_NS)

            # Extract authors
            authors = []
            author_names = []
            for author_elem in entry.findall('atom:author', ATOM_NS):
                author_name = author_elem.findtext('atom:name', '', ATOM_NS)
                if author_name:
                    authors.append({'name': author_name})
                    author_names.append(author_name)

            author_str = ', '.join(author_names) if author_names else 'Unknown'

            # Extract summary/description
            summary = entry.findtext('atom:summary', '', ATOM_NS) or entry.findtext('atom:content', '', ATOM_NS)

            # Extract categories/tags
            categories = []
            for category in entry.findall('atom:category', ATOM_NS):
                label = category.get('label') or category.get('term')
                if label:
                    categories.append(label)

            # Extract publication date
            published = entry.findtext('atom:published', '', ATOM_NS) or entry.findtext('atom:updated', '', ATOM_NS)

            # Extract cover URL from links (use external_url for browser access)
            cover_url = self.get_cover_url(book_id)
            for link in entry.findall('atom:link', ATOM_NS):
                rel = link.get('rel', '')
                if rel == 'http://opds-spec.org/image' or rel == 'http://opds-spec.org/image/thumbnail':
                    href = link.get('href', '')
                    if href.startswith('http'):
                        cover_url = href
                    elif href.startswith('/'):
                        # Use external_url for browser-accessible URLs
                        cover_url = f"{self.external_url}{href}"
                    break

            return {
                'id': book_id,
                'uid': f"calibre-{book_id}",
                'title': title,
                'author': author_str,
                'authors': authors,
                'cover_url': cover_url,
                'reader_url': self.get_reader_url(book_id),
                'categories': categories,
                'description': summary,
                'published': published,
                'publisher': '',
                'isbn': '',
                'rating': 0,
                'formats': [],
            }

        except Exception as e:
            logger.warning(f"Error parsing OPDS entry: {e}")
            return None

    def _extract_book_id(self, entry_id: str) -> Optional[int]:
        """
        Extract numeric book ID from OPDS entry ID.

        Args:
            entry_id: Entry ID string (e.g., "urn:uuid:1" or "tag:calibre-web:book:42")

        Returns:
            Book ID as integer, or None if extraction fails
        """
        try:
            # Try different ID formats
            # Format 1: urn:uuid:NUMBER
            if 'urn:uuid:' in entry_id:
                return int(entry_id.split('urn:uuid:')[-1])

            # Format 2: tag:calibre-web:book:NUMBER
            if ':book:' in entry_id:
                return int(entry_id.split(':book:')[-1])

            # Format 3: Just a number
            if entry_id.isdigit():
                return int(entry_id)

            # Try to find any number in the ID
            import re
            numbers = re.findall(r'\d+', entry_id)
            if numbers:
                return int(numbers[-1])

            return None
        except (ValueError, IndexError):
            return None

    def health_check(self) -> bool:
        """
        Check if Calibre-Web is accessible.

        Returns:
            True if Calibre-Web is reachable, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/opds", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False


# Singleton instance
_calibre_client: Optional[CalibreWebClient] = None


def get_calibre_client() -> CalibreWebClient:
    """Get the global CalibreWebClient instance."""
    global _calibre_client
    if _calibre_client is None:
        _calibre_client = CalibreWebClient()
    return _calibre_client


def init_calibre_client(base_url: Optional[str] = None) -> CalibreWebClient:
    """
    Initialize or reinitialize the global Calibre-Web client.

    Args:
        base_url: Optional base URL to override config

    Returns:
        Initialized CalibreWebClient instance
    """
    global _calibre_client
    _calibre_client = CalibreWebClient(base_url)
    return _calibre_client
