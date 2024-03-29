import os
import json
import requests
from loguru import logger

from .headers import HEDAERS
from .packages import PackagesDownload
from .version_manifest import VersionManifest


class DownloadClinet:
    def __init__(
            self,
            version: str,
            to_dir: str = os.path.join(os.getcwd(), ".minecraft")
        ) -> None:
        """
        Download Client
        :param version: 需要下载的版本
        :param to_dir: 下载到，默认当前文件夹。
        """
        if os.path.isdir(to_dir) is False:
            try:
                os.makedirs(to_dir)
            except Exception as e:
                logger.error(e)
        
        # 下载游戏客户端本体
        logger.info(f"开始下载游戏本体：{version}.jar")
        json_url = VersionManifest().by_version_get(version)
        if not json_url:
            raise Exception("获取游戏版本的 json url 失败！")

        with requests.get(json_url, headers=HEDAERS) as response:
            if response.status_code != 200:
                raise Exception("获取游戏版本的数据失败！")
            version_json = response.json()
            version_downlaod_url = version_json['downloads']['client']['url']
        
        if not version_downlaod_url:
            raise Exception("获取游戏本体失败！")
        
        versions_path = os.path.join(to_dir, "versions", version)
        if os.path.isdir(versions_path) is False:
            os.makedirs(versions_path)

        # 保存json文件
        with open(os.path.join(versions_path, f"{version}.json"), "w+", encoding="utf-8") as wfp:
            wfp.write(json.dumps(version_json, indent=4))
        # 下载.jar文件
        with requests.get(version_downlaod_url, headers=HEDAERS, stream=True) as response:
            with open(os.path.join(versions_path, f"{version}.jar"), "wb+") as wfp:
                for chunk in response.iter_content(chunk_size=1024):
                    wfp.write(chunk)
        logger.info(f"游戏本体 “{version}.jar” 下载成功！")

        # 下载游戏数据包
        PackagesDownloadResult = PackagesDownload(json_url, to_dir).start()
        if PackagesDownloadResult is False:
            raise Exception("资源文件下载失败！")