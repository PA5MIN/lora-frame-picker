# Security

## Local data

The desktop application processes media locally. The WebUI stores uploads and
exports only in the folders shown at startup. Local folder settings are stored
in the current user's application-data directory and are never required in the
repository.

The WebUI listens on the local network by default so a phone can connect. Every
start creates a new random access key. Use it only on a trusted network, stop it
with the WebUI button (or `Ctrl+C` in source mode) when finished, and do not share the complete URL with untrusted
people. It is not designed to be exposed directly to the public internet.

## Reporting a vulnerability

Please open a GitHub Security Advisory instead of a public issue when a report
contains an undisclosed vulnerability or sensitive information. Do not attach
private media, access URLs, HAR files, tokens, session files, or local settings.
