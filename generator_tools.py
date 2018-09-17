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
import sys
import getopt
import shutil
import yaml


class GeneratorTools(object):

    def __copy_network_files(self, output='networks'):
        if output is None or len(output) < 1:
            raise IOError('output dir is undefined.')

        log.line('copy networks file')
        log.info('copy network files to "%s"' % output)

        if os.path.exists(output):
            shutil.rmtree(output)
        else:
            # os.makedirs(output, exist_ok=True)
            pass

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

    def transform_model(self):
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

        log.debug('orderers: %s' % str(orderers))
        log.debug('peers: %s' % str(peers))
        log.debug('kafka: %s' % str(kafka))
        log.debug('zookeeper: %s' % str(zookeeper))

        log.done('transfor settings to model')
        return settings, orderers, peers, kafka, zookeeper

    def clean_output(self):
        settings, *_ = self.transform_model()

        output = settings['output']
        if output is None or len(output) < 1:
            raise IOError('output dir is undefined.')

        log.title('clean networks directory')
        log.info('clean networks directory: "%s"' % output)

        if not os.path.exists(output):
            log.info('[%s] networks directory is not exists' % output)
        else:
            shutil.rmtree(output)

        log.done('clean networks directory')

    def generator_networks(self, generator_queues=None):
        log.title('generator networks')

        settings, orderers, peers, kafka, zookeeper = self.transform_model()
        tools = GenFabricNetworkTools(settings['output'])

        if generator_queues is None:
            self.__copy_network_files(settings['output'])

        if generator_queues is None or 'crypto' in generator_queues:
            result = tools.gen_crypto_config(orderers, peers)
        if generator_queues is None or 'configtx' in generator_queues:
            result = tools.gen_configtx(orderers, peers, kafka, settings['orderer_type'])
        if generator_queues is None or 'shell' in generator_queues:
            result = tools.gen_generate_shell(peers)
        if generator_queues is None or 'fabric' in generator_queues:
            result = tools.gen_fabric_compose(orderers, peers, zookeeper, kafka)
        if generator_queues is None or 'zookeeper_kafka' in generator_queues:
            result = tools.gen_zookeeper_kafka(zookeeper, kafka)
        if generator_queues is None or 'template' in generator_queues:
            result = tools.gen_fabric_template(orderers, peers, zookeeper, kafka)
        if generator_queues is None or 'couchdb' in generator_queues:
            result = tools.gen_couchdb(orderers, peers, zookeeper, kafka)
        if generator_queues is None or 'monitor' in generator_queues:
            result = tools.gen_monitor(orderers, peers, zookeeper, kafka)
        if generator_queues is None or 'properties' in generator_queues:
            result = tools.gen_properties(orderers, peers)

        # print(result)
        log.done('generator networks')


def main(argv):
    log.debug('argv: %s' % argv)

    help_usage = '''
    USAGE: python generator_tools.py [OPTIONS] COMMANDS

    OPTIONS: 
      -h     use the help manual.
      -c     generator fabric network core config file, create configtx.yaml
      -x     generator fabric channel & block core config file, create crypto-config.yaml
      -f     generator fabric orderer/peer service, create docker-compose-fabric.yaml
      -z     generator fabric zookeeper/kafka service, create docker-compose-zookeeper-kafka.yaml
      -t     generator fabric ca service and fabric network config, create docker-compose-fabric-template.yaml
      -d     generator couchdb service, create docker-compose-couchdb.yaml
      -m     generator prom monitor service network, create docker-compose-fabric-monitor.yaml
      -p     generator connect fabric network properties config, create fabric-chaincode.*.properties
    
    COMMANDS:
      gen         generator fabric network config files
      regen       regenerator fabric network config files
      clean       clean fabric networks files
      help        use the help manual.
        
    EXAMPLES: 
      python generator_tools.py -h
      python generator_tools.py help
    
      python generator_tools.py gen
      python generator_tools.py clean
      
      python generator_tools.py -c gen
      python generator_tools.py -cx gen
      python generator_tools.py -cx clean gen
      
      python generator_tools.py -hcxsfztdmp gen
      python generator_tools.py -hcxsfztdmp clean gen
    '''

    # default generator all networks
    tools = GeneratorTools()
    if len(argv) < 1:
        tools.generator_networks()
        sys.exit()

    try:
        long_opts = ["help", "crypto", "configtx", "shell", "fabric", "zk", "template", "couchdb", "monitor", "properties"]
        opts, args = getopt.getopt(argv, "hcxsfztdmp", long_opts)
        log.debug('opts: %s, args: %s' % (opts, args))
    except getopt.GetoptError:
        print(help_usage)
        sys.exit(2)

    generator_queues = []
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help_usage)
            sys.exit()
        elif opt in ("-c", "--crypto"):
            generator_queues.append('crypto')
        elif opt in ("-x", "--configtx"):
            generator_queues.append('configtx')
        elif opt in ("-s", "--shell"):
            generator_queues.append('shell')
        elif opt in ("-f", "--fabric"):
            generator_queues.append('fabric')
        elif opt in ("-z", "--zk"):
            generator_queues.append('zookeeper_kafka')
        elif opt in ("-t", "--template"):
            generator_queues.append('template')
        elif opt in ("-d", "--couchdb"):
            generator_queues.append('couchdb')
        elif opt in ("-m", "--monitor"):
            generator_queues.append('monitor')
        elif opt in ("-p", "--properties"):
            generator_queues.append('properties')

    if len(generator_queues) == 0:
        generator_queues = None

    for arg in args:
        if arg == 'clean':
            tools.clean_output()
        elif arg == 'gen' or arg == 'generator':
            tools.generator_networks(generator_queues)
        elif arg == 'regen':
            tools.clean_output()
            tools.generator_networks(generator_queues)
        else:
            print(help_usage)
            sys.exit()

    if len(args) < 0:
        print(help_usage)
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
