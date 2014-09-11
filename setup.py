from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='quality_checking',
    version=version,
    description='Quality Checking',
    author='Indictrans technologies Pvt Ltd',
    author_email='rohit.w@indictranstech.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
