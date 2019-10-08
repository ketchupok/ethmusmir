# LOOK_STORAGE_PATH=/tmp gunicorn --reload 'mirserver.app:get_app()'
# gunicorn --reload mirserver.app
LOOK_STORAGE_PATH=tmp/ gunicorn --reload 'mirserver.app:get_app()'
