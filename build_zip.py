"""
Builds CareerCompass_AI_Windows.zip directly from source files.
"""

import os
import zipfile

def build_zip():
    archive_name = "CareerCompass_AI_Windows.zip"
    files_to_pack = [
        "app.py",
        "career_engine.py",
        "chatbot.py",
        "storage.py",
        "requirements.txt",
        "README.md",
        "run.bat",
        "test.bat",
        ".gitignore",
        os.path.join("data", "careers.csv"),
        os.path.join("templates", "index.html"),
        os.path.join("static", "style.css"),
        os.path.join("static", "app.js"),
        os.path.join("tests", "test_career_engine.py"),
        os.path.join("tests", "test_api.py"),
        os.path.join("tests", "test_storage.py"),
        os.path.join("tests", "test_chatbot.py")
    ]

    with zipfile.ZipFile(archive_name, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files_to_pack:
            if os.path.exists(f):
                # Archive with forward slashes for cross-platform compatibility
                arcname = os.path.join("CareerCompass_AI", f).replace("\\", "/")
                zf.write(f, arcname)
                print(f"Added {f} -> {arcname}")
            else:
                print(f"Warning: {f} not found!")

    size = os.path.getsize(archive_name)
    print(f"\nSuccessfully built {archive_name} ({size:,} bytes)")

if __name__ == "__main__":
    build_zip()
