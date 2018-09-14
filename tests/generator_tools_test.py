#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2018-09-12
# @copyright by hoojo @2018
# @changelog generator fabric network config tools core TestCase


# ===============================================================================
# 标题：generator fabric network config tools core TestCase
# ===============================================================================
# 描述：生成 fabric 网络配置 TestCase
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 构建 fabric 网络配置生成工具 TestCase
# -------------------------------------------------------------------------------
import unittest
from generator.generator_tools import OrdererOrg
from generator.generator_tools import PeerOrg
from generator.generator_tools import GenFabricNetworkTools


class TestGenFabricNetworkTools(unittest.TestCase):
    orderers = None
    peers = None

    def setUp(self):
        print('init by setUp...')

        orderer = OrdererOrg(hostnames=['foo', 'bar'], count=5)
        orderer2 = OrdererOrg("Orderer2", domain="hoojo.top")
        orderer3 = OrdererOrg("Orderer3", domain="hoojo.xyz")

        self.orderers = [orderer, orderer2, orderer3]

        peer = PeerOrg(domain='simple.com')
        peer2 = PeerOrg("Org2", hostnames=['foo', 'bar'], user_count=3, template_count=4)
        peer3 = PeerOrg("Org3", domain='example.com')

        self.peers = [peer, peer2, peer3]

    def tearDown(self):
        print('end by tearDown...')

    def test_gen_crypot_config(self):
        GenFabricNetworkTools().gen_crypot_config(self.orderers, self.peers)

    def test_gen_configtx(self):
        GenFabricNetworkTools().gen_configtx(self.orderers, self.peers)

    def test_gen_generate_shell(self):
        GenFabricNetworkTools().gen_generate_shell(self.peers)


if __name__ == '__main__':

    # 执行所有用例测试
    # unittest.main()

    # 装载测试用例
    test_cases = unittest.TestLoader().loadTestsFromTestCase(TestGenFabricNetworkTools)

    # 使用测试套件并打包测试用例
    test_suit = unittest.TestSuite()
    test_suit.addTests(test_cases)

    # 运行测试套件，并返回测试结果
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suit)

    # 生成测试报告
    print("testsRun: %s" % test_result.testsRun)
    print("failures: %s" % len(test_result.failures))
    print("errors: %s" % len(test_result.errors))
    print("skipped: %s" % len(test_result.skipped))
