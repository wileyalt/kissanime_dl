from setuptools import setup

#Read README.md
with open("README.md", "rb") as f:
	long_descr = f.read().decode("utf-8")

setup(name='kissanime_dl',
	version='1.4.0',
	description='Easy downloading .mp4s from kissanime.to',
	long_description= long_descr,
	url="https://github.com/wileyyugioh/kissanime_dl",
	author='Wiley Y.',
	author_email="wileythrowaway001@gmail.com",
	license='MIT',
	packages=['kissanime_dl'],
	install_requires=[
	'requests',
	'lxml'
	],
	zip_safe=False,
	#Disabled because it doesn't work in windows
	#scripts=['bin/kissanime-dl.py']
	entry_points = {
		"console_scripts" : ['kissanime-dl = kissanime_dl.command_line:main']
	}
	)