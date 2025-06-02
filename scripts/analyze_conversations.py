import json
import polars as pl
from polars import col, lit
from model.conversation import Conversation

pl.Config(
    set_tbl_cols=100,
)


def main():
    with open('2-conversations-clean.json', 'r') as f:
        conversations = json.load(f)

    convos = [Conversation.model_validate(c) for c in conversations]

    convo_rows: list[dict] = []
    for convo in convos:
        row = convo.model_dump(exclude={'mapping'})
        messages = list(convo.mapping.values())
        row['message_count'] = len(messages)

        model_slugs: set[str] = set()
        tools_used: set[str] = set()
        content_types: set[str] = set()
        for msg in messages:
            if msg.parent is None:
                continue
            content_types.add(msg.content.content_type)
            if msg.role == 'user':
                continue
            if msg.metadata.model_slug:
                model_slugs.add(msg.metadata.model_slug)
            if msg.role == 'tool':
                tools_used.add(msg.name)

        row['model_slugs_used'] = ','.join(sorted(model_slugs)) or None
        row['tools_used'] = ','.join(sorted(tools_used)) or None
        row['content_types'] = ','.join(sorted(content_types)) or None

        convo_rows.append(row)

    df = (
        pl.DataFrame(convo_rows, infer_schema_length=None)
        .with_columns(
            create_time=pl.from_epoch('create_time'),
            update_time=pl.from_epoch('update_time'),
            title=col('title').replace('New chat', None),
        )
        .drop(
            'id',
            'update_time',
            'current_node',
            'is_archived',
            'is_starred',
            'conversation_origin',
            'voice',
            'is_do_not_remember',
            'memory_scope',
            'moderation_results',
            'blocked_urls',
            'conversation_id',
        )
        # Remove custom GPT convos, since there's so few for me
        .filter(col('conversation_template_id').is_null())
        .drop(
            'conversation_template_id',
            'gizmo_id',
            'gizmo_type',
        )
        .with_columns(
            col('disabled_tool_ids').list.join(',').replace('', None)
        )
        # Remove 3rd party plugin convos since there's so few, and they're old
        .filter(col('plugin_ids').is_null())
        .drop('plugin_ids')
    )

    print(df)


if __name__ == '__main__':
    main()
