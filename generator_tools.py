#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2018-09-12
# @copyright by hoojo @2018
# @changelog generator fabric network config tools


# ===============================================================================
# 标题：generator fabric network config tools
# ===============================================================================
# 使用：利用 Jinja2 template engine 生成 fabric 配置
# -------------------------------------------------------------------------------
# 描述：生成 fabric 网络配置
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 构建 fabric 网络配置生成工具Class
# -------------------------------------------------------------------------------
from generator.app_log import AppLog as log
import os
import shutil


class GeneratorTools(object):

    def copy_network_files(self, output='networks'):
        if output is None or len(output) < 1:
            raise IOError('output dir is undefined.')

        log.title('copy networks file')
        log.info('copy network files to "%s"' % output)

        if not os.path.exists(output):
            os.makedirs(output)
        else:
            shutil.rmtree(output)

        shutil.copytree('templates', output)
        shutil.rmtree('%s/commons-macro' % output)

        log.done('copy networks file')

    def reader_setting_config(self):
        with open('settings.yaml', 'r', encoding=u'utf-8') as file:
            data = file.readlines()

        pass

    def generator_networks(self):
        pass


GeneratorTools().copy_network_files()