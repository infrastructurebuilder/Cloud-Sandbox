# cloudflow-plotting

Plotting routines for ROMS and FVCOM model output: one PNG per field
and time step, cut to map tiles, and a helper that joins the PNGs into
a movie with `ffmpeg`.

It is a separate distribution that installs into the `cloudflow`
namespace, so the code is imported as `cloudflow.plotting`:

```python
from cloudflow.plotting import plot_roms

plot_roms.plot("/com/nos/cbofs.2020030900/nos.cbofs.fields.f001.20200309.t00z.nc", "/com/nos/plots", "temp")
```

The [cloudflow](../cloudflow/) project depends on it.

## This is a copy

This directory is a copy made inside the Cloud-Sandbox repository. The
files under `src/`, `legacy/`, `legacy-tests/` and `requirements/` come
from `cloudflow/plotting/` and its neighbours, and are byte-identical
to their originals except for one correction that is kept as a patch.
[../MAP.md](../MAP.md) lists every file, the correction, and how this
project would be moved to a repository of its own. Do not edit the
copied files here: change the original and copy again, or add a patch.

## Layout

| Path | What |
| --- | --- |
| `src/cloudflow/plotting/` | The package: `plot_roms`, `plot_fvcom`, `shared`, `tile`, and the script `hlfs.py` |
| `tests/` | Tests that need no model output |
| `legacy-tests/` | The original test script; it needs model output under `/com` |
| `legacy/setup.py` | The `setup.py` that built the old `plotting` distribution |
| `requirements/` | The original requirements note |

There is no `src/cloudflow/__init__.py`, on purpose. `cloudflow` is a
namespace shared by two distributions, and a namespace has none.

## Working on it

```sh
just init        # create the environment
just test        # lint, type-check, fast tests
just full-test   # also build the wheel and try it in an empty environment
```

`hlfs.py` is an exported notebook that runs when it is imported. What
it needs is in the `hlfs` extra: `uv sync --extra hlfs`.
