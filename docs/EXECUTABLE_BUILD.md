# Building Executable Guide

## 📦 Approach Summary

This project is structured to be easily converted to standalone executables using **PyInstaller**.

### Why This Approach?

✅ **Tkinter** - Standard library, no extra dependencies  
✅ **Single entry point** - `gui.py` or `main.py`  
✅ **Clean architecture** - Core logic separated from UI  
✅ **Assets bundled** - Sound files included automatically  
✅ **Cross-platform** - Works on Windows, macOS, Linux  

## 🚀 Quick Build

```bash
# Install build dependencies
uv sync --group build

# Build executable (uses src/__main__.py as entry point)
python build.py
```

The executable supports both interfaces:
```bash
./dist/FreeTimer            # Terminal interface (default)
./dist/FreeTimer --gui      # GUI interface
./dist/FreeTimer --debug    # With debug logging
```

## 📁 Output

- **Linux/macOS**: `dist/FreeTimer`
- **Windows**: `dist/FreeTimer.exe`

## 🛠️ Build Options

### PyInstaller Configuration (in `build.py`)

```python
-m src          # Use unified entry point (src/__main__.py)
--onefile       # Single executable file
--windowed      # No console window (GUI mode)
--add-data      # Include Assets/Sounds folder
--icon          # Application icon (optional)
```

### Manual Build

```bash
pyinstaller --name=FreeTimer \
            --onefile \
            --windowed \
            --add-data="Assets/Sounds:Assets/Sounds" \
            -m src
```

## 🎯 Best Practices for Executable Conversion

### 1. **Use Standard Library When Possible**
- ✅ Tkinter (GUI)
- ✅ threading, dataclasses, logging
- ❌ Avoid heavy frameworks (Qt, Electron)

### 2. **Separate Business Logic from UI**
```
src/
  core/          # Pure business logic (reusable)
  services/      # Application services
  interfaces/    # UI layers (swappable)
```

### 3. **Handle Assets Correctly**
```python
# Use relative paths from entry point
ASSETS_DIR = Path(__file__).parent / "Assets" / "Sounds"
```

### 4. **Entry Point Design**
- ✅ **Unified entry point**: `src/__main__.py`
- ✅ **Interface selection**: via `--gui` flag
- Keep entry point simple
- Parse arguments early
- Initialize services
- Launch appropriate interface

### 5. **Dependencies Management**
```toml
[project]
dependencies = [
    "playsound3",  # Only essential runtime deps
    "rich",
]

[dependency-groups]
build = ["pyinstaller"]  # Separate build tools
```

## 📊 Executable Size Comparison

| Approach | Typical Size | Pros | Cons |
|----------|-------------|------|------|
| **Tkinter + PyInstaller** | 15-25 MB | ✅ Small, fast | Limited styling |
| Qt + PyInstaller | 100-150 MB | ✅ Modern UI | Large size |
| Electron | 150-200 MB | ✅ Web tech | Very large |

## 🔄 Development Workflow

```bash
# Development - Terminal
python -m src --debug

# Development - GUI
python -m src --gui --debug

# Testing
pytest tests/ -v

# Build
python build.py

# Test executable - Terminal
./dist/FreeTimer

# Test executable - GUI
./dist/FreeTimer --gui
```

## 🐛 Troubleshooting

### Missing Modules
```bash
# Add hidden imports to build.py
--hidden-import=module_name
```

### Assets Not Found
```bash
# Verify data files
--add-data="source:destination"
```

### Icon Not Working
```bash
# Create icon.ico (Windows) or icon.icns (macOS)
--icon=path/to/icon.ico
```

## 🌟 Advantages of Current Structure

1. **Multiple Interfaces**: Terminal, GUI, Web (future) share core logic
2. **Easy Testing**: Core logic isolated from UI
3. **Small Executables**: Minimal dependencies
4. **Fast Build**: Simple structure, quick compilation
5. **Professional**: Standard patterns, maintainable code

## 🔮 Future Considerations

### For Even Smaller Executables
- Use **Nuitka** instead of PyInstaller (compiles to C)
- Remove unused stdlib modules
- Compress with UPX

### For Better Distribution
- Create installers (NSIS for Windows, DMG for macOS)
- Code signing certificates
- Auto-update mechanism

---

**Current Recommendation**: Stick with Tkinter + PyInstaller for best balance of size, compatibility, and ease of use.
