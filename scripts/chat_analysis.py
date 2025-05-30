import json
from typing import Any, Self
import tiktoken
from dataclasses import dataclass
from model.conversation import Conversation, Message


def main():
    with open('conversations.json') as f:
        data = json.load(f)

    # create a list of conversation history from the raw data
    convo_history = [Conversation(**obj) for obj in data]

    # create a list of sub conversations from the conversation history
    sub_convo = []
    for convo in convo_history:
        sub_convo.extend(sub_converstaions(convo))

    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0
    num_messages = 0

    for item in sub_convo:
        input_token, output_token, total_token = token_consumption_per_chat(
            item, 'gpt-4'
        )
        total_input_tokens += input_token
        total_output_tokens += output_token
        total_tokens += total_token
        num_messages += len(item)

    price = calculate_token_consumption(
        total_input_tokens, total_output_tokens, 'gpt-4'
    )

    # usage summary
    print(f'Total number of conversations: {len(convo_history)}')
    print(f'Total number of messages: {num_messages}')
    print(f'Total input tokens: {total_input_tokens}')
    print(f'Total output tokens: {total_output_tokens}')
    print(f'Total tokens: {total_tokens}')
    print(f'OpenAI API Pricing Equivalent: $ {round(price, 2)}')


@dataclass
class MessageContent:
    role: str
    content: list[str]

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any]) -> Self:
        role = mapping.get('message', {}).get('author', {}).get('role', None)
        content = mapping.get('message', {}).get('content', {}).get('parts', [''])
        return cls(role, content)


@dataclass
class ConversationHistory:
    title: str
    id_: str
    messages: list[MessageContent]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        title = data['title']
        id_ = data['id']
        messages = [
            MessageContent.from_mapping(value)
            for key, value in data['mapping'].items()
            if value.get('message')
        ]
        return cls(title, id_, messages)

    def add_message(self, message: MessageContent):
        self.messages.append(message)


def message_to_string(message: Message) -> str:
    """
    Handle different message types and return the message content as a string.
    Note that this function doesn't handle the case where the message is a
    image content. Usually, the content is stored in node.message.content.parts
    in a list[str] format, so we only need to handle when it's not the case.

    Args:
        node (MessageNode): the node to extract the message content from
    Returns:
        str: the message content as a string
    """
    content = message.content

    if content.content_type == 'code':
        return content.text

    if content.content_type == 'execution_output':
        return content.text

    if content.content_type == 'system_error':
        return content.text

    # handle for user message
    if content.content_type == 'text':
        return ' '.join(content.parts)

    if content.content_type == 'multimodal_text':
        str_parts = [p for p in content.parts if isinstance(p, str)]
        return ' '.join(str_parts)

    if content.content_type == 'tether_browsing_display':
        return content.result

    return ''


def sub_converstaions(conversation: Conversation) -> list:
    """
    Extract the sub-conversations from the conversation tree. The token
    consumption is calculated based on the sub-conversations. From the
    root node, traverse the tree using depth-first search and construct
    all sub-conversations from root to leaf nodes.

    Args:
        node (Conversation): the root node of the conversation tree
    Returns:
        list: a list of sub-conversations
    """

    def dfs(conversation, node_id, current_path, results):
        current_node = conversation.mapping[node_id]

        # Append the current node's message to the path
        current_path.append(current_node)

        # If the current node is a leaf node, append the current_path to results
        if not current_node.children:
            results.append(current_path.copy())
        else:
            # Recurse for each child
            for child in current_node.children:
                dfs(conversation, child, current_path, results)

        # Remove the last node from current_path to backtrack as we return from recursion
        current_path.pop()

    results = []
    for node in conversation.mapping.values():
        # Start DFS from the root node
        if node.parent is None and node.message is None:
            for child in node.children:
                dfs(conversation, child, [], results)
    return results


def token_consumption_per_chat(conversation: list, model: str) -> list:
    # model args: gpt-4, gpt-3.5-turbo, text-embedding-ada-002, text-embedding-3-small, text-embedding-3-large
    encoding = tiktoken.encoding_for_model(model)
    input_tokens = 0
    output_tokens = 0
    total_net_tokens = 0
    total_tokens = 0

    for message in conversation:
        text = message_to_string(message)
        role = message.message.author.role
        num_tokens = len(encoding.encode(text))
        total_net_tokens += num_tokens
        if role != 'user' and role != 'tool':
            output_tokens += num_tokens
        else:
            input_tokens += total_net_tokens

    total_tokens = input_tokens + output_tokens
    return [input_tokens, output_tokens, total_tokens]


def calculate_token_consumption(
    input_tokens: float, output_tokens: float, model: str
) -> float:
    if model == 'gpt-4':
        return input_tokens / 1000 * 0.03 + output_tokens / 1000 * 0.06
    if model == 'gpt-3.5-turbo':
        return input_tokens / 1000 * 0.0005 + output_tokens / 1000 * 0.0015
    return input_tokens / 1000 * 0.0005 + output_tokens / 1000 * 0.0015
