from typing import List, Dict, Union
import requests
from .headers import HEDAERS


VERSION_MANIFEST_JSON_URL = "https://piston-meta.mojang.com/mc/game/version_manifest.json"

class VersionManifest:
    def __init__(self) -> None:
        with requests.get(VERSION_MANIFEST_JSON_URL, headers=HEDAERS) as response:
            if response.status_code == 200:
                self.versions_json = response.json()
            else:
                raise requests.RequestException(
                    f"No JSON data obtained / 未获取到json数据 | url: {VERSION_MANIFEST_JSON_URL}"
                    )
                self.versions_json = None
    
    def get_versions(self) -> List[str]:
        """
        Get Versions / 获取到所有版本
        :return List[str]
        """
        result = []
        if not self.versions_json:
            return result
        
        for versions in self.versions_json['versions']:
            result.append(versions['id'])
        
        return result

    def get_latest(self) -> Dict:
        """
        Get latest Version / 获取到最新版本
        :return Dict[str]
        """
        if not self.versions_json:
            return {}
        
        return self.versions_json['latest']
    
    def by_version_get(self, version: str) -> Union[str, None]:
        """
        By Version Get Url / 通过版本号获取url
        :return Union[str, None]
        """
        if not self.versions_json:
            return None
        
        for versions in self.versions_json['versions']:
            if versions['id'] == version:
                return versions['url']
            
        return None
    