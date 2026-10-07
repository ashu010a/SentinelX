import os
for root, _, files in os.walk('.'):
    for file in files:
        if file.startswith('verify_') and file.endswith('.py') or file == 'final_e2e_test.py':
            path = os.path.join(root, file)
            with open(path, 'r') as f: content = f.read()
            content = content.replace('"/api/', '"/api/v1/')
            # Also fix SessionLocal -> SyncSessionLocal
            content = content.replace('SessionLocal()', 'SyncSessionLocal()')
            content = content.replace('from app.database import SessionLocal', 'from app.database import SyncSessionLocal')
            
            with open(path, 'w') as f: f.write(content)
