from setuptools import setup, find_packages

setup(
    name='django-queryset-csv',
    version='0.1.1',
    description='A simple python module for writing querysets to csv',
    author='Steve Lamb',
    author_email='slamb@azavea.com',
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
