import os
import importlib
from loguru import logger


class PluginManager:
    # name -> module object
    successful_modules: dict[str, object] = {}
    # list of (name, error)
    problematic_modules: list[tuple[str, str]] = []
    # set of disabled module names
    disabled_modules: set[str] = set()

    @classmethod
    def load_modules(cls):
        modules_dir = "modules"
        disabled_modules_dir = "modules/disabled"

        module_files = [
            file_name
            for file_name in os.listdir(modules_dir)
            if file_name.endswith(".py") and not file_name.startswith("__")
        ]

        cls.successful_modules.clear()
        cls.problematic_modules.clear()
        cls.disabled_modules = {
            os.path.splitext(file_name)[0]
            for file_name in os.listdir(disabled_modules_dir)
            if file_name.endswith(".py")
        }

        for file_name in module_files:
            module_name = file_name[:-3]

            # Skip disabled modules
            if module_name in cls.disabled_modules:
                logger.info(f"Модуль {module_name} вимкнений, пропускаю...")
                continue

            module_path = f"{modules_dir}.{module_name}"

            try:
                module = importlib.import_module(module_path)

                if not hasattr(module, "start_module"):
                    raise AttributeError("Модуль не має start_module() метода.")

                module.start_module()

                cls.successful_modules[module_name] = module
                logger.success(f"Модуль ініціалізовано: {module_name}")

            except Exception as e:
                cls.problematic_modules.append((module_name, str(e)))
                logger.error(f"Помилка ініціалізації модуля {module_name}: {e}")

        logger.info(
            f"Плагіни ініціалізовано: "
            f"{len(cls.successful_modules)} успішно, "
            f"{len(cls.problematic_modules)} з помилкою, "
            f"{len(cls.disabled_modules)} вимкнено"
        )

    # ====== Accessors ======

    @classmethod
    def get_successful_modules(cls) -> dict[str, object]:
        return cls.successful_modules

    @classmethod
    def get_problematic_modules(cls) -> list[tuple[str, str]]:
        return cls.problematic_modules

    @classmethod
    def get_disabled_modules(cls) -> set[str]:
        return cls.disabled_modules
