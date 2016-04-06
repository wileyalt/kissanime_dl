from setuptools import setup

setup(name='kissanime_dl',
	version='1.5.4.5',
	description='Easy downloading .mp4s from kissanime.to',
	url="https://github.com/wileyyugioh/kissanime_dl",
	author='Wiley Y.',
	author_email="wileythrowaway001@gmail.com",
	license='MIT',
	packages=['kissanime_dl'],
	install_requires=[
	'requests==2.9.1',
	'lxml==3.5.0',
	'js2py==0.35',
	],
	zip_safe=False,
	#Disabled because it doesn't work in windows
	#scripts=['bin/kissanime-dl.py']
	entry_points = {
		"console_scripts" : ['kissanime-dl = kissanime_dl.command_line:main']
	}
	)