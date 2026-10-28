// swift-tools-version: 5.9
import PackageDescription
let package = Package(
    name: "OpenSceneGraph",
    platforms: [.iOS("18.0")],
    products: [.library(name: "OpenSceneGraph", targets: ["OpenSceneGraph"])],
    dependencies: [
        .package(url: "https://github.com/mkrasnorutsky/ANGLE.git", exact: "0.1.1"),
        .package(url: "https://github.com/mkrasnorutsky/FreeType.git", exact: "0.1.0")
    ],
    targets: [
        .binaryTarget(name: "COpenSceneGraph", url: "https://github.com/mkrasnorutsky/OpenSceneGraph/releases/download/0.1.0/OpenSceneGraph.xcframework.zip", checksum: "b4e8f90e559ef0c4722b92429cfa0e0e073028cc9b08c1bf26fa76b837cc3a51"),
        .target(name: "OpenSceneGraph", dependencies: ["COpenSceneGraph", .product(name: "ANGLE", package: "angle"), .product(name: "FreeType", package: "freetype")],
            path: "apple/SPM", publicHeadersPath: "include", cxxSettings: [.define("OSG_LIBRARY_STATIC"), .define("OPENTHREADS_LIBRARY_STATIC")],
            linkerSettings: [.linkedLibrary("z"), .linkedFramework("Foundation"), .linkedFramework("UIKit"), .linkedFramework("ImageIO"), .linkedFramework("CoreGraphics"), .linkedFramework("Accelerate"), .linkedFramework("MobileCoreServices")])
    ],
    cxxLanguageStandard: .cxx11
)
