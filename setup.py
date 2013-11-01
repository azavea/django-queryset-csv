from distutils.core import setup
import setuptools  # NOQA

setup(
    name='Django Queryset CSV Writer',
    version='0.1.1',
    author='Steve Lamb',
    author_email='slamb@azavea.com',
    packages=['djqscsv'],
    requires=['django'],
    url='http://github.com/steventlamb/django-queryset-csv/',
    description='A simple python module for writing querysets to csv',
    keywords="django queryset csv",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
    ]
)
