try:
    from app.models import User
    print("SUCCESS: Models imported")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
