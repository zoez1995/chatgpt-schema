from datetime import datetime
import pickle
import polars as pl
from polars import col
import polars.selectors as cs
from model.conversation import Conversation, Message
from analyze_messages import get_all_messages

pl.Config(
    set_tbl_cols=100,
    set_tbl_rows=70,
    set_fmt_str_lengths=45,
    set_fmt_table_cell_list_len=1,
    set_tbl_hide_column_data_types=True,
    set_tbl_hide_dataframe_shape=True,
)
EMPTY = '–'

run_convo_ids: list[str] = [
    # 'da8-46b86e43bd71',  # o3, single "Does chartjs accept css variables as color values?"
    # '5e6-96029a4e15e7',  # 4o, double "Does zillow only list property in the US?"
    # '845-ca07f82cecb4',  # o3, single that uses 5 content types
    # '884-4e70deb283fc',  # 4o, quad from 2024 that uses browser and code interpreter
    # 'b41-0092ac161c08',  # o3, single with really long search chain
    # 'd35-afb3de7a366c',  # o3, double with no tools, just thought. Short
    # '897-82c9b349baa0',  # gpt4, 8x with bio and browser
    # '337-cdbac456537d',  # gpt4, 3x code interpreter workflow
    # '900-a0a852ce869d',
    # 'b85-54fd482a9c5a',
    '0a5-462f5694886a',
]
active_path: bool = True


def main():
    with open('1-conversations-clean.pkl', 'rb') as f:
        convos = pickle.load(f)

    df_all_messages = get_all_messages()

    convos_map = {c.id: c for c in convos}

    outputs = [
        analyze_convo(convos_map[convo_id], df_all_messages)
        for convo_id in run_convo_ids
    ]
    result = '\n\n\n\n'.join(outputs)
    print(result)


def analyze_convo(convo: Conversation, df_all_messages: pl.DataFrame) -> str:
    messages: list[Message] = []
    if not active_path:
        for message in convo.mapping.values():
            if message.role == 'root':
                continue
            messages.append(message)
    else:
        current_node: str | None = convo.current_node
        while current_node:
            message = convo.mapping[current_node]
            current_node = message.parent
            if message.role != 'root':
                messages.insert(0, message)

    # dumped = [m.model_dump(exclude={'metadata'}) for m in messages]
    # print(json.dumps(dumped, indent=2))
    # quit()

    # dumped = [m.model_dump() for m in messages]
    # for msg in dumped:
    #     metadata = msg['metadata']
    #     metadata.pop('content_references', None)
    #     metadata.pop('citations', None)
    #     metadata.pop('search_result_groups', None)
    #     metadata.pop('image_results', None)
    # print(json.dumps(dumped, indent=2))
    # quit()
    message_ids = [m.id for m in messages]

    df = (
        df_all_messages.filter(
            col('convo_id') == convo.id,
            col('id').is_in(message_ids),
            col('role') != 'system',
        )
        # .pipe(lambda df: print(df) or quit())
        .drop('convo_id', 'id', 'children')
        .with_columns(
            text=col('text').str.replace('\n', ' ', n=-1).str.replace(' +', ' ', n=-1),
            end_turn=col('end_turn').cast(str).replace('false', None),
            content_type=col('content_type')
            .replace('text', None)
            .replace('tether_browsing_display', 'tether_results'),
            recipient=col('recipient').replace('all', None),
        )
        .with_columns(text=col('text').str.slice(0, 40))
    )
    result = create_summary(convo, df)
    return result


def create_summary(
    convo: Conversation,
    df: pl.DataFrame,
) -> str:
    def get_uniques(df: pl.DataFrame, col_name: str) -> list[str]:
        return df.select(col(col_name).unique().drop_nulls().sort())[col_name].to_list()

    if len(df.filter(col('thoughts').is_not_null())) == 0:
        df = df.drop('thoughts')

    id = convo.id
    date = datetime.fromtimestamp(convo.create_time).date().isoformat()
    title = convo.title
    num_turns = len(df.filter(col('end_turn') == 'true'))
    num_messages = len(df)
    models = get_uniques(df, 'model_slug')
    if len(models) <= 1:
        df = df.drop('model_slug')
    tools = get_uniques(df, 'name')
    content_types = get_uniques(df, 'content_type')
    models_str = ', '.join(models)
    tools_str = ', '.join(tools)
    content_types_str = ', '.join(content_types)
    pretty_df = df.with_columns(
        cs.string().replace(None, EMPTY).replace('', EMPTY),
    )
    pretty_df = str(pretty_df)
    pretty_df = pretty_df.replace(' null  ', f' {EMPTY[0]}     ')

    highlight_rows = [
        ['', ''],
        ['Summary', f'Used `{models_str}` on `{date}` in convo `{id}`'],
        ['Size', f'{num_turns} turns, {num_messages} messages'],
        ['Tools', tools_str],
        ['Content Types', content_types_str],
        ['Topic', title],
    ]
    highlight_table = markdown_table(highlight_rows)
    return f"""
{highlight_table}


<details>
    <summary>Details</summary>

```
{pretty_df}
```

</details>

---
    """.strip()


def markdown_table(rows: list[list]) -> str:
    col_widths = [max([len(row[i]) for row in rows]) for i in range(len(rows[0]))]
    rows = [[f'{f"{val}":<{col_widths[i]}}' for i, val in enumerate(r)] for r in rows]
    rows.insert(1, ['-' * width for width in col_widths])
    return '\n'.join([f'| {" | ".join(row)} |' for row in rows])


if __name__ == '__main__':
    main()
