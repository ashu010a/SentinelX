import os

env_path = 'backend/alembic/env.py'
with open(env_path, 'r') as f:
    content = f.read()

# Replace metadata
content = content.replace(
    'target_metadata = None',
    'import sys\nsys.path.insert(0, ".")\nfrom app.database import Base\nfrom app.models.schema import *\ntarget_metadata = Base.metadata'
)

# Replace DB URL dynamically
url_injector = """
from app.config import get_settings
config.set_main_option("sqlalchemy.url", get_settings().sync_database_url)

if context.is_offline_mode():
"""
content = content.replace('if context.is_offline_mode():', url_injector)

with open(env_path, 'w') as f:
    f.write(content)
