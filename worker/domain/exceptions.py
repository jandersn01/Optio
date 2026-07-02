class InvalidMessageError(Exception):
    """Raised when a message is invalid."""
    pass

class SearchNotFoundError(Exception):
    """Raised when a search request is not found."""
    pass