import os
import importlib
from loguru import logger


class PluginManager:
    successful_modules = []
    problematic_modules = []
    disabled_modules = set()

    @classmethod
    def load_modules(cls):
        modules_dir = "modules"
        disabled_modules_dir = "modules/disabled"
        module_files = [
            file_name
            for file_name in os.listdir(modules_dir)
            if file_name.endswith(".py") and not file_name.startswith("__")
        ]

        cls.successful_modules = []
        cls.problematic_modules = []
        cls.disabled_modules = set(
            os.path.splitext(file_name)[0]
            for file_name in os.listdir(disabled_modules_dir)
        )

        # Clear all help sections before loading
        from service.help_manager import HelpManager

        HelpManager._help_sections.clear()

        for module_name in module_files:
            module_path = f"{modules_dir}.{module_name[:-3]}"
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, "start_module"):
                    module.start_module()
                    cls.successful_modules.append(module_name[:-3])
                else:
                    raise AttributeError("Module does not have start_module attribute.")
            except Exception as e:
                cls.problematic_modules.append((module_name[:-3], str(e)))
                logger.error(f"Failed to load module {module_name[:-3]}: {e}")

        logger.info(
            f"Plugins started: "
            f"{len(cls.successful_modules)} successful, "
            f"{len(cls.problematic_modules)} with problems, "
            f"{len(cls.disabled_modules)} disabled"
        )

    @classmethod
    def get_successful_modules(cls):
        return cls.successful_modules

    @classmethod
    def get_problematic_modules(cls):
        return cls.problematic_modules

    @classmethod
    def get_disabled_modules(cls):
        return cls.disabled_modules
