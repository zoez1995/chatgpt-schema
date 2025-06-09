from __future__ import annotations
import json
import black
from typing import Any, Literal as Lit, Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator, Discriminator


class Model(BaseModel):
    model_config = ConfigDict(extra='forbid')


def main():
    with open('stream-raw.txt', 'r') as f:
        text = f.read()

    lines = [line.strip() for line in text.splitlines()]

    chunks: list[list[str]] = [[]]
    for line in lines:
        if line:
            chunks[-1].append(line)
        else:
            chunks.append([])

    if chunks[0][0] == 'event: delta_encoding':
        chunks.pop(0)

    def keep_chunk(chunk: list[str]) -> bool:
        if not chunk:
            return False
        if len(chunk) == 1:
            value = chunk[0]
            if value.startswith(': '):
                return False
            if value == 'data: [DONE]':
                return False
        return True

    chunks = [c for c in chunks if keep_chunk(c)]

    class Item(Model):
        key: str
        value: str

    def unpack_item(line: str) -> Item:
        idx = line.index(': ')
        return Item(key=line[:idx], value=line[idx + 2 :])

    unpacked_chunks: list[list[Item]] = [
        [unpack_item(line) for line in chunk] for chunk in chunks
    ]

    class TempDeltaEvent(Model):
        event: Lit['delta']
        data: TempDelta

    class TempEvents(Model):
        events: list[Annotated[TempDeltaEvent | MessageEvent, Discriminator('event')]]

    class TempTest(Model):
        test: Annotated[TempDeltaEvent | MessageEvent, Discriminator('event')]

    class TempDelta(Model):
        p: str | None = None
        o: Lit['add', 'replace', 'append', 'patch'] | None = None
        v: Any
        c: int | None = None

    raw_events = [{item.key: item.value for item in chunk} for chunk in unpacked_chunks]
    for event in raw_events:
        if 'data' in event:
            event['data'] = json.loads(event['data'])
        if 'event' not in event:
            event['event'] = 'message'

        try:
            TempTest.model_validate({'test': event})
        except Exception as e:
            print(json.dumps(event, indent=4))
            raise e

    events = TempEvents.model_validate({'events': raw_events})

    temp_deltas: list[TempDelta] = [e.data for e in events.events if e.event == 'delta']

    curr_p = temp_deltas[0].p
    curr_o = temp_deltas[0].o
    for delta in temp_deltas:
        if delta.p is not None:
            curr_p = delta.p
        if delta.o is not None:
            curr_o = delta.o
        delta.p = curr_p
        delta.o = curr_o

    # deltas_with_patches: list[Delta] = deltas
    # deltas = []
    # for delta in deltas_with_patches:
    #     if delta.o != 'patch':
    #         deltas.append(delta)
    #     else:
    #         assert delta.p == '' and isinstance(delta.v, list)
    #         deltas.extend([Delta.model_validate(p) for p in delta.v])

    class Deltas(Model):
        deltas: list[Delta]

    deltas = Deltas.model_validate({'deltas': [d.model_dump(exclude_unset=True) for d in temp_deltas]})

    print(
        black.format_str(
            json.dumps([d.model_dump() for d in deltas.deltas]), mode=black.Mode()
        )
    )


class MessageEvent(Model):
    event: Lit['message']
    data: dict[str, Any]


class DeltaEvent(Model):
    event: Lit['delta']
    data: Delta


type Event = Annotated[DeltaEvent | MessageEvent, Discriminator('event')]


class Events(Model):
    events: list[Event]


type Delta = Annotated[
    OperationDelta | PatchDelta, Discriminator('o')
]

class AddDelta(Model):
    p: str
    o: Lit['add']
    v: Any
    c: int


class AppendDelta(Model):
    p: str
    o: Lit['append']
    v: str | list[Any] | dict = Field(min_length=1)


class ReplaceDelta(Model):
    p: str
    o: Lit['replace']
    v: Any


type OperationDelta = Annotated[
    AddDelta | AppendDelta | ReplaceDelta, Discriminator('o')
]

class PatchDelta(Model):
    p: str
    o: Lit['patch']
    v: list[OperationDelta] = Field(min_length=1)


if __name__ == '__main__':
    main()
