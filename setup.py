from setuptools import setup, find_packages
setup(
    name='Japanese Data Horder',
    version='1.0',
    packages = find_packages(),
    install_requires=install_requires[
        "geckodriver-autoinstaller==0.1.0"
        "Pillow==9.2.0",
        "requests==2.28.1",
        "selenium==4.4.3",
        "beautifulsoup4==4.11.1"
    ]
)
