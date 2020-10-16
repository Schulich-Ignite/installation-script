
# Standard Library Dependencies
import os                       # Used for path validation
import logging                  # Used for optional logging details
import subprocess               # Used to invoke installer binaries
from shutil import copyfile     # Used to copy files between directories
from sys import platform, argv  # Used to validate which os script is on, and how many arguments at terminal

# Third-Party Dependencies
import requests                 # Used to download files
from tqdm import tqdm           # Used to generate progress bar on donwloads


# Setting up Constants

#  OS name booleans
mac = True if platform == "darwin" else False
windows = True if os.name == "nt" else False
linux = True if platform == "linux" or platform == "linux2" else False

# Instalation and download folders
DOWNLOAD_FOLDER = f"{os.getenv('USERPROFILE')}\\Downloads" if windows else f"{os.getenv('HOME')}/Downloads" 
DOCUMENTS_FOLDER = f"{os.getenv('USERPROFILE')}\\Documents" if windows else f"{os.getenv('HOME')}/Documents" 

# Executable paths
if windows:
    PIP_EXECUTABLE = os.path.realpath(f"{os.environ['APPDATA']}\\..\\Local\\Programs\\Python\\Python38\\Scripts\\pip.exe")
    JUPYTER_EXECUTABLE = os.path.realpath(f"{os.environ['APPDATA']}\\..\\Local\\Programs\\Python\\Python38\\Scripts\\jupyter.exe")
    JUPYTER_LAB_EXECUTABLE = os.path.realpath(f"{os.environ['APPDATA']}\\..\\Local\\Programs\\Python\\Python38\\Scripts\\jupyter-lab.exe")
else:
    PIP_EXECUTABLE = "python3.8 -m pip"


def _download(name, url, extension):
    """Downloads binaries from remote sources"""
    logging.info(f"Downloading {name}")
    file_path = f"{DOWNLOAD_FOLDER}{os.sep}{name}{extension}"

    if os.path.exists(file_path): # If file already exists
        return

    logging.info("Starting binary download")

    # Setting up necessary download variables
    file_stream = requests.get(url, stream=True) # The open http request for the file
    chunk_size = 1024 # Setting the progress bar chunk size to measure in kb
    total_length = int(file_stream.headers.get('content-length')) # Getting file size

    # Setting up the download progress bar
    progress_bar = tqdm(total=total_length, unit='iB', unit_scale=True)
    progress_bar.set_description(f"Download progress for {name}:")

    # Write the incoming data stream to a file and update progress bar as it downloads
    with open(file_path, 'wb') as download_file: 
        for chunk in file_stream.iter_content(chunk_size): 
            if chunk:
                progress_bar.update(len(chunk))
                download_file.write(chunk)
    progress_bar.close()

def _install(path, args):
    """Install executable files with provided args"""
    logging.debug("Installing: " + str([path, *args]))
    installer = subprocess.call([path, *args], shell=True)
    while installer.poll:
        ... # Wait for installer to finish
    os.remove(path)


def step_1():
    """install python 3.8.6"""
    if windows:
        _download("python-installer", "https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe", ".exe") 
        _install(f"{DOWNLOAD_FOLDER}{os.sep}python-installer.exe", ["/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0"])
        print("2")
    elif linux:
        ...
    elif mac:
        ...

def step_2():
    """Install NodeJS"""
    if windows:
        _download("node", "https://nodejs.org/dist/v12.19.0/node-v12.19.0-x64.msi", ".msi")
        _install(f"{DOWNLOAD_FOLDER}{os.sep}msiexec.exe", ["/i", "node.msi", r'INSTALLDIR="C:\Program Files\NodeJS"', "/quiet", "/promptrestart"])
    elif linux:
        ...
    elif mac:
        _download("node", "https://nodejs.org/dist/v12.19.0/node-v12.19.0.pkg", ".pkg")

def step_3_to_6():
    """Install pip packages; jupyterlab, ipywidgets, ipycanvas, ipyevents, spark"""
    for package in ["jupyterlab", "ipywidgets", "ipycanvas", "ipyevents", os.path.realpath(f".{os.sep}spark")]:
        subprocess.call([PIP_EXECUTABLE, "install", package], shell=True)

    for jupyter_package in ["jupyterlab-manager@2.0", "jupyterlab-manager ipycanvas", "jupyterlab-manager ipyevents"]:
        subprocess.call([JUPYTER_EXECUTABLE, "labextension", "install", f"@jupyter-widgets/{jupyter_package}"], shell=True)

def step_7():
    """Install the spark package for use in jupyterlab"""
    os.chdir("spark")
    subprocess.call([PIP_EXECUTABLE, "install", "."], shell=True)
    os.chdir("..")

def step_8_to_9():
    """Create a folder in the documents folder called ignite_notebooks with a default notebook called ignite.ipynb"""
    os.mkdir(f"{DOCUMENTS_FOLDER}{os.sep}ignite_notebooks")
    copyfile("ignite.ipynb",f"{DOCUMENTS_FOLDER}{os.sep}ignite_notebooks{os.sep}ignite.ipynb")

def step_10():
    """Adds an ignite icon to the desktop for easy launching"""
    copyfile(f".{os.sep}ignite.ico",f"{DOCUMENTS_FOLDER}{os.sep}ignite_notebooks{os.sep}ignite.ico")
    if windows:
        import winshell  # Allows execution of built-in windows shell functions
        from win32com.client import Dispatch  # Instantiate COM objects to dispatch through
        desktop = winshell.desktop()  # Get desktop path
        path = os.path.join(desktop, "Ignite.lnk")  # Setup path for shortcut
        target = JUPYTER_LAB_EXECUTABLE  # Setup path for target executable
        wDir = f"{DOCUMENTS_FOLDER}\\ignite_notebooks"  # Set directory to run executeable from
        icon = f"{DOCUMENTS_FOLDER}{os.sep}ignite_notebooks{os.sep}ignite.ico"  # Set icon path
        shell = Dispatch('WScript.Shell')  # Grab the WScript shell function to build shortcuts
        shortcut = shell.CreateShortCut(path)  # Begin creating shortcut objects
        # Add previously built variables to shortcut object
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save() # Flush shortcut to the desktop

if __name__ == "__main__":
    if len(argv) > 1: # if an argument is passed then go into debug logging
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%y-%m-%d %H:%M:%S",
            )
        logging.getLogger(__name__)
    step_1()
    step_2()
    step_3_to_6()
    step_7()
    step_8_to_9()
    step_10()