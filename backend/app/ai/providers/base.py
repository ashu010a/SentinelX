from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str) -> dict:
        pass
    @abstractmethod
    def health_check(self) -> bool:
        pass
