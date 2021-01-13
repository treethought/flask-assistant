"""
Flask-Assistant
-------------
Framework for Building Virtual Assistants with API.AI
"""
from setuptools import setup

with open("./README.md", "r") as f:
    long_description = f.read()


setup(
    name="Flask-Assistant",
    version="0.5.3",
    url="https://github.com/treethought/flask-assistant",
    license="Apache 2.0",
    author="Cam Sweeney",
    author_email="cpsweene@gmail.com",
    description="Framework for Building Virtual Assistants with Dialogflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["flask_assistant", "flask_assistant.response", "api_ai"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[
        "Flask",
        "requests",
        "ruamel.yaml",
        "aniso8601",
        "google-auth",
        "dialogflow",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    test_suite="tests",
    extras_require={"HassRemote": ["homeassistant>=0.37.1"]},
    entry_points={
        "console_scripts": [
            "schema=api_ai.cli:schema",
            "query=api_ai.cli:query",
            "templates=api_ai.cli:gen_templates",
            "entities=api_ai.cli:entities",
            "intents=api_ai.cli:intents",
            "check=api_ai.cli:check",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Framework :: Flask",
        "Programming Language :: Python",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
