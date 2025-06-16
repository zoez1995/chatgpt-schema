"""
This script validates all the data in `conversations.json` against the `Conversation`
pydantic model.

Because Conversation is deeply nested and has lots of type unions, we can't just
do this:

    for c in conversations:
        try:
            Conversation(**c)

If the validation error is deep enough, you'll get useless error messages. So we need
a more granular approach.

---

Our current approach is to validate each message type (UserMessage, SystemMessage, etc.)
first, and then validate Conversation last.
This is mostly effective, but it's not perfect. `ToolMessage` in particular is very
complex, with at least 6 different content types. All these unions make the validation
errors less reliable. This could be improved by breaking up the values of `content` into
groups based on `content.content_type`, and validating each group separately against its
respective model.
The `metadata` field `ToolMessage` is also highly complex and messy. It doesn't have its
own key to identify its type. So breaking this field up into a union of different types
might require a more hacky approach, like grouping them based on the node's `author.name`
or `content.content_type`.
"""

import re
import pickle
import json
from typing import Any
import pydantic
from pydantic import BaseModel
from model.conversation import Conversation, Node

# Show the convo that failed validation
DISPLAY_FAILED_RECORD = True


def main():
    with open('conversations.json', 'r') as f:
        raw_convos = json.load(f)

    raw_convos = shorten_all_uuids(raw_convos, last_chars=16, test=True)

    # Since all messages are valid, now validate the conversations
    convos = validate_model(Conversation, raw_convos)
    print(f'Conversation is valid for all {len(convos)} records.')

    for convo in convos:
        sort_mapping(convo)

    convos = list(sorted(convos, key=lambda c: c.create_time, reverse=True))

    with open('1-conversations-clean.pkl', 'wb') as f:
        pickle.dump(convos, f)


def validate_model[T: BaseModel](model: type[T], documents: list[dict]) -> list[T]:
    """
    Validates each item in `documents` against `model`.
    """

    results: list[T] = []
    for index, doc in enumerate(documents):
        try:
            results.append(model(**doc))
        except pydantic.ValidationError as e:
            if DISPLAY_FAILED_RECORD:
                print('\n\n\n\n\n' + json.dumps(doc, indent=4) + '\n')
            print(format_error(str(e)))
            print(f'\nFailed on {model.__name__} {index} / {len(documents)}')
            quit()

    return results


def format_error(err: str) -> str:
    "Tweaks, such as removing unnecessary URL lines from the error message"
    lines = err.split('\n')
    # Put empty line before error details
    lines = [lines[0], '', *lines[1:]]
    # Remove all URL lines
    lines = [l for l in lines if 'https://errors.pydantic.dev' not in l]
    return '\n'.join(lines)


def shorten_all_uuids(data: Any, last_chars: int, test: bool = False) -> Any:
    def shorten_all_uuids_rec(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                shorten_all_uuids_rec(k): shorten_all_uuids_rec(v)
                for k, v in obj.items()
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

    if test:

        def shorten_uuid(uuid: str) -> str:
            full_uuids_seen.add(uuid)
            shortened = uuid[-last_chars:]
            shortened_uuids.add(shortened)
            return shortened
    else:

        def shorten_uuid(uuid: str) -> str:
            return uuid[-last_chars:]

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

    result = shorten_all_uuids_rec(data)
    assert len(full_uuids_seen) == len(shortened_uuids)
    return result


def sort_mapping(convo: Conversation) -> None:
    num_messages = len(convo.mapping)
    sorted_nodes: list[Node] = []

    def add_node(id: str) -> None:
        node = convo.mapping[id]
        sorted_nodes.append(node)
        for child in node.children:
            add_node(child)

    root = convo.get_root_node()
    add_node(root.id)

    assert num_messages == len(sorted_nodes)

    convo.mapping = {node.id: node for node in sorted_nodes}


if __name__ == '__main__':
    main()
