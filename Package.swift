// swift-tools-version: 5.9
import PackageDescription
let package = Package(
    name: "OpenSceneGraph",
    platforms: [.iOS("18.0")],
    products: [.library(name: "OpenSceneGraph", targets: ["OpenSceneGraph"])],
    dependencies: [
        .package(url: "https://github.com/mkrasnorutsky/ANGLE.git", exact: "0.1.1"),
        .package(url: "https://github.com/mkrasnorutsky/FreeType.git", exact: "0.1.1")
    ],
    targets: [
        .binaryTarget(name: "COpenSceneGraph", url: "https://github.com/mkrasnorutsky/OpenSceneGraph/releases/download/0.1.1/OpenSceneGraph.xcframework.zip", checksum: "9898acad48383ed4d0970b65fae055ce7169d955dc62994a40034e3ab6efd09f"),
        .target(name: "OpenSceneGraph", dependencies: ["COpenSceneGraph", .product(name: "ANGLE", package: "angle"), .product(name: "FreeType", package: "freetype")],
            path: "apple/SPM", publicHeadersPath: "include", cxxSettings: [.define("OSG_LIBRARY_STATIC"), .define("OPENTHREADS_LIBRARY_STATIC")],
            linkerSettings: [.linkedLibrary("z"), .linkedFramework("Foundation"), .linkedFramework("UIKit"), .linkedFramework("ImageIO"), .linkedFramework("CoreGraphics"), .linkedFramework("Accelerate"), .linkedFramework("MobileCoreServices")])
    ],
    cxxLanguageStandard: .cxx11
)
