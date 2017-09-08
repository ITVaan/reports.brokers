from setuptools import setup, find_packages
import os

version = '1.0'

requires = [
    'setuptools',
    'PyYAML',
    'chaussette',
    'gevent',
    'mock',
    'pyramid_exclog',
    'requests',
    'pyramid',
    'pytz',
    'simplejson',
    'request_id_middleware',
    'server_cookie_middleware'
]

test_requires = requires + [
    'webtest',
    'python-coveralls',
    'mock==1.0.1',
    'requests_mock==1.3.0',
    'mysql-connector==2.1.6',
    'bottle'
]

databridge_test_requires = requires + [
    'webtest',
    'python-coveralls',
    'mock==1.0.1',
    'requests_mock==1.3.0',
    'bottle'
]

databridge_requires = requires + [
    'mysql-connector==2.1.6',
    'PyYAML',
    'gevent',
    'LazyDB',
    'ExtendedJournalHandler',
    'requests',
    'openprocurement_client>=1.0b2'
]

api_test_requires = requires + [

]

api_requires = requires + [

]

entry_points = {
    'paste.app_factory': [
        'main = reports.brokers.api:main'
    ],
    'console_scripts': [
        'reports_brokers_bridge = reports.brokers.databridge:main',
        'reports_brokers_api = reports.brokers.api:main',
        'main = reports.brokers.api:main',
    ]
}

setup(name='reports.brokers',
      version=version,
      description="",
      long_description=open("README.rst").read(),
      classifiers=[
          "Framework :: Pylons",
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
      ],
      keywords="web services",
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      url='https://github.com/ITVaan/reports.brokers',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require={'databridge': databridge_requires,
                      'databridge_test': databridge_test_requires,
                      'test': test_requires,
                      'api': api_requires,
                      'api_test': api_test_requires},
      entry_points=entry_points,
      )
