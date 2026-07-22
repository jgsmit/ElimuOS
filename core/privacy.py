import re

EMAIL_RE = re.compile(r'(?P<first>[^@\s])[^@\s]*(?P<last>[^@\s])@(?P<domain>[^@\s]+)')
PHONE_RE = re.compile(r'(?<!\d)(?:\+?\d[\d\s().-]{6,}\d)(?!\d)')
SENSITIVE_KEYS = {'password', 'token', 'secret', 'api_key', 'authorization'}


def redact_value(value):
    if value is None:
        return None
    text = str(value)
    text = EMAIL_RE.sub(lambda match: f"{match.group('first')}***{match.group('last')}@{match.group('domain')}", text)
    text = PHONE_RE.sub('***REDACTED_PHONE***', text)
    return text


def redact_mapping(data):
    redacted = {}
    for key, value in data.items():
        if key.lower() in SENSITIVE_KEYS:
            redacted[key] = '***REDACTED***'
        elif isinstance(value, dict):
            redacted[key] = redact_mapping(value)
        else:
            redacted[key] = redact_value(value)
    return redacted
