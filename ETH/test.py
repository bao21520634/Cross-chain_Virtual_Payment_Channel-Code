import json
import time

import eth_keys
import numpy as np
from eth_account.messages import encode_defunct
from eth_utils import decode_hex
from web3 import Web3


def getPublicKey(val):
  msg='abc'
  message=encode_defunct(text=msg)
  sign_message=web3.eth.account.sign_message(message,private_key=val)
  k=web3.eth.account.recover_message(message,signature=sign_message.signature)
  return k
def to_32byte_hex(val):
        return web3.to_hex(web3.to_bytes(val).rjust(32,b'\0'))

# 连接.sol文件
with open('helloworld_sol_Greeter.abi', 'r') as f:
    abi = json.load(f)
with open('helloworld_sol_Greeter.bin', 'r') as f:
    code = f.read()

with open('committee1_sol_committee.abi', 'r') as f:
    abi_2 = json.load(f)
with open('committee1_sol_committee.bin', 'r') as f:
    code_2 = f.read()


# 测试连接ganache
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
print(web3.is_connected())

# 获取一下Ingrid，3用户的公钥
Ingrid = web3.eth.accounts[5]
Ingrid_privateKey = eth_keys.keys.PrivateKey(decode_hex('f9d6e6759e244ee6041dfcbfefd6a6c88cd3ab3feca396fef1e6a5fef17e79f8'))
Ingrid_publicKey = getPublicKey(Ingrid_privateKey)
print('Ingrid_publicKey******:',Ingrid_publicKey)
Bob = web3.eth.accounts[6]
Bob_privateKey = eth_keys.keys.PrivateKey(decode_hex('086ef77b5fea1611e70a3d7c82fbd836ad0c109fbf3f61653c1f0f4ea68a1db3'))
Bob_publicKey = getPublicKey(Bob_privateKey)



# Deploy smart contracts that build virtual channels
def Deployment_channel_contract():
  global Channels
  Greeter = web3.eth.contract(bytecode=code,abi=abi)
  option = {"from": Ingrid, "gas": 3000000}
  tx_hash = Greeter.constructor().transact(option)
  tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
  contract_address = web3.to_checksum_address(tx_receipt.contractAddress)
  print("channel_contract_address:", contract_address)
  # Then use Channels to call smart contract functions
  Channels = web3.eth.contract(contract_address,abi=abi)

Voter_1 = web3.eth.accounts[7]
Voter_2 = web3.eth.accounts[8]
Voter_3 = web3.eth.accounts[9]
# Deploy committee smart contract 
def Deployment_committee_contract():
  committee = web3.eth.contract(bytecode=code_2, abi=abi_2)
  option_2 = {"from": Voter_1, "gas": 3000000}
  tx_hash_2 = committee.constructor().transact(option_2)
  tx_receipt_2 = web3.eth.wait_for_transaction_receipt(tx_hash_2)
  committee_contract_address = web3.to_checksum_address(tx_receipt_2.contractAddress)
  print("committee_contract_address:", committee_contract_address)

count=0
message=[] # information array
message_Ingrid=[]
sign_message_Ingrid=[]
ec_Ingrid_hash=[]
ec_Ingrid_v=[]
ec_Ingrid_r=[]
ec_Ingrid_s=[]
message_b=[]
sign_message_b=[]
ec_b_hash=[]
ec_b_v=[]
ec_b_r=[]
ec_b_s=[]
total_amount=0#The total amount of money transferred
total_amount_all=[]#The amount of money transferred each time


# Create payment channel
def deploy_lc(Ingrid,Bob,value):
  # Both parties transfer money to the smart contract, and value is the amount.
  tx_hash = Channels.functions.pay().transact({"from":Ingrid,"value":value})
  tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
  tx_hash2 = Channels.functions.pay().transact({"from":Bob,"value":value})
  tx_receipt2 = web3.eth.wait_for_transaction_receipt(tx_hash2)
  # save public key
  tx_hash3 = Channels.functions.saveAccount_publickey(Ingrid_publicKey,Bob_publicKey).transact({"from":Ingrid,"value":value})
  tx_receipt3 = web3.eth.wait_for_transaction_receipt(tx_hash3)
  # save address
  tx_hash4 = Channels.functions.saveAccount(Ingrid,Bob).transact({"from":Ingrid,"value":value})
  tx_receipt4 = web3.eth.wait_for_transaction_receipt(tx_hash4) 
  # Calculate costs
  costs = tx_receipt.gasUsed + tx_receipt2.gasUsed
  # costs=tx_receipt.gasUsed+tx_receipt2.gasUsed+tx_receipt3.gasUsed+tx_receipt4.gasUsed
  print( "lc deploy cost: ",costs)

# Update payment channel
def update_lc(value=0):
  global count
  count = count + 1
  message.append('Number:count'+str(count)+'Ingrid.balance:'+ str(~value)+'Bob.balance:'+str(value))
  message_Ingrid.append(encode_defunct(text=message[count-1]))
  sign_message_Ingrid.append(web3.eth.account.sign_message(message_Ingrid[count-1], private_key = Ingrid_privateKey))
  ec_recover_args_a = (msghash,v,r,s)=(web3.to_hex(sign_message_Ingrid[count-1].messageHash),sign_message_Ingrid[count-1].v,
            to_32byte_hex(sign_message_Ingrid[count-1].r),to_32byte_hex(sign_message_Ingrid[count-1].s))
  ec_Ingrid_hash.append(ec_recover_args_a[0])
  ec_Ingrid_v.append(ec_recover_args_a[1])
  ec_Ingrid_r.append(ec_recover_args_a[2])
  ec_Ingrid_s.append(ec_recover_args_a[3])
  message_b.append(encode_defunct(text=message[count-1]))
  sign_message_b.append(web3.eth.account.sign_message(message_b[count-1],private_key=Bob_privateKey))
  ec_recover_args_b=(msghash,v,r,s)=(web3.to_hex(sign_message_b[count-1].messageHash),sign_message_b[count-1].v,
            to_32byte_hex(sign_message_b[count-1].r),to_32byte_hex(sign_message_b[count-1].s))
  ec_b_hash.append(ec_recover_args_b[0])
  ec_b_v.append(ec_recover_args_b[1])
  ec_b_r.append(ec_recover_args_b[2])
  ec_b_s.append(ec_recover_args_b[3])

# Closing payment channels (optimistic case)
def close_lc(value):
  load_count_a = 1
  tx_hash = Channels.functions.submit_transaction_a(load_count_a,value,value,ec_b_hash[load_count_a-1],ec_b_v[load_count_a-1],
            ec_b_r[load_count_a-1],ec_b_s[load_count_a-1], 30).transact({"from":Ingrid,"value":0})
  tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
  load_count_b=1
  tx_hash2 = Channels.functions.submit_transaction_b(load_count_b,value,value,ec_Ingrid_hash[load_count_b-1],ec_Ingrid_v[load_count_b-1],
            ec_Ingrid_r[load_count_b-1],ec_Ingrid_s[load_count_b-1],Ingrid,Bob).transact({"from":Bob,"value":0})
  tx_receipt2 = web3.eth.wait_for_transaction_receipt(tx_hash2)
  print("lc optimistic closed cost : ",tx_receipt.gasUsed + tx_receipt2.gasUsed)

# Closing the payment channel (pessimistic case)
def close_lc_pessimistic(value):
  load_count_a = 1
  load_count_b = 1
  cvc_count_b = 2
  tx_hash = Channels.functions.submit_transaction_a(load_count_a,value,value,ec_b_hash[load_count_a-1],ec_b_v[load_count_a-1],
            ec_b_r[load_count_a-1],ec_b_s[load_count_a-1],30).transact({"from":Ingrid,"value":0})
  tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
  tx_hash1 = Channels.functions.check_cvc_Validity(ec_a_hash_cvc[cvc_count_b-1],ec_a_v_cvc[cvc_count_b-1],
            ec_a_r_cvc[cvc_count_b-1],ec_a_s_cvc[cvc_count_b-1]).transact({"from":Ingrid,"value":0})
  tx_receipt1 = web3.eth.wait_for_transaction_receipt(tx_hash1)
  tx_hash2 = Channels.functions.submit_transaction_b(load_count_b,value,value,ec_Ingrid_hash[load_count_b-1],
            ec_Ingrid_v[load_count_b-1],ec_Ingrid_r[load_count_b-1],ec_Ingrid_s[load_count_b-1],Ingrid,Bob).transact({"from":Bob,"value":0})
  tx_receipt2=web3.eth.wait_for_transaction_receipt(tx_hash2)
  print("lc pessimistic closed cost : ",tx_receipt.gasUsed+tx_receipt1.gasUsed+tx_receipt2.gasUsed)

def get_balance(account):
  print(1)
  tx_hash=Channels.functions.getBalance1(account).call()
  tx_receipt=web3.eth.wait_for_transaction_receipt(tx_hash)
  print(tx_receipt)

message_cvc = []
cvc_Ingrid_balance = 0
cvc_Bob_balance = 0
cvc_count = 0   # Indicates the array index of message_vc[]
cvc_OpenMessage_Ingrid = []
sign_cvc_OpenMessage_Ingrid = [] # Save the information signed by ingrid
message_b_cvc = []
sign_cvc_OpenMessage_Bob = []
ec_a_hash_cvc = []
ec_a_v_cvc = []
ec_a_r_cvc = []
ec_a_s_cvc = []
ec_b_hash_cvc = []
ec_b_v_cvc = []
ec_b_r_cvc = []
ec_b_s_cvc = []

# Open a cross-chain virtual channel
def deploy_cvc(Ingrid,Bob,value,time_cvc):
  # The amount locked by both parties
  global cvc_Ingrid_balance
  global cvc_Bob_balance
  global cvc_count
  cvc_Ingrid_balance=value
  cvc_Bob_balance=value
  # Creation information of cross-chain virtual channel
  message_cvc.append("open a virtual channel with initial balance Ingrid"+str(cvc_Ingrid_balance)+"Bob"+str(cvc_Bob_balance))
  cvc_OpenMessage_Ingrid.append(encode_defunct(text=message_cvc[cvc_count]))
  # Signature lock information
  start = time.time()
  a = web3.eth.account.sign_message(cvc_OpenMessage_Ingrid[cvc_count],private_key=Ingrid_privateKey)
  print("a",a)
  end = time.time()
  Times.append(end-start)
  print("sign_time", end-start)
  sign_cvc_OpenMessage_Ingrid.append(a)

  start = time.time()
  b = web3.eth.account.recover_message(cvc_OpenMessage_Ingrid[cvc_count], signature ='0xbcfc8fa75b64043b9cb74bc310e7fc7f0dfd5844f29c9a3674623a1c6a866a07439b487e72d451f8706ac94018499f5f536a4730753f0f68fad600ddb47cd4431c')
  end = time.time()
  print("验证时间：****", end-start)
  print('Ingrid_publicKey******:',Ingrid_publicKey)
  print("地址：*******", b)


  # Calculate the size of open cross-chain virtual channel messages (Ingrid)
  CVC_Open_Message_Signed_by_Ingrid_bytes = len(web3.to_hex(sign_cvc_OpenMessage_Ingrid[cvc_count].signature))/2
  print("CVC_Open_Message_Signed_by_Ingrid_hex",web3.to_hex(sign_cvc_OpenMessage_Ingrid[cvc_count].signature))
  print("CVC_Open_Message_Signed_by_Ingrid_bytes:",CVC_Open_Message_Signed_by_Ingrid_bytes)
  
  # Take out the hash, v, r, s in the signature information (mainly passed to the smart contract for signature verification to facilitate smart contract signature verification)
  ec_recover_args_a_cvc=(msghash,v,r,s)=(web3.to_hex(sign_cvc_OpenMessage_Ingrid[cvc_count].messageHash),sign_cvc_OpenMessage_Ingrid[cvc_count].v,
            to_32byte_hex(sign_cvc_OpenMessage_Ingrid[cvc_count].r),to_32byte_hex(sign_cvc_OpenMessage_Ingrid[cvc_count].s))
  ec_a_hash_cvc.append(ec_recover_args_a_cvc[0])
  ec_a_v_cvc.append(ec_recover_args_a_cvc[1]) 
  ec_a_r_cvc.append(ec_recover_args_a_cvc[2])
  ec_a_s_cvc.append(ec_recover_args_a_cvc[3])

  message_b_cvc.append(encode_defunct(text=message_cvc[cvc_count]))
  sign_cvc_OpenMessage_Bob.append(web3.eth.account.sign_message(message_b_cvc[cvc_count],private_key=Bob_privateKey))
  
  # Calculate the size of open cross-chain virtual channel messages (Ingrid)
  CVC_Open_Message_Signed_by_Bob_bytes = len(web3.to_hex(sign_cvc_OpenMessage_Bob[cvc_count].signature))/2
  print("CVC_Open_Message_Signed_by_Bob_hex",web3.to_hex(sign_cvc_OpenMessage_Bob[cvc_count].signature))
  print("CVC_Open_Message_Signed_by_Bob_bytes:",CVC_Open_Message_Signed_by_Bob_bytes)

  # Take out the hash, v, r, s in the signature information (mainly passed to the smart contract for signature verification to facilitate smart contract signature verification)
  ec_recover_args_b_cvc=(msghash,v,r,s)=(web3.to_hex(sign_cvc_OpenMessage_Bob[cvc_count].messageHash),sign_cvc_OpenMessage_Bob[cvc_count].v,
            to_32byte_hex(sign_cvc_OpenMessage_Bob[cvc_count].r),to_32byte_hex(sign_cvc_OpenMessage_Bob[cvc_count].s))
  ec_b_hash_cvc.append(ec_recover_args_b_cvc[0])
  ec_b_v_cvc.append(ec_recover_args_b_cvc[1])
  ec_b_r_cvc.append(ec_recover_args_b_cvc[2])
  ec_b_s_cvc.append(ec_recover_args_b_cvc[3])
  # Send signature to smart contract
  # tx_hash=Channels.functions.open_cvc(ec_a_hash_cvc[0],ec_a_v_cvc[0],ec_a_r_cvc[0],ec_a_s_cvc[0],time_cvc,ec_b_hash_cvc[0],
  #           ec_b_v_cvc[0],ec_b_r_cvc[0],ec_b_s_cvc[0]).transact({"from":Ingrid,"value":value})
  # tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
  print("cvc open...")


# Update virtual channel
def update_cvc(value):
  global cvc_count
  cvc_count=cvc_count+1
  message_cvc.append('Number:count'+str(cvc_count)+'accounta.balance:'+str(~value)+'accountb.balance:'+str(value))
  cvc_OpenMessage_Ingrid.append(encode_defunct(text=message_cvc[cvc_count]))
  sign_cvc_OpenMessage_Ingrid.append(web3.eth.account.sign_message(cvc_OpenMessage_Ingrid[cvc_count],private_key=Ingrid_privateKey))
  ec_recover_args_a_cvc=(msghash,v,r,s)=(web3.to_hex(sign_cvc_OpenMessage_Ingrid[cvc_count].messageHash),sign_cvc_OpenMessage_Ingrid[cvc_count].v,
            to_32byte_hex(sign_cvc_OpenMessage_Ingrid[cvc_count].r),to_32byte_hex(sign_cvc_OpenMessage_Ingrid[cvc_count].s))
  ec_a_hash_cvc.append(ec_recover_args_a_cvc[0])
  ec_a_v_cvc.append(ec_recover_args_a_cvc[1])
  ec_a_r_cvc.append(ec_recover_args_a_cvc[2])
  ec_a_s_cvc.append(ec_recover_args_a_cvc[3])
  message_b_cvc.append(encode_defunct(text=message_cvc[cvc_count]))
  sign_cvc_OpenMessage_Bob.append(web3.eth.account.sign_message(message_b_cvc[cvc_count],private_key=Bob_privateKey))
  ec_recover_args_b_cvc=(msghash,v,r,s)=(web3.to_hex(sign_cvc_OpenMessage_Bob[cvc_count].messageHash),sign_cvc_OpenMessage_Bob[cvc_count].v,
            to_32byte_hex(sign_cvc_OpenMessage_Bob[cvc_count].r),to_32byte_hex(sign_cvc_OpenMessage_Bob[cvc_count].s))
  ec_b_hash_cvc.append(ec_recover_args_b_cvc[0])
  ec_b_v_cvc.append(ec_recover_args_b_cvc[1])
  ec_b_r_cvc.append(ec_recover_args_b_cvc[2])
  ec_b_s_cvc.append(ec_recover_args_b_cvc[3])
  print("cvc update...")

# Normally close the virtual channel
def close_cvc(value):
  cvc_count_a=2
  cvc_count_b=2
  # tx_hash = Channels.functions.submit_close_cvc(value,value,ec_a_hash_cvc[cvc_count_b-1],ec_a_v_cvc[cvc_count_b-1],ec_a_r_cvc[cvc_count_b-1],
  #           ec_a_s_cvc[cvc_count_b-1],ec_b_hash_cvc[cvc_count_a-1],ec_b_v_cvc[cvc_count_a-1],ec_b_r_cvc[cvc_count_a-1],
  #           ec_b_s_cvc[cvc_count_a-1]).transact({"from":Ingrid,"value":0})
  # tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
  print("cvc close...")

# Closing the cross-chain virtual channel under abnormal circumstances (first case)
def close_cvc_abnormal(committeeAddress,transactionId,Ingrid_and_Bob_Balance, zero, value):
  cvc_count_a=2
  # ingrid提交OCb 和 CCi
  tx_hash=Channels.functions.close_cvc_abnormal(ec_b_hash_cvc[0],ec_b_v_cvc[0],ec_b_r_cvc[0],ec_b_s_cvc[0],ec_a_hash_cvc[cvc_count_a-1],
            ec_a_v_cvc[cvc_count_a-1],ec_a_r_cvc[cvc_count_a-1],ec_a_s_cvc[cvc_count_a-1]).transact({"from":Ingrid,"value":0})
  tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash) # view 0 gas
  # Launch committee vote
  print("voting.........")
  committee(1,3000000000000000000)
  # Allocate balances based on voting results
  tx_hash1 = Channels.functions.close_cvc_abnormal_1(committeeAddress,transactionId,Ingrid_and_Bob_Balance,zero).transact({"from":Ingrid,"value":value})
  tx_receipt1 = web3.eth.wait_for_transaction_receipt(tx_hash1)
  print("close_cvc_abnomal cost : ", tx_receipt.gasUsed+tx_receipt1.gasUsed)
  
  
# def close_cvc_abnormal_and_exchange_coins(Ingrid_and_Bob_Balance, zero, value):

# Take a committee vote
def committee(transactionId,value):
  # Create voting event
  tx_hash1=commit.functions.createVote(transactionId,value).transact({"from":Voter_1,"value":0})
  tx_receipt1=web3.eth.wait_for_transaction_receipt(tx_hash1)
  # Members pay deposit
  tx_hash2=commit.functions.pay().transact({"from":Voter_1,"value":value})
  tx_hash3=commit.functions.pay().transact({"from":Voter_2,"value":value})
  tx_hash4=commit.functions.pay().transact({"from":Voter_3,"value":value})
  tx_receipt2=web3.eth.wait_for_transaction_receipt(tx_hash2)
  tx_receipt3=web3.eth.wait_for_transaction_receipt(tx_hash3)
  tx_receipt4=web3.eth.wait_for_transaction_receipt(tx_hash4)
  # Take a vote
  tx_hash5=commit.functions.vote(Voter_1,1,transactionId).transact({"from":Voter_1,"value":0})
  tx_hash6=commit.functions.vote(Voter_2,1,transactionId).transact({"from":Voter_1,"value":0})
  tx_hash7=commit.functions.vote(Voter_3,1,transactionId).transact({"from":Voter_1,"value":0})
  tx_receipt5=web3.eth.wait_for_transaction_receipt(tx_hash5)
  tx_receipt6=web3.eth.wait_for_transaction_receipt(tx_hash6)
  tx_receipt7=web3.eth.wait_for_transaction_receipt(tx_hash7)
  # Get voting results
  tx_hash8=commit.functions.getVoteRes(transactionId).transact({"from":Voter_1,"value":0})
  tx_receipt8=web3.eth.wait_for_transaction_receipt(tx_hash8)
  res=commit.functions.getTrue(transactionId).call()
  print("voting_result:", res)
  # punish
  # tx_hash9=commit.functions.punishment(transactionId).transact({"from":Voter_1,"value":0})
  # tx_receipt9=web3.eth.wait_for_transaction_receipt(tx_hash9)
  print("commitee cost : ",tx_receipt1.gasUsed+tx_receipt2.gasUsed+tx_receipt3.gasUsed+tx_receipt4.gasUsed+tx_receipt5.gasUsed+
            tx_receipt6.gasUsed+tx_receipt7.gasUsed+tx_receipt8.gasUsed)
  return res

# Choose a middleman
def chooseIntermediary(account):
  tx_hash=commit.functions.chooseIntermediary(account).transact({"from":Voter_1,"value":0})
  tx_receipt=web3.eth.wait_for_transaction_receipt(tx_hash)
  print("chooseIntermediary cost :",tx_receipt)

# Get a person's f-value
def getF(account):
  tx_hash=commit.functions.getF(account).transact({"from":Voter_1,"value":0})
  tx_receipt=web3.eth.wait_for_transaction_receipt(tx_hash)
  m=commit.functions.getf(account).call()
  print(m)
  print("getf cost :",tx_receipt)

# Get everyone's f-value
def getAllF():
  for i in range (0,9):
      account=web3.eth.accounts[i]
      Channels.functions.getF(account).transact({"from":Voter_1,"value":0})
      t=Channels.functions.getf(account).call()
      print(t)

Times = []
# First deploy the committee contract, obtain the address of the committee contract, and then proceed to the following steps:
Deployment_committee_contract()
for i in range (1):
  committee_contract_address = "0x474214148d6e2089288e41e8fEDEEd8467a51013"
  commit = web3.eth.contract(committee_contract_address, abi=abi_2)
  Deployment_channel_contract()
  deploy_lc(Ingrid,Bob,0)   # Build a ledger channel
  update_lc(0)    # Update ledger channel
  deploy_cvc(Ingrid, Bob, 0, 0)    # Build a cross-chain virtual channel
  update_cvc(0)   # Update cross-chain virtual channel
  close_cvc(0)    # Close the cross-chain virtual channel normally
  close_cvc_abnormal(committee_contract_address,1,0,0,0)   # Abnormal closure of cross-chain virtual channel
  close_lc(0)   # Close the ledger channel normally
  close_lc_pessimistic(0)   # Abnormally closing the ledger channel

Times = np.array(Times) 
print(Times.mean())

















