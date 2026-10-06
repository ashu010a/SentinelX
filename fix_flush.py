with open('backend/importers.py', 'r') as f:
    code = f.read()

code = code.replace("db.add(finding)\n                        # Add masked evidence", "db.add(finding)\n                        db.flush()\n                        # Add masked evidence")

with open('backend/importers.py', 'w') as f:
    f.write(code)
