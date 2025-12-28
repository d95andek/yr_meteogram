"""Image platform for Yr Meteogram."""
from __future__ import annotations

import datetime
import logging
from typing import Any

import yr_meteogram_util
from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
    UpdateFailed,
)

from .const import (
    CONF_CROP,
    CONF_DARK_MODE,
    CONF_LOCATION_ID,
    CONF_MAKE_TRANSPARENT,
    CONF_UNHIDE_DARK_OBJECTS,
    DEFAULT_CROP,
    DEFAULT_DARK_MODE,
    DEFAULT_MAKE_TRANSPARENT,
    DEFAULT_UNHIDE_DARK_OBJECTS,
    DOMAIN,
    UPDATE_INTERVAL_MINUTES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Yr Meteogram image platform."""
    location_id = entry.data[CONF_LOCATION_ID]
    
    # We need to get the settings from options if available, otherwise data
    # This allows live updates of settings
    # However, the coordinator needs to know about these settings to fetch the right image.
    # So we might need to recreate the coordinator or pass the entry to it.
    
    coordinator = YrMeteogramCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([YrMeteogramImage(coordinator, entry)])


class YrMeteogramCoordinator(DataUpdateCoordinator[bytes]):
    """Class to manage fetching Yr Meteogram data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=datetime.timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )
        self.entry = entry
        self.session = async_get_clientsession(hass)
        self.last_update_success_time: datetime.datetime | None = None

    @property
    def location_id(self) -> str:
        """Return the location ID."""
        return self.entry.data[CONF_LOCATION_ID]

    @property
    def dark_mode(self) -> bool:
        """Return dark mode setting."""
        return self.entry.options.get(
            CONF_DARK_MODE, self.entry.data.get(CONF_DARK_MODE, DEFAULT_DARK_MODE)
        )

    @property
    def crop(self) -> bool:
        """Return crop setting."""
        return self.entry.options.get(
            CONF_CROP, self.entry.data.get(CONF_CROP, DEFAULT_CROP)
        )

    @property
    def make_transparent(self) -> bool:
        """Return make transparent setting."""
        return self.entry.options.get(
            CONF_MAKE_TRANSPARENT,
            self.entry.data.get(CONF_MAKE_TRANSPARENT, DEFAULT_MAKE_TRANSPARENT),
        )

    @property
    def unhide_dark_objects(self) -> bool:
        """Return unhide dark objects setting."""
        return self.entry.options.get(
            CONF_UNHIDE_DARK_OBJECTS,
            self.entry.data.get(CONF_UNHIDE_DARK_OBJECTS, DEFAULT_UNHIDE_DARK_OBJECTS),
        )

    async def _async_update_data(self) -> bytes:
        """Fetch data from API."""
        try:
            svg_content = await yr_meteogram_util.fetch_svg_async(
                self.location_id,
                dark=self.dark_mode,
                crop=self.crop,
                make_transparent=self.make_transparent,
                unhide_dark_objects=self.unhide_dark_objects,
                session=self.session,
            )
            self.last_update_success_time = datetime.datetime.now(datetime.timezone.utc)
            return svg_content.encode("utf-8")
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class YrMeteogramImage(CoordinatorEntity[YrMeteogramCoordinator], ImageEntity):
    """Representation of a Yr Meteogram Image."""

    _attr_content_type = "image/svg+xml"
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: YrMeteogramCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the image."""
        super().__init__(coordinator)
        ImageEntity.__init__(self, coordinator.hass)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_image"
        
        # Generate a name based on settings
        name_parts = ["Meteogram"]
        if coordinator.dark_mode:
            name_parts.append("Dark")
        if coordinator.crop:
            name_parts.append("Cropped")
        if coordinator.make_transparent:
            name_parts.append("Transparent")
        
        self._attr_name = " ".join(name_parts)
        
        # Device Info
        # We fetch the location name from the SVG data if possible, but we only have bytes in coordinator.data
        # We can parse it.
        location_name = "Yr Meteogram"
        if coordinator.data:
            try:
                location_name = yr_meteogram_util.get_location_name(coordinator.data.decode("utf-8"))
            except Exception:
                pass

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.location_id)},
            name=location_name,
            manufacturer="Yr.no",
            model="Meteogram",
            entry_type=None,
        )

    @property
    def image_last_updated(self) -> datetime.datetime | None:
        """The time when the image was last updated."""
        return self.coordinator.last_update_success_time

    async def async_image(self) -> bytes | None:
        """Return bytes of image."""
        return self.coordinator.data
