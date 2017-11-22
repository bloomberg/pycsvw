# Copyright 2017 Bloomberg Finance L.P.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

setup(
    name='pycsvw',
    version="1.0.2",
    description='Generate JSON and RDF from csv files with metadata',
    url='https://github.com/bloomberg/pycsvw',
    author='Dev Ramudit, Erman Korkut',
    author_email='dramudit2@bloomberg.net, ekorkut1@bloomberg.net',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],

    keywords='csv metadata rdf json csvw',
    packages=find_packages(),
    install_requires=['click', 'six', 'future', 'rdflib', 'rdflib-jsonld', 'python-dateutil'],
    tests_require=['pytest', 'mock'],
    entry_points='''
        [console_scripts]
        pycsvw=pycsvw.scripts.cli:main        
        ''',
)
