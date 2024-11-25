from invoke import task


@task
def lint(c):
    c.run("python -m black .")
    c.run("python -m isort .")


@task
def populate(c):
    c.run("python populate_database.py")


@task
def run(c):
    c.run("fastapi dev main.py")


@task
def reqs(c):
    c.run("pip install -r requirements.txt")


@task
def test(c):
    c.run("pytest")
