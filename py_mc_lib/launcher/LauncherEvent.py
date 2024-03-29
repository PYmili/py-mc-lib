import os
import json
import platform
import subprocess
from typing import Union
from loguru import logger
from . import natives

UUID = "0000000000003006998F555B76269803"
ACCESSTOKEN = "0000000000003006998F555B76269803"
OS_NAME = platform.system().lower()
JVM_DEF = "-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump"


class Launcher:
    def __init__(
            self,
            game_version: str,
            game_dir: str,
            java_path: str = None,
            options: dict = {}
        ) -> None:
        """
        launcher / 游戏启动器
        :param game_version: str 游戏版本
        :param game_dir: str 游戏路径
        :param java_path: str java路径
        :param options: dict 其他参数
        """
        self.java_path = java_path
        self.game_version = game_version
        self.game_dir = game_dir
        self.options = options
        self.libraries_directory = os.path.join(game_dir, "libraries")
        self.natives_directory = os.path.join(
            game_dir, "versions", game_version, "natives"
        
        )
        if os.path.isdir(game_dir) is False:
            raise FileNotFoundError(f"未找到路径：{self.game_dir}")
        
        self.game_version_json = os.path.join(
            self.game_dir, "versions", 
            self.game_version, self.game_version+".json"
        )
        if os.path.isfile(self.game_version_json) is False:
            raise Exception("游戏目录缺少版本json文件。")

    def start_game(self) -> None:
        """
        start game / 启动游戏
        :return None
        """
        result = self.GenerateCommand()
        if not result:
            return None
        # print("\n".join(result))
        # print(result)
        subprocess.run(result)

    def get_java_path(self) -> None:
        if not self.java_path:
            try:
                output = subprocess.check_output(['where', 'java'], stderr=subprocess.DEVNULL)
                java_executable = output.decode().strip()
                java_executable = os.path.dirname(java_executable)
            except subprocess.CalledProcessError:
                return None
            self.java_path = os.path.join(java_executable, "java.exe")
        
    def GenerateCommand(self) -> Union[str, None]:
        """
        Generate Command / 生成启动命令
        :return Union[str, None]
        """
        # 默认参数初始化
        self.get_java_path()
        self.options[self.java_path] = ""
        self.options["-XX:+UseG1GC"] = ""
        self.options["-XX:-UseAdaptiveSizePolicy"] = ""
        self.options["-XX:-OmitStackTraceInFastThrow"] = ""
        self.options["-Dfml.ignoreInvalidMinecraftCertificates=True"] = ""
        self.options["-Dfml.ignorePatchDiscrepancies=True"] = ""
        self.options["-Dlog4j2.formatMsgNoLookups=true"] = ""
        self.options[JVM_DEF] = ""

        # 读取游戏版本的json文件
        with open(self.game_version_json, "r", encoding="utf-8") as rfp:
            version_json: dict = json.loads(rfp.read())
        if not version_json:
            raise AttributeError("版本json文件数据为空。")
        
        # 读取arguments中的命令行格式，版本<1.16.x将跳过。
        arguments = version_json.get('arguments')
        if arguments is not None:
            for jvm in arguments['jvm']:
                if type(jvm) != dict:
                    split_jvm = jvm.split("${")
                    if split_jvm[-1].strip("}") == "natives_directory":
                        self.options[f"{split_jvm[0]}{self.natives_directory}"] = ""
                    continue
                
                if jvm['rules'][0]['os'].get('name') != OS_NAME:
                    continue

                rules_version = jvm['rules'][0].get('version')
                if (rules_version is not None) and (platform.release().strip() not in rules_version):
                    continue
                    
                if type(jvm['value']) != list:
                    self.options[jvm['value']] = ""
                    continue

                for jvm_value in jvm['value']:
                    self.options[jvm_value] = ""
                    
        # 启动器版本（暂未设置自定义）
        float_game_version = float(".".join(self.game_version.split(".")[0:2]))
        if float_game_version > 1.12:
            self.options["-Dminecraft.launcher.brand=py_mc_lib"] = ""
            self.options["-Dminecraft.launcher.version=1"] = ""
        else:
            # 此处补充natives
            self.options[f"-Djava.library.path={self.natives_directory}"] = ""

        # -cp 有使用的所有libraries，使用";"分割
        cp = []
        for libraries in version_json['libraries']:
            rules = libraries.get('rules')
            if rules is not None:
                if len(rules) == 2:
                    if rules[-1]['action'] != "disallow":
                        print(True)
                        continue
                else:
                    if rules[0]['os']['name'] != OS_NAME:
                        continue

            # 载入natives
            classifiers = libraries['downloads'].get("classifiers")
            natives_osname = None
            if classifiers is not None:
                natives_osname = classifiers.get(f'natives-{OS_NAME}')
            if natives_osname is not None:
                natives_file = os.path.join(self.libraries_directory, natives_osname['path'])
                if os.path.isfile(natives_file) is False:
                    continue
                if float_game_version > 1.12:
                    cp.append(natives_file)
                    continue
                
                # 解压natives
                if os.path.isdir(self.natives_directory) is False:
                    try:
                        os.makedirs(self.natives_directory)
                    except Exception as e:
                        raise e
                natives.NativesEvent(natives_file, self.natives_directory).extract_dlls()

            # 将artifact中的librarie载入
            artifact = libraries['downloads'].get('artifact')
            if not artifact:
                continue
            librarie_file_path = os.path.join(self.libraries_directory, artifact['path'])
            if os.path.isfile(librarie_file_path) is True:
                cp.append(librarie_file_path)
        # 载入固定值，游戏本体。
        cp.append(os.path.join(self.game_dir, "versions", self.game_version, self.game_version+".jar"))
        self.options['-cp'] = ";".join(cp)

        # 载入固定值（暂未制作自定义）
        # self.options["-Xmn256m"] = ""
        # self.options["-Xmx1024m"] = ""
        self.options["-Dlog4j2.formatMsgNoLookups=true"] = ""
        self.options["--add-exports"] = "cpw.mods.bootstraplauncher/cpw.mods.bootstraplauncher=ALL-UNNAMED"
        self.options[version_json['mainClass']] = ""

        # 载入游戏名称，可自定义
        if self.options.get("username"):
            self.options['--username'] = self.options.get("username")
            del self.options['username']
        else:
            self.options['--username'] = "Test"

        # 载入启动固定值
        self.options["--version"] = self.game_version
        self.options["--gameDir"] = self.game_dir
        self.options["--assetsDir"] = os.path.join(self.game_dir, "assets")
        self.options["--assetIndex"] = version_json['assetIndex']['id']
        self.options['--uuid'] = UUID
        self.options['--accessToken'] = ACCESSTOKEN
        self.options['--userType'] = 'msa'
        self.options['--versionType'] = 'release'
        self.options["--width 854"] = ""
        self.options["--height 480"] = ""

        # 处理命令
        result = []
        for key, value in self.options.items():
            if not value:
                result.append(key)
                continue
            result.append(key)
            result.append(value)

        return result
    