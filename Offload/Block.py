#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/30 15:13
# @Author  : archer_oneee
# @File    : Block.py
# @Software: PyCharm
import BlockHead
import SignVerfiy
import utils


class Block:

    prevHash = utils.my_sha256('0')
    height = 0
    blockHash = utils.my_sha256('0')
    head = None
    body = []
    size = 0
    commiteeAddr = ['0x430910932cEC29f3F3695eFc61A2fc9e5aFDDB2b',
                    '0x82971f37E5BCB03cF13fd735658236420e7796D2',
                    '0x6261A516C70fFF814344Bd4e8445B88A49bbcc4d',
                    '0x1721db279341d960B90631389b54fB951f68DF82',
                    '0xE4d8408d1448d86488D85738B118d1972d8cb867']

    def mine(self, preBlock, info, memSigs):
        count = 0
        agreeAddr = []
        for memSig in memSigs:
            addr = SignVerfiy.sig_verify(info, memSig)
            agreeAddr.append(addr)
        agreeAddr = list(set(agreeAddr))
        headL = []
        for addr in agreeAddr:
            if addr in self.commiteeAddr:
                headL.append(addr)
        if len(headL) < 3:
            return False
        self.body.append(info)
        self.height += preBlock.height + 1
        self.prevHash = preBlock.blockHash
        self.head = BlockHead.block_head(self.size + 225, headL)
        self.getBlkHash()
        return True

    def getSize(self):
        count = 0
        count += len(self.prevHash)
        count += len(str(self.height))
        count += 64
        count += len(''.join(self.body))
        self.size = count

    def getBlkHash(self):
        string = ''

        string += self.prevHash
        string += str(self.height).ljust(8,'0')
        string += str(self.size).ljust(8,'0')
        string += ''.join(self.body)
        self.blockHash = utils.my_sha256(string)



