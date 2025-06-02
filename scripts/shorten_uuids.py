import re
import json
from typing import Any


def main():
    with open('1-conversations-validated.json', 'r') as f:
        conversations = json.load(f)

    conversations = shorten_all_uuids_rec(conversations)

    with open('2-conversations-clean.json', 'w') as f:
        json.dump(conversations, f)


def shorten_all_uuids_rec(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            shorten_all_uuids_rec(k): shorten_all_uuids_rec(v) for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [shorten_all_uuids_rec(x) for x in obj]
    if isinstance(obj, tuple):
        return tuple(shorten_all_uuids_rec(x) for x in obj)
    if isinstance(obj, str) and is_uuid(obj):
        return shorten_uuid(obj)
    return obj


full_uuids_seen: set[str] = set()
shortened_uuids: set[str] = set()


def shorten_uuid(uuid: str) -> str:
    full_uuids_seen.add(uuid)
    shortened = uuid[-21:]
    shortened_uuids.add(shortened)
    return shortened


UUID_RE_LOWER = re.compile(
    r'^[0-9a-f]{8}-'
    r'[0-9a-f]{4}-'
    r'[0-9a-f]{4}-'
    r'[0-9a-f]{4}-'
    r'[0-9a-f]{12}$'
)
UUID_RE_UPPER = re.compile(
    r'^[0-9A-F]{8}-'
    r'[0-9A-F]{4}-'
    r'[0-9A-F]{4}-'
    r'[0-9A-F]{4}-'
    r'[0-9A-F]{12}$'
)


def is_uuid(s: str) -> bool:
    return bool(UUID_RE_LOWER.match(s)) or bool(UUID_RE_UPPER.match(s))


if __name__ == '__main__':
    main()
    assert len(full_uuids_seen) == len(shortened_uuids)
