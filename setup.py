from setuptools import setup
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('kissanime_dl/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setup(name='kissanime_dl',
	version=main_ns['__version__'],
	description='Easy downloading .mp4s from kissanime.to',
	url="https://github.com/wileyyugioh/kissanime_dl",
	author='Wiley Y.',
	author_email="wileythrowaway001@gmail.com",
	license='MIT',
	packages=['kissanime_dl'],
	install_requires=[
	'requests==2.9.1',
	'lxml>=3.5.0',
	'js2py==0.35',
	],
	zip_safe=False,
	#Disabled because it doesn't work in windows
	#scripts=['bin/kissanime-dl.py']
	entry_points = {
		"console_scripts" : ['kissanime-dl = kissanime_dl.command_line:main']
	}
	)
