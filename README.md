# Politisys

## Necessary tools
- [Python](https://www.python.org/)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/)
- [Npm/Node](https://nodejs.org/en/)

## Building
Before executing app it's necessary to build and prepare environment.
```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements
npm install
npm run build
python manage.py runserver
```
