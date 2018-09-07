import os
import glob
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape


TEMPLATES_PATH = 'content/templates'
POSTS_PATH = '{}/posts'.format(TEMPLATES_PATH)
POSTS_DIRNAME = 'posts'

TAGS_DIRNAME = 'tags'

VIRTUAL_PATH = 'virtual'
STATICS_DIRECTORY = 'static'
DISTRIBUTION_DIRECTORY = 'dist'
POST_DISTRIBUTION_PATH = '{}/posts'.format(DISTRIBUTION_DIRECTORY)
TAGS_DISTRIBUTION_PATH = '{}/tags'.format(DISTRIBUTION_DIRECTORY)


class Page(object):
    def __str__(self):
        return 'Abstract Page'

    def url(self):
        raise NotImplementedError()


class TopLevelPage(Page):
    title = None
    filename = None

    def __init__(self, title, filename):
        self.title = title
        self.filename = filename

    def __str__(self):
        return self.title

    @property
    def url(self):
        if self.filename == 'index':
            return '/'
        return '/{}.html'.format(self.filename)


class Post(Page):
    serial_num = None
    title = None
    tags = []

    def __init__(self, serial_num, title, tags):
        self.serial_num = serial_num
        self.title = title
        self.tags = tags

    def __str__(self):
        return self.serial_num

    @property
    def url(self):
        post_name = glob.glob(
            '{0}/{1}-*.html'.format(POSTS_PATH, self.serial_num))[0]
        return '/{0}/{1}'.format(POSTS_DIRNAME, os.path.basename(post_name))


class Tag(Page):
    name = None

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    @property
    def normalized_name(self):
        norm = self.name.lower()
        norm = norm.replace(' ', '-')
        return norm

    @property
    def url(self):
        return '/{0}/{1}.html'.format(TAGS_DIRNAME, self.normalized_name)


def get_tag_from_normalized_name(normalized_name):
    for tag in TAGS:
        if tag.normalized_name == normalized_name:
            return tag


def sort_posts(posts):
    ordered_posts = list(posts)
    ordered_posts = sorted(ordered_posts, key=lambda post: post.serial_num,
                           reverse=True)
    return ordered_posts


TOP_LEVEL_PAGES = [
    TopLevelPage('Index', 'index'),
    TopLevelPage('Contact', 'contact'),
    TopLevelPage('CV', 'cv'),
    TopLevelPage('Blog', 'blog'),
    TopLevelPage('All posts', 'old-posts')
]

TAGS = [
    Tag('software development'),
    Tag('JavaScript'),
    Tag('automation')
]

POSTS = {
    '0001': Post(
        serial_num='0001',
        title='Lean frontend framework based on jQuery for entrepreneurs',
        tags=[Tag('software development'), Tag('JavaScript')]
    ),
    '0002': Post(
        serial_num='0002',
        title='Static site generator with Python and Jinja',
        tags=[Tag('software development'), Tag('automation')]
    ),
    '0003': Post(
        serial_num='0003',
        title='Third Third Third Third Third',
        tags=[Tag('software development'), Tag('JavaScript')]
    )
}


def url(value):
    for page in TOP_LEVEL_PAGES:
        if value == page.filename:
            return page.url


def create_distribution_directory():
    if os.path.isdir(DISTRIBUTION_DIRECTORY):
        shutil.rmtree(DISTRIBUTION_DIRECTORY)
    os.mkdir(DISTRIBUTION_DIRECTORY)


def copy_statics():
    shutil.copytree(STATICS_DIRECTORY, '{}/{}'.format(
        DISTRIBUTION_DIRECTORY,
        STATICS_DIRECTORY
    ))


def get_latest_blog_post_content(last_post):
    last_post_path = '{0}/{1}'.format(TEMPLATES_PATH, last_post.url)
    with open(last_post_path) as latest:
        last_post_content = latest.read()
    last_post_content = last_post_content.replace(
        '{% extends "blog.html" %}', '')
    last_post_content = last_post_content.replace(
        '{% block post %}', '')
    last_post_content = last_post_content.replace(
        '{% endblock %}', '')
    return last_post_content


def generate_blog(env):
    tags_to_posts = {}
    os.mkdir(POST_DISTRIBUTION_PATH)
    for post_serial_num, post in POSTS.items():
        post_route = glob.glob(
            '{0}/{1}-*.html'.format(POSTS_PATH, post_serial_num))[0]
        post_filename = os.path.basename(post_route)
        template = env.get_template('{0}/{1}'
                                    .format(POSTS_DIRNAME, post_filename))
        distribution_path = '{}/{}'.format(POST_DISTRIBUTION_PATH,
                                           post_filename)
        post_serial_num = post_filename.split('-')[0]

        for tag in post.tags:
            norm_tag = tag.normalized_name
            if norm_tag in tags_to_posts:
                tags_to_posts[norm_tag].add(post)
            else:
                tags_to_posts[norm_tag] = set([post])
        template.stream(tags=post.tags).dump(distribution_path)
    return tags_to_posts


def generate_blog_tags_pages(env, tags_to_posts):
    os.mkdir(TAGS_DISTRIBUTION_PATH)
    for norm_tag, posts in tags_to_posts.items():
        tag = get_tag_from_normalized_name(norm_tag)
        template = env.get_template('{}/blog-tag.html'.format(VIRTUAL_PATH))
        distribution_path = '{0}/{1}.html'.format(TAGS_DISTRIBUTION_PATH,
                                                  norm_tag)
        template.stream(tag=tag, posts=sort_posts(posts)).dump(
            distribution_path)


def generate_main_pages(env, sorted_posts, last_post_content):
    for page in TOP_LEVEL_PAGES:
        template_name = '{}.html'.format(page.filename)
        template = env.get_template(template_name)
        distribution_path = '{}/{}'.format(DISTRIBUTION_DIRECTORY,
                                           template_name)
        template.stream(
            posts=sorted_posts,
            last_post_content=last_post_content
        ).dump(distribution_path)


def clean_temp_latest_blog_post():
    os.remove('content/templates/posts/latest.html')


def main():
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_PATH, followlinks=True),
        autoescape=select_autoescape(['html'])
    )
    env.filters['url'] = url

    create_distribution_directory()
    all_sorted_posts = sort_posts(POSTS.values())
    last_post = all_sorted_posts[0]
    tags_to_posts = generate_blog(env)
    generate_blog_tags_pages(env, tags_to_posts)
    last_post_content = get_latest_blog_post_content(last_post)
    generate_main_pages(env, all_sorted_posts, last_post_content)
    copy_statics()


if __name__ == '__main__':
    main()
