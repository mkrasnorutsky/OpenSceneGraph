#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
import os
WORK=Path(os.environ.get("APPLE_BUILD_ROOT", str(ROOT))).expanduser().resolve()
p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
out=WORK/'dist';archive=out/'OpenSceneGraph.xcframework.zip'
if archive.exists():archive.unlink()
subprocess.run(['ditto','-c','-k','--sequesterRsrc','--keepParent',str(out/'OpenSceneGraph.xcframework'),str(archive)],check=True)
checksum=hashlib.sha256(archive.read_bytes()).hexdigest()
manifest=(ROOT/'apple/Package.local.swift').read_text().replace('path: "dist/OpenSceneGraph.xcframework"',f'url: "https://github.com/mkrasnorutsky/OpenSceneGraph/releases/download/{a.tag}/OpenSceneGraph.xcframework.zip", checksum: "{checksum}"')
(out/'Package.swift').write_text(manifest)
(out/'checksums.json').write_text(json.dumps({'OpenSceneGraph':checksum},indent=2)+'\n');print('Release prepared in',out)
