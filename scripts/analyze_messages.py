import polars as pl
from polars import col
import polars.selectors as cs

pl.Config(
    set_fmt_str_lengths=45,
    set_tbl_cols=50,
    set_tbl_rows=50,
)


def main():
    df = (
        get_all_messages()
        .with_columns(
            text=col('text').str.replace('\n', ' ', n=-1).str.slice(0, 40)
        )
        .filter(
            col('finish_details').struct.field('type') == 'interrupted',
            col('end_turn') == True,
            # col('role') == 'assistant',
            # col('status') == 'in_progress',
            # col('content_type') != 'thoughts',
        )
        # .head(50)
    )
    print(df)


def get_all_messages() -> pl.DataFrame:

    df = (
        pl.read_parquet('2-conversations-clean-message-rows.parquet')
        .with_columns(
            create_time=pl.from_epoch('create_time'),
            update_time=pl.from_epoch('update_time'),
        )
        .pipe(remove_boring_columns)
        .drop(
            # 'convo_id',
            # 'id',
            'parent',
            # 'children',
            # 'role',
            # 'name',
            'author_metadata',
            # 'create_time',
            'update_time',
            # 'status',
            # 'end_turn',
            'weight',
            # 'recipient',
            'channel',
            # 'content_type',
            # 'text',
            'reasoning_status',
            'is_visually_hidden_from_conversation',
            'is_complete',
            'is_user_system_message',
            'user_context_message_data',
            'rebase_system_message',
            'rebase_developer_message',
            # 'model_slug',
            'requested_model_slug',
            'default_model_slug',
            'parent_id',
            'request_id',
            'timestamp_',
            'attachments',
            # 'finish_details',
            'pad',
            'targeted_reply',
            'selected_sources',
            'selected_github_repos',
            'serialization_metadata',
            'paragen_variants_info',
            'paragen_variant_choice',
            'caterpillar_selected_sources',
            'system_hints',
            'message_locale',
            'finished_duration_sec',
            'search_source',
            'client_reported_search_source',
            'search_display_string',
            'searched_display_string',
            'filter_out_for_training',
            'debug_sonic_thread_id',
            'augmented_paragen_prompt_label',
            'safe_urls',
            'search_queries',
            'sonic_classification_result',
            # 'thoughts',
            'source_analysis_msg_id',
            'language',
            'aggregate_result',
            'cite_metadata',
            'initial_text',
            'finished_text',
            'cloud_doc_urls',
            'command',
            'args',
            'kwargs',
            'invoked_plugin',
            'ada_visualizations',
            'canvas',
            'parts',
            'summary',
            'assets',
            'url',
            'domain',
            'title',
        )
    )
    return df


def remove_boring_columns(df: pl.DataFrame) -> pl.DataFrame:
    boring = (
        df.select(
            cs.string(include_categorical=True),
            cs.numeric(),
            cs.temporal(),
            cs.by_dtype(pl.Null, pl.Boolean),
        )
        .select(pl.all().cast(str).unique().count())
        .transpose(include_header=True)
        .filter(col('column_0') == 0)
    )
    names = boring['column'].to_list()
    return df.drop(names)


if __name__ == '__main__':
    main()
