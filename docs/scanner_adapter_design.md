# Scanner Adapter Design

## Principles
1. **Decoupling:** The core backend does not know how Nuclei or Nmap works.
2. **Normalization:** Every scanner must output a standardized Python object (Pydantic).

## Base Interface
```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class NormalizedFinding(BaseModel):
    title: str
    severity: str
    asset_identifier: str
    raw_evidence: str

class BaseScannerAdapter(ABC):
    @abstractmethod
    def build_command(self, target: str) -> list[str]:
        pass

    @abstractmethod
    def parse_output(self, raw_output: str) -> list[NormalizedFinding]:
        pass
```
