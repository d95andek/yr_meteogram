"""Test the Yr Meteogram image entity."""
from unittest.mock import patch

import pytest
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.yr_meteogram.const import DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_image_entity(hass: HomeAssistant) -> None:
    """Test the image entity."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "location_id": "2-5847504",
            "dark_mode": True,
            "crop": False,
            "make_transparent": False,
            "unhide_dark_objects": False,
        },
        title="Oslo",
    )
    config_entry.add_to_hass(hass)

    with patch(
        "yr_meteogram_util.fetch_svg_async",
        return_value="<svg>Oslo</svg>",
    ), patch(
        "yr_meteogram_util.get_location_name",
        return_value="Oslo",
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    entity_id = "image.oslo_meteogram_dark"
    # Note: The entity ID generation depends on how HA handles naming. 
    # Since we set has_entity_name=True, and device name is "Oslo", and entity name is "Meteogram Dark",
    # it should be something like image.oslo_meteogram_dark.
    # However, we can just search for the entity.
    
    entity_registry = er.async_get(hass)
    entries = entity_registry.entities.values()
    assert len(entries) == 1
    entry = list(entries)[0]
    assert entry.platform == DOMAIN
    
    state = hass.states.get(entry.entity_id)
    assert state is not None
    assert state.state == "unknown" # Image entities often have unknown state, but attributes matter
    assert state.attributes["friendly_name"] == "Meteogram Dark"
