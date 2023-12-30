# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import Mine
import utils
from Block import Block
from Node import Node

BitcoinTx = 'efd0b51a9c4e5f3449f4eeacb195bf48659fbc00d2f4001bf4c088ba0779fb33'

AliceSk = '0x32ed923b0eda25c79b177402d2236e4aedf2779cdfe87aa657baba4db9e7466c'
BobSk = '0x2232ee3cd5960d63387795bf2cfa12289860c2649250a70fc915bfe2991ee155'
IngridSk = '0xb9a2a8af08449b0671b11713d630f99c6bf226a29574c410a19729fb36e353e4'

skList = ['0x04b9a0b158321d75067a4e9709d9f056df17bc1a29ea40344feffcb5fd1afe19',
      '0xace2550ec3ce23fcc239c89c653b9783bfc3fab2c347b4c8433f3fbb6c3b5b62',
      '0x076f7850d0a323cbdf451342c25350e415b6de532b0b082ee9d6edb6e3e82d02',
      '0x266a08d0bbd3490f5edd8dcc97fdd14e81e32043f91ec0749a344783dbe92329',
      '0x65be0793567bd20e8cfb428782948c303a4bbf601eb6cadf8ea0c8c40542dbf4']

nodeList = []
for sk in skList:
      node = Node(sk)
      nodeList.append(node)

genesis_block = Block()
blockList = [genesis_block]

while True:
      Mine.mine(blockList, nodeList, BitcoinTx)
