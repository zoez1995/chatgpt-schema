import pickle
import polars as pl
from polars.dependencies import pickle
from model.conversation import Conversation, Message

pl.Config(
    set_tbl_cols=8,
    set_tbl_rows=10,
)


def main():
    with open('1-conversations-clean.pkl', 'rb') as f:
        convos: list[Conversation] = pickle.load(f)

    messages_rows = get_all_message_rows(convos)
    messages_df = pl.DataFrame(messages_rows, infer_schema_length=None)
    print(messages_df)
    messages_df.write_parquet('2-conversations-clean-message-rows.parquet')

    convos_rows = get_all_convo_rows(convos)
    convos_df = pl.DataFrame(convos_rows, infer_schema_length=None)
    print(convos_df)
    convos_df.write_parquet('2-conversations-clean-convo-rows.parquet')


def get_all_message_rows(convos: list[Conversation]) -> list[dict]:
    rows: list[dict] = []
    for convo in convos:
        for message in convo.mapping.values():
            if message.role == 'root':
                continue
            dumped = {
                'convo_id': convo.id,
                'id': message.id,
                'parent': message.parent,
                'children': message.children,
                **message.model_dump(
                    exclude={'id', 'parent', 'children', 'content', 'metadata'}
                ),
                **message.content.model_dump(),
                **message.metadata.model_dump(
                    exclude={
                        'content_references',
                        'citations',
                        'search_result_groups',
                        'image_results',
                    }
                ),
            }
            rows.append(dumped)

    return rows


def get_all_convo_rows(convos: list[Conversation]) -> list[dict]:
    rows: list[dict] = []
    for convo in convos:
        row = convo.model_dump(exclude={'mapping'})
        messages: list[Message] = [
            m for m in convo.mapping.values() if m.role != 'root'
        ]
        row['message_count'] = len(messages)

        message_count = 0
        turn_count = 0
        model_slugs: set[str] = set()
        tools_used: set[str] = set()
        content_types: set[str] = set()
        for msg in messages:
            if msg.role not in {'system', 'root'}:
                message_count += 1
            content_types.add(msg.content.content_type)
            if msg.role == 'user':
                continue
            if msg.metadata.model_slug:
                model_slugs.add(msg.metadata.model_slug)
            if msg.role == 'tool':
                tools_used.add(msg.name)
            if msg.role == 'assistant' and msg.end_turn:
                turn_count += 1

        row['turn_count'] = turn_count
        row['model_slugs_used'] = ','.join(sorted(model_slugs)) or None
        row['tools_used'] = ','.join(sorted(tools_used)) or None
        row['content_types'] = ','.join(sorted(content_types)) or None

        rows.append(row)

    return rows


if __name__ == '__main__':
    main()
