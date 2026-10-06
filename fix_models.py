import re
with open('backend/models.py', 'r') as f:
    code = f.read()

if "criticality = " not in code:
    code = code.replace("is_live = Column(Boolean, default=True)", "is_live = Column(Boolean, default=True)\n    criticality = Column(String, default='medium')\n    exposed = Column(Boolean, default=False)")

if "confidence = " not in code:
    code = code.replace("kev = Column(Boolean, default=False)", "kev = Column(Boolean, default=False)\n    epss = Column(Float, default=0.0)\n    confidence = Column(String, default='certain')")

with open('backend/models.py', 'w') as f:
    f.write(code)
