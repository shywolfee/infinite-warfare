# Regression checks

Run these from source using the same NVGT installation used to build the game:

```powershell
& C:/nvgt/nvgt.exe tools/tests/wallet_regression.nvgt
& C:/nvgt/nvgt.exe tools/tests/client_regression_runner.nvgt
& C:/nvgt/nvgt.exe tools/tests/acoustic_regression_runner.nvgt
& C:/nvgt/nvgt.exe tools/tests/world_objects_regression.nvgt
python tools/tests/world_editor_regression.py
cd iwserver; & C:/nvgt/nvgt.exe world_editor_regression_runner.nvgt; cd ..
python tools/build_maps.py
python tools/validate_maps.py
```

Reports and synthetic wallet records go in uniquely named `IW-*-regression-*`
directories under the current user's Local AppData Temp directory. No real
accounts, settings or game connections are used. The large inventory fixture
takes time to construct; the report distinguishes setup from browsing timings.

The acoustic test loads Freya's Ascent geometry directly from the source tree
and compares narrowed wall traces with the pre-optimization reference. It also
checks conservative bounds after rotating and translating a dynamic object.
The client test compiles the actual game functions with a separate test entry
point; normal client builds do not include that entry point or test code.

The world-object test uses production parsing, damage, client geometry and
late-join handlers with isolated network/audio sinks. It checks the real maps'
component parity and verifies their sound names inside the existing sound pack.
The Python validator floods walkable foot positions in ordered map geometry,
including headroom and furniture, and checks all spawns, POIs, doors and services.

The world editor has two checks. The client test runs every builder with its
default settings on a blank map, with spawn points on every floor of the
building, at the top of the stairs and on the bridge, and writes it to
`IW-editor-test` in Local AppData Temp; `world_editor_regression.py` then runs
the server's own line validator over it (`map_line_check.nvgt`) and the raster
validator, so a builder that writes a line the server would refuse, or builds
a floor nobody can reach, fails. The server test
(`iwserver/world_editor_regression_runner.nvgt`, run from `iwserver`) drives the
real request handler: creating, travelling to and editing a map, undo and
redo, properties and lobby listing, content files and reloading, and refusing
requests without permission. It removes what it made and writes its report to
`iwserver/administration/world_editor_regression.txt`.
