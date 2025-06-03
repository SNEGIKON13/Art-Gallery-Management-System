from setuptools import setup, find_packages

setup(
    name="gallery_management",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'python-dotenv>=0.19.0',
        'pydantic>=2.0.0',
        'minio>=7.1.0',
    ],
    python_requires='>=3.8',
)
