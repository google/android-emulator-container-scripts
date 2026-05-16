The (sub)directories here contain templates that will be used to create the final docker image.
The layout should follow the desired layout in the container.

Make sure to update `pyproject.toml` (and `MANIFEST.in` if needed) if you add new directories
here, so the templates ship with the installed package.
