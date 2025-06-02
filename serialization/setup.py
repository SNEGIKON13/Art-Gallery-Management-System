from setuptools import setup, find_packages

setup(
    name="gallery-serialization",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'lxml>=4.9.0',  # для XML сериализации
    ],
    entry_points={
        'gallery.serialization': [
            'json = serialization.implementations.json.json_serializer:JsonSerializer',
            'json_deserializer = serialization.implementations.json.json_deserializer:JsonDeserializer',
            'xml = serialization.implementations.xml.xml_serializer:XmlSerializer',
            'xml_deserializer = serialization.implementations.xml.xml_deserializer:XmlDeserializer',
        ],
    },
    python_requires='>=3.8',
    author="Валиуллин Константин",
    author_email="your.email@example.com",
    description="Плагин сериализации для системы управления художественной галереей",
    long_description=open('README.md').read() if open('README.md') else "",
    long_description_content_type="text/markdown",
    keywords="serialization, json, xml, gallery",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
