# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import json

from flask import Blueprint, render_template
from flask import request

from utils.mwplugin import MwPlugin
from admin.user_login_check import panel_login_required

from admin import model

import core.mw as mw
import utils.config as utils_config


blueprint = Blueprint('plugins', __name__, url_prefix='/plugins', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
@panel_login_required
def index():
    return render_template('plugins.html')

# 初始化检查,首页提示选择安装
@blueprint.route('/init', endpoint='init', methods=['POST'])
@panel_login_required
def init():
    plugin_names = {
        'openresty': '1.25.3',
        'php': '56',
        'swap': '1.1',
        'mysql': '5.7',
        'phpmyadmin': '4.4.15',
    }

    pn_dir = mw.getPluginDir()
    pn_server_dir = mw.getServerDir()
    pn_list = []
    for pn in plugin_names:
        info = {}
        pn_json = pn_dir + '/' + pn + '/info.json'
        pn_server = pn_server_dir + '/' + pn
        if not os.path.exists(pn_server):

            tmp = mw.readFile(pn_json)
            tmp = json.loads(tmp)

            info['title'] = tmp['title']
            info['name'] = tmp['name']
            info['versions'] = tmp['versions']
            info['default_ver'] = plugin_names[pn]
            pn_list.append(info)
        else:
            return mw.returnData(False, 'ok')

    return mw.returnData(True, 'ok', pn_list)

# 首页软件展示
@blueprint.route('/index_list', endpoint='index_list', methods=['GET','POST'])
@panel_login_required
def index_list():
    pg = MwPlugin.instance()
    return pg.getIndexList()

# 插件列表
@blueprint.route('/list', endpoint='list', methods=['GET'])
@panel_login_required
def list():
    plugins_type = request.args.get('type', '0')
    page = request.args.get('p', '1')
    search = request.args.get('search', '').lower()

    if not mw.isNumber(plugins_type):
        plugins_type = 1

    if not mw.isNumber(page):
        page = 0

    pg = MwPlugin.instance()
    return pg.getList(plugins_type, search, int(page))

# 插件设置是否在首页展示
@blueprint.route('/set_index', endpoint='set_index', methods=['POST'])
@panel_login_required
def set_index():
    name = request.form.get('name', '')
    status = request.form.get('status', '0')
    version = request.form.get('version', '')

    pg = MwPlugin.instance()
    if status == '1':
        return pg.addIndex(name, version)
    return pg.removeIndex(name, version)

# 插件安装
@blueprint.route('/install', endpoint='install', methods=['POST'])
@panel_login_required
def install():
    name = request.form.get('name', '')
    version = request.form.get('version', '')

    upgrade = None
    if hasattr(request.form, 'upgrade'):
        upgrade = True

    pg = MwPlugin.instance()
    return pg.install(name, version, upgrade=upgrade)

# 插件卸载
@blueprint.route('/uninstall', endpoint='uninstall', methods=['POST'])
@panel_login_required
def uninstall():
    name = request.form.get('name', '')
    version = request.form.get('version', '')
    pg = MwPlugin.instance()
    return pg.uninstall(name, version)

# 文件读取
@blueprint.route('/menu', endpoint='menu', methods=['GET'])
@panel_login_required
def menu():
    data = utils_config.getGlobalVar()
    pg = MwPlugin.instance()
    tag = request.args.get('tag', '')

    hook_menu = model.getOptionByJson('hook_menu',type='hook',default=[])
    content = ''
    for menu_data in hook_menu:
        if tag == menu_data['name'] and 'path' in menu_data:
            t = pg.menuGetAbsPath(tag, menu_data['path'])
            content = mw.readFile(t)
    #------------------------------------------------------------
    data['hook_tag'] = tag
    data['plugin_content'] = content
    return render_template('plugin_menu.html', data=data)

# 文件读取
@blueprint.route('/file', endpoint='file', methods=['GET'])
@panel_login_required
def file():
    name = request.args.get('name', '')
    if name.strip() == '':
        return ''

    f = request.args.get('f', '')
    if f.strip() == '':
        return ''

    file = mw.getPluginDir() + '/' + name + '/' + f
    if not os.path.exists(file):
        return ''

    suffix = mw.getPathSuffix(file)
    if suffix == '.css':
        content = mw.readFile(file)
        from flask import Response
        from flask import make_response
        v = Response(content, headers={'Content-Type': 'text/css; charset="utf-8"'})
        return make_response(v)
    content = open(file, 'rb').read()
    return content

# 插件设置页
@blueprint.route('/setting', endpoint='setting', methods=['GET'])
@panel_login_required
def setting():
    name = request.args.get('name', '')
    html = mw.getPluginDir() + '/' + name + '/index.html'
    return mw.readFile(html)


# 插件统一回调入口API
@blueprint.route('/run', endpoint='run', methods=['GET','POST'])
@panel_login_required
def run():
    name = request.form.get('name', '')
    func = request.form.get('func', '')
    version = request.form.get('version', '')
    args = request.form.get('args', '')
    script = request.form.get('script', 'index')

    pg = MwPlugin.instance()
    data = pg.run(name, func, version, args, script)
    if data[1] == '':
        r = mw.returnData(True, "OK", data[0].strip())
    else:
        r = mw.returnData(False, data[1].strip())
    return r


# 插件统一回调入口API
@blueprint.route('/callback', endpoint='callback', methods=['GET','POST'])
@panel_login_required
def callback():
    name = request.form.get('name', '')
    func = request.form.get('func', '')
    args = request.form.get('args', '')
    script = request.form.get('script', 'index')

    pg = MwPlugin.instance()
    data = pg.callback(name, func, args=args, script=script)
    if data[0]:
        return mw.returnData(True, "OK", data[1])
    return mw.returnData(False, data[1])

