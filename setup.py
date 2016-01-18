from setuptools import find_packages, setup

from ats_sms_operator.version import get_version


setup(
    name='django-ats-sms-operator',
    version=get_version(),
    description="ATS SMS operator library.",
    keywords='django, sms receiver',
    author='Lubos Matl',
    author_email='matllubos@gmail.com',
    url='https://github.com/matllubos/django-ats-sms-operator',
    license='LGPL',
    package_dir={'ats_sms_operator': 'ats_sms_operator'},
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 1 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU LESSER GENERAL PUBLIC LICENSE (LGPL)',
        'Natural Language :: Czech',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    install_requires=[
        'django>=1.6',
        'beautifulsoup4>=4.4.0',
        'html5lib>=0.999999',
        'django-ipware>=1.0.0',
        'requests==2.9.0',
        'responses==0.5.0',
        'germanium==1.0.5',
        'django-factory_boy==1.0.0',
        'django-ipware>=1.0.0',
        'django-is-core>=1.3.89',
    ],
    dependency_links=[
        'https://github.com/getsentry/responses/tarball/0.5.0#egg=responses-0.5.0',
        'https://github.com/LukasRychtecky/germanium/tarball/1.0.5#egg=germanium-1.0.5',
        'https://github.com/matllubos/django-is-core/tarball/1.3.89#egg=django-is-core-1.3.89',
    ],
    zip_safe=False,
)
