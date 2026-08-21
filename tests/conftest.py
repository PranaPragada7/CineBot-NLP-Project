import os

# Importing src.app constructs the ASGI application. Individual tests inject their
# own repository instances; this flag only makes that module-level test app usable.
os.environ.setdefault("AUTO_CREATE_SCHEMA", "true")
