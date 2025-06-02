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

# Show the convo that failed validation
DISPLAY_FAILED_RECORD = True


def main():
    with open('conversations.json', 'r') as f:
        conversations = json.load(f)

    # Since all messages are valid, now validate the conversations
    validate_model(Conversation, conversations)
    print(f'Conversation is valid for all {len(conversations)} records.')

    result = [Conversation.model_validate(c).model_dump() for c in conversations]
    with open('1-conversations-validated.json', 'w') as f:
        json.dump(result, f)


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
