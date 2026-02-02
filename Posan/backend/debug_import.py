
try:
    from app.core import security
    print("Successfully imported app.core.security")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
