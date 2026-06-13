"""
Data generation utilities.

This module provides functions for generating unique identifiers and n-grams for text search.
"""

import random
import time
from typing import List, Set


def generate_unique_number() -> str:
    """
    Generate a unique 20-digit number based on timestamp and random value.

    Use case: Create unique identifiers for transactions, records, or objects.

    Process:
    1. Get current timestamp with microsecond precision
    2. Generate random 2-digit number
    3. Combine to create 20-digit unique identifier

    Returns:
        20-digit unique number as string
    """
    time_stamp: int = round(time.time() * 100000000)
    random_num: int = random.randint(11, 99)
    return f"{time_stamp}{random_num}"


def generate_ngrams(text: str, min_length: int = 2) -> List[str]:
    """
    Generate all possible substrings (n-grams) from text for fuzzy search.

    Use case: Create searchable tokens for partial text matching in encrypted fields.

    Process:
    1. Normalize text to lowercase
    2. Add full text as n-gram
    3. Extract and add individual words
    4. Generate character-level n-grams for each word
    5. Return unique list of all n-grams

    Args:
        text: Input text to generate n-grams from
        min_length: Minimum length of n-grams to generate

    Returns:
        List of unique n-gram strings
    """
    text = text.lower().strip()
    ngrams: Set[str] = set()

    # Add full text
    ngrams.add(text)

    # Add words
    words: List[str] = text.split()
    for word in words:
        if len(word) >= min_length:
            ngrams.add(word)

    # Add character n-grams for each word
    for word in words:
        for i in range(len(word)):
            for j in range(i + min_length, len(word) + 1):
                substring: str = word[i:j]
                if len(substring) >= min_length:
                    ngrams.add(substring)

    return list(ngrams)
