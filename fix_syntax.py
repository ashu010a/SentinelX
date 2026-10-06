import re

with open('backend/models.py', 'r') as f:
    code = f.read()

# Fix the broken line
code = code.replace("status = Column(String, default=\\'OPEN\\')", "status = Column(String, default='OPEN')")
code = code.replace("\\'", "'")

with open('backend/models.py', 'w') as f:
    f.write(code)
