#!/usr/bin/python3
from bottle import route, run, static_file, post, redirect
import os
import shutil
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
BUILD_ROOT = os.path.join(BASE_DIR, "docs", "_build")
DEBUG = os.environ.get("DEBUG")


def run_command(command):
    print(">> ", *command)
    subprocess.check_call(command)


def ensure_up_to_date():
    os.chdir(os.path.join(BASE_DIR, "theme"))
    run_command(["git", "pull"])
    run_command(["npm", "run", "build"])
    os.chdir(os.path.join(BASE_DIR, "docs"))
    run_command(["git", "pull"])
    run_command(["make", "html"])
    run_command(["make", "epub"])
    shutil.copy(os.path.join(BUILD_ROOT, "epub", "sphinx.epub"), os.path.join(BUILD_ROOT, "html", "notes.epub"))


@route('/')
def index():
    redirect("/index.html")

@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root=os.path.join(BASE_DIR, "docs", "_build", "html"))


@post('/update')
def update():
    ensure_up_to_date()
    return "OK"


def serve():
    if DEBUG:
        run(host='localhost', port=8080, debug=True)
    else:
        run(host="0.0.0.0", post="80")


def main():
    print("Base dir is ", BASE_DIR)
    ensure_up_to_date()
    serve()


main()