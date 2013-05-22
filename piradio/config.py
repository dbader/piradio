import json
import re


def strip_comments(text):
    """Return `text` with // and /**/ comments removed.
    Also handles nesting and ignores comments that appear within
    double-quoted strings.
    Originally from: http://stackoverflow.com/q/241327
    """
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return ""
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)


def load_config(path):
    with open(path) as f:
        text = f.read()
        return json.loads(strip_comments(text))


def get(key, default_value=None):
    return CONFIG.get(key, default_value)

CONFIG = load_config('config.json')
