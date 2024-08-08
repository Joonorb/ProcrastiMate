import winreg
import os

def get_installed_programs():
    programs = []

    # Registry paths to check for installed programs
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    try:
        for path in registry_paths:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    sub_key_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, sub_key_name) as sub_key:
                        try:
                            program_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                            executable = winreg.QueryValueEx(sub_key, "InstallLocation")[0]
                            if executable:
                                executable = os.path.join(executable, program_name + '.exe')
                                if os.path.exists(executable):
                                    programs.append((program_name, executable))
                        except (FileNotFoundError, OSError):
                            continue
    except Exception as e:
        print(f"Error retrieving installed programs: {e}")

    # Common installation directories
    common_dirs = [
        os.path.join(os.environ['ProgramFiles'], 'Steam'),
        os.path.join(os.environ['ProgramFiles(x86)'], 'Steam')
    ]

    for dir_path in common_dirs:
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.exe'):
                        program_name = file[:-4]  # Remove '.exe'
                        programs.append((program_name, os.path.join(root, file)))

    return programs
