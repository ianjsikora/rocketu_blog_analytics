from fabric.api import *
from fabric.contrib.files import upload_template
from fabric.decorators import task


env.hosts = ['54.200.131.55']
env.user = 'ubuntu'
env.key_filename = '~/.ssh/blog_analytics.pem'
env.shell = "/bin/bash -l -i -c"

@task
def restart_app():
    with prefix("workon blog_analytics"):
        with cd("/home/ubuntu/rocketu_blog_analytics"):
            sudo("service supervisor restart")
            sudo("service nginx restart")

@task
def deploy():
    with prefix("workon blog_analytics"):
        with cd("/home/ubuntu/rocketu_blog_analytics"):
            run("git pull origin master")
            run("pip install -r requirements.txt")
            run("python manage.py makemigrations")
            run("python manage.py migrate")
            run("python manage.py collectstatic")

    restart_app()


@task
def setup_postgres(database_name, password):
    sudo("adduser {}".format(database_name))
    sudo("apt-get install postgresql postgresql-contrib libpq-dev")

    with settings(sudo_user='postgres'):
        sudo("createuser {}".format(database_name))
        sudo("createdb {}".format(database_name))
        alter_user_statement = "ALTER USER {} WITH PASSWORD '{}';".format(database_name, password)
        sudo('psql -c "{}"'.format(alter_user_statement))

    restart_app()

@task
def setup_gunicorn(project_name):
    with prefix("workon blog_analytics"):
        run("pip install gunicorn --upgrade")
        upload_template("./deploy/gunicorn.conf",
                        "/{}".format(project_name),
                        {'project_name': project_name},
                        use_sudo=True,
                        backup=False)

        restart_app()

@task
def setup_gunicorn(project_name):
    with prefix("workon blog_analytics"):
        run("pip install gunicorn --upgrade")
        upload_template("./deploy/gunicorn.conf",
                        "/{}".format(project_name),
                        {'project_name': project_name},
                        use_sudo=True,
                        backup=False)

        restart_app()

@task
def setup_supervisor(project_name, virtualenv_name):
    with prefix("workon blog_analytics"):
        run("sudo apt-get install supervisor --upgrade")
        upload_template("./deploy/gunicorn.conf",
                        "/{}".format(project_name),
                        {'project_name': project_name},
                        {'virtualenv_name': virtualenv_name},
                        use_sudo=True,
                        backup=False)

        restart_app()

@task
def setup_nginx(project_name, server_name):
    upload_template("./deploy/nginx.conf",
                    "/etc/nginx/sites-enabled/{}.conf".format(project_name),
                    {'server_name': server_name},
                    use_sudo=True,
                    backup=False)

    restart_app()

