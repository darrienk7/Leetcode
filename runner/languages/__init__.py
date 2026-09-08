from runner.languages.base import LanguageAdapter
from runner.languages.cpp import CppAdapter
from runner.languages.java import JavaAdapter
from runner.languages.python import PythonAdapter


ADAPTERS: dict[str, LanguageAdapter] = {
    "cpp": CppAdapter(),
    "java": JavaAdapter(),
    "python": PythonAdapter(),
}


def get_adapter(language: str) -> LanguageAdapter:
    try:
        return ADAPTERS[language.lower()]
    except KeyError as error:
        supported = ", ".join(sorted(ADAPTERS))
        raise ValueError(
            f"Unsupported language {language!r}; currently available: {supported}"
        ) from error
