# TikTok Downloader - Multilingual Implementation

This document describes the internationalization (i18n) implementation for the TikTok Downloader website.

## Overview

The website has been updated to support multiple languages through a translation system based on Flask-Babel and YAML translation files. This allows for easy addition of new languages and maintenance of existing translations.

## Features

- Support for multiple languages
- Language detection based on browser settings
- Language switching via dropdown menu
- Persistent language selection with cookies
- Translations stored in YAML files for easy maintenance

## Directory Structure

```
languages/
├── en/
│   └── translations.yaml    # English translations
├── es/
│   └── translations.yaml    # Spanish translations
└── [lang]/                  # Other language folders
    └── translations.yaml    # Translations for that language
```

## Adding a New Language

To add a new language:

1. Create a new folder in the `languages` directory with the language code (e.g., `fr` for French)
2. Create a `translations.yaml` file in that folder
3. Copy the content from the English translations file and translate all values
4. Update the `get_locale` function in `app.py` to include the new language code in the `best_match` list

## Translation File Structure

The translation files are structured hierarchically to organize content by page and component. For example:

```yaml
# Common elements across pages
common:
  website_name: "TikTok Downloader"
  website_tagline: "Download TikTok Videos Without Watermark"

# Navigation items
navigation:
  home: "Home"
  mp3_download: "MP3 Download"
  # ...
```

## Using Translations in Templates

Translations are accessed in templates using the `t()` function:

```html
<h1>{{ t('home.hero.title') }}</h1>
<p>{{ t('home.hero.subtitle') }}</p>
```

For values with variables:

```html
{{ t('common.copyright_text', {'year': '2023'}) | safe }}
```

## Language Switcher

The language switcher component is included in the header and allows users to change the website language. The selected language is stored in a cookie for persistence.

## Implementation Details

### Backend

- Flask-Babel is used for i18n support
- Custom YAML-based translation system for more flexible translations
- Language detection based on:
  1. URL parameter (`?lang=en`)
  2. Cookie (`lang`)
  3. Browser language settings
  4. Default to English

### Frontend

- Language switcher dropdown in the header
- JavaScript to handle language switching and cookie storage
- CSS for styling the language switcher

## Files Modified/Added

- `app.py` - Added i18n support
- `languages/` - Directory for translation files
- `templates/components/language-switcher.html` - Language switcher component
- `static/css/language-switcher.css` - Styling for language switcher
- `static/js/language-switcher.js` - JavaScript for language switching
- All template files - Updated to use translation keys

## Dependencies

- Flask-Babel
- PyYAML

## Future Improvements

- Add more languages
- Implement right-to-left (RTL) support for languages like Arabic
- Add translation management interface
- Implement automatic translation suggestions 