import setuptools

setuptools.setup(
    name="apoweroftrance-backend",
    version="0.0.1",
    author="whiteblue3",
    author_email="hd2dj07@gmail.com",
    description="A Power of Trance Backend Service",
    long_description="A Power of Trance Backend Service",
    long_description_content_type="text/markdown",
    url="https://github.com/whiteblue3/apoweroftrance-post",
    packages=setuptools.find_packages(exclude=(
        "app/", "post/migrations", "system/migrations", "manage.py"
    )),
    include_package_data=True,
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
        "django-phonenumber-field[phonenumbers]",
        "django-phonenumber-field[phonenumberslite]",
        "django-pgcrypto",
        "aiohttp",
        "redis",
        "django-redis",
        "djangorestframework",
        "psycopg2-binary < 2.9",
        "tzdata",
        "pyjwt",
        "pycrypto",
        "mutagen",
    ],
    dependency_links=[
        "./apoweroftrance-django-utils-0.0.1.tar.gz",
        "./apoweroftrance-account-0.0.1.tar.gz",
        "./apoweroftrance-radio-0.0.1.tar.gz",
    ],
    python_requires='>=3.6,<3.8',
)
