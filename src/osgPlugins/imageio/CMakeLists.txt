SET(TARGET_SRC ReaderWriterImageIO.cpp )

IF (APPLE) 
   IF(OSG_BUILD_PLATFORM_IPHONE OR CMAKE_SYSTEM_NAME STREQUAL "iOS")
     # compile as objective-c++
     SET_SOURCE_FILES_PROPERTIES(ReaderWriterImageIO.cpp PROPERTIES COMPILE_FLAGS "-x objective-c++")
   ENDIF()
ENDIF()

SET(TARGET_ADDED_LIBRARIES)
SET(TARGET_LIBRARIES_VARS IMAGEIO_LIBRARY )
IF(CMAKE_SYSTEM_NAME STREQUAL "iOS")
    SET(TARGET_EXTERNAL_LIBRARIES "-framework Accelerate" "-framework UIKit" "-framework ImageIO" "-framework CoreGraphics" "-framework Foundation" "-framework MobileCoreServices")
ELSE()
    SET(TARGET_EXTERNAL_LIBRARIES "/System/Library/Frameworks/Accelerate.framework")
ENDIF()

#### end var setup  ###
SETUP_PLUGIN(imageio)

