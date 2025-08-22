from setuptools import setup, find_packages

setup(
    name="elsa_module",
    version="3.2.2",
    description="ELSA Virtual Assistant System",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "speechrecognition",
        "wikipedia",
        "psutil",
        "pygame",
        "requests",
        "opencv-python",
        "numpy",
        "pyaudio",
        "plyer",
        "websockets",
        "pyttsx3",
        "beautifulsoup4",
        "gtts",
        "python-dateutil",
        "ultralytics"
    ],
    entry_points={
        'console_scripts': [
            'elsa=elsa_module.main:virtual_assistant',
            'elsa-cli=elsa_module.cli:main',
        ],
    },
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
)
