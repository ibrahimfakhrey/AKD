"""Verification service — AI image verification with pluggable backends."""
import random


class MockVerifier:
    """Always-approve verifier for development."""

    def verify(self, image_path, context=None):
        """Return a mock verification result."""
        confidence = round(random.uniform(0.75, 0.99), 2)
        return {
            'verified': False,
            'confidence': confidence,
            'labels': ['kindness', 'helping', 'community'],
            'verifier': 'mock',
            'details': 'Mock verifier — auto-approved for development.',
        }


class GoogleVisionVerifier:
    """Google Cloud Vision API verifier (stub — implement with real API key)."""

    def __init__(self, api_key=None):
        self.api_key = api_key

    def verify(self, image_path, context=None):
        # TODO: Implement real Google Vision API call
        return {
            'verified': False,
            'confidence': 0.0,
            'labels': [],
            'verifier': 'google_vision',
            'details': 'Google Vision verifier not yet configured.',
        }


def get_verifier(verifier_type='mock', **kwargs):
    """Factory function to get the appropriate verifier."""
    verifiers = {
        'mock': MockVerifier,
        'google_vision': GoogleVisionVerifier,
    }
    verifier_class = verifiers.get(verifier_type, MockVerifier)
    return verifier_class(**kwargs)
