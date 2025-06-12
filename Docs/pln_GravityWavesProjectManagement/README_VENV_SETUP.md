# Virtual Environment Setup for pln_GravityWavesProjectManagement

This project uses a dedicated Python virtual environment named `.pln_venv` located in this directory.

## Creating the Virtual Environment

If the virtual environment is not already created, you can create it by running:

```bash
python3 -m venv .pln_venv
```

## Activating the Virtual Environment

- On Linux/macOS (bash/zsh):

```bash
source .pln_venv/bin/activate
```

- On Windows (PowerShell):

```powershell
.pln_venv\Scripts\Activate.ps1
```

- On Windows (cmd.exe):

```cmd
.pln_venv\Scripts\activate.bat
```

## Installing Dependencies

If you have a `requirements.txt` file, install dependencies with:

```bash
pip install -r requirements.txt
```

## Deactivating the Virtual Environment

To deactivate the virtual environment, simply run:

```bash
deactivate
```

## Notes

- Make sure to select the Python interpreter from `.pln_venv` in your IDE or editor to avoid import errors.
- Restart your IDE/editor after switching the interpreter to refresh the environment.
