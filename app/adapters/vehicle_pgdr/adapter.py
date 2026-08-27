from typing import Any, Protocol


class VehiclePGDRAdapter(Protocol):
    """Future Vehicle PGDR adapter interface."""

    def prepare_input(self, context: dict[str, Any]) -> dict[str, Any]:
        ...

    def invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...

    def validate_output(self, output: dict[str, Any]) -> bool:
        ...

    def map_error(self, error: Exception) -> dict[str, Any]:
        ...
