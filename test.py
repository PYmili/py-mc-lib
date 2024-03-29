from py_mc_lib import version_manifest
from py_mc_lib import packages
from py_mc_lib import JavaClient
from py_mc_lib import LauncherEvent

# vm = version_manifest.VersionManifest()
# print(vm.get_versions())
# print(vm.get_latest())

# pd = packages.PackagesDownload(version_url=vm.by_version_get("1.20.4"))
# pd.start()

# JavaClient.DownloadClinet("1.20.2")

cmd = LauncherEvent.Launcher("1.20.2", ".minecraft")
cmd.start_game()