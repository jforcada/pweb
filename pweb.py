import os
import shutil
from jinja2 import Environment, PackageLoader, select_autoescape


CONTENT_DIRECTORY = 'content'
TEMPLATE_SUBDIRECTORY = 'templates'
STATICS_DIRECTORY = 'static'
TEMPLATE_SUBDIRECTORY_FULL = '{0}/{1}'.format(
    CONTENT_DIRECTORY, TEMPLATE_SUBDIRECTORY)
DISTRIBUTION_DIRECTORY = 'dist'

env = Environment(
    loader=PackageLoader(CONTENT_DIRECTORY, TEMPLATE_SUBDIRECTORY),
    autoescape=select_autoescape(['html'])
)

# [Re]Create distribution directory
if os.path.isdir(DISTRIBUTION_DIRECTORY):
    shutil.rmtree(DISTRIBUTION_DIRECTORY)
os.mkdir(DISTRIBUTION_DIRECTORY)

# Generate templates
# TODO: Recursive to recreate structure in distribution directory
for template_name in os.listdir(path=TEMPLATE_SUBDIRECTORY_FULL):
    if template_name[-5:] == '.html':
        template = env.get_template(template_name)
        distribution_path = '{}/{}'.format(DISTRIBUTION_DIRECTORY,
                                           template_name)
        template.stream(the='variables', go='here').dump(distribution_path)

# Copy other statics into dist dir
shutil.copytree(STATICS_DIRECTORY, '{}/{}'.format(
    DISTRIBUTION_DIRECTORY,
    STATICS_DIRECTORY
))
