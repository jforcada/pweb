# PWeb

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

### Blockers to release

- Push to github
- Add github link to this project in static site generator post
- Add layer scheme to acceptance testing: view | business logic | database models

### Posts

1. Recover all wordpress posts
2. ReactJS opinion
3. Django testing II: Integration tests
4. Django testing III: Unit tests

### Generator

- Make tags unique in content.json to avoid missing them
- Find a better way to format code
