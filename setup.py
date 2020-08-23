from setuptools import setup
setup(
    name="njzjzwikibot",
    version="0.0.1",
    packages=['njzjzwikibot'],
    install_requires=['bs4', 'pywikibot', 'requests'],
    entry_points={
        'console_scripts': [
            'njzjzwikibot = njzjzwikibot.main:main']
    }
)
