import os
from abc import ABC, abstractmethod

class StorageProvider(ABC):
    @abstractmethod
    def save(self, file_id: str, content: str) -> str:
        pass

class LocalStorageProvider(StorageProvider):
    # WARNING: Local disk is ephemeral in environments like Railway/Heroku.
    # Reports generated locally will be lost on container restart.
    def __init__(self):
        os.makedirs("exports", exist_ok=True)
        
    def save(self, file_id: str, content: str) -> str:
        path = f"exports/{file_id}"
        with open(path, "w") as f:
            f.write(content)
        return path

# Future implementation: S3StorageProvider
def get_storage_provider() -> StorageProvider:
    return LocalStorageProvider()
