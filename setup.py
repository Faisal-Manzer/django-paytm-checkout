import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

# This call to setup() does all the work
setup(
    name='django-paytm-checkout',
    version='0.0.1',
    description='A simple and modular django app to help with Paytm checkout and custom checkout',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/Faisal-Manzer/django-paytm-checkout',
    author='Faisal Manzer',
    author_email='faisal_manzer@yahoo.in',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(include=('paytm*', )),
    include_package_data=True,
    install_requires=['django', 'djangorestframework'],
    download_url='https://github.com/Faisal-Manzer/django-paytm-checkout/archive/0.0.1.tar.gz',
    entry_points={
    },
)
