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

import json
import pydantic
from pydantic import BaseModel
from model.conversation import Conversation
from model.user import UserMessage
from model.system import SystemMessage
from model.assistant import AssistantMessage
from model.tool import ToolMessage

PATH_TO_CONVERSATIONS = 'conversations.json'
# Set DISPLAY_FAILED_RECORD to False to disable printing the failed record and only see
# the error message.
DISPLAY_FAILED_RECORD = True


def main():
    with open(PATH_TO_CONVERSATIONS, 'r') as f:
        conversations = json.load(f)

    messages: dict[str, tuple[type[BaseModel], list[dict]]] = dict(
        system=(SystemMessage, []),
        user=(UserMessage, []),
        assistant=(AssistantMessage, []),
        tool=(ToolMessage, []),
    )

    # Sort the messages into their respective lists by role
    for c in conversations:
        for _, node in c['mapping'].items():
            msg = node['message']
            # Root nodes have no message
            if not msg:
                continue

            role = msg['author']['role']
            # Add the message to the list for the role
            messages[role][1].append(msg)

    # One role at a time, in order, validate all messages for that role
    for role, (model, messages_for_role) in messages.items():
        validate_model(model, messages_for_role)
        print(f'{model.__name__} is valid for all {len(messages_for_role)} records.')

    # Since all messages are valid, now validate the conversations
    validate_model(Conversation, conversations)
    print(f'Conversation is valid for all {len(conversations)} records.')


def validate_model(model: type[BaseModel], documents: list[dict]):
    """
    Validates each item in `documents` against `model`.
    """

    for index, doc in enumerate(documents):
        try:
            model(**doc)
        except pydantic.ValidationError as e:
            if DISPLAY_FAILED_RECORD:
                print('\n\n\n\n\n' + json.dumps(doc, indent=4) + '\n')
            print(format_error(str(e)))
            print(f'\nFailed on {model.__name__} {index} / {len(documents)}')
            quit()


def format_error(err: str) -> str:
    "Tweaks, such as removing unnecessary URL lines from the error message"
    lines = err.split('\n')
    # Put empty line before error details
    lines = [lines[0], '', *lines[1:]]
    # Remove all URL lines
    lines = [l for l in lines if 'https://errors.pydantic.dev' not in l]
    return '\n'.join(lines)


if __name__ == '__main__':
    main()
