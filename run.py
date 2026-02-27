import sys
import pathlib
import uvicorn

# Ensure `src/` is on sys.path so `tt_agenda_v2` can be imported when running
# the project from the repository root (without installing the package).
root = pathlib.Path(__file__).resolve().parent
src_dir = str(root / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from tt_agenda_v2 import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
