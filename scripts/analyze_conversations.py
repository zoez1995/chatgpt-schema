import polars as pl
from polars import col

pl.Config(
    set_tbl_cols=100,
    set_tbl_rows=50,
)


def main():
    df = (
        pl.read_parquet('2-conversations-clean-convo-rows.parquet')
        .with_columns(
            create_time=pl.from_epoch('create_time'),
            update_time=pl.from_epoch('update_time'),
            title=col('title').replace('New chat', None),
        )
        .drop(
            # 'id',
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
            # Temp
            'safe_urls',
            'async_status',
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
        # -----
        # EXTRA
        # -----
        # .filter(col('model_slugs_used') == 'gpt-4o')
        .filter(
            # col('content_types').str.split(',').list.len() > 3,
            # col('tools_used').str.contains('python'),
            # col('title').str.contains('Performance'),
        )
        .sort('create_time', descending=True)
        .head(50)
    )

    print(df)


if __name__ == '__main__':
    main()
