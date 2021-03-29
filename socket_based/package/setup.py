from setuptools import setup

setup(
    name = "audiosockets",
    version=1.3,
    author="Nicolas Shu",
    author_email="nicolas.s.shu@gmail.com",
    packages = ["audiosockets"],
    description = "A networking package to perform real-time recording and real-time analysis over the audio",
    install_requires = [
        "numpy",
        "sounddevice"
    ]
)