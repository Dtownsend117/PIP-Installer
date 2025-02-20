# I have included every PIP Package installed on my system in this
# Feel free to add your own and more


import subprocess
import sys
import os
import pkg_resources
import pyttsx3
import requests
import speech_recognition as sr

def speak(text):
    """
    Uses text-to-speech to announce the given text.
    
    :param text: The text to be spoken
    """
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)
    engine.setProperty("rate",180)
    engine.say(text)
    engine.runAndWait()
    
def listen():
    """
    Listens for verbal input and returns the recognized text.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)  # Listening timeout
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start.")
            return ""
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""

def check_pip_version():
    """
    Checks if there is a newer version of pip available.
    """
    current_version = pkg_resources.get_distribution("pip").version
    response = requests.get("https://pypi.org/pypi/pip/json")
    latest_version = response.json()["info"]["version"]
    
    if current_version != latest_version:
        speak(f"A newer version of pip is available: {latest_version}.")
        print(f"A newer version of pip is available: {latest_version}.")
        return True
    else:
        speak("You have the latest version of pip.")
        print("You have the latest version of pip.")
        return False

def list_installed_packages():
    """
    Lists all installed packages and their count.
    """
    installed_packages = pkg_resources.working_set
    package_list = sorted([f"{pkg.key}=={pkg.version}" for pkg in installed_packages])
    speak("Here are the installed packages:")
    print("\nInstalled packages:")
    for package in package_list:
        print(package)
    speak(f"There are {len(package_list)} installed packages.")
    print(f"\nTotal installed packages: {len(package_list)}")
def check_for_upgrades():
    """
    Checks for available upgrades for installed packages.
    
    :return: A list of packages that have available upgrades.
    """
    upgrades = []
    installed_packages = pkg_resources.working_set
    for package in installed_packages:
        try:
            # Check for available upgrades using pip
            command = [sys.executable, '-m', 'pip', 'list', '--outdated', '--format=freeze']
            outdated = subprocess.check_output(command).decode('utf-8').strip().split('\n')
            for line in outdated:
                if line:
                    pkg_name = line.split('==')[0]
                    upgrades.append(pkg_name)
        except subprocess.CalledProcessError as e:
            print(f"Error checking for upgrades: {e}")
    return upgrades

def search_packages(query):
    """
    Searches for packages on PyPI based on the query.
    
    :param query: The search term for the package name.
    """
    response = requests.get(f"https://pypi.org/pypi?%3Aaction=search&term={query}&submit=search")
    if response.status_code == 200:
        results = response.json().get('hits', {}).get('hits', [])
        if results:
            speak(f"Found {len(results)} packages matching '{query}'.")
            print(f"Found {len(results)} packages matching '{query}':")
            for result in results:
                package_name = result['name']
                package_version = result['version']
                print(f"{package_name} (version: {package_version})")
            return results
        else:
            speak("No packages found.")
            print("No packages found.")
            return []
    else:
        speak("Error occurred while searching for packages.")
        print("Error occurred while searching for packages.")
        return []

def upgrade_packages():
    """
    Upgrades all installed packages using pip.
    """
    if check_pip_version():
        speak("Would you like to upgrade pip now?")
        response = listen()
        if "yes" in response:
            try:
                #speak("Upgrading pip...")
                print("Upgrading pip...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
                #speak("Successfully upgraded pip.")
                print("Successfully upgraded pip.")
            except subprocess.CalledProcessError as e:
                speak(f"Failed to upgrade pip. Error: {e}")
                print(f"Failed to upgrade pip. Error: {e}")

    installed_packages = pkg_resources.working_set
    for package in installed_packages:
        try:
            #speak(f"Upgrading {package.key}...")
            print(f"Upgrading {package.key}...")
            command = [sys.executable, '-m', 'pip', 'install', '--upgrade', package.key]
            subprocess.check_call(command)
            #speak(f"Successfully upgraded {package.key}.")
            print(f"Successfully upgraded {package.key}")
        except subprocess.CalledProcessError as e:
            speak(f"Failed to upgrade {package.key}. Error: {e}")
            print(f"Failed to upgrade {package.key}. Error: {e}")

def install_packages(package_list, requirements_file=None):
    """
    Installs a list of packages using pip.

    :param package_list: List of package names to install
    :param requirements_file: Path to a requirements file
    """
    if requirements_file:
        if os.path.exists(requirements_file):
            with open(requirements_file, 'r') as f:
                package_list = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        else:
            print(f"Requirements file {requirements_file} does not exist.")
            return

    for package in package_list:
        try:
            #speak(f"Installing {package}...")
            print(f"Installing {package}...")
            command = [sys.executable, '-m', 'pip', 'install']
            command.append(package)
            subprocess.check_call(command)
            #speak(f"Successfully installed {package}.")
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            speak(f"Failed to install {package}. Error: {e}")
            print(f"Failed to install {package}. Error: {e}")

def ask_for_another_action():
    """
    Asks the user if they want to perform another action or exit.
    """
    speak("Would you like to perform another action? Say yes to continue or no to exit.")
    response = listen()
    return "yes" in response

if __name__ == "__main__":
    while True:
        speak("Please choose an option.")
        print("Please choose an option:")
        print("Display {Lists installed packages}")
        print("Upgrade {Upgrades installed packages")
        print("Install {Installs stored packages}}")

        choice = listen()
        
        if "display" in choice:
            list_installed_packages()
        elif "upgrade" in choice:
            speak("The process will take several minutes, feel free to keep using your computer.")
            upgrade_packages()
        elif "install" in choice:
            speak("The process will take several minutes, feel free to keep using your computer.")
            # Example usage
            packages_to_install = [
                'absl-py',
                'aenum',
                'aescipher',
                'aiofiles',
                'aiohappyeyeballs',
                'aiohttp',
                'aiosignal',
                'alabaster',
                'algebra',
                'altgraph',
                'amqp',
                'annotated-types',
                'ansi2html',
                'ansimarkup',
                'anyio',
                'api',
                'apiai',
                'arg',
                'argcomplete',
                'argon2-cffi',
                'argon2-cffi-bindings',
                'arrow',
                'artificial',
                'asgiref',
                'astropy',
                'astropy-iers-data',
                'asttokens',
                'astunparse',
                'async',
                'async-generator',
                'async-lru',
                'async-timeout',
                'asyncio',
                'attr',
                'attrs',
                'audioread',
                'autocommand',
                'Automat',
                'axju-jokes',
                'babel',
                'backcall',
                'backends',
                'bcrypt',
                'beartype',
                'beautifulsoup4',
                'bing',
                'bleach',
                'blinker',
                'blis',
                'block-stdout',
                'bokeh',
                'boto3',
                'botocore',
                'bottle',
                'bottle-websocket',
                'bs4',
                'cachetools',
                'cairocffi',
                'CairoSVG',
                'call',
                'casttube',
                'catalogue',
                'category-encoders',
                'ccompiler',
                'cellular',
                'certifi',
                'cffi',
                'cfgv',
                'chardet',
                'charset-normalizer',
                'chatbot',
                'cheroot',
                'CherryPy',
                'click',
                'clock',
                'cloudpath',
                'cloudpathlib',
                'cloudpickle',
                'cmake',
                'colorama',
                'colorlog',
                'comm',
                'commonmark',
                'complete',
                'comtypes',
                'confection',
                'constantly',
                'contextlib2',
                'contourpy',
                'cortana',
                'coverage',
                'cryptography',
                'css',
                'cssselect',
                'cssselect2',
                'ctypes-callable',
                'cx_Freeze',
                'cx_Logging',
                'cycler',
                'cymem',
                'Cython',
                'dash',
                'dash-core-components',
                'dash-html-components',
                'dash-table',
                'DateTime',
                'debugpy',
                'decorator',
                'deep-translator',
                'deepdiff',
                'defusedxml',
                'desk',
                'Distance',
                'distlib',
                'distro',
                'Django',
                'django-appconf',
                'django-classy-tags',
                'django-easy-maps',
                'dnspython',
                'docker',
                'docopt',
                'docutils',
                'duty',
                'EAST',
                'EasyProcess',
                'easyrsa',
                'ecapture',
                'ecc',
                'edge-tts',
                'edith',
                'email_validator',
                'encryptedsocket',
                'entrypoint2',
                'entrypoints',
                'exceptiongroup',
                'exe',
                'executing',
                'face_recognition_models',
                'faddr',
                'failprint',
                'fastai',
                'fastcore',
                'fastdownload',
                'fastjsonschema',
                'fastprogress',
                'fbchat',
                'fbchatbot',
                'fdm',
                'file-explorer',
                'filelock',
                'Flask',
                'flatbuffers',
                'fontools',
                'fonttools',
                'FORD',
                'forecast',
                'fqdn',
                'freezegun',
                'friday',
                'frozenlist',
                'fsspec',
                'future',
                'gast',
                'gcloud',
                'geocoder',
                'geographiclib',
                'geojson',
                'geopy',
                'gevent',
                'gevent-websocket',
                'gif',
                'gitverse',
                'gmail',
                'gmail-connector',
                'google',
                'google-api-core',
                'google-api-python-client',
                'google-auth',
                'google-auth-httplib2',
                'google-auth-oauthlib',
                'google-cloud',
                'google-cloud-texttospeech',
                'google-pasta',
                'google-workspace',
                'googleapis-common-protos',
                'googlehomepush',
                'googlemaps',
                'googlesearch-python',
                'googletrans',
                'graphviz',
                'greenlet',
                'grpcio',
                'grpcio-status',
                'gTTS',
                'gTTS-token',
                'h11',
                'h2',
                'h3',
                'h5py',
                'hijri',
                'hijri-converter',
                'holidays',
                'hpack',
                'hstspreload',
                'html2text',
                'httpcore',
                'httplib2',
                'httpsx',
                'httpx',
                'huggingface-hub',
                'hyperframe',
                'hyperlink',
                'icalendar',
                'identify',
                'idna',
                'ifaddr',
                'image',
                'imageai',
                'imageio',
                'imagesize',
                'imbalanced-learn',
                'importlib-metadata',
                'importlib_resources',
                'incremental',
                'inflect',
                'iniconfig',
                'instagram',
                'intel-cmplr-lib-ur',
                'intel-openmp',
                'intelligence',
                'ipdb',
                'ipykernel',
                'ipython',
                'ipython-genutils',
                'ipywidgets',
                'isodate',
                'isoduration',
                'itemadapter',
                'itemloaders',
                'itsdangerous',
                'jaraco.classes',
                'jaraco.collections',
                'jaraco.context',
                'jaraco.functools',
                'jaraco.text',
                'javascript',
                'jax',
                'jaxlib',
                'jedi',
                'Jinja2',
                'jiter',
                'jmespath',
                'joblib',
                'Js2Py',
                'json5',
                'jsonpointer',
                'jsonschema',
                'jsonschema-specifications',
                'jupyter',
                'jupyter_client',
                'jupyter-console',
                'jupyter_core',
                'jupyter-events',
                'jupyter-lsp',
                'jupyter_server',
                'jupyter_server_terminals',
                'jupyterlab',
                'jupyterlab_pygments',
                'jupyterlab_server',
                'jupyterlab_widgets',
                'keras',
                'Keras-Applications',
                'Keras-Preprocessing',
                'keyboard',
                'keyring',
                'keyrings.alt',
                'Kivy',
                'kivy-deps.angle',
                'kivy-deps.glew',
                'kivy-deps.sdl2',
                'Kivy-Garden',
                'kiwisolver',
                'kombu',
                'korean-lunar-calendar',
                'kubernetes',
                'langcodes',
                'langdetect',
                'language_data',
                'lazy_loader',
                'lazyme',
                'libclang',
                'libretranslatepy',
                'librosa',
                'lief',
                'lightgbm',
                'linkedin',
                'llvmlite',
                'locket',
                'loguru',
                'lxml',
                'macholib',
                'maps',
                'marisa-trie',
                'Markdown',
                'markdown-include',
                'markdown-it-py',
                'MarkupSafe',
                'marshmallow',
                'mashumaro',
                'matplotlib',
                'matplotlib-inline',
                'mdurl',
                'mediapipe',
                'messenger',
                'meteostat',
                'microphone',
                'microsoft',
                'mistune',
                'mkl',
                'ml-dtypes',
                'mlpack',
                'modulegraph',
                'more-itertools',
                'mouse',
                'MouseInfo',
                'mpmath',
                'msgpack',
                'mss',
                'multidict',
                'munch',
                'murmurhash',
                'namex',
                'nbclient',
                'nbconvert',
                'nbformat',
                'nest-asyncio',
                'network',
                'networkx',
                'newsapi',
                'newsapi-python',
                'nh3',
                'nltk',
                'nodeenv',
                'noneprompt',
                'north',
                'nose',
                'notebook',
                'notebook_shim',
                'notify2',
                'nox',
                'numba',
                'numpy',
                'oauth2',
                'oauth2client',
                'oauthlib',
                'of',
                'omnitools',
                'onedrive',
                'openai',
                'openai-whisper',
                'opencv-contrib-python',
                'opencv-python',
                'opt-einsum',
                'optree',
                'ordered-set',
                'orderly-set',
                'orjson',
                'outcome',
                'overrides',
                'packaging',
                'paho-mqtt',
                'panda',
                'pandas',
                'pandocfilters',
                'paramiko',
                'paramiko-expect',
                'parse',
                'parsedatetime',
                'parsel',
                'parso',
                'partd',
                'pathlib_abc',
                'pathlib2',
                'pathy',
                'patsy',
                'pcpp',
                'pdfminer.six',
                'pdfplumber',
                'pefile',
                'pi',
                'pick',
                'pickleshare',
                'pillow',
                'pip',
                'pipwin',
                'pkce',
                'pkginfo',
                'platformdirs',
                'playsound',
                'plotly',
                'plotly-resampler',
                'pluggy',
                'pluginmanager',
                'plum-dispatch',
                'plyer',
                'pmdarima',
                'pooch',
                'portalocker',
                'portend',
                'pre-commit',
                'preshed',
                'prometheus_client',
                'prompt_toolkit',
                'Protego',
                'proto-plus',
                'protobuf',
                'psutil',
                'pure_eval',
                'pvporcupine',
                'py',
                'py-avataaars',
                'py2app',
                'py3-tts',
                'pyarrow',
                'pyasn1',
                'pyasn1_modules',
                'pyasynchat',
                'pyasyncore',
                'PyAudio',
                'PyAutoGUI',
                'pyavatar',
                'PyBrain',
                'pybrightness',
                'pycaw',
                'PyChromecast',
                'pycontrols',
                'pycountry',
                'pycparser',
                'pycryptodome',
                'pycw',
                'pyda',
                'pydantic',
                'pydantic_core',
                'pydantic-settings',
                'PyDirectInput',
                'PyDispatcher',
                'pydub',
                'pyerfa',
                'pyfaidx',
                'pyfnutils',
                'pyftpdlib',
                'pygame',
                'pygeocoder',
                'PyGetWindow',
                'Pygments',
                'pyicloud',
                'pyinput',
                'pyinstaller',
                'pyinstaller-hooks-contrib',
                'pyjokes',
                'pyjsparser',
                'PyJWT',
                'pylance',
                'pymongo',
                'PyMsgBox',
                'pymyq',
                'PyNaCl',
                'pynotification',
                'pynput',
                'pyOpenSSL',
                'pyotp',
                'pyowm',
                'pyparsing',
                'pypdfium2',
                'pyperclip',
                'pypinyin',
                'pypiwin32',
                'PyPrind',
                'pypsutil',
                'PyQt5',
                'PyQt5-Qt5',
                'PyQt5_sip',
                'PyRect',
                'pyrh',
                'pyrsistent',
                'pyscreenshot',
                'PyScreeze',
                'pySmartDL',
                'PySocks',
                'pytest',
                'pytest-cov',
                'python-dateutil',
                'python-dotenv',
                'python-env',
                'python-json-logger',
                'python-magic',
                'python-markdown-math',
                'python-multipart',
                'python-weather',
                'pytils',
                'pyttsx3',
                'pytube',
                'pytweening',
                'pytz',
                'PyWavelets',
                'pywebostv',
                'pywhatkit',
                'pywifi-controls',
                'pywin32',
                'pywin32-ctypes',
                'pywinpty',
                'pywslocker',
                'PyYAML',
                'pyzmq',
                'qtconsole',
                'QtPy',
                'queuelib',
                'randfacts',
                'ratelim',
                'readme_renderer',
                'recommonmark',
                'referencing',
                'regex',
                'requests',
                'requests-file',
                'requests-oauthlib',
                'requests-toolbelt',
                'retrying',
                'rfc3339-validator',
                'rfc3986',
                'rfc3986-validator',
                'rgb',
                'rich',
                'rise',
                'rpds-py',
                'rsa',
                'rse',
                's3transfer',
                'safetensors',
                'schedule',
                'schemdraw',
                'scikit-base',
                'scikit-image',
                'scikit-learn',
                'scikit-plot',
                'scipy',
                'Scrapy',
                'seaborn',
                'selenium',
                'Send2Trash',
                'service-identity',
                'setuptools',
                'shellingham',
                'shutup',
                'simplejson',
                'six',
                'sktime',
                'smart-open',
                'sniffio',
                'snowballstemmer',
                'sortedcontainers',
                'sounddevice',
                'soundfile',
                'soupsieve',
                'South',
                'soxr',
                'spacy',
                'spacy-legacy',
                'spacy-loggers',
                'SpeechRecognition',
                'speedtest-cli',
                'Sphinx',
                'sphinx-automodapi',
                'sphinxcontrib-applehelp',
                'sphinxcontrib-devhelp',
                'sphinxcontrib-htmlhelp',
                'sphinxcontrib-jsmath',
                'sphinxcontrib-qthelp',
                'sphinxcontrib-serializinghtml',
                'SQLAlchemy',
                'sqlparse',
                'srsly',
                'stack-data',
                'starlette',
                'statsmodels',
                'style',
                'sympy',
                'tbats',
                'tbb',
                'tempora',
                'tenacity',
                'tensorboard',
                'tensorboard-data-server',
                'tensorboard-plugin-wit',
                'tensorflow',
                'tensorflow-estimator',
                'tensorflow-gpu-estimator',
                'tensorflow-intel',
                'termcolor',
                'terminado',
                'testpath',
                'testtools',
                'thinc',
                'think',
                'threadpoolctl',
                'threadwrapper',
                'tifffile',
                'tiktoken',
                'timezonefinder',
                'tinycss2',
                'tldextract',
                'to',
                'tokenizers',
                'tomli',
                'tony',
                'tools',
                'toolz',
                'toposort',
                'torch',
                'torchvision',
                'tornado',
                'tqdm',
                'traitlets',
                'transformers',
                'translate',
                'trio',
                'trio-websocket',
                'trython',
                'tsdownsample',
                'ttp',
                'twine',
                'Twisted',
                'twisted-iocpsupport',
                'twitter',
                'typeguard',
                'typer',
                'types-python-dateutil',
                'typing_extensions',
                'tzdata',
                'tzlocal',
                'unencryptedsocket',
                'update',
                'uri-template',
                'uritemplate',
                'urllib3',
                'uvicorn',
                'vehicle',
                'vexmessage',
                'vine',
                'virtualenv',
                'Voice',
                'voices',
                'volume-control',
                'vpn-server',
                'w3lib',
                'wasabi',
                'Wave',
                'wcwidth',
                'weasel',
                'webcolors',
                'webencodings',
                'websocket-client',
                'websockets',
                'webull',
                'Werkzeug',
                'wheel',
                'whichcraft',
                'widgetsnbextension',
                'wikipedia',
                'win32-setctime',
                'windows',
                'windows-curses',
                'winshell',
                'WMI',
                'wolframalpha',
                'wrapt',
                'ws4py',
                'wsproto',
                'wxPython',
                'xgboost',
                'xmltodict',
                'xxhash',
                'xyzservices',
                'yarl',
                'yellowbrick',
                'zc.lockfile',
                'zeroconf',
                'zipp',
                'zope.event',
                'zope.interface',
                'zstandard',
            ]
            install_packages(packages_to_install)
        else:
            speak("I didn't understand your choice. Please try again.")

        if not ask_for_another_action():
            #speak("Exiting the program. Goodbye!")
            print("Exiting the program. Goodbye!")
            break
