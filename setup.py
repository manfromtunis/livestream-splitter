from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="livestream-splitter",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to split long livestream recordings into smaller segments with intro/outro support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/livestream-splitter",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.0",
        "ffmpeg-python>=0.2.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "tqdm>=4.65.0",
    ],
    extras_require={
        "web": ["fastapi>=0.100.0", "uvicorn>=0.23.0", "python-multipart>=0.0.6"],
        "dev": ["pytest>=7.4.0", "pytest-cov>=4.1.0", "black>=23.0.0", "flake8>=6.0.0", "mypy>=1.4.0"],
        "advanced": ["opencv-python>=4.8.0", "numpy>=1.24.0"],
    },
    entry_points={
        "console_scripts": [
            "stream-splitter=stream_splitter.cli:main",
        ],
    },
)