from setuptools import setup, find_packages

author = 'Steve Lamb'
author_email = 'slamb@azavea.com'

setup(
    name='django-queryset-csv',
    version='0.2.5',
    description='A simple python module for writing querysets to csv',
    long_description=open('README.rst').read(),
    author=author,
    author_email=author_email,
    maintainer=author,
    maintainer_email=author_email,
    url='http://github.com/azavea/django-queryset-csv',
    packages=find_packages(exclude=('test_app',)),
    keywords="django queryset csv",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Environment :: Plugins",
        "Framework :: Django",
        "License :: OSI Approved :: GNU General Public License (GPL)"
    ],
    install_requires=['django>=1.5'],
)
