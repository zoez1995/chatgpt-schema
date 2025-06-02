"""
Constants and configurations for the project.
"""

from typing import Literal as Lit
from pydantic import BaseModel, ConfigDict


def to_camel(name: str) -> str:
    is_camel_or_pascal = '_' not in name

    if is_camel_or_pascal:
        return name[0].lower() + name[1:]

    s = name.replace('_', ' ').title().replace(' ', '')
    return s[0].lower() + s[1:]


class Model(BaseModel):
    """
    The model from which all others should inherit.
    """

    model_config = ConfigDict(
        # Ensure an error is raised when extra, unexpected arguments (keys) are present.
        extra='forbid',
        # Prevent automatic type coercion. Otherwise, the value `1` would be coerced to `1.0`,
        # and for strings, `1` would be coerced to `'1'`. strict=True will raise an error instead.
        strict=True,
        # By default, certain namespaces cannot be used as keys in a model attribute.
        # The namespace that conflicts with ChatGPT is `model`. ChatGPT has some attributes, such
        # as `model_slug`, that will cause errors if used in a model. This model disables that feature.
        protected_namespaces=(),
        alias_generator=to_camel,
        populate_by_name=True,
    )


# !! CUSTOMIZE ME !!
# Please set `PluginName` to a Literal with the names of the plugins you've used in
# chatgpt. If you haven't used any, set it to one of the default tool names, such as
# `Lit['python']`. You can find the names of the plugins you've used, either by
# looking at the `author.name` for each message, or by setting it to `Literal['test']`
# and running the tests to get a validation error when an unknown plugin name comes up.
# By changing `PluginName` to a Literal, all the model fields that are annotated with
# `DefaultToolName | PluginName` will now be validated by Pydantic as an enum, letting
# you find out (from a validation error) when ChatGPT has added a new default tool.
# When that happens, please add the new tool name to `DefaultToolName` and make a PR with
# the change.
#
# PluginName = Lit[
#     'AskTheCode.GetRepositoryStructure',
# ]
type PluginName = Lit[
    'AskTheCode.GetRepositoryStructure',
    'a8km123',
    'canmore.create_textdoc',
]


# When ChatGPT gets a new default tool, put em here.
type DefaultToolName = Lit[
    'python',
    'browser',
    'bio',
    'web',
    'web.run',
    'dalle.text2im',
]

type ModelName = Lit[
    'gpt-4',
    'gpt-4-1',
    'gpt-4-5',
    'gpt-4-all-tools-hogwild-topk',
    'gpt-4-browsing',
    'gpt-4-code-interpreter',
    'gpt-4-gizmo',
    'gpt-4-mobile',
    'gpt-4-plugins',
    'gpt-4o',
    'gpt-4o-mini',
    'o1',
    'o1-mini',
    'o1-preview',
    'o3',
    'o3-mini',
    'o3-mini-high',
    'o4-mini-high',
    'text-davinci-002-plugins',
    'text-davinci-002-render',
    'text-davinci-002-render-sha',
    'text-davinci-002-render-sha-mobile',
]
