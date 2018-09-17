#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2018-09-16
# @copyright by hoojo @2018
# @changelog generator fabric network config tools value model code


# ===============================================================================
# 标题：generator fabric network config tools value model code
# ===============================================================================
# 描述：生成 fabric 网络配置 传递数据模型对象
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 构建 fabric 网络配置 所需要的 value model
# -------------------------------------------------------------------------------


class OrdererOrg(object):
    """
    Orerer org configuration class
    """

    __default_name = "Orderer"
    __default_domain = "hoojo.me"
    __default_hostnames = [__default_name]

    def __init__(self, name=__default_name, domain=__default_domain, hostnames=None, count=0):

        self.name = name
        self.domain = domain
        self.hostnames = hostnames
        self.count = count

        if hostnames is None:
            self.hostnames = set(self.__default_hostnames)

        if self.count is None or self.count < 0:
            self.count = 0

    def __str__(self):
        return "{name: %s, domain: %s, hostnames: %s, count: %s}" % (self.name, self.domain, self.hostnames, self.count)

    def __repr__(self):
        return self.__str__()


class PeerOrg(object):
    """
    Peer org configuration class
    """

    __default_name = "Org"
    __default_domain = "hoojo.cn"
    __default_hostnames = None

    __template_count = 2
    __user_count = 1

    def __init__(self, name=__default_name, domain=__default_domain, hostnames=None, template_count=__template_count, user_count=__user_count):

        self.name = name
        self.domain = domain
        self.hostnames = hostnames

        self.template_count = template_count
        self.user_count = user_count

        if self.template_count is None or self.template_count < self.__template_count:
            self.template_count = self.__template_count

        if self.user_count is None or self.user_count < self.__user_count:
            self.user_count = self.__user_count

    def __str__(self):
        return "{name: %s, domain: %s, hostnames: %s, template_count: %s, user_count: %s}" \
               % (self.name, self.domain, self.hostnames, self.template_count, self.user_count)

    def __repr__(self):
        return self.__str__()
