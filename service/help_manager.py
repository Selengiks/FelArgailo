from typing import Dict, Optional


class HelpManager:
    _help_sections: Dict[str, str] = {}

    @classmethod
    def register_help(cls, module_name: str, help_text: str) -> None:
        """Реєструє довідку для модуля"""
        cls._help_sections[module_name] = help_text

    @classmethod
    def unregister_help(cls, module_name: str) -> None:
        """Видаляє довідку для модуля"""
        cls._help_sections.pop(module_name, None)

    @classmethod
    def get_help(cls, module_name: Optional[str] = None) -> str:
        """Повертає довідку для конкретного модуля або всю довідку"""
        if module_name:
            return cls._help_sections.get(
                module_name, "Довідка для цього модуля відсутня"
            )

        if not cls._help_sections:
            return "Довідка відсутня"

        full_help = "**Кібер-Фелікс**:\n__Система довідки__\n\n"
        for section in cls._help_sections.values():
            full_help += f"{section}\n\n"
        return full_help.strip()
