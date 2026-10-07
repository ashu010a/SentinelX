with open('backend/Dockerfile', 'r') as f:
    content = f.read()

content = content.replace('CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]', 'CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers')

with open('backend/Dockerfile', 'w') as f:
    f.write(content)
