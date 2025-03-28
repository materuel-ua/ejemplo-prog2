source .venv/bin/activate
pyinstaller -F example.py
cp config.json dist/config.json
rm -rf build
rm example.spec
deactivate