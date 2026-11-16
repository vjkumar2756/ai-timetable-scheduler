"""
streamlit_app.py
Root entry point executing frontend/app.py on every Streamlit rerun cycle.
Ensures module cache freshness across hot reloads.
"""
import os
import sys
import importlib

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Evict cached frontend views from sys.modules so code changes reflect immediately
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith("frontend.views.") or mod_name in ("frontend.theme", "frontend.api_client"):
        del sys.modules[mod_name]

app_path = os.path.join(BASE_DIR, "frontend", "app.py")
with open(app_path, "r", encoding="utf-8") as f:
    code = compile(f.read(), app_path, "exec")
    exec(code, globals())
