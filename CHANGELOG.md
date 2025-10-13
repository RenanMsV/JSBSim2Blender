# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2025-10-12

### Added

- Released extension in the [Blender Extensions Platform](https://extensions.blender.org/add-ons/io-scene-jsbsim/).

### Changed

- Removed tags Scene and 3D View as requested by reviewer.

## [0.2.1] - 2025-10-7

### Fixed

- Fixed way of calculating units, as it could be wrong.
- Fixed not showing engines if no position was present.

### Added

- Settings column when importing.
    #### Plotted Objects
    - Scale factor (double)
    - Show name in viewport (bool)
    - Show axes in viewport (bool)

    #### Parenting:
    - Automatically parenting Thrusters to their Engines (bool)

    #### Include/Exclude from importing
    - Metrics (bool)
    - Mass Balance (bool)
    - Ground Reactions (bool)
    - External Reactions (bool)
    - Propulsion (bool)

### Changed

- Internal automation changes.

## [0.2.0] - 2025-10-07

### Changed

- Migrated legacy add-on to Blender 4.2 extension format
- New versioning scheme. 0.0.2 becomes 0.2.0.
- Relicensed from GPL2 to GPL3.

## [0.0.2] - 2023-07-31

### Added

- Added Changelog file.

### Fixed

- PR #2 aims to fix an error when a tag does not exist. Explained in issue #1.

## [0.0.1] - 2023-03-31

### Added

- Add Simple positioning the FDM in the 3d space.

[0.2.2]: https://github.com/RenanMsV/JSBSim-Viewer/tree/v0.2.2
[0.2.1]: https://github.com/RenanMsV/JSBSim-Viewer/tree/v0.2.1
[0.2.0]: https://github.com/RenanMsV/JSBSim-Viewer/commit/5ed7959eb6f627b37c0deb60ac6677e0fd6cd2b6
[0.0.2]: https://github.com/RenanMsV/JSBSim-Viewer/tree/4.2-legacy
[0.0.1]: https://github.com/RenanMsV/JSBSim-Viewer/tree/2.8.0
