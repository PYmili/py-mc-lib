import os
import platform
from typing import Dict, Union
import requests
from loguru import logger
from .headers import HEDAERS
from .downloader import Downloader

# 获取系统名称
OS_NAME = platform.system().lower()


def libraries_interpreter(libraries_data: Dict) -> Union[list, None]:
    """
    Libraries interpreter / 解读器，用于packages中的资源处理。

    :param libraries_data: Dict 需要解读的数据
    :return Union[list, None]
    """
    result = []
    if not libraries_data:
        return result
    
    for libraries in libraries_data:
        rules = libraries.get("rules")
        if not rules:
            result.append(libraries)
            continue
        
        os = rules[0].get('os')
        if os is None:
            result.append(libraries)
            continue

        if os['name'] == OS_NAME:
            result.append(libraries)

    return result


def assets_interpreter(assets_url: Dict) -> Union[dict, None]:
    """
    Assets interpreter / 针对assets数据的解析

    :param assets_url: Dict 需要解读数据的url
    :return Union[list, None]
    """
    result = {}

    with requests.get(assets_url, headers=HEDAERS) as response:
        if response.status_code != 200:
            logger.error("获取assets的json数据时出现错误！")
            return None
        
        assets_json: dict = response.json()    
        for key, values in assets_json.items():
            result[key] = []
            for _, filedata in values.items():
                hash = filedata['hash']
                result[key].append({
                    "path": os.path.join(hash[0:2], hash),
                    "url": f"https://resources.download.minecraft.net/{hash[0:2]}/{hash}"
                })

    return result


class PackagesDownload:
    def __init__(
            self,
            version_url: str,
            to_dir: str = os.path.join(os.getcwd(), ".minecraft")
        ) -> None:
        """
        PackagesDownland / 游戏数据下载
        :param version_url: str 版本json的url
        """
        self.version_url = version_url
        self.to_dir = to_dir
        if os.path.isdir(to_dir) is False:
            try:
                os.makedirs(to_dir)
            except Exception as e:
                logger.error(e)

    def start(self) -> bool:
        """
        start / 开始
        :return bool
        """
        try:
            os.makedirs(os.path.join(self.to_dir, "libraries"))
            os.makedirs(os.path.join(self.to_dir, "assets"))
        except Exception as e:
            logger.error(e)

        with requests.get(self.version_url, headers=HEDAERS) as response:
            if response.status_code != 200:
                return False
            packages_json = response.json()            
            libraries_interpreter_result = libraries_interpreter(packages_json['libraries'])
            if not libraries_interpreter_result:
                return False
            
            if self.download_libraries(libraries_interpreter_result) is False:
                logger.error("libraries下载失败！")
                return False
            
            assets_interpreter_result = assets_interpreter(packages_json['assetIndex']['url'])
            if self.download_assets(assets_interpreter_result, packages_json['assetIndex']) is False:
                logger.error("assets下载失败！")
                return False
    
        return True

    def download_libraries(self, libraries_list: list) -> bool:
        """
        Download libraries / 下载librares数据
        :return bool
        """
        logger.info("Download Libraries")
        # 为多线程下载 libraries 创建任务
        libraries_download_tasks = []
        for libraries in libraries_list:
            classifiers = libraries['downloads'].get("classifiers")
            natives_osname = None
            if classifiers is not None:
                natives_osname = classifiers.get(f"natives-{OS_NAME}")
            if natives_osname is not None:
                libraries_download_tasks.append((
                    natives_osname['url'],
                    os.path.join(self.to_dir, "libraries", natives_osname['path'])
                ))

            artfact = libraries['downloads'].get('artifact')
            if artfact is not None:
                libraries_download_tasks.append((
                    artfact['url'],
                    os.path.join(self.to_dir, "libraries", libraries['downloads']['artifact']['path'])
                ))

        # 多线程下载器开始下载 libraries
        downloader = Downloader(libraries_download_tasks)
        downloader.download_files_with_threads()
        return True
        
    def download_assets(self, assets_list: dict, assetIndex: dict) -> bool:
        """
        Download assets / 下载assets数据
        :return bool
        """
        logger.info("Download Assets")
        # 为多线程下载 assets 创建任务
        assets_download_tasks = []
        for keys, values in assets_list.items():
            for value in values:
                assets_download_tasks.append((
                    value['url'],
                    os.path.join(self.to_dir, "assets", keys, value['path'])
                ))

        assets_download_tasks.append((
            assetIndex['url'],
            os.path.join(self.to_dir, "assets", "indexes", assetIndex['id']+".json")
        ))
        
        # 多线程下载器开始下载 assets
        downloader = Downloader(assets_download_tasks)
        downloader.download_files_with_threads()
        return True