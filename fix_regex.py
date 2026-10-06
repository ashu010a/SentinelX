with open('backend/app/ai/ai_context.py', 'r') as f:
    code = f.read()

# Just replace the whole list assignment
code = code.replace(
    r"""SECRET_PATTERNS = [
    r'(?i)(api[_-]?key|password|secret|token)[\s:=]+(["'\w\-]+)'
]""",
    """SECRET_PATTERNS = [
    r'(?i)(api[_-]?key|password|secret|token)[\\\\s:=]+([a-zA-Z0-9]+)'
]"""
)

with open('backend/app/ai/ai_context.py', 'w') as f:
    f.write(code)
