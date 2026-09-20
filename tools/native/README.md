# Windows ReactPhysics3D runtime repair

Experimental migration runtime; **not a game release**. Nothing installs into
`C:/nvgt`. The shipping game remains unchanged until integration gates pass.

Pinned NVGT source: `9d64630b48fd4604a5321f00217dd7b22e33b9b8` from
https://github.com/samtupy/nvgt. ReactPhysics3D is 0.10.2.
Poco source: `fee4dccb44396911e9559c6875e88146f64b7f55` (1.14.1) from
https://github.com/pocoproject/poco.

The patch marks altered NVGT code and preserves its upstream license. It fixes
the ContactPoint value/pointer ABI mismatch, exposes real force/torque methods,
adds concrete fixed/hinge/slider/ball joint factories and rejects the unsafe
generic JointInfo factory. Raw native handles still require ownership wrappers.
Collision callbacks now propagate exceptions, accept null listeners, and detach
the listener from the world before destroying it.
Generic capsule destruction now dispatches through RP3D's CAPSULE type rather
than incorrectly expecting capsules to be convex polyhedra. The compiler also
defines `IW_REACTPHYSICS_RUNTIME` so the client can use this revision's built-in
HTTP API without loading an obsolete curl plugin.

The official Windows SDK timestamp used is `1788117066`. SHA256 fingerprints:

- `reactphysics3d.lib`: `7A3C4F218337EDD7D33BCD41EEEEB2F4605B303F35B444177D208A2E3C0EC131`
- `angelscript.lib`: `043646829579DC7E9A8D524E6807167099457C12AC2C1050C36992EAB3C16FCD`
- `PocoNet.lib`: `EFE1DD88C4F189D033F90F066298EA9CC49C0E38892D63BBF0258572EF85C059`

Build requirements: x64 MSVC Build Tools, Windows SDK, Python, SCons 4.11.1.
Use project-local clones `runtime_build/nvgt` and `runtime_build/poco`, checked
out at the commits above (enable `core.longpaths` for the NVGT clone).
Apply `nvgt-reactphysics.patch` with `git apply` inside the NVGT clone.
Download/extract the official https://nvgt.dev/windev.zip into its `windev`
directory and verify the fingerprints above. This URL is mutable: do not
silently accept a changed SDK as the tested build.

From `tools/native`, run SCons with `-f rebuild_poco_net.scons`. This compiles
Poco's unmodified MessageHeader.cpp with the local compiler, linked before
PocoNet, avoiding a newer-compiler-only STL symbol in the prebuilt SDK. It does
not emulate missing CRT functions or modify the original SDK library.

Then from the NVGT clone run:

```
python -m SCons -Q deps=unmanaged no_stubs=1 no_shared_plugins=1 no_user=1
```

Use a local Python virtual environment if SCons is not installed. Always use
`deps=unmanaged` after verification, preventing automatic SDK replacement.
The initial build omits game executable stubs: it runs source tests only.
Matched release stubs/plugins and full game packaging remain release gates.
For matched Windows stubs, the verified build command is:

```
python -m SCons -Q deps=unmanaged no_user=1
```

The client also needs its existing `notifications.dll`, `nvgt_app_volume.dll`
and `voice_command.dll` in the project-local runtime's `release/lib` for
compilation. These three copied game helper plugins passed compilation with
this runtime; full interactive helper regression testing is still required.
Client/server compatibility builds and a compiled actor regression have passed.
Use `-s build.output_basename=<dedicated-test-path>` to avoid overwriting the
shipping executable. The pinned runtime defaults to a ZIP bundle; set
`-s build.windows_bundle=1` for a folder or `0` for an executable only.

Run `runtime_build/nvgt/release/nvgt.exe tools/tests/reactphysics_capabilities.nvgt`
from the game directory. Inspect the newest
`%LOCALAPPDATA%/Temp/IW-reactphysics-capabilities-*/results.txt`; process exit
status alone is insufficient because NVGT can return zero on script failure.
The file must end with `Failures: 0` and `Stage: complete`.
The regression runner `tools/tests/run_reactphysics.ps1` also checks the owner
and all four compiled maps, rejecting stale reports and compile failures.
