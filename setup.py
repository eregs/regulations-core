from setuptools import setup, find_packages

setup(
    name="regcore",
    version="2.0.0",
    license="public domain",
    packages=find_packages(),
    install_requires=[
        'anyjson',
        'django==1.8',
        'jsonschema',
        'streql'
    ]
)
