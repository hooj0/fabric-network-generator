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
from generator.generator_networks import GenFabricNetworkTools
from generator.network_model import OrdererOrg
from generator.network_model import PeerOrg
import os
import shutil
import yaml


class GeneratorTools(object):

    def __copy_network_files(self, output='networks'):
        if output is None or len(output) < 1:
            raise IOError('output dir is undefined.')

        log.line('copy networks file')
        log.info('copy network files to "%s"' % output)

        if not os.path.exists(output):
            os.makedirs(output)
        else:
            shutil.rmtree(output)

        shutil.copytree('templates', output)
        shutil.rmtree('%s/commons-macro' % output)

        log.done('copy networks file')

    def __reader_setting_config(self):
        log.line('reader settings config')

        config = 'settings.yaml'
        if not os.path.exists(config):
            log.error('%s is not found!' % config)
            raise IOError('%s is not found!' % config)

        with open(config, 'r', encoding=u'utf-8') as file:
            data = file.read()

        settings = yaml.load(data)['settings']
        log.debug('settings config data: %s' % settings)

        log.done('reader settings config')
        return settings

    def __transfor_model(self):
        settings = self.__reader_setting_config()

        log.line('transfor settings to model')
        orderers, peers = [], []
        for orderer in settings['orderers']:
            name, domain, count, hostnames = None, None, None, None

            if 'name' in orderer:
                name = orderer['name']

            if 'domain' in orderer:
                domain = orderer['domain']

            if 'count' in orderer:
                count = orderer['count']

            if 'hostnames' in orderer:
                hostnames = orderer['hostnames']

            orderers.append(OrdererOrg(name, domain, hostnames, count))

        for peer in settings['peers']:
            name = domain = hostnames = template_count = user_count = None

            if 'name' in peer:
                name = peer['name']

            if 'domain' in peer:
                domain = peer['domain']

            if 'hostnames' in peer:
                hostnames = peer['hostnames']

            if 'template_count' in peer:
                template_count = peer['template_count']
            if 'user_count' in peer:
                user_count = peer['user_count']

            peers.append(PeerOrg(name, domain, hostnames, template_count, user_count))

        kafka = settings['kafka']
        zookeeper = settings['zookeeper']

        log.debug('orderers: %s' % orderers)
        log.debug('peers: %s' % peers)
        log.debug('kafka: %s' % kafka)
        log.debug('zookeeper: %s' % zookeeper)

        log.done('transfor settings to model')
        return settings, orderers, peers, kafka, zookeeper

    def generator_networks(self):
        log.title('generator networks')

        settings, orderers, peers, kafka, zookeeper = self.__transfor_model()

        self.__copy_network_files(settings['output'])
        tools = GenFabricNetworkTools(settings['output'])

        result = tools.gen_crypto_config(orderers, peers)
        result = tools.gen_configtx(orderers, peers)
        result = tools.gen_generate_shell(peers)
        result = tools.gen_fabric_compose(orderers, peers, zookeeper, kafka)
        result = tools.gen_zookeeper_kafka(zookeeper, kafka)
        result = tools.gen_fabric_template(orderers, peers, zookeeper, kafka)
        result = tools.gen_couchdb(orderers, peers, zookeeper, kafka)
        result = tools.gen_monitor(orderers, peers, zookeeper, kafka)

        result = tools.gen_properties(orderers, peers)

        # print(result)
        log.done('generator networks')


GeneratorTools().generator_networks()