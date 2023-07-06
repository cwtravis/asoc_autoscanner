# ASoC AutoScanner Changelog

All notable changes to this project will be documented in this file.

## Version 1.0.1 - 2023-07-06

- Added support for environment variables "HTTP_PROXY" and "HTTPS_PROXY". These will be picked up by the scripts and honored.
- - Example:  `HTTPS_PROXY=123.123.123.123:4444`
- ASoC object now uses a requests Session object to manage persistent proxy and header data

## Version 1.0.0 - Initial Version

- Released