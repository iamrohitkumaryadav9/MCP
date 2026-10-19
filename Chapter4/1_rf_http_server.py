"""
Chapter 4 - Same typed RF server, served over Streamable HTTP.

Self-contained so it can be packaged alone in a Docker image (see Dockerfile).
The MCP endpoint is http://<host>:8070/mcp

Exposes tools over a small, made-up set of RF test results.
The type hints and Field descriptions below are turned by FastMCP into the
JSON input schema the LLM sees, and every call is validated against it
(e.g. an unknown band is rejected before our code even runs).
"""
import os
from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

mcp = FastMCP("rf-test-data")

Band = Literal["n77", "n78", "B3", "B7"]

# Fake demo data: device_id -> band -> measurements
TEST_RESULTS: dict[str, dict[str, dict]] = {
    "DEV-001": {
        "n77": {"tx_power_dbm": 23.1, "evm_pct": 2.4, "passed": True},
        "n78": {"tx_power_dbm": 22.8, "evm_pct": 2.7, "passed": True},
        "B3": {"tx_power_dbm": 24.0, "evm_pct": 1.9, "passed": True},
    },
    "DEV-002": {
        "n77": {"tx_power_dbm": 21.2, "evm_pct": 3.6, "passed": False},
        "n78": {"tx_power_dbm": 22.5, "evm_pct": 2.9, "passed": True},
        "B7": {"tx_power_dbm": 23.4, "evm_pct": 2.2, "passed": True},
    },
    "DEV-003": {
        "n77": {"tx_power_dbm": 22.9, "evm_pct": 2.5, "passed": True},
        "B3": {"tx_power_dbm": 20.7, "evm_pct": 4.1, "passed": False},
    },
}


def _lookup(device_id: str, band: str) -> dict:
    if device_id not in TEST_RESULTS:
        raise ToolError(f"Unknown device '{device_id}'. Use list_devices first.")
    if band not in TEST_RESULTS[device_id]:
        raise ToolError(f"No {band} results for {device_id}.")
    return TEST_RESULTS[device_id][band]


@mcp.tool()
def list_devices() -> list[str]:
    """List all device IDs that have RF test results."""
    return sorted(TEST_RESULTS)


@mcp.tool()
def get_device_stats(
    device_id: Annotated[str, Field(description="Device ID, e.g. 'DEV-001'")],
    band: Annotated[Band, Field(description="Frequency band to look up")],
) -> dict:
    """Get transmit power (dBm), EVM (%) and pass/fail for one device on one band."""
    return {"device_id": device_id, "band": band, **_lookup(device_id, band)}


@mcp.tool()
def compare_bands(
    device_id: Annotated[str, Field(description="Device ID, e.g. 'DEV-002'")],
    band_a: Band,
    band_b: Band,
) -> dict:
    """Compare one device's results on two bands (band_b minus band_a)."""
    a, b = _lookup(device_id, band_a), _lookup(device_id, band_b)
    return {
        "device_id": device_id,
        "bands": [band_a, band_b],
        "tx_power_diff_db": round(b["tx_power_dbm"] - a["tx_power_dbm"], 2),
        "evm_diff_pct": round(b["evm_pct"] - a["evm_pct"], 2),
    }


@mcp.tool()
def find_failures(
    max_evm_pct: Annotated[float, Field(gt=0, description="EVM limit in %")] = 3.0,
) -> list[dict]:
    """Find every device/band that failed its test or has EVM above the limit."""
    return [
        {"device_id": dev, "band": band, **m}
        for dev, bands in TEST_RESULTS.items()
        for band, m in bands.items()
        if not m["passed"] or m["evm_pct"] > max_evm_pct
    ]


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8070")),
        show_banner=False,
    )
