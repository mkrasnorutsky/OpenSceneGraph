#!/usr/bin/env python3
"""Link OSG classes and static plugin/serializer registration for every iOS slice."""
from pathlib import Path
import plistlib,subprocess,tempfile
from dependencies import ROOT,fetch,select
import os
WORK=Path(os.environ.get("APPLE_BUILD_ROOT", str(ROOT))).expanduser().resolve()
artifact=WORK/'dist/OpenSceneGraph.xcframework';info=plistlib.loads((artifact/'Info.plist').read_bytes())
assert len(info['AvailableLibraries'])==2
packages=fetch()
for entry in info['AvailableLibraries']:
    sim=entry.get('SupportedPlatformVariant')=='simulator'
    assert entry['SupportedPlatform']=='ios'
    assert set(entry['SupportedArchitectures'])==({'arm64','x86_64'} if sim else {'arm64'})
    folder=artifact/entry['LibraryIdentifier'];archive=folder/entry['LibraryPath'];headers=folder/entry['HeadersPath']
    subprocess.run(['lipo',str(archive),'-verify_arch',*entry['SupportedArchitectures']],check=True)
    frameworks=[]
    for name in ['libEGL','libGLESv2']:
        depfolder,depentry=select(packages[name],sim);frameworks+=['-F'+str(depfolder)]
    ftfolder,ftentry=select(packages['FreeType'],sim)
    sdk=subprocess.check_output(['xcrun','--sdk','iphonesimulator' if sim else 'iphoneos','--show-sdk-path'],text=True).strip()
    for arch in entry['SupportedArchitectures']:
        triple=arch+'-apple-ios18.0'+('-simulator' if sim else '')
        with tempfile.TemporaryDirectory(prefix='osg-client-') as directory:
            client=Path(directory)/'client.cpp'
            client.write_text('#include "OpenSceneGraphSPM.h"\n#include <osg/Group>\n#include <osgDB/Registry>\nint main(){OSGSPMRegisterPlugins(); osg::ref_ptr<osg::Group> root=new osg::Group; return OSGSPMVersion() && root.valid() ? 0 : 1;}\n')
            subprocess.run(['xcrun','clang++','-target',triple,'-isysroot',sdk,'-std=c++11','-DOSG_LIBRARY_STATIC','-DOPENTHREADS_LIBRARY_STATIC',
                '-I'+str(headers),'-I'+str(ROOT/'apple/SPM/include'),*frameworks,str(client),str(ROOT/'apple/SPM/OpenSceneGraphSPM.cpp'),str(archive),str(ftfolder/ftentry['LibraryPath']),
                '-framework','libGLESv2','-framework','libEGL','-lz',
                *[item for framework in ['Foundation','UIKit','ImageIO','CoreGraphics','Accelerate','MobileCoreServices'] for item in ['-framework',framework]],
                '-o',directory+'/client'],check=True)
print('PASS: device and both Simulator slices link OSG, ANGLE, FreeType and static plugin/serializer registration')
