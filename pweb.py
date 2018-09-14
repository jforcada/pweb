import os
import glob
import shutil
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape


CONTENT_FILE_PATH = 'content/content.json'
TEMPLATES_PATH = 'content/templates'
POSTS_PATH = '{}/posts'.format(TEMPLATES_PATH)
POSTS_DIRNAME = 'posts'
TAGS_DIRNAME = 'tags'
VIRTUAL_PATH = 'virtual'
STATICS_DIRECTORY = 'static'
DISTRIBUTION_DIRECTORY = 'dist'
POST_DISTRIBUTION_PATH = '{}/posts'.format(DISTRIBUTION_DIRECTORY)
TAGS_DISTRIBUTION_PATH = '{}/tags'.format(DISTRIBUTION_DIRECTORY)


TOP_LEVEL_PAGES = []
BLOG_PAGE = None
POSTS = []
TAGS = []


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

    def __init__(self, serial_num, title, date, tags):
        self.serial_num = serial_num
        self.title = title
        self.date = date
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


def load_site(content_file_path):
    global BLOG_PAGE
    with open(content_file_path) as f:
        data = json.load(f)

    for page in data['topLevel']:
        TOP_LEVEL_PAGES.append(TopLevelPage(page['title'], page['filename']))

    BLOG_PAGE = TopLevelPage(data['blog']['title'], data['blog']['filename'])
    for post in data['blog']['posts']:
        if 'hide' not in post or not post['hide']:
            POSTS.append(
                Post(
                    post['serialNum'],
                    post['title'],
                    post['date'],
                    [Tag(tag) for tag in post['tags']])
                )
    for tag in data['blog']['tags']:
        TAGS.append(Tag(tag))


def url(value):
    for page in TOP_LEVEL_PAGES:
        if value == page.filename:
            return page.url

    if value == BLOG_PAGE.filename:
        return BLOG_PAGE.url


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


def generate_blog(env, last_post):
    tags_to_posts = {}
    os.mkdir(POST_DISTRIBUTION_PATH)

    # Generate posts
    for post in POSTS:
        post_route = glob.glob(
            '{0}/{1}-*.html'.format(POSTS_PATH, post.serial_num))[0]
        post_filename = os.path.basename(post_route)
        template = env.get_template('{0}/{1}'
                                    .format(POSTS_DIRNAME, post_filename))
        distribution_path = '{}/{}'.format(POST_DISTRIBUTION_PATH,
                                           post_filename)
        for tag in post.tags:
            norm_tag = tag.normalized_name
            if norm_tag in tags_to_posts:
                tags_to_posts[norm_tag].add(post)
            else:
                tags_to_posts[norm_tag] = set([post])
        template.stream(post=post).dump(distribution_path)

    # Generate front page
    last_post_raw = get_latest_blog_post_content(last_post)
    last_post_template = env.from_string(last_post_raw)
    last_post_rendered = last_post_template.render(post=last_post)

    template_name = '{}.html'.format(BLOG_PAGE.filename)
    template = env.get_template(template_name)
    distribution_path = '{}/{}'.format(DISTRIBUTION_DIRECTORY,
                                       template_name)
    template.stream(last_post=last_post_rendered).dump(distribution_path)
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


def generate_main_pages(env, sorted_posts):
    for page in TOP_LEVEL_PAGES:
        template_name = '{}.html'.format(page.filename)
        template = env.get_template(template_name)
        distribution_path = '{}/{}'.format(DISTRIBUTION_DIRECTORY,
                                           template_name)
        template.stream(
            posts=sorted_posts
        ).dump(distribution_path)


def copy_robotstxt():
    shutil.copy(
        '{}/robots.txt'.format(TEMPLATES_PATH),
        '{}/robots.txt'.format(DISTRIBUTION_DIRECTORY)
    )


def main():
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_PATH, followlinks=True),
        autoescape=select_autoescape(['html'])
    )
    env.filters['url'] = url

    create_distribution_directory()
    load_site(CONTENT_FILE_PATH)
    all_sorted_posts = sort_posts(POSTS)
    last_post = all_sorted_posts[0]
    tags_to_posts = generate_blog(env, last_post)
    generate_blog_tags_pages(env, tags_to_posts)
    generate_main_pages(env, all_sorted_posts)
    copy_robotstxt()
    copy_statics()


if __name__ == '__main__':
    main()
