"""
Flask-Assistant
-------------
Easy Alexa Skills Kit integration for Flask
"""
from setuptools import setup


setup(
    name='Flask-Assistant',
    version='0.0.9',
    url='https://github.com/treethought/flask-assistant',
    license='Apache 2.0',
    author='Cam Sweeney',
    author_email='cpsweene@gmail.com',
    description='Flask extension for developing assistants for Google Home / Google Actions via API-AI',
    long_description=__doc__,
    packages=['flask_assistant'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'pyOpenSSL',
        'PyYAML',
        'aniso8601',
        'six',
    ],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Framework :: Flask',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)