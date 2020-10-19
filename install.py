
# Standard Library Dependencies
import os                       # Used for path validation
import logging                  # Used for optional logging details
import subprocess               # Used to invoke installer binaries
from shutil import copyfile     # Used to copy files between directories
from sys import platform, argv  # Used to validate which os script is on, and how many arguments at terminal

# Third-Party Dependencies
import requests                 # Used to download files
from tqdm import tqdm           # Used to generate progress bar on donwloads
import winshell                 # Allows execution of built-in windows shell functions
from win32com.client import Dispatch  # Instantiate COM objects to dispatch through

# Setting up Constants

#  OS name booleans
mac = True if platform == "darwin" else False
windows = True if os.name == "nt" else False
linux = True if platform == "linux" or platform == "linux2" else False

# Instalation and download folders
DOWNLOAD_FOLDER = f"{os.getenv('USERPROFILE')}\\Downloads" if windows else f"{os.getenv('HOME')}/Downloads"
DESKTOP_FOLDER = f"{os.getenv('USERPROFILE')}\\Desktop" if windows else f"{os.getenv('HOME')}/Desktop" 
DOCUMENTS_FOLDER = f"{os.getenv('USERPROFILE')}\\Documents" if windows else f"{os.getenv('HOME')}/Documents" 

# Executable paths
if windows:
    PIP_EXECUTABLE = os.path.realpath(f"{os.environ['LocalAppData']}\\Programs\\Python\\Python38\\Scripts\\pip.exe")
    JUPYTER_EXECUTABLE = os.path.realpath(f"{os.environ['LocalAppData']}\\Programs\\Python\\Python38\\Scripts\\jupyter.exe")
    JUPYTER_LAB_EXECUTABLE = os.path.realpath(f"{os.environ['LocalAppData']}\\Programs\\Python\\Python38\\Scripts\\jupyter-lab.exe")
else:
    PIP_EXECUTABLE = "python3.8 -m pip"


def _download(name, url, extension) -> str:
    """Downloads binaries from remote sources"""
    file_path = f"{DOWNLOAD_FOLDER}{os.sep}{name}{extension}"

    if os.path.exists(file_path): # If file already exists
        logging.info(f"File {file_path} already downloaded")
        return file_path

    logging.info(f"Downloading {name}")
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

    return file_path

def _install(path, args):
    """Install executable files with provided args"""
    print(f"Installing {path}")
    logging.debug(f"Installing {path}")
    logging.debug("Installing: " + str([path, *args]))
    subprocess.call([path, *args], shell=True)


def step_1():
    """install python 3.8.6"""
    print("Entering Step 1; Install Python 3.8.6")
    logging.debug("Entering Step 1; Install Python 3.8.6")
    if windows:
        exc_path = _download("python-installer", "https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe", ".exe") 
        _install(exc_path, ["/quiet", "PrependPath=1"])
        os.remove(exc_path)
    elif linux:
        ...
    elif mac:
        ...

def step_2():
    """Install NodeJS"""
    print("Entering Step 2; Install NodeJS")
    logging.debug("Entering Step 2; Install NodeJS")
    if windows:
        exc_path = _download("node", "https://nodejs.org/dist/v12.19.0/node-v12.19.0-x64.msi", ".msi")
        # Can't use _install() because need to use msi tools
        subprocess.call(["msiexec.exe", "/i", exc_path, "/passive" ], shell=True)
        os.remove(exc_path)
    elif linux:
        ...
    elif mac:
        exc_path = _download("node", "https://nodejs.org/dist/v12.19.0/node-v12.19.0.pkg", ".pkg")

def step_3_to_6():
    """Install pip packages; jupyterlab, ipywidgets, ipycanvas, ipyevents, spark"""
    print("Entering Steps 3-6; Install Python and Jupyterlab Packages")
    logging.debug("Entering Steps 3-6; Install Python and Jupyterlab Packages")

    # Updating pip
    subprocess.call([PIP_EXECUTABLE, "install","--user", "--upgrade", "pip"], shell=True)

    logging.info("Installing pip packages")
    for package in ["jupyterlab", "ipywidgets", "ipycanvas", "ipyevents"]:
        logging.debug(f"Installing pip package {package} with pip executable {PIP_EXECUTABLE}")
        subprocess.call([PIP_EXECUTABLE, "install", package], shell=True)

    logging.debug("Installing ipywidgets")
    subprocess.call([JUPYTER_EXECUTABLE, "labextension", "install", f"@jupyter-widgets/jupyterlab-manager"], shell=True)

    logging.info("Installing jupyter packages")
    for jupyter_package in ["ipycanvas", "ipyevents"]:
        logging.debug(f"Installing JupyterLab package {jupyter_package} with jupyter executable {JUPYTER_EXECUTABLE}")
        subprocess.call([JUPYTER_EXECUTABLE, "labextension", "install", "@jupyter-widgets/jupyterlab-manager", jupyter_package], shell=True)

    logging.debug("Finished installing all pip and jupyter packages")

def step_7():
    """Install the spark package for use in jupyterlab"""
    # Install git
    if windows:
        exc_path = _download("git", "https://github.com/git-for-windows/git/releases/download/v2.28.0.windows.1/Git-2.28.0-64-bit.exe", ".exe")
        _install(exc_path, ["/VERYSILENT", "/NORESTART"])
        os.remove(exc_path)
    elif linux:
        subprocess.call(["sudo", "apt", "update"])
        subprocess.call(["sudo", "apt", "install", "git", "-y"])
    else: # Mac OS is guarenteed to have git installed
        ...

    print("Entering Step 7; Install Spark")
    logging.debug("Entering Step 7; Install Spark")
    subprocess.call([PIP_EXECUTABLE, "install", "git+https://github.com/Schulich-Ignite/spark"], shell=True)

def step_8_to_9():
    """Create a folder in the documents folder called ignite_notebooks with a default notebook called ignite.ipynb"""
    print("Entering Step 8-9; Setup Default ignite folder and notebook")
    logging.debug("Entering Step 8-9; Setup Default ignite folder and notebook")

    # Create default notebook folder
    if not os.path.exists(f"{DOCUMENTS_FOLDER}{os.sep}ignite_notebooks"):
        logging.debug("No default notebook folder found, initializing")
        os.mkdir(f"{DOCUMENTS_FOLDER}{os.sep}ignite_notebooks")
    else:
        logging.debug("Default notebook folder found, skipping creation")
    
    # Create default notebook file
    if not os.path.exists(f"{DOCUMENTS_FOLDER}{os.sep}ignite_notebooks{os.sep}ignite.ipynb"):
        logging.debug("No default notebook found, initializing")
        copyfile("ignite.ipynb",f"{DOCUMENTS_FOLDER}{os.sep}ignite_notebooks{os.sep}ignite.ipynb")
    else:
        logging.debug("Default notebook found, skipping creation")

def step_10():
    """Adds an ignite icon to the desktop for easy launching"""
    print("Entering Step 10; Setup Desktop Shortcut")
    logging.debug("Entering Step 10; Setup Desktop Shortcut")
    # TODO: Change path to Schulich Ingnite repo
    icon_file = _download("ignite", "https://raw.githubusercontent.com/Descent098/installation-script/master/ignite.ico", "ico")
    copyfile(icon_file,f"{DOCUMENTS_FOLDER}{os.sep}ignite_notebooks{os.sep}ignite.ico")
    if windows:

        logging.debug("Setting up shortcut attributes")
        path = os.path.join(DESKTOP_FOLDER, "Ignite.lnk")  # Setup path for shortcut
        target = JUPYTER_LAB_EXECUTABLE  # Setup path for target executable
        wDir = f"{DOCUMENTS_FOLDER}\\ignite_notebooks"  # Set directory to run executeable from
        icon = f"{DOCUMENTS_FOLDER}{os.sep}ignite_notebooks{os.sep}ignite.ico"  # Set icon path

        logging.debug("Grabbing windows shell scripts")
        shell = Dispatch('WScript.Shell')  # Grab the WScript shell function to build shortcuts

        logging.debug("Creating shortcut template")
        shortcut = shell.CreateShortCut(path)  # Begin creating shortcut objects
        # Add previously built variables to shortcut object

        logging.debug("Writing shortcut attributes to object")
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon

        logging.debug("Flushing shortcut")
        shortcut.save() # Flush shortcut to the desktop

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler("ignite_install.log"),
                        logging.StreamHandler()]
        )
        
    logger = logging.getLogger(__name__)
    step_1()
    step_2()
    step_3_to_6()
    step_7()
    step_8_to_9()
    step_10()

if __name__ == "__main__":
    main()
