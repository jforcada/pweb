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

## Format code

http://hilite.me/

With `monokai` theme. For plain output YAML and `autumn`.

## TODO

- Projects page
- Responsive
- Highlight tags on hover
