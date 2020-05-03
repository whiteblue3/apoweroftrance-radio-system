import setuptools

setuptools.setup(
    name="accounts",
    version="0.0.1",
    author="whiteblue3",
    author_email="hd2dj07@gmail.com",
    description="A Power of Trance Accounts App",
    long_description="A Power of Trance Accounts App",
    long_description_content_type="text/markdown",
    url="https://github.com/whiteblue3/django-accounts",
    packages=setuptools.find_packages(exclude=(
        "app", "manage.py", "accounts/migrations"
    )),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "django>=2.0,<3.0",
        "django-admin-rangefilter",
        "django-admin-list-filter-dropdown",
        "django-admin-numeric-filter",
        "django-monthfield",
        "aiohttp",
        "redis",
        "djangorestframework",
        "drf-yasg",
        "psycopg2-binary",
        "pycrypto",
        "pyjwt",
        "fleep",
    ],
    python_requires='>=3.6',
)
