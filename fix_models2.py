import re
with open('backend/models.py', 'r') as f:
    code = f.read()

# Add to Asset
code = code.replace(
    "value = Column(String, index=True)",
    "value = Column(String, index=True)\n    criticality = Column(String, default='medium')\n    exposed = Column(Boolean, default=False)"
)

# Add to Finding
code = code.replace(
    "cvss = Column(Float, nullable=True)",
    "cvss = Column(Float, nullable=True)\n    kev = Column(Boolean, default=False)\n    epss = Column(Float, default=0.0)\n    confidence = Column(String, default='certain')"
)

with open('backend/models.py', 'w') as f:
    f.write(code)
