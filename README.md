# ChatGPT Schema

Pydantic models to describe, with maximum strictness, the schema of a **ChatGPT data
export**'s `conversations.json`.

**Contributions are highly encouraged, from anyone!**

## Purpose

This project exists solely for research purposes, to help the community understand how
ChatGPT structures its app data.

The Pydantic models for ChatGPT conversations are designed to be as strict and precise
as possible.

Consequently, you'll find silly or unconventional type definitions in this project...

```py
# model/assistant.py
class Author(Model):
    role: Literal['assistant']
    name: None
    metadata: Literal[{}]  # type:ignore
```

Annotations like `name: None` and `metadata: Literal[{}]` appear useless, but they
are important to us. They tell us that, for everyone who has used this project so far,
`name` is always null, and `metadata` is always an empty object, for every assistant
message encountered in the data. This indicates that OpenAI probably isn't using these
fields yet. If they do, we'll know immediately, because Pydantic's validation will break.
(Note: yes, Pydantic *will* enforce `Literal[{}]` even though this is considered invalid
by static type checkers)

# Getting Started

Clone this project, and `uv sync`.

Export your ChatGPT data. Place your `conversations.json` in the root of this project.

Run `scripts/parse_and_validate.py` to process your conversations, see the output, and
identify any validation errors.

Based on Pydantic's descriptive error messages (if any), update the models as
needed. When you're done, we would greatly appreciate a pull request!

### Updating the models

#### Type Annotations & Strictness

When updating the models, the general rule of thumb is to be as strict as possible. For
example, if a new field named `text` appears somewhere in the data, you might be _tempted_
to annotate it as `str`. But if all the values are null, then the annotation should be
`None` until proven otherwise.

#### Naming Stuff

For simplicity and consistency across the project, your model names do not need to be
globally unique. For example, each role's module has its own `Author` model, rather than
`AssistantAuthor` and `UserAuthor`, etc. The intention is to import and use these
modules as namespaces, like `assistant.Author`, `user.Author`, etc.
