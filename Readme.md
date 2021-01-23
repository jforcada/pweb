# PWeb

A simple static site generator. It run generates https://jforcada.com.

## HowTo

To compile the site:

    $ python pweb.py

To serve it:

    $ cd dist/ && python -m http.server

To compile it for production:

    $ python pweb.py --prod

## Install Python environment to develop

Create pipenv management infrastructure:

    $ pipenv --python 3.8.5

Install requirements:

    $ pipenv install --dev

Enter the virtualenv shell:

    $ pipenv shell

## Interactive development

Install `fswatch`:

    $ sudo apt install fswatch

Run it:

    $ fswatch -o content static | xargs -n1 -I{} python pweb.py

## Format code

http://hilite.me/

With `monokai` theme. For plain output YAML and `autumn`.

## TODO

### Posts

1. Recover all wordpress posts
2. ReactJS opinion
3. Django testing II: Integration tests
4. Django testing III: Unit tests
5. PicoCTF https://picoctf.org/
6. PWN College https://pwn.college/
7. Book Review: Modern C

### Generator

- Make tags unique in content.json to avoid missing them
- Find a better way to format code
- Add leela as a project
- Ubuntu Mono for code snippets
- favicon not alpha, but white background
