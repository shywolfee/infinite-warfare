# Infinite Warfare NV_form integration

This is Ivan Soto's NV_form with the Markdown document and named-group APIs
ported from `breach_factor/client/form` for Infinite Warfare 0.5.9.2.
Original source notices and attribution are retained. This directory is a
modified integration, not an unmodified upstream distribution.

## Game-specific hooks

- Keep the network pump and live dashboard shell hooks in form monitoring.
- Preserve touchscreen navigation, visual-form capture and configurable UI
  cues, including independent dashboard sound preferences.
- Do not process form shortcuts while the game keyboard area has focus.
- Nested screen shortcuts take priority over shared dashboard shortcuts.
- Hidden and disabled actions cannot claim shortcuts or default activation.
- Form navigation must terminate even when every control is unavailable.

## Document-reader fixes

Unhandled keys return to the containing form so Tab can leave a document.
Character navigation reads each directional key once. The dashboard leaves
Escape to the document's elements list while that list is open.

The game opens only HTTP and HTTPS document links externally; other link
targets are announced rather than executed.
