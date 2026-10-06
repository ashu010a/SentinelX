"""Import all models so they register with Base.metadata."""

from app.models.project import Project  # noqa: F401
from app.models.asset import Asset  # noqa: F401
from app.models.service import Service  # noqa: F401
from app.models.endpoint import Endpoint  # noqa: F401
from app.models.vulnerability import Vulnerability  # noqa: F401
from app.models.scan_job import ScanJob  # noqa: F401
