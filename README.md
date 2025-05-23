# logical-geometry Conan Package

This repository contains a Conan package for the `logical-geometry` header-only library, which provides classes for mapping `pixel_id <-> (x,y,z,p)`.

## Upgrading the Version

To bump the version:

1. Edit `conanfile.py` and update the version field:

```python
class LogicalgeometryConan(ConanFile):
    name = "logical-geometry"
    version = "1.2.0"  # ← Update this
```

2. Create a merge request with this change and get it approved.

3. Once merged, tag the commit in Git:

```bash
git tag 1.2.0
git push origin 1.2.0
```

4. The pipeline will start automatically and upload the package to the remote.
