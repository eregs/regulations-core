from setuptools import find_packages, setup

setup(
    name="regcore",
    version="2.0.1",
    license="public domain",
    packages=find_packages(),
    install_requires=[
        'django>=1.8,<1.10',
        'django-mptt',
        'jsonschema',
        'six',
    ]
)
