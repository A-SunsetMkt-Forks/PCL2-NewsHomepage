import json
import requests
import re
import os
from pathlib import Path

LAUNCHER_MANIFSET_URL = 'https://piston-meta.mojang.com/mc/game/version_manifest.json'

SNAPSHOT_PATTERN = re.compile(r'^[0-9]{2}[w|W][0-9]{2}[A-Za-z]$')
PRE_RELEASE_PATTERN = re.compile(r'^.*-pre[0-9]+$')
RELEASE_CANDIDATE_PATTERN = re.compile(r'^.*-rc[0-9]+$')
RELEASE_PATTERN = re.compile(r'^1\.[0-9]+(\.[0-9]+)?$')

CURRENT_MAJOR_DEVELOPING_VERSION = "1.21"
CURRENT_MINOR_DEVELOPING_VERSION = "1.21.9"

require_update = False

def get_version_type(vid:str):
    if re.match(SNAPSHOT_PATTERN,vid):
        return 'Snapshot'
    if re.match(PRE_RELEASE_PATTERN,vid):
        return 'Pre-Release'
    if re.match(RELEASE_CANDIDATE_PATTERN,vid):
        return 'Release-Candidate'
    if re.match(RELEASE_PATTERN,vid):
        return 'Release'
    return 'Others'

def generate_filepath(ver_type:str, ver_id:str):
    if ver_type == 'Snapshot':
        return Path(f'Snapshot/20{ver_id[:2]}/{ver_id}.md')
    if ver_type == 'Pre-Release':
        return Path(f'Pre-Release/{ver_id[:4]}/{ver_id}.md')
    if ver_type == 'Release-Candidate':
        return Path(f'Release-Candidate/{ver_id}.md')
    if ver_type == 'Release':
        return Path(f'Release/{ver_id}.md')

def update_library(version_mainfest, version_libloc:str, ver_type:str, ver_id:str):
    #gen content
    content = '---\n'
    content += 'version-image-link: null\n'
    #content += 'version-image-link-fallback: null\n'
    content += 'not_finished: true\n'
    content += f'server-jar: {get_server_jar(version_mainfest, ver_id)}\n'
    content += 'translator: null\n'
    content += f"cats: ['{CURRENT_MAJOR_DEVELOPING_VERSION}','{CURRENT_MINOR_DEVELOPING_VERSION}']\n"
    content += '---\n'
    #write file
    filepath = Path(version_libloc) / generate_filepath(ver_type, ver_id)
    if os.path.exists(filepath):
        #print(f'版本库内已存在 {ver_type} 版 {ver_id} 的文件，跳过添加')
        return False
    else:
        with open(filepath.absolute(), "w", encoding='UTF-8') as file:
            file.write(content)
        #print(f'已添加 {ver_type} 版 {ver_id} 的文件到版本库')
        return True

def get_server_jar(version_mainfest,version_id):
    versions = version_mainfest.get('versions')
    for version in versions:
        if version['id'] == version_id:
            response = requests.get(version['url'])
            return json.loads(response.content)['downloads']['server']['url']
    return None  

try:
    response = requests.get(LAUNCHER_MANIFSET_URL)
    VERSION_MAINFEST = json.loads(response.content)
except Exception as e:
    print(f'error_log={e.with_traceback()}')
    exit(1)

def main():
    latest_snapshot_id = VERSION_MAINFEST['latest']['snapshot']
    latest_release_id = VERSION_MAINFEST['latest']['release']

    latest_snapshot_type = get_version_type(latest_snapshot_id)
    latest_release_type = get_version_type(latest_release_id)

        #print(f'● 最新 {latest_release_type} 版: {latest_release_id}') 
        #print(f'● 最新 {latest_snapshot_type} 版: {latest_snapshot_id}') 

    dir_location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    version_lib_location = f'{dir_location}{os.sep}Project{os.sep}libraries{os.sep}Versions{os.sep}'

    release_require_update = \
    update_library(VERSION_MAINFEST,version_lib_location,
                latest_release_type,latest_release_id)
    snapshot_require_update = \
    update_library(VERSION_MAINFEST,version_lib_location,
                latest_snapshot_type,latest_snapshot_id)

    print(f'latest_release_type={latest_release_type}')
    print(f'latest_snapshot_type={latest_snapshot_type}')
    print(f'latest_release_id={latest_release_id}')
    print(f'latest_snapshot_id={latest_snapshot_id}')
    print(f'require_update={release_require_update or snapshot_require_update}')

if __name__ == '__main__':
    main()
