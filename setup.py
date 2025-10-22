"""
Setup script for SingletonProxyObserver
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='singleton-proxy-observer',
    version='1.0.0',
    author='UADER - FCyT - IS2',
    description='Sistema de gestión de datos corporativos con patrones Singleton, Proxy y Observer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/uader/singleton-proxy-observer',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'spo-server=singleton_proxy_observer.server.main:main',
            'spo-client=singleton_proxy_observer.clients.singleton_client:main',
            'spo-observer=singleton_proxy_observer.clients.observer_client:main',
        ],
    },
)
