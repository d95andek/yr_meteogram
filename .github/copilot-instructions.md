This project is for creating and mantaining a Home Assistant integration that uses yr_meteogram_util PyPi package to generate meteograms from yr.no weather data.

The yr_meteogram_util package can be found here: https://pypi.org/project/yr-meteogram-util/. The package provides functionality to fetch weather meteograms (svg images) from yr.no. It's syntax is:

```python
async def fetch_svg_async(location_id: str, dark: bool = False, crop: bool = False, make_transparent: bool = False, unhide_dark_objects: bool = false, session: Optional[aiohttp.ClientSession] = None) -> str
def fetch_svg(location_id: str, dark: bool = False, crop: bool = False, make_transparent: bool = False, unhide_dark_objects = False) -> str
def get_location_name(meteogram: str) -> str
```

The package can be installed via pip:

```bash
pip install yr_meteogram_util
```

And updated with:

```bash
pip install --upgrade yr_meteogram_util
```

Exeample usage:

```python
import asyncio # if using the async version
import yr_meteogram_util

# The location to fetch.
LOCATION_ID = '2-5847504'

standard_meteogram = yr_meteogram_util.fetch_svg(LOCATION_ID)
dark_cropped_transparent_meteogram = yr_meteogram_util.fetch_svg(LOCATION_ID, dark = True, crop = True, make_transparent = True, unhide_dark_objects = True)
location_name = yr_meteogram_util.get_location_name(standard_meteogram)
```

This integration uses the above package to fetch meteograms for specified locations and display them within Home Assistant. It shoould aim for the highest possible compatibility with Home Assistant's architecture and best practices for integration development. The aim is for Platinum level quality code.

The integration should provide configuration options for users to specify their desired locations and meteogram settings (e.g., dark mode, cropping, transparency). It should also handle errors gracefully, such as when a location ID is invalid or when there are network issues fetching the meteogram data. The configuration shall be done via Home Assistant's configuration flow system and the UI shall be localized for multiple languages. English shall be the default language and translations for Swedish shall be provided.

During setup it shall be possible to add multiple locations (the user will need to enter each location's ID), each with their own settings for the meteogram. All added locations shall be displayed in a list with options to edit or remove each location. It shall also be possible to add a location ID multiple times with different settings. At configuration time, the integration shall validate each location ID by attempting to fetch a meteogram using the provided ID. If the fetch fails, an appropriate error message shall be displayed to the user, prompting them to correct the ID before proceeding.

Each confuration shall result in a separate Image entity in Home Assistant, which will display the corresponding meteogram. The entities shall update their images periodically (e.g., every 30 minutes) to ensure that the displayed meteograms are current. It shall not be possible to alter the default interval. The name of each entity shall be generated based on the location name retrieved from the meteogram data, combined with user-defined settings to ensure uniqueness.

A good and thorough documentation shall be provided, including installation instructions, configuration options, and usage examples. The documentation should also include troubleshooting tips for common issues users might encounter.

### Technical Requirements for Platinum Quality

1. **Async I/O**: The integration must strictly use the asynchronous method `fetch_svg_async` to ensure the Home Assistant event loop is never blocked.
2. **Type Safety**: All code must use strict Python type hinting.
3. **Device Registry**: Entities should be associated with a Device in the Home Assistant Device Registry. Group entities by their Location ID (e.g., a device named "Oslo" containing both the "Dark" and "Light" meteogram entities).
4. **Manifest**: The `manifest.json` should define the domain as `yr_meteogram` and the `iot_class` as `cloud_polling`.
5. **Testing**: Generate a `tests/` directory with `pytest` coverage for:
    - Config Flow (form validation, success, error handling).
    - Entity initialization and state updates.
