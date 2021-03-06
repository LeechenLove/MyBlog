from fabric import task
from invoke import Responder

def _get_github_auth_responders():
    """返回Github用户密码填充器"""
    username_responder = Responder(
        pattern="Username for 'https://github.com':",
        response='{}\n'.format("test")
    )
    password_responder = Responder(
        pattern="Password for 'https://github.com':",
        response='{}\n'.format("test")
    )
    return [username_responder, password_responder]

@task()
def deploy(c):
    supervisor_conf_path = '~/etc/'
    supervisor_program_name = 'MyBlog'

    project_root_path = '~/apps/MyBlog/'

    # 停止应用
    with c.cd(supervisor_conf_path):
        cmd = 'supervisorctl stop {}'.format(supervisor_program_name)
        c.run(cmd)

    # 进入项目根目录，从Git拉取最新代码
    with c.cd(project_root_path):
        cmd = 'git pull'
        responders = _get_github_auth_responders()
        c.run(cmd, watchers = responders)

    # 安装依赖,迁移数据库，收集静态文件
    with c.cd(project_root_path):
        c.run('pipenv install --deploy --ignore-pipfile')
        c.run('pipenv run python manage.py makemigrations')
        c.run('pipenv run python manage.py migrate')
        c.run('pipenv run python collectstatic --noinput')

    # 重新启动应用
    with c.cd(supervisor_conf_path):
        cmd = 'supervisorctl start {}'.format(supervisor_program_name)
        c.run(cmd)
