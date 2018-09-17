#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2018-09-13
# @copyright by hoojo @2018
# @changelog generator fabric network config tools application log class


# ===============================================================================
# 标题：log class support application log print
# ===============================================================================
# 使用：利用 控制台 有色输出日志信息，提高可辨认度
# -------------------------------------------------------------------------------
# 描述：打印出不同颜色的日志内容、级别、格式
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 构建 fabric 网络配置生成工具Class
# -------------------------------------------------------------------------------
from random import choice


class AppLog(object):
    """
    examples
        print("\033[0;37;40m\t this is message.\033[0m")

    数值表示的参数含义：
        显示方式: 0（默认\）、1（高亮）、22（非粗体）、4（下划线）、24（非下划线）、 5（闪烁）、25（非闪烁）、7（反显）、27（非反显）
        前景色:   30（黑色）、31（红色）、32（绿色）、 33（黄色）、34（蓝色）、35（洋 红）、36（青色）、37（白色）
        背景色:   40（黑色）、41（红色）、42（绿色）、 43（黄色）、44（蓝色）、45（洋 红）、46（青色）、47（白色）
    """

    __color_list = [31, 32, 33, 34, 35, 36]

    def __log(message, level='DEBUG', line_before=False, line_after=False):
        width = len(message) + 20
        line = AppLog.color_text("=" * width)

        if line_before:
            print(line)

        if level == 'DEBUG':
            print("\033[1;33;42m %s \033[0m ===> \033[0;36m%s\033[0m" % (level.rjust(8), message))
        elif level == 'INFO':
            print("\033[1;33;42m %s \033[0m ===> \033[0;35m%s\033[0m" % (level.rjust(8), message))
        elif level == 'WARN':
            print("\033[1;33;42m %s \033[0m ===> \033[0;33m%s\033[0m" % (level.rjust(8), message))
        elif level == 'ERROR':
            print("\033[1;33;42m %s \033[0m ===> \033[0;31m%s\033[0m" % (level.rjust(8), message))
        else:
            print("\033[1;33;42m %s \033[0m ===> \033[1;37m%s\033[0m" % (level.rjust(8), message))

        if line_after:
            print(line)

    @staticmethod
    def color_random():
        return '\033[1;' + str(choice(AppLog.__color_list)) + 'm%s\033[0m'

    @staticmethod
    def color_text(message):
        return AppLog.color_random() % message

    @staticmethod
    def line(message=None, char='=', width=120):
        if message:
            message = message.center(len(message) + 4).center(width, char)

            print(AppLog.color_text(message))
        else:
            print(AppLog.color_text(char * width))

    @staticmethod
    def title(content, char="=", width=120):
        AppLog.titles([content], char, width)

    @staticmethod
    def titles(contents, char="=", width=120, align='center'):
        padding = 30
        width = min(160, width)

        line = char * width
        color = AppLog.color_random()

        print(color % line)
        for content in contents:
            if len(content) > width - padding:
                content = content[0:width - padding - 8] + "......"

            if align == 'center':
                title = content.center(width - padding).center(width, char)
            else:
                content = " " + content
                title = content.ljust(width - padding).center(width, char)

            print(color % title)
        print(color % line)

    @staticmethod
    def info(message, line_before=False, line_after=False):
        AppLog.__log(message, 'INFO', line_before, line_after)

    @staticmethod
    def warn(message, line_before=False, line_after=False):
        AppLog.__log(message, 'WARN', line_before, line_after)

    @staticmethod
    def debug(message, line_before=False, line_after=False):
        AppLog.__log(message, 'DEBUG', line_before, line_after)

    @staticmethod
    def error(message, line_before=False, line_after=False):
        AppLog.__log(message, 'ERROR', line_before, line_after)

    @staticmethod
    def out(message, action='TRACE', line_before=False, line_after=False):
        AppLog.__log(message, action, line_before, line_after)

    @staticmethod
    def done(action):
        print("\n\033[1;33m%s\033[0m %s \033[1;32m%s\033[0m\n" % (action, '.' * 20, 'Done!'))

