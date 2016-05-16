from setuptools import setup, dist
from setuptools.command.install import install
from setuptools.command.install_scripts import install_scripts
from distutils.util import convert_path
import os

#-----------------------------------------------------------------------------
# Hack to overcome pip/setuptools problem on Win 10.  See:
#   https://github.com/tomduck/pandoc-eqnos/issues/6
#   https://github.com/pypa/pip/issues/2783
# Note that cmdclass must be be hooked into setup().

# Custom install command class for setup()
class custom_install(install):
    """Ensures setuptools uses custom install_scripts."""
    def run(self):
        super().run()

# Custom install_scripts command class for setup()
class install_scripts_quoted_shebang(install_scripts):
    """Ensure there are quotes around shebang paths with spaces."""
    def write_script(self, script_name, contents, mode="t", *ignored):
        shebang = str(contents.splitlines()[0])
        if shebang.startswith('#!') and ' ' in shebang[2:].strip() \
          and '"' not in shebang:
            quoted_shebang = '#!"%s"' % shebang[2:].strip()
            contents = contents.replace(shebang, quoted_shebang)
        super().write_script(script_name, contents, mode, *ignored)

# The custom command classes only need to be used on Windows machines
if os.name == 'nt':
    cmdclass = {'install': custom_install,
                'install_scripts': install_scripts_quoted_shebang},

    # Below is another hack to overcome a separate bug.  The
    # dist.Distribution.cmdclass dict should not be stored in a length-1 list.

    # Save the original method
    dist.Distribution._get_command_class = dist.Distribution.get_command_class

    # Define a new method that repairs self.cmdclass if needed
    def get_command_class(self, command):
        """Pluggable version of get_command_class()"""
        try:
            # See if the original behaviour works
            return dist.Distribution._get_command_class(self, command)
        except TypeError:
            # If self.cmdclass is the problem, fix it up
            if type(self.cmdclass) is tuple and type(self.cmdclass[0]) is dict:
                self.cmdclass = self.cmdclass[0]
                return dist.Distribution._get_command_class(self, command)
            else:
                # Something else went wrong
                raise

    # Hook in the new method
    dist.Distribution.get_command_class = get_command_class

else:
    cmdclass = {}

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
	entry_points = {
		"console_scripts" : ['kissanime-dl = kissanime_dl.command_line:main']
	},
	cmdclass=cmdclass
	)
