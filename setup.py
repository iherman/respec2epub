# -*- coding: utf-8 -*-

from distutils.core import setup
from rp2epub import __version__

setup(
	name = 'rp2epub',
	version = __version__,
	packages = ['rp2epub'],
	scripts = ['script/rp2epub'],
	url = 'https://github.com/iherman/respec2epub',
	download_url='https://github.com/iherman/tr2epub/archive/master.zip',
	license = 'W3C® SOFTWARE NOTICE AND LICENSE <http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>',
	author = 'Ivan Herman',
	author_email = 'ivan@ivan-herman.net',
	description = 'Generate EPUB3 files from respec based W3C Technical Reports, possibly generating from respec on the fly',
	keywords='W3C EPUB3',
	platforms='any',
        install_requires = ['html5lib'],
)
