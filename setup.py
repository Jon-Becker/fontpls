from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fontpls",
    version="0.1.0",
    author="Jon-Becker",
    author_email="jonathan@jbecker.dev",
    description="A minimal cli tool for extracting fonts from websites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jon-becker/fontpls",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "cssutils>=2.3.0",
        "fonttools>=4.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
        ],
    },
    entry_points={
        "console_scripts": [
            "fontpls=fontpls.cli:main",
        ],
    },
)
