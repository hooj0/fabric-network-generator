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
from generator.app_log import AppLog as log
from generator.network_model import OrdererOrg
from generator.network_model import PeerOrg
from generator.template_engine import TemplateEngine


class GenFabricNetworkTools(object):

    def __init__(self, output=None):
        if output is None:
            output = 'networks'

        self.output_directory = output

    def __default_args(self, orderers, peers, kafka=None, zookeeper=None):
        if orderers is None:
            orderers = [OrdererOrg()]
        if peers is None:
            peers = [PeerOrg('Org1'), PeerOrg('Org2')]
        if kafka is None:
            kafka = {'domain': 'example.com', 'count': 4}
        if zookeeper is None:
            zookeeper = {'domain': 'example.com', 'count': 3}

        return orderers, peers, kafka, zookeeper

    def gen_crypto_config(self, orderers, peers, orderer_type='kafka'):
        log.line('start generator crypto config')

        orderers, peers, *_ = self.__default_args(orderers, peers)
        log.debug('default orderers: %s' % orderers)
        log.debug('default peers: %s' % peers)

        args = dict(orderers=orderers, peers=peers, orderer_type=orderer_type)
        result = TemplateEngine.generator(self.output_directory, "fabric-configs/crypto-config.yaml", args)

        log.done('generator crypto config')
        return result

    def gen_configtx(self, orderers, peers, kafka, orderer_type):
        log.line('start generator configtx config')

        orderers, peers, kafka, _ = self.__default_args(orderers, peers, kafka)
        log.debug('default orderers: %s' % orderers)
        log.debug('default peers: %s' % peers)
        log.debug('default kafka: %s' % kafka)

        args = dict(orderers=orderers, peers=peers, orderer_type=orderer_type, kafka_count=kafka['count'])
        result = TemplateEngine.generator(self.output_directory, "fabric-configs/configtx.yaml", args)

        log.done('generator configtx config')
        return result

    def gen_generate_shell(self, peers):
        log.line('start generator shell script')

        _, peers, *_ = self.__default_args(None, peers)
        log.debug('default peers: %s' % peers)

        result = TemplateEngine.generator(self.output_directory, "fabric-configs/generate.sh", dict(peers=peers))

        log.done('generator shell script')
        return result

    def gen_fabric_compose(self, orderers, peers, zookeeper, kafka):
        log.line('start generator fabric compose file')

        orderers, peers, kafka, zookeeper = self.__default_args(orderers, peers, kafka, zookeeper)
        log.debug('default orderers: %s' % orderers)
        log.debug('default peers: %s' % peers)
        log.debug('default kafka: %s' % kafka)
        log.debug('default zookeeper: %s' % zookeeper)

        args = dict(orderers=orderers, peers=peers, zookeeper_count=zookeeper['count'], kafka_count=kafka['count'])
        result = TemplateEngine.generator(self.output_directory, "docker-compose-fabric.yaml", args)

        log.done('generator fabric compose file')
        return result

    def gen_zookeeper_kafka(self, zookeeper, kafka):
        log.line('start generator fabric zookeeper-kafka file')

        _, _, kafka, zookeeper = self.__default_args(None, None, kafka, zookeeper)
        log.debug('default kafka: %s' % kafka)
        log.debug('default zookeeper: %s' % zookeeper)

        args = dict(zookeeper_count=zookeeper['count'], kafka_count=kafka['count'])
        result = TemplateEngine.generator(self.output_directory, "docker-compose-zookeeper-kafka.yaml", args)

        log.done('generator fabric zookeeper-kafka file')
        return result

    def gen_fabric_template(self, orderers, peers, zookeeper, kafka):
        log.line('start generator fabric template file')

        orderers, peers, kafka, zookeeper = self.__default_args(orderers, peers, kafka, zookeeper)
        log.debug('default orderers: %s' % orderers)
        log.debug('default peers: %s' % peers)
        log.debug('default kafka: %s' % kafka)
        log.debug('default zookeeper: %s' % zookeeper)

        args = dict(zookeeper=zookeeper, kafka=kafka, orderers=orderers, peers=peers)
        result = TemplateEngine.generator(self.output_directory, "docker-compose-fabric-template.yaml", args)

        log.done('generator fabric template file')
        return result

    def gen_couchdb(self, orderers, peers, zookeeper, kafka):
        log.line('start generator couch db file')

        orderers, peers, kafka, zookeeper = self.__default_args(orderers, peers, kafka, zookeeper)
        log.debug('default orderers: %s' % orderers)
        log.debug('default peers: %s' % peers)
        log.debug('default kafka: %s' % kafka)
        log.debug('default zookeeper: %s' % zookeeper)

        args = dict(zookeeper=zookeeper, kafka=kafka, orderers=orderers, peers=peers)
        result = TemplateEngine.generator(self.output_directory, "docker-compose-couch.yaml", args)

        log.done('generator couch db file')
        return result

    def gen_monitor(self, orderers, peers, zookeeper, kafka):
        log.line('start generator monitor file')

        orderers, peers, kafka, zookeeper = self.__default_args(orderers, peers, kafka, zookeeper)
        log.debug('default orderers: %s' % orderers)
        log.debug('default peers: %s' % peers)
        log.debug('default kafka: %s' % kafka)
        log.debug('default zookeeper: %s' % zookeeper)

        args = dict(zookeeper=zookeeper, kafka=kafka, orderers=orderers, peers=peers)
        result = TemplateEngine.generator(self.output_directory, "docker-compose-fabric-monitor.yaml", args)

        log.done('generator monitor file')
        return result

    def gen_properties(self, orderers, peers):
        log.line('start generator properties file')

        orderers, peers, *_ = self.__default_args(orderers, peers)
        log.debug('default orderers: %s' % orderers)
        log.debug('default peers: %s' % peers)

        args = dict(orderers=orderers, peers=peers)
        result = TemplateEngine.generator(self.output_directory, "properties/fabric-chaincode.produce.properties", args)
        result = TemplateEngine.generator(self.output_directory, "properties/fabric-chaincode.produce-safe.properties", args)

        log.done('generator properties file')
        return result

