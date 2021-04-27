import setuptools

setuptools.setup(
    name="automint",
    version="0.0.1",
    author="Marcus Lee",
    author_email="mlkt12x@gmail.com",
    description="Cardano NFT minting and transactions python library",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires = [
        'requests'
    ],
    license_files=('LICENSE',),
)
