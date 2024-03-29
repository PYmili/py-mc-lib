import os
import concurrent.futures
import requests
from loguru import logger

class Downloader:
    def __init__(self, tasks: list) -> None:
        """
        Downloader / 下载器用于多线程下载文件。

        :param tasks: tasks是一个包含元组的列表，每个元组为(url, target_path)
        """
        self.tasks = tasks

    def download_file(self, url: str, target_path: str):
        if os.path.isdir(os.path.split(target_path)[0]) is False:
            try:
                os.makedirs(os.path.split(target_path)[0])
            except Exception as e:
                logger.error(e)

        if os.path.isfile(target_path) is True:
            return

        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(target_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                logger.info(f'{url} downloaded successfully to {target_path}')
            else:
                logger.error(f'Failed to download {url}, status code: {response.status_code}')
        except Exception as e:
            logger.error(f'Error occurred while downloading {url}: {e}')

    def download_files_with_threads(self, max_workers=None):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.download_file, url, target_path): (url, target_path) for url, target_path in self.tasks
                }
            
            for future in concurrent.futures.as_completed(futures):
                url, target_path = futures[future]
                try:
                    future.result()  # 获取结果，如果下载过程中有异常，这里会重新抛出
                except Exception as exc:
                    logger.error(f'Thread for {url} generated an exception: {exc}')


# 使用示例：
# file_urls_and_paths = [('http://example.com/file1.zip', 'file1.zip'), ('http://example.com/file2.zip', 'file2.zip')]
# downloader = Downloader(file_urls_and_paths)
# downloader.download_files_with_threads(5)  # 同时最多开启5个线程下载