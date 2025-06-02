import json
import polars as pl
from model.conversation import Conversation

pl.Config(
    set_tbl_cols=100,
)

convo_id_or_idx = 0


def main():
    with open('2-conversations-clean.json', 'r') as f:
        conversations = json.load(f)

    convos = [Conversation.model_validate(c) for c in conversations]

    if isinstance(convo_id_or_idx, int):
        convo = convos[convo_id_or_idx]
    else:
        for c in convos:
            if c.id == convo_id_or_idx:
                convo = c
                break
        else:
            raise ValueError(f'Conversation with ID {convo_id_or_idx} not found.')

    messages = list(convo.mapping.values())
    dumped = [m.model_dump(exclude={'metadata'}) for m in messages]

    df = pl.DataFrame(dumped, infer_schema_length=None)
    print(df)


if __name__ == '__main__':
    main()
