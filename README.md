# Yr Meteogram Home Assistant Integration

This integration fetches weather meteograms from [yr.no](https://www.yr.no) using the `yr_meteogram_util` package and displays them as Image entities in Home Assistant.

## Features

- **Async I/O**: Fully asynchronous to ensure Home Assistant remains responsive.
- **Configurable**: Customize dark mode, cropping, transparency, and more.
- **Localization**: Available in English and Swedish.
- **Device Registry**: Groups entities by location.
- **Auto-updating**: Refreshes meteograms every 30 minutes.

## Installation

1. Copy the `custom_components/yr_meteogram` directory to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Yr Meteogram**.
4. Enter the **Location ID** (e.g., `2-5847504` for Oslo). You can find this ID in the URL of the forecast page on yr.no (e.g., `https://www.yr.no/en/forecast/daily-table/2-5847504/Norway/Oslo/Oslo/Oslo`).
5. Configure optional settings:
    - **Dark Mode**: Use the dark version of the meteogram.
    - **Crop Image**: Crop the image to remove whitespace.
    - **Make Transparent**: Make the background transparent.
    - **Unhide Dark Objects**: Make dark objects visible on dark backgrounds.

## Usage

Once configured, an Image entity will be created (e.g., `image.oslo_meteogram`). You can add this to your Lovelace dashboard using the Picture Entity card.

## Troubleshooting

- **Invalid Location ID**: Ensure you are using the correct ID format (e.g., `2-5847504`).
- **Image not updating**: Check the logs for connection errors. The image updates every 30 minutes.
