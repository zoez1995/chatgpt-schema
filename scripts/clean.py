import json
from model.conversation import Conversation
from sort_mapping import sort_mappings
from shorten_uuids import shorten_all_uuids_rec

models = [
    'o3-mini',
    'gpt-4o-mini',
    'gpt-4o',
    'o1-preview',
    'o3',
    'o4-mini-high',
    'gpt-4',
    'gpt-4-1',
    'o3-mini-high',
    'gpt-4-5',
    'text-davinci-002-render-sha',
    'o1-mini',
    'o1',
]


def main():
    with open('1-conversations-validated.json', 'r') as f:
        conversations = json.load(f)

    conversations = shorten_all_uuids_rec(conversations)

    convos = [Conversation.model_validate(c) for c in conversations]

    convos = sort_mappings(convos)

    convos = list(sorted(convos, key=lambda c: c.create_time, reverse=True))
    result = [c.model_dump() for c in convos]
    print(json.dumps(result[0], indent=2))
    with open('2-conversations-clean.json', 'w') as f:
        json.dump(result, f)


if __name__ == '__main__':
    main()
