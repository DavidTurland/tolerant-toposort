from setuptools import setup

import re
import ast

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('src/tolerant/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    version         =  version,
    name             = 'tolerant_toposort',
    author           = 'David Turland',
    author_email     = 'david@turland.org',
    description      = 'Extension of toposort to tolerate existing but disabled nodes',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url              = 'https://github.com/DavidTurland/tolerant-toposort',
    license          = 'Apache',
    classifiers      = [   'Programming Language :: Python :: 3',
                           'License :: OSI Approved :: Apache Software License',
                           'Operating System :: OS Independent',
                      ],
    install_requires= [ "Flask>=2,<3" ],
    test_suite      = 'nose2.collector.collector',
    tests_require   = ['nose2'],
    package_dir     = {'': 'src'},
    packages        = ['tolerant'],
    keywords        ='toposort graph tolerant',
    project_urls    = {   'Issue Tracker': 'https://github.com/DavidTurland/tolerant-toposort/issues',
                          'Original'     : 'https://pypi.org/project/toposort',
                          'SetupTools'   : 'https://setuptools.pypa.io/en/latest/userguide/index.html',
                      },
    python_requires= '>=3',
)
