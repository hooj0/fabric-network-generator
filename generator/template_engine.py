#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2018-09-12
# @copyright by hoojo @2018
# @changelog generator fabric network config tools template engine code


# ===============================================================================
# 标题：generator fabric network config tools template engine code
# ===============================================================================
# 使用：利用 Jinja2 template engine 生成 fabric 配置
# -------------------------------------------------------------------------------
# 描述：生成 fabric 网络配置的模板引擎
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 构建 fabric 网络配置生成工具的模板引擎
# -------------------------------------------------------------------------------
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import select_autoescape
from generator.app_log import AppLog as log
import os


class TemplateEngine(object):

    # 从指定位置加载模板的环境
    __loader = FileSystemLoader('templates')

    # 更多配置参考：http://jinja.pocoo.org/docs/2.10/api/#high-level-api
    __env = Environment(loader=__loader,
                        autoescape=select_autoescape(['yml', 'yaml', 'js', 'sh']),
                        block_start_string='{%', block_end_string='%}',
                        variable_start_string='%{', variable_end_string='}',

                        line_statement_prefix="%%",
                        line_comment_prefix="%#",
                        trim_blocks=True, keep_trailing_newline=True, lstrip_blocks=True)

    @staticmethod
    def render(template_file, args):
        log.info("generator config template file: %s" % template_file)
        log.debug("generator args: %s" % args)

        # 获取模板
        template = TemplateEngine.__env.get_template(template_file)
        # 渲染模板
        result = template.render(args)

        return result

    @staticmethod
    def writer(output, template_file, data):
        log.debug("generator config to location: %s" % output)

        file_path = output + "/" + template_file
        realpath = os.path.realpath(file_path)
        dirname = os.path.dirname(realpath)
        log.info('generator file to absolute path: %s' % realpath)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(file_path, 'w', encoding=u'utf-8') as file:
            file.seek(0)
            file.truncate()   # 清空文件

            file.write(data)

            file.flush()
            file.close()

    @staticmethod
    def generator(output, template_file, args):
        log.line('template engine generator file')

        result = TemplateEngine.render(template_file, args)

        TemplateEngine.writer(output, template_file, result)

        log.done("template engine generator file")
        return result
