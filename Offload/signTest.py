#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/28 19:15
# @Author  : archer_oneee
# @File    : signTest.py
# @Software: PyCharm
from web3 import Web3, EthereumTesterProvider
from eth_account.messages import encode_defunct
w3 = Web3(EthereumTesterProvider())
msg = "abcd"
private_key = 'f9d6e6759e244ee6041dfcbfefd6a6c88cd3ab3feca396fef1e6a5fef17e79f8'
private_key_list = ['f9d6e6759e244ee6041dfcbfefd6a6c88cd3ab3feca396fef1e6a5fef17e79f8', '086ef77b5fea1611e70a3d7c82fbd836ad0c109fbf3f61653c1f0f4ea68a1db3', '14f7e64d09d3aa07326c655f5867106d5a98271d300a569cf96d6b863efcc356', '3609186c7c96947c485f24dacc128d18143098e6f560b6dbcea8a500fa71a6b5', 'f4be75b6048a38f8c121d573cd7345dc889f9a31907ef012d5dee59753e40f3d', 'd3cb92f3112684cc2845b4845475deacfc3c969a4f68f9c46c4282b044d7c27a', '9421e80e9004eba3f2913914963925e0afac1fae807de2bfbf2a45f79efc9537']
message = encode_defunct(text=msg)
signed_message = w3.eth.account.sign_message(message, private_key)

print(signed_message)
print("r: ", '0x{:064x}'.format(signed_message['r']))
print("s: ", '0x{:064x}'.format(signed_message['s']))

message = encode_defunct(text="abcd")
result = w3.eth.account.recover_message(message, signature=signed_message.signature)
print(result)

for key in private_key_list:
    sm = w3.eth.account.sign_message(encode_defunct(text=msg), key)
    print(f"[{sm['v']}, \"{'0x{:064x}'.format(sm['r'])}\", \"{'0x{:064x}'.format(sm['s'])}\"]")