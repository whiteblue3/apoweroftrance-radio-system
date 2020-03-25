import setuptools

setuptools.setup(
    name="django_utils",
    version="0.0.1",
    author="whiteblue3",
    author_email="hd2dj07@gmail.com",
    description="Private DJango Utility Functions",
    long_description="Private DJango Utility Functions",
    long_description_content_type="text/markdown",
    url="https://github.com/whiteblue3/django-utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "django>=2.0,<3.0",
        "djangorestframework",
        "psycopg2-binary",
        "pycrypto",
        "django-storages",
        "boto3",
        "google-cloud-storage",
    ],
    python_requires='>=3.6',
)
