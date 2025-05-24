# TikTok Downloader

A web application that allows users to download TikTok videos without watermarks. The application supports downloading videos in different formats and also downloading just the audio track as MP3.

## Features

- Download TikTok videos without watermark
- Multiple download formats available
- MP3 audio extraction
- Clean, responsive user interface

## Requirements

- Python 3.7 or higher
- Flask
- yt-dlp

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/tiktok-downloader.git
cd tiktok-downloader
```

2. Install the requirements:

```bash
pip install -r requirements.txt
```

## Usage

Run the application using the provided run.py script:

```bash
python run.py
```

This will start the web server on http://localhost:5000

### Command Line Options

The run.py script supports several command line options:

- `--port PORT` - Set the port to run the server on (default: 5000)
- `--debug` - Run in debug mode
- `--no-browser` - Don't automatically open the browser

Example:

```bash
python run.py --port 8080 --debug
```

## Project Structure

- `app.py` - Main Flask application
- `run.py` - Application runner
- `static/` - Static files (CSS, JavaScript)
- `templates/` - HTML templates
- `downloads/` - Downloaded videos are stored here

## Browser Support

The application works with all modern browsers, including:

- Google Chrome
- Mozilla Firefox
- Safari
- Microsoft Edge

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Please respect copyright restrictions and terms of service of TikTok. Always ensure you have the right to download and use the content before doing so. 