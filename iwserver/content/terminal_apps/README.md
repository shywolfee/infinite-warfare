# HyperComp application definitions

Each application is a key=value .app file in a category folder. The world/content editor exposes these files under HyperComp applications.

Required fields are name, size (positive GB), price (wallet credits), systems (all or comma-separated OS identifiers), feature (description), handler (registered application handler), and builtin (true or false).

Supported OS identifiers are frontier_os, aegis_os, openwave and minimal_recovery. Incompatible installed apps remain on disk but cannot run. Built-in apps occupy storage and cannot be uninstalled.

The handler connects the definition to a real game interface or report. Use an existing handler when adding a variant; adding an entirely new behavior also requires registering server/client behavior. Do not add placeholder handlers that only claim a service is ready.

Reload applications through the content editor after edits. Connected clients fetch the authoritative catalogue when opening or refreshing the desktop/app manager. Update both client and server for this change; no sound-pack rebuild is required.
