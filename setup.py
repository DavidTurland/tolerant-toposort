from setuptools import setup

setup(
    install_requires=[
        "Flask>=2,<3"
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
