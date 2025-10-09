# backend/model_utils.py
import re
import math
from urllib.parse import urlparse

SUSPICIOUS_TOKENS = [
    'login','secure','verify','update','bank','account','confirm','pay','signin','webscr','auth'
]

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    entropy = 0.0
    L = len(s)
    for v in freq.values():
        p = v / L
        entropy -= p * math.log2(p)
    return entropy

def extract_features_from_url(url: str) -> dict:
    u = url.strip()
    if not re.match(r'^https?://', u, re.I):
        u = 'http://' + u
    try:
        p = urlparse(u)
    except Exception:
        p = None

    host = p.hostname if p else ''
    path = (p.path or '') + (p.query or '')
    features = {}

    # length features
    features['len_url'] = len(u)
    features['len_host'] = len(host or '')
    features['num_dots'] = (host or '').count('.')

    # tokens & flags
    features['has_at'] = 1 if '@' in u else 0
    features['has_ip'] = 1 if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', host or '') else 0
    features['susp_token'] = 0
    for t in SUSPICIOUS_TOKENS:
        if t in (host or '').lower() or t in path.lower():
            features['susp_token'] = 1
            break

    # entropy and punctuation
    features['host_entropy'] = shannon_entropy(host or '')
    features['num_special'] = len(re.findall(r'[^A-Za-z0-9\.\-]', u))
    features['has_punycode'] = 1 if (host or '').startswith('xn--') else 0
    features['num_path_segments'] = len([seg for seg in (p.path or '').split('/') if seg]) if p else 0

    # small derived flags
    features['long_url'] = 1 if features['len_url'] > 75 else 0

    return features
