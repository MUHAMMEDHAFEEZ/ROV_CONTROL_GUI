# ROV Control GUI - Release Instructions

This guide will help you create a release with an executable file for the ROV Control GUI.

## Prerequisites

1. Python 3.9+ installed
2. Git installed and repository cloned
3. All dependencies installed

## Building the Executable Locally

### Step 1: Install Build Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-build.txt
```

### Step 2: Build the Executable

```bash
python build_exe.py
```

This will create:
- `dist/ROV_Control_GUI.exe` - The main executable
- `dist/install.bat` - Installation script for system-wide installation

### Step 3: Test the Executable

1. Navigate to the `dist` folder
2. Run `ROV_Control_GUI.exe` to test functionality
3. Verify all features work correctly

## Creating a GitHub Release

### Method 1: Automatic Release (Recommended)

1. **Create and push a tag:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **GitHub Actions will automatically:**
   - Build the executable
   - Create a release
   - Upload the files

### Method 2: Manual Release

1. **Build locally** (steps above)

2. **Create release on GitHub:**
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Tag version: `v1.0.0`
   - Release title: `ROV Control GUI v1.0.0`

3. **Upload files:**
   - `ROV_Control_GUI.exe`
   - `install.bat`
   - `config.ini`
   - `README.md`

## Release Checklist

- [ ] All features tested and working
- [ ] Version number updated in `main.py`
- [ ] README.md updated with latest features
- [ ] All dependencies listed in requirements.txt
- [ ] Executable builds without errors
- [ ] Executable runs on clean Windows system
- [ ] GitHub Actions workflow passes
- [ ] Release notes written

## Troubleshooting Build Issues

### Common Issues:

1. **Missing modules:**
   - Add hidden imports to `build_exe.py`
   - Example: `--hidden-import=missing_module`

2. **Large executable size:**
   - Use `--exclude-module` for unnecessary modules
   - Consider using `--onedir` instead of `--onefile`

3. **Runtime errors:**
   - Test on clean system
   - Include all required data files with `--add-data`

### Build Optimization:

```python
# In build_exe.py, add these options:
'--exclude-module=tkinter',
'--exclude-module=matplotlib.tests',
'--exclude-module=numpy.tests',
```

## Version Management

Update version numbers in:
- `main.py` (line ~19): `app.setApplicationVersion("1.0.0")`
- GitHub tag: `v1.0.0`
- Release title: `ROV Control GUI v1.0.0`

## Post-Release

1. **Announce the release:**
   - Update project documentation
   - Share on relevant platforms

2. **Monitor feedback:**
   - Watch for GitHub issues
   - Respond to user feedback

3. **Plan next release:**
   - Create milestone for next version
   - Organize feature requests
