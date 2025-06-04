"""
Exceptions for cloud storage operations.
"""


class CloudStorageError(Exception):
    """Base exception for all cloud storage errors."""
    pass


class BucketCreationError(CloudStorageError):
    """Exception raised when bucket creation fails."""
    pass


class ObjectUploadError(CloudStorageError):
    """Exception raised when object upload fails."""
    pass


class ObjectDownloadError(CloudStorageError):
    """Exception raised when object download fails."""
    pass


class ObjectDeleteError(CloudStorageError):
    """Exception raised when object deletion fails."""
    pass


class ObjectNotFoundError(CloudStorageError):
    """Exception raised when an object is not found."""
    pass


class BucketNotFoundError(CloudStorageError):
    """Exception raised when a bucket is not found."""
    pass


class AuthenticationError(CloudStorageError):
    """Exception raised when authentication to the cloud service fails."""
    pass


class ConnectionError(CloudStorageError):
    """Exception raised when connecting to the cloud service fails."""
    pass
