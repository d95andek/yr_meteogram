"""Test the Yr Meteogram config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.yr_meteogram.const import DOMAIN


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "yr_meteogram_util.fetch_svg_async",
        return_value="<svg>Oslo</svg>",
    ), patch(
        "yr_meteogram_util.get_location_name",
        return_value="Oslo",
    ), patch(
        "custom_components.yr_meteogram.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "location_id": "2-5847504",
                "dark_mode": False,
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Oslo"
    assert result2["data"] == {
        "location_id": "2-5847504",
        "dark_mode": False,
        "crop": False,
        "make_transparent": False,
        "unhide_dark_objects": False,
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_location(hass: HomeAssistant) -> None:
    """Test we handle invalid location."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "yr_meteogram_util.fetch_svg_async",
        side_effect=ValueError("Invalid location"),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "location_id": "invalid",
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "invalid_location"}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle connection error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "yr_meteogram_util.fetch_svg_async",
        side_effect=Exception("Connection error"),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "location_id": "2-5847504",
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}
