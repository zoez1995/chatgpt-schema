import json
from model.conversation import Conversation, Node


def main():
    with open('1-conversations-validated.json', 'r') as f:
        conversations = json.load(f)

    convos = [Conversation.model_validate(c) for c in conversations]

    convos = sort_mappings(convos)

    result = [c.model_dump() for c in convos]
    with open('2-conversations-clean.json', 'w') as f:
        json.dump(result, f)


def sort_mappings(convos: list[Conversation]) -> list[Conversation]:
    return [sort_mapping(c) for c in convos]


def sort_mapping(convo: Conversation) -> Conversation:
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

    convo.mapping = {
        node.id: node for node in sorted_nodes
    }
    return convo


def move_root_to_top(convos: list[Conversation]) -> list[Conversation]:
    """
    Move the root node to the top of the conversation.
    """
    for convo in convos:
        roots = []
        root_idx = 100
        for idx, node in enumerate(convo.mapping.values()):
            if node.parent is None:
                roots.append(node)
                root_idx = idx

        assert len(roots) == 1
        root = roots[0]
        if root_idx != 0:
            del convo.mapping[root.id]
            convo.mapping = {root.id: root, **convo.mapping}

    return convos


if __name__ == '__main__':
    main()
