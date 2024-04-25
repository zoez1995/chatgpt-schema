# ChatGPT Schema

Pydantic models to describe, with maximum strictness, the schema of a **ChatGPT data
export**'s `conversations.json`.

**Contributions are _highly_ encouraged, from anyone!**

## Purpose

This project exists for research purposes, and is **not** intended for production use.
The Pydantic models for ChatGPT conversations are designed to be as strict and precise
as possible, and should break as soon as the schema changes.

Consequently, you'll find some unconventional practices in this project, such as:
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

Clone this project, and run `pip install -r requirements.txt` to install dependencies.

Run a ChatGPT export. Place your `conversations.json` in the root of this project.

Take a look at the code (particularly `config` and `parse_and_validate`) to understand
what's going on.

Run `parse_and_validate.py` to process your conversations, see the output, and
identify any validation errors.

Based on Pydantic's descriptive error messages (if any), update the models as
needed. When you're done, we would greatly appreciate a pull request!

# Contributions

Since everyone's data is different, contributions are _necessary_ for this project to be
effective. If you encounter a validation error, this means either the schema has changed
(and you're the first to notice), or your data is different from what we've seen so far.

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

### Code Style, Formatting, and Linting

Let's be honest: this is a simple project. We don't care what you use. We'd rather you
push messy code than not push at all.

But for transparency:
- **Formatter**: `black`, with `--skip-string-normalization` because single quotes
   are better :)
- **Static Type Checking**: `pyright`