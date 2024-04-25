"""
Constants and configurations for the project.
"""

from typing import Literal, get_args
from pydantic import BaseModel


class Model(BaseModel):
    """
    The model from which all others should inherit.
    """

    class Config:
        # Ensure an error is raised when extra, unexpected arguments (keys) are present.
        extra = 'forbid'
        # Prevent automatic type coercion. Otherwise, the value `1` would be coerced to `1.0`,
        # and for strings, `1` would be coerced to `'1'`. strict=True will raise an error instead.
        strict = True
        # By default, certain namespaces cannot be used as keys in a model attribute.
        # The namespace that conflicts with ChatGPT is `model`. ChatGPT has some attributes, such
        # as `model_slug`, that will cause errors if used in a model. This model disables that feature.
        protected_namespaces = ()


# !! CUSTOMIZE ME !!
# Please set `PluginName` to a Literal with the names of the plugins you've used in
# chatgpt. If you haven't used any, set it to one of the default tool names, such as
# `Literal['python']`. You can find the names of the plugins you've used, either by
# looking at the `author.name` for each message, or by setting it to `Literal['test']`
# and running the tests to get a validation error when an unknown plugin name comes up.
# By changing `PluginName` to a Literal, all the model fields that are annotated with
# `DefaultToolName | PluginName` will now be validated by Pydantic as an enum, letting
# you find out (from a validation error) when ChatGPT has added a new default tool.
# When that happens, please add the new tool name to `DefaultToolName` and make a PR with
# the change.
#
# PluginName = Literal[
#     'AskTheCode.GetRepositoryStructure',
# ]
PluginName = str


# When ChatGPT gets a new default tool, put em here.
DefaultToolName = Literal[
    'python',
    'browser',
    'dalle.text2im',
]
default_tool_names = list(get_args(DefaultToolName))
