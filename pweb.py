import os
import glob
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape


CONTENT_DIRECTORY = 'content'
TEMPLATE_SUBDIRECTORY = 'templates'
POSTS_SUBSUBDIRECTORY = 'posts'
STATICS_DIRECTORY = 'static'
TEMPLATE_SUBDIRECTORY_FULL = '{0}/{1}'.format(
    CONTENT_DIRECTORY, TEMPLATE_SUBDIRECTORY)
DISTRIBUTION_DIRECTORY = 'dist'


TAGS = {
    '0001': [('software development', '#'), ('JavaScript', '#')],
}


def url(value):
    if 'post:' in value:
        _, postnum = value.split(':')
        post_name = glob.glob('content/templates/posts/{}-*.html'.format(postnum))[0]
        return 'posts/{}'.format(os.path.basename(post_name))

    LINKS = {
        'cv': '/cv.html',
        'contact': '/contact.html',
        'blog': '/blog.html',
        'old-posts': '/old-posts.html'
    }
    return LINKS[value]


env = Environment(
    loader=FileSystemLoader(TEMPLATE_SUBDIRECTORY_FULL, followlinks=True),
    autoescape=select_autoescape(['html'])
)
env.filters['url'] = url

# [Re]Create distribution directory
if os.path.isdir(DISTRIBUTION_DIRECTORY):
    shutil.rmtree(DISTRIBUTION_DIRECTORY)
os.mkdir(DISTRIBUTION_DIRECTORY)

# Generate blog
post_distribution_path = 'dist/posts'
os.mkdir(post_distribution_path)
last_post = None
for post_filename in sorted(os.listdir(path='content/templates/posts')):
    if post_filename[-5:] == '.html':
        last_post = post_filename
        template = env.get_template('posts/{}'.format(post_filename))
        distribution_path = '{}/{}'.format(post_distribution_path,
                                           post_filename)
        post_serial_num = post_filename.split('-')[0]
        if post_serial_num in TAGS:
            tags = TAGS[post_filename.split('-')[0]]
        else:
            tags = ()
        template.stream(tags=tags).dump(distribution_path)

# Link last post to include it in the main blog page
shutil.copyfile('content/templates/posts/{}'.format(last_post),
                'content/templates/posts/latest.html')
last_post_content = ''
with open('content/templates/posts/latest.html') as latest:
    last_post_content = latest.read()
last_post_content = last_post_content.replace('{% extends "blog.html" %}', '')
with open('content/templates/posts/latest.html', 'w') as latest:
    latest.write(last_post_content)

# Generate main templates
# TODO: Recursive to recreate structure in distribution directory to refactor
# with blog
for template_name in os.listdir(path=TEMPLATE_SUBDIRECTORY_FULL):
    if template_name[-5:] == '.html':
        template = env.get_template(template_name)
        distribution_path = '{}/{}'.format(DISTRIBUTION_DIRECTORY,
                                           template_name)
        template.stream(the='variables', go='here').dump(distribution_path)

os.remove('content/templates/posts/latest.html')

# Copy other statics into dist dir
shutil.copytree(STATICS_DIRECTORY, '{}/{}'.format(
    DISTRIBUTION_DIRECTORY,
    STATICS_DIRECTORY
))
