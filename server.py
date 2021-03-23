#!/usr/bin/python3 -u
from bottle import route, run, static_file, post, redirect, request
import hmac
import os
import shutil
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
BUILD_ROOT = os.path.join(BASE_DIR, "docs", "_build")
DEBUG = os.environ.get("DEBUG")
SECRET = os.environ.get("SECRET")

assert(SECRET or DEBUG)


def run_command(command):
    print(">> ", *command)
    subprocess.check_call(command)


def ensure_up_to_date():
    os.chdir(os.path.join(BASE_DIR, "theme"))
    run_command(["git", "pull"])
    run_command(["npm", "install"])
    run_command(["npm", "run", "build"])
    os.chdir(os.path.join(BASE_DIR, "docs"))
    run_command(["git", "pull"])
    shutil.rmtree(BUILD_ROOT, ignore_errors=True)
    run_command(["make", "html"])
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
    if SECRET:
        signature = request.headers.get('X-Hub-Signature')
        sha, signature = signature.split('=')
        hashhex = hmac.new(SECRET.encode(), request.body.read(), digestmod='sha1').hexdigest()
        if not hmac.compare_digest(hashhex, signature):
            return "403"
    ensure_up_to_date()
    return "OK"


def serve():
    if DEBUG:
        run(host='localhost', port=8080, debug=True)
    else:
        run(host="0.0.0.0", port=8080, server='waitress')


def main():
    print("Base dir is ", BASE_DIR)
    print("Build root is ", BUILD_ROOT)
    ensure_up_to_date()
    serve()


main()