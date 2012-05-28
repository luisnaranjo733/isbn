from setuptools import setup,find_packages
#from distutils.core import setup
import os

def read(fname):  # TODO: Implement this
    fpath = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), fname)
    with open(fpath, 'r') as fhandle:
        return fhandle.read()
    
setup(
    name = "isbn",
    version = '1.0',
    author = 'Jose Luis Naranjo Gomez',
    author_email = 'luisnaranjo733@hotmail.com',
    description = ("A Python isbn request library using http://xisbn.worldcat.org/services"),
    license = "GNU GPL",
    keywords = "isbn upc_a ean_13 isbn-10 isbn-13",
    url = "https://github.com/doubledubba/isbn",
    packages = ['isbn'],
    #package_data = {'periodic': ['table.db']}
    include_package_data = True,
    #long_description=read('README.rst'),
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Utilities",
    ],

)
