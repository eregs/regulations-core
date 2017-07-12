from setuptools import find_packages, setup

setup(
    name="regcore",
    version="3.1.0",
    license="public domain",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.8,<1.12',
        'django-mptt',
        'jsonschema',
        'six',
    ],
    extras_require={
        'backend-elastic': ['pyelasticsearch'],
        'backend-django': ['django-haystack'],
        'all-backends': ['django-haystack', 'pyelasticsearch'],
    },
)
