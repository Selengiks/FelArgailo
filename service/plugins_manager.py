# service/plugins_manager.py

import os
import importlib
from loguru import logger


class PluginManager:
    @staticmethod
    def load_modules():
        modules_dir = "modules"
        disabled_modules_dir = "modules/disabled"
        module_files = [
            file_name
            for file_name in os.listdir(modules_dir)
            if file_name.endswith(".py") and not file_name.startswith("__")
        ]

        successful_modules = []
        problematic_modules = []
        disabled_modules = set(os.listdir(disabled_modules_dir))

        for module_name in module_files:
            module_path = f"{modules_dir}.{module_name[:-3]}"
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, "start_module"):
                    module.start_module()
                    successful_modules.append(module_name[:-3])
                else:
                    raise AttributeError("Module does not have start_module attribute.")
            except Exception as e:
                problematic_modules.append((module_name[:-3], str(e)))
                logger.error(f"Failed to load module {module_name[:-3]}: {e}")

        logger.info(
            f"Plugins started: "
            f"{len(successful_modules)} successful, "
            f"{len(problematic_modules)} with problems, "
            f"{len(disabled_modules)} disabled"
        )


def load_modules():
    PluginManager.load_modules()
