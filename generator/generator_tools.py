#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2018-09-12
# @copyright by hoojo @2018
# @changelog generator fabric network config tools core code


# ===============================================================================
# 标题：generator fabric network config tools core code
# ===============================================================================
# 使用：利用 Jinja2 template engine 生成 fabric 配置
# -------------------------------------------------------------------------------
# 描述：生成 fabric 网络配置
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 构建 fabric 网络配置生成工具Class
# -------------------------------------------------------------------------------
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import select_autoescape
from generator.app_log import AppLog as log
import os


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

        if self.count < 0:
            self.count = 0


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

        if self.template_count < self.__template_count:
            self.template_count = self.__template_count

        if self.user_count < self.__user_count:
            self.user_count = self.__user_count


class TemplateEngine(object):

    # 从指定位置加载模板的环境
    __loader = FileSystemLoader('../templates')

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
        # 获取模板
        template = TemplateEngine.__env.get_template(template_file)

        # 渲染模板
        result = template.render(args)

        return result

    @staticmethod
    def writer(output, template_file, data):
        file_path = output + "/" + template_file

        realpath = os.path.realpath(file_path)
        dirname = os.path.dirname(realpath)
        log.info('generator file to realpath: %s' % realpath)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(file_path, 'w', encoding=u'utf-8') as file:
            file.seek(0)
            file.truncate()   #清空文件

            file.write(data)

            file.flush()
            file.close()

    @staticmethod
    def generator(output, template_file, args):
        log.info("start generator config: %s" % template_file)
        log.debug("generator config to: %s" % output)
        log.debug("generator args: %s" % args)

        result = TemplateEngine.render(template_file, args)
        print(result)

        TemplateEngine.writer(output, template_file, result)

        log.done("generator config [%s]" % template_file)


class GenFabricNetworkTools(object):

    def gen_crypot_config(self, orderers, peers):
        if orderers is None:
            orderers = [OrdererOrg()]

        if peers is None:
            peers = [PeerOrg('Org1'), PeerOrg('Org2')]

        TemplateEngine.generator("networks", "fabric-configs/crypto-config.yaml", dict(orderers=orderers, peers=peers))

    def gen_configtx(self, orderers, peers):
        if orderers is None:
            orderers = [OrdererOrg()]

        if peers is None:
            peers = [PeerOrg('Org1'), PeerOrg('Org2')]

        TemplateEngine.generator("networks", "fabric-configs/configtx.yaml", dict(orderers=orderers, peers=peers))

    def gen_generate_shell(self, peers):
        if peers is None:
            peers = [PeerOrg('Org1'), PeerOrg('Org2')]

        TemplateEngine.generator("networks", "fabric-configs/generate.sh", dict(peers=peers))

    def gen_fabric_compose(self, orderers, peers):
        if orderers is None:
            orderers = [OrdererOrg('orderer_Org1'), OrdererOrg('orderer_Org2', domain='hoojo.xyz')]

        if peers is None:
            peers = [PeerOrg('Org1', domain='simple.top', hostnames=['foo', 'bar']), PeerOrg('Org2', domain='example.cn', hostnames=['zyz', 'abc'])]

        TemplateEngine.generator("networks", "docker-compose-fabric.yaml", dict(orderers=orderers, peers=peers, zookeeper_count=2, kafka_count=5))

    def gen_zookeeper_kafka(self, zookeeper_count=3, kafka_count=4):
        TemplateEngine.generator("networks", "docker-compose-zookeeper-kafka.yaml", dict(zookeeper_count=zookeeper_count, kafka_count=kafka_count))


GenFabricNetworkTools().gen_zookeeper_kafka()