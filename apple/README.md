# FlightGear OpenSceneGraph for iOS / Swift Package Manager

This repository preserves the FlightGear OpenSceneGraph source and upstream history at revision `838cc974b28f8e738dc77199da71bd8b2073ed51`, plus OneClickPilot's iOS/GLES fixes. It builds the FlightGear fork's existing library subset with ANGLE Metal/GLES 3 and packages it as a static XCFramework.

## Add the package

Add `https://github.com/mkrasnorutsky/OpenSceneGraph.git` in Xcode, select version **0.1.0** or later, and add the **OpenSceneGraph** product. ANGLE and FreeType **0.1.0** are declared transitive SPM dependencies; do not also link the old local copies. Minimum iOS is **18.0**. Supported architectures: **arm64 iPhone, arm64 Simulator and x86_64 Simulator**.

[Release 0.1.0](https://github.com/mkrasnorutsky/OpenSceneGraph/releases/tag/0.1.0) provides the static XCFramework ZIP, checksum and build manifest. SPM integrates binaries; it does not run CMake while resolving the package.

Before loading models or fonts, call `OSGSPMRegisterPlugins()` once. Include `OpenSceneGraphSPM.h` for this function, and include the standard `<osg/...>`, `<osgDB/...>` etc. headers from C++ code. The bootstrap retains/registers all bundled plugins and serializer translation units without requiring runtime plugin dylibs or `-force_load`. `OSGSPMVersion()` returns the underlying OSG version.

The package includes OpenThreads, osg, osgDB, osgUtil, osgGA, osgText, osgViewer, osgParticle, osgSim and osgTerrain, plus their serializers and the fork's deprecated serializers. Static format plugins: DDS, FreeType fonts, Apple ImageIO, OSG/OSG2, RGB, TGA and TXF. Other optional desktop formats and applications are not built. Full upstream sources remain available.

Window creation and EGL lifecycle belong to the application. The OSG build uses `OSG_WINDOWING_SYSTEM=None`, matching OneClickPilot's UIKit/ANGLE integration; it does not create a Cocoa or legacy EAGL window.

## Build from source

Requirements: macOS, Xcode with device and Simulator SDKs, CMake, Python 3 and Git. No signing identity is needed for these static artifacts.

```sh
git clone https://github.com/mkrasnorutsky/OpenSceneGraph.git
cd OpenSceneGraph
python3 apple/scripts/build_xcframework.py --jobs 6
python3 apple/scripts/validate_xcframework.py
```

The build downloads checksum-verified ANGLE and FreeType release archives specified in `apple/dependencies.json`; it never uses a developer's machine-specific library installation. CMake compiles each architecture separately; Apple's libtool combines core libraries and static plugins, lipo combines only Simulator architectures, and Xcode creates `dist/OpenSceneGraph.xcframework`. Static registration references are generated from exported serializer symbols so the linker's dead stripping cannot silently omit serializers.

The validation script links a client against OSG, every registration anchor, FreeType and ANGLE for all three targets. This checks binary architecture selection, external symbols and plugin retention; it does not establish rendering performance or runtime correctness on every device/Simulator.

A manual GitHub Actions workflow performs the same build and link validation. Original license and attribution files are retained in the sources and distribution. Review `LICENSE.txt` for OSG's terms and the transitive packages' notices when redistributing an application.

To use local rebuilt binaries, copy `apple/Package.local.swift` to the root `Package.swift` before adding this folder as a local package. Restore the release manifest when done.

## Release packaging

```sh
python3 apple/scripts/package_release.py --tag 0.2.0
```

Upload the resulting ZIP/checksums to that version's GitHub release, and commit `dist/Package.swift` as the root manifest at the release revision. Published archive bytes and checksums must remain immutable. The local template remains in `apple/Package.local.swift`.
