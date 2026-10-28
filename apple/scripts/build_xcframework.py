#!/usr/bin/env python3
"""Build the FlightGear OSG subset and static plugins as one iOS XCFramework."""
from pathlib import Path
import argparse,json,shutil,subprocess
from dependencies import ROOT,fetch,select
PLUGINS=['dds','freetype','imageio','osg','rgb','tga','txf']
def run(*args,**kw):
    print('+',' '.join(map(str,args)),flush=True);return subprocess.run(list(map(str,args)),check=True,**kw)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--jobs',type=int,default=6);a=p.parse_args()
    dependencies=fetch();built={}
    for label,sdk,arch in [('ios-arm64','iphoneos','arm64'),('simulator-arm64','iphonesimulator','arm64'),('simulator-x86_64','iphonesimulator','x86_64')]:
        build=ROOT/'out/apple'/label;prefix=build/'install';compat=build/'angle';frameworks=compat/'out/iOS';frameworks.mkdir(parents=True,exist_ok=True)
        for name in ['libEGL','libGLESv2']:
            folder,entry=select(dependencies[name],sdk=='iphonesimulator');source=folder/entry['LibraryPath'];destination=frameworks/source.name
            if not destination.exists():shutil.copytree(source,destination)
            for group in (['EGL','KHR'] if name=='libEGL' else ['GLES2','GLES3']):
                headers=compat/'include'/group;headers.mkdir(parents=True,exist_ok=True)
                for header in (source/'Headers').glob('*.h'):shutil.copy2(header,headers/header.name)
        ftfolder,ftentry=select(dependencies['FreeType'],sdk=='iphonesimulator')
        include=ftfolder/ftentry['HeadersPath'];library=ftfolder/ftentry['LibraryPath']
        flags=['-DCMAKE_SYSTEM_NAME=iOS','-DCMAKE_OSX_SYSROOT='+sdk,'-DCMAKE_OSX_ARCHITECTURES='+arch,'-DCMAKE_OSX_DEPLOYMENT_TARGET=18.0',
            '-DCMAKE_POLICY_VERSION_MINIMUM=3.5','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_INSTALL_PREFIX='+str(prefix),
            '-DDYNAMIC_OPENSCENEGRAPH=OFF','-DDYNAMIC_OPENTHREADS=OFF','-DBUILD_OSG_APPLICATIONS=OFF','-DBUILD_OSG_EXAMPLES=OFF',
            '-DBUILD_OSG_PLUGINS_BY_DEFAULT=OFF','-DBUILD_OSG_DEPRECATED_SERIALIZERS=ON','-DOSG_ANGLE_ROOT='+str(compat),'-DOPENGL_PROFILE=GLES3',
            '-DOPENGL_HEADER1=#include <libGLESv2/gl32.h>','-DOPENGL_HEADER2=#include <libGLESv2/gl2ext.h>',
            '-DFREETYPE_INCLUDE_DIR_freetype2='+str(include),'-DFREETYPE_INCLUDE_DIR_ft2build='+str(include),'-DFREETYPE_LIBRARY='+str(library),
            '-DCMAKE_CXX_FLAGS=-F'+str(frameworks),'-DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=BOTH','-DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=BOTH']
        flags+=['-DBUILD_OSG_PLUGIN_'+x.upper()+'=ON' for x in PLUGINS]
        flags+=['-DCMAKE_DISABLE_FIND_PACKAGE_'+x+'=ON' for x in ['CURL','Fontconfig','GDAL','OpenEXR','RSVG','TIFF','JPEG','PNG','GIF','SDL','FFmpeg','COLLADA','Inventor','Lua51','Poco']]
        run('cmake','-S',ROOT,'-B',build,*flags)
        run('cmake','--build',build,'--parallel',a.jobs)
        run('cmake','--install',build)
        archives=sorted((prefix/'lib').rglob('*.a'))
        assert archives,'No installed static libraries'
        merged=build/'libOpenSceneGraph.a';run('xcrun','libtool','-static','-o',merged,*archives)
        built[label]={'prefix':prefix,'archive':merged,'archives':[x.name for x in archives]}
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    staging=out/'staging'
    if staging.exists():shutil.rmtree(staging)
    staging.mkdir();sim=staging/'libOpenSceneGraph.a'
    run('lipo','-create',built['simulator-arm64']['archive'],built['simulator-x86_64']['archive'],'-output',sim)
    headers=staging/'Headers';shutil.copytree(built['ios-arm64']['prefix']/'include',headers)
    (headers/'module.modulemap').write_text('module COpenSceneGraph { requires cplusplus\n header "OSGSPMHeaders.h"\n export *\n}\n')
    (headers/'OSGSPMHeaders.h').write_text('#pragma once\n#include <osg/Group>\n#include <osgDB/Registry>\n')
    config=headers/'osg/Config';config.write_text('#ifndef OSG_LIBRARY_STATIC\n#define OSG_LIBRARY_STATIC\n#endif\n'+config.read_text())
    artifact=out/'OpenSceneGraph.xcframework'
    if artifact.exists():shutil.rmtree(artifact)
    run('xcodebuild','-create-xcframework','-library',built['ios-arm64']['archive'],'-headers',headers,'-library',sim,'-headers',headers,'-output',artifact)
    notices=artifact/'Licenses';notices.mkdir()
    for name in ['LICENSE.txt','LICENSE','COPYING.txt','AUTHORS.txt']:
        if (ROOT/name).is_file():shutil.copy2(ROOT/name,notices/name)
    manifest={'source_revision':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
        'upstream_revision':'838cc974b28f8e738dc77199da71bd8b2073ed51','minimum_ios':'18.0','linkage':'static','plugins':PLUGINS,
        'dependencies':json.loads((ROOT/'apple/dependencies.json').read_text()),'archives':{k:v['archives'] for k,v in built.items()}}
    (out/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Created',artifact)
if __name__=='__main__':main()
