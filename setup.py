from setuptools import setup, find_packages
import glob

setup(
    name='gaelib',
    version='0.1.0',
    description='Google App Engine Library for Flask',
    author='Nishad Musthafa',
    license='gpl-3.0',
    packages=find_packages(where='.') + find_packages(exclude=("tests",)),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'wheel',
        'google-cloud-speech',
        'google-cloud-core',
        'grpcio',
        'google-auth',
        'google-cloud-datastore',
        'requests',
        'google-cloud-logging',
        'google-cloud-storage',
        'py-dateutil',
        'pyjwt',
        'hyper',
        'google-cloud-tasks',
        'googleapis_common_protos',
        'firebase-admin',
        'python-jose',
        'nose',
        'mock',
        'google-cloud',
        'Flask-Cors',
        'Flask',
        'gunicorn',
        'Jinja2',
        'six',
        'Werkzeug',
        'twilio',
        'certifi',
        'chardet',
        'click',
        'cachetools',
        'constants'
    ],
    setup_requires=[
        'wheel'
    ]
)
