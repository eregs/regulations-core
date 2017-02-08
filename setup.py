from setuptools import find_packages, setup

setup(
    name="regcore",
    version="3.0.0",
    license="public domain",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.8,<1.10',
        'django-mptt',
        'jsonschema',
        'six',
    ]
)
