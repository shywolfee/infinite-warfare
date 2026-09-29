# In-game dashboard

The dashboard is Infinite Warfare's persistent, screen-reader-first gameplay
interface. It exists so routine management does not force a player to leave a
fight, disconnect from live chat, or lose access to direct game controls.

## Opening and navigating

In Dashboard mode, Tab and Shift+Tab move among the game keyboard area, game
options, the live player list, the selected conversation transcript, the
conversation list, its message field, and Send. Alt+G immediately focuses the
game keyboard area. That area gives keys back to direct movement, combat, and
world interaction while the current dashboard screen remains open.

Alt+F switches between Dashboard mode and Inventory mode. Inventory mode makes
Tab and Shift+Tab cycle carried items. Switching modes keeps an unfinished chat
message so it can be sent later.

Escape goes back one screen inside dashboard menus. At the dashboard root it
returns to the game keyboard area. The separate Escape game menu contains only
the choices to resume or leave the match.

## Why it stays live

Every in-game NV Form opened from the dashboard retains the shared shell. A
player can inspect equipment, groups, companions, terminal apps, announcements,
or another player's profile, press Alt+G to react to combat, then Tab back to
the same control and reading position. Player and conversation lists continue
updating while another screen is open.

This design is deliberately different from a traditional modal game menu:
information and administration remain available without pausing an online
world, while combat input is active only when the game keyboard area has focus.

## Shortcuts and conversations

Dashboard options announce their Alt-key shortcuts after their descriptions.
These shortcuts activate only while dashboard controls have focus, preventing
menu commands from colliding with combat controls. Conversation controls retain
draft text, support Enter or Alt+S to send, and expose global, map, team, group,
and private conversations as live readable lists.

Nested screens provide a Close, Back, or Cancel action. Escape activates that
action directly, so returning through a menu hierarchy never requires tabbing
to its final button.
