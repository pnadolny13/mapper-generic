# `mapper-generic`

Generic Singer mapper for overriding with a lightweight script.

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Capabilities

* `stream-maps`

## Settings

| Setting          | Required | Default | Description |
|:-----------------|:--------:|:-------:|:------------|
| code_path        | False    | None    | A path to the python file that contains your custom mapper code. The module should contain a `Mapper` class with optional overrides for map_schema_message, map_record_message, map_state_message, and map_activate_version_message. If none of those methods are overridden in your custom script then the mapper will do nothing and pass all message to the target. |
| stream_maps      | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config| False    | None    | User-defined config values to be used within map expressions. |

A full list of supported settings and capabilities is available by running: `mapper-generic --about`

## Supported Python Versions

* 3.8
* 3.9
* 3.10
* 3.11

## Usage

This mapper is meant to be versatile and lightweight so users can install it and do simple transformations of their data without having to build a new standalone mapper or add functionality into the Meltano SDK.

To use the mapper you configure it to reference a script using the `code_path` setting.
The script should contain code similar to the following so the mapper can access it properly.
The code below only overrides the `map_record_message` to make some minor adjustments to the data.

```python
import typing as t

from singer_sdk._singerlib.messages import (
    Message,
)

class Mapper():

    def map_record_message(self, message_dict: dict) -> t.Iterable[Message]:
        page_content = message_dict["record"]["page_content"]
        text_nl = " ".join(page_content.split("\n"))
        text_spaces = " ".join(text_nl.split())
        message_dict["record"]["page_content"] = text_spaces
        return message_dict
```

Currently the mapper expects a `Mapper` class in the script and allows you to override each of the 4 methods provided:
- map_record_message
- map_schema_message
- map_state_message
- map_activate_version_message

Usually `map_state_message` and `map_activate_version_message` shouldn't need to be overridden and `map_schema_message` should only be, and is required to be, overridden if the records structure is changed i.e. a property is added, removed, renamed.

### Additional Dependencies

If you're running this mapper with Meltano you can add additional dependencies to the `pip_url` so that they're accessible to your mapper script.

```
  - name: mapper-generic
    namespace: mapper_generic
    pip_url: git+https://github.com/pnadolny13/mapper-generic.git <MY_EXTRA_DEPENDENCY>
```

### Accepted Config Options

A full list of supported settings and capabilities for this
mapper is available by running:

```bash
mapper-generic --about
```

### Configure using environment variables

This Singer mapper will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

## Usage

You can easily run `mapper-generic` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Mapper Directly

```bash
mapper-generic --version
mapper-generic --help
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `mapper-generic` CLI interface directly using `poetry run`:

```bash
poetry run mapper-generic --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This mapper will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd mapper-generic
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Run a test `run` pipeline:
meltano run tap-smoke-test mapper-generic target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps, targets, and mappers.
