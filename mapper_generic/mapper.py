"""Generic mapper class."""

from __future__ import annotations

import importlib.util
import os
import typing as t
from typing import TYPE_CHECKING

import singer_sdk.typing as th
from singer_sdk import _singerlib as singer
from singer_sdk.mapper import PluginMapper
from singer_sdk.mapper_base import InlineMapper

from mapper_generic.sdk_fixes.messages import RecordMessage

if TYPE_CHECKING:
    from pathlib import PurePath


class GenericMapper(InlineMapper):
    """Generic Singer mapper for overriding with a lightweight script."""

    name = "mapper-generic"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "code_path",
            th.StringType,
            description="A path to the python file that contains your custom mapper "
            "code. The module should contain a `Mapper` class with optional overrides "
            "for map_schema_message, map_record_message, map_state_message, and "
            "map_activate_version_message. If none of those methods are overridden "
            "in your custom script then the mapper will do nothing and pass all message"
            " to the target.",
        ),
    ).to_dict()

    def __init__(
        self,
        *,
        config: dict | PurePath | str | list[PurePath | str] | None = None,
        parse_env_config: bool = False,
        validate_config: bool = True,
    ) -> None:
        """Create a new inline mapper.

        Args:
            config: Mapper configuration. Can be a dictionary, a single path to a
                configuration file, or a list of paths to multiple configuration
                files.
            parse_env_config: Whether to look for configuration values in environment
                variables.
            validate_config: True to require validation of config settings.
        """
        super().__init__(
            config=config,
            parse_env_config=parse_env_config,
            validate_config=validate_config,
        )

        self.mapper = PluginMapper(plugin_config=dict(self.config), logger=self.logger)
        module = os.path.basename(self.config["code_path"]).split(".")[0]
        spec = importlib.util.spec_from_file_location(f"{module}.Mapper", self.config["code_path"])
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        self.custom_mapper = foo.Mapper()

    def _is_defined(self, method_name):
        invert_op = getattr(self.custom_mapper, method_name, None)
        if callable(invert_op):
            return True
        else:
            return False

    def map_schema_message(self, message_dict: dict) -> t.Iterable[singer.Message]:
        """Map a schema message to zero or more new messages.

        Args:
            message_dict: A SCHEMA message JSON dictionary.
        """
        if self._is_defined("map_schema_message"):
            stream_name = message_dict["stream"]
            transformed_message = self.custom_mapper.map_schema_message(
                message_dict
            )
            if transformed_message["stream"] != stream_name:
                raise Exception(
                    "Altering stream name using this mapper is unsafe and not allowed."
                )
            yield singer.SchemaMessage.from_dict(transformed_message)
        else:
            yield singer.SchemaMessage.from_dict(message_dict)

    def map_record_message(
            self,
            message_dict: dict
    ) -> t.Iterable[singer.RecordMessage]:
        """Map a record message to zero or more new messages.

        Args:
            message_dict: A RECORD message JSON dictionary.
        """
        if self._is_defined("map_record_message"):
            yield t.cast(
                RecordMessage,
                RecordMessage.from_dict(
                    self.custom_mapper.map_record_message(
                        message_dict
                    )
                )
            )
        else:
            yield t.cast(RecordMessage, RecordMessage.from_dict(message_dict))

    def map_state_message(self, message_dict: dict) -> t.Iterable[singer.Message]:
        """Map a state message to zero or more new messages.

        Args:
            message_dict: A STATE message JSON dictionary.
        """
        if self._is_defined("map_state_message"):
            yield singer.StateMessage.from_dict(
                self.custom_mapper.map_state_message(
                    message_dict
                )
            )
        else:
           yield singer.StateMessage.from_dict(message_dict)

    def map_activate_version_message(
        self,
        message_dict: dict,
    ) -> t.Iterable[singer.Message]:
        """Map a version message to zero or more new messages.

        Args:
            message_dict: An ACTIVATE_VERSION message JSON dictionary.
        """
        if self._is_defined("map_activate_version_message"):
            yield singer.ActivateVersionMessage.from_dict(
                self.custom_mapper.map_activate_version_message(
                    message_dict
                )
            )
        else:
           yield singer.ActivateVersionMessage.from_dict(message_dict)


if __name__ == "__main__":
    GenericMapper.cli()
