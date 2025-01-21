from setuptools import setup

setup(
    name="pythonldap3wrapper",
    version="1.00",
    py_modules=["ldap3_wrapper"],
    install_requires=[
        "ldap3==2.9.1",
    ],
    author="Thomas Obarowski",
    author_email="tjobarow@gmail.com",
    description="A wrapper making it easier to use the ldap3 module",
    long_description="",
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
