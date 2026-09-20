# Version 0.5.1.1 regression checks

Run these from source using the same NVGT installation used to build the game:

```powershell
& C:/nvgt/nvgt.exe tools/tests/wallet_regression.nvgt
& C:/nvgt/nvgt.exe tools/tests/client_regression_runner.nvgt
& C:/nvgt/nvgt.exe tools/tests/acoustic_regression_runner.nvgt
& C:/nvgt/nvgt.exe tools/tests/world_objects_regression.nvgt
python tools/validate_exploration_maps.py
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
