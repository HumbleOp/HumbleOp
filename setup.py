from setuptools import setup, find_packages

setup(
    name="HumbleOp",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask",  # Add your dependencies here
        "pytest",
    ],
)