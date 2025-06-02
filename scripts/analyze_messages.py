import json
import polars as pl
from polars import col
from model.conversation import Conversation

pl.Config(
    set_tbl_cols=100,
)


def main():
    with open('2-conversations-clean.json', 'r') as f:
        conversations = json.load(f)

    convos = [Conversation.model_validate(c) for c in conversations]

    rows: list[dict] = []
    for convo in convos:
        for message in convo.mapping.values():
            if message.role == 'root':
                continue
            dumped = {
                'id': message.id,
                'parent': message.parent,
                'children': message.children,
                **message.model_dump(
                    exclude={'id', 'parent', 'children', 'metadata', 'content'}
                ),
                **message.content.model_dump(),
            }
            rows.append(dumped)

    df = (
        pl.DataFrame(rows, infer_schema_length=None)
        .with_columns(
            create_time=pl.from_epoch('create_time'),
            update_time=pl.from_epoch('update_time'),
        )
        .drop(
            'id',
            'parent',
            'children',
            'author_metadata',
            'update_time',
            'status',
            'weight',
            'channel',
            'assets',
            'tether_id',
            'response_format_name',
        )
    )
    print(df)


if __name__ == '__main__':
    main()
