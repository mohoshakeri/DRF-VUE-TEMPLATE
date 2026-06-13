"""
List and queryset manipulation utilities.

This module provides functions for searching objects, extracting parameters,
and splitting lists/querysets into chunks.
"""

import re
from typing import List, Any, Optional, Callable, TypeVar

T = TypeVar('T')


def search_in_objects(
    objects: List[object],
    search_term: str,
    fields: List[str],
    ignore_case: bool = True,
) -> List[object]:
    """
    Search for objects containing a term in specified fields.

    Use case: Filter objects based on text search across multiple fields.

    Process:
    1. Extract nested attributes from objects using dot notation
    2. Compile regex pattern for search term
    3. Match pattern against each field value
    4. Return objects with at least one matching field

    Args:
        objects: List of objects to search
        search_term: Text to search for
        fields: List of field names (supports dot notation for nested attributes)
        ignore_case: Perform case-insensitive search

    Returns:
        List of matching objects
    """

    def get_nested_attr(obj: object, field: str, default: str = "") -> Any:
        """Extract nested attribute from object using dot notation."""
        parts: List[str] = field.split(".")
        for part in parts:
            try:
                obj = getattr(obj, part)
            except AttributeError:
                return default
        return obj

    flags: int = re.IGNORECASE if ignore_case else 0
    pattern: re.Pattern = re.compile(re.escape(search_term), flags)

    return [
        obj
        for obj in objects
        if any(pattern.search(str(get_nested_attr(obj, field))) for field in fields)
    ]


def get_param(params: dict, param_name: str, class_name: Callable) -> Optional[Any]:
    """
    Extract and convert parameter from dictionary.

    Use case: Safely extract and type-cast query parameters from request data.

    Args:
        params: Dictionary of parameters
        param_name: Name of parameter to extract
        class_name: Type/class to convert value to

    Returns:
        Converted parameter value, or None if not found or conversion fails
    """
    val: Any = params.get(param_name)
    if val is not None:
        try:
            return class_name(val)
        except ValueError:
            return None
    return None


def nsplit(lst: List[T], num_splits: int, current_number: int) -> List[T]:
    """
    Split list into equal parts and return specified chunk.

    Use case: Distribute work across multiple workers or processes.

    Process:
    1. Validate split index is within range
    2. Calculate split size with remainder distribution
    3. Generate splits ensuring even distribution
    4. Return requested split

    Args:
        lst: List to split
        num_splits: Number of splits to create
        current_number: Index of split to return (0-based)

    Returns:
        Requested split of the list, empty list if index out of range
    """
    if current_number < 0 or current_number >= num_splits:
        return []

    split_size: int = len(lst) // num_splits
    remainder: int = len(lst) % num_splits

    splits: List[List[T]] = []
    start_index: int = 0

    for i in range(num_splits):
        end_index: int = start_index + split_size + (1 if i < remainder else 0)
        splits.append(lst[start_index:end_index])
        start_index = end_index

    selected_part: List[T] = splits[current_number]
    return selected_part


def queryset_split(queryset: Any, num_splits: int, current_number: int) -> Any:
    """
    Split Django queryset into equal parts and return specified chunk.

    Use case: Distribute database query results across multiple workers efficiently.

    Process:
    1. Validate split index is within range
    2. Calculate total count and split size
    3. Determine start and end indices for requested split
    4. Return sliced queryset

    Args:
        queryset: Django queryset to split
        num_splits: Number of splits to create
        current_number: Index of split to return (0-based)

    Returns:
        Sliced queryset for requested split, empty queryset if index out of range
    """
    if current_number < 0 or current_number >= num_splits:
        return queryset.none()

    total_count: int = queryset.count()
    split_size: int = total_count // num_splits
    remainder: int = total_count % num_splits

    # Calculate start and end index for requested split
    start_index: int = current_number * split_size + min(current_number, remainder)
    end_index: int = start_index + split_size + (1 if current_number < remainder else 0)

    return queryset[start_index:end_index]
