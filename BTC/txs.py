from typing import Tuple

from bitcoinutils.transactions import Transaction, TxOutput, TxInput
from bitcoinutils.script import Script
from identity import Id
import init
import scripts
import consts
from helper import hash256

init.initNetwork()

# The TXf of the ledger channel is the input of users Alice and Ingrid, and the output requires the signatures of both Alice and Ingrid (on-chain)
def get_TX_multisig(tx_in0: TxInput, tx_in1: TxInput, id_1: Id, id_2: Id, c: int, fee: int, timedelay: int = 0x02) -> Transaction:
    
    tx_out = TxOutput(c , scripts.get_script_2sig(id_1, id_2))  # (Sent currency value, receiver’s public key script)

    tx = Transaction([tx_in0, tx_in1], [tx_out])  # Package transaction ([input 1, input 2], output)

    sig_1 = id_1.sk.sign_input(tx, 0, id_1.p2pkh)  # signature of a
    sig_2 = id_2.sk.sign_input(tx, 1, id_2.p2pkh)  # signature of a

    tx_in0.script_sig = Script([sig_1, id_1.pk.to_hex()])  
    tx_in1.script_sig = Script([sig_2, id_2.pk.to_hex()])  
    return tx
#####################


def get_TXc(tx_in: TxInput, id_1: Id, id_2: Id, c: float, fee: float, timedelay: int = 0x02) \
        -> Transaction:
    tx_out = TxOutput(c, scripts.get_script_ln_ct(id_1, id_2))

    tx = Transaction([tx_in], [tx_out])

    script_in = scripts.get_script_2sig(id_1, id_2)

    sig_a = id_1.sk.sign_input(tx, 0, script_in)
    sig_i = id_2.sk.sign_input(tx, 0, script_in)

    tx_in.script_sig = Script([sig_a, sig_i])
    return tx


#############################

def get_TXs(tx_in: TxInput, id_1: Id, id_2: Id, c: float, fee: float, timedelay: int = 0x02) \
        -> Transaction:
    
    tx_out = TxOutput(c , scripts.get_script_TXs(id_1, id_2))

    tx = Transaction([tx_in], [tx_out])

    script_in = scripts.get_script_2sig(id_1, id_2)
    
    sig_a = id_1.sk.sign_input(tx, 0, script_in)
    sig_i = id_2.sk.sign_input(tx, 0, script_in)
    
    tx_in.script_sig = Script([sig_a, sig_i])
    return tx
#############################

def get_TXf_V(tx_in: TxInput, id_1: Id, id_2: Id, id_3: Id, c: float, fee: float,
               timedelay: int = 0x02) \
        -> Transaction:
    tx_out = TxOutput(c, Script([
        id_1.pk.to_hex(), 'OP_CHECKSIGVERIFY', id_3.pk.to_hex(), 'OP_CHECKSIGVERIFY', 0x1]))

    tx = Transaction([tx_in], [tx_out])

    script_in = scripts.scripts.get_script_2sig(id_1, id_2)

    sig_Alice = id_1.sk.sign_input(tx, 0, script_in)
    sig_Ingrid = id_2.sk.sign_input(tx, 0, script_in)

    tx_in.script_sig = Script([sig_Alice, sig_Ingrid])

    return tx
#################################

# def get_return(tx_in: TxInput, id_1 : Id, id_2 : Id, c : int, fee : int)\
#         -> Transaction:
#     tx_out = 'moUDVi9sE5J14w7a9tAMeY4zanp2ghzgXB'

