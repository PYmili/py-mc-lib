import os
import zipfile


class NativesEvent:
    def __init__(
            self, 
            jar_file: str, 
            native_output_dir: str = os.path.join(os.getcwd(), ".minecraft", "libraries")
        ) -> None:
        """
        Native Event / 解压.jar文件中的Native数据包
        :param jar_file: str 需要解压的.jar文件
        :param native_output_dir: str 解压至的目录
        :return None
        """
        if not os.path.isfile(jar_file):
            raise FileNotFoundError(f"{jar_file} 文件不存在！")
        
        self.jar_file = jar_file
        self.native_output_dir = native_output_dir

    def extract_dlls(self):
        with zipfile.ZipFile(self.jar_file, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith('.dll') is False:
                    continue

                # 如果是.dll文件，则解压
                source = zip_ref.open(member)
                target_path = os.path.join(self.native_output_dir, member)
                if not os.path.exists(os.path.dirname(target_path)):
                    os.makedirs(os.path.dirname(target_path))
                with open(target_path, 'wb') as out_file:
                    out_file.write(source.read())
                    out_file.close()
                source.close()
