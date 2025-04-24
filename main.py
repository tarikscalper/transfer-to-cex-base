import time
import random
from web3 import Web3
from eth_account import Account

# ==== НАЛАШТУВАННЯ ====
BASE_RPC = 'https://mainnet.base.org'
MAX_GAS_FEE_USD = 0.10
ETH_USD = 1700  # онови вручну або автоматизуй
GAS_LIMIT = 21_000

w3 = Web3(Web3.HTTPProvider(BASE_RPC))

# ==== ЗАГРУЗКА ГАМАНЦІВ ====
with open('wallets.txt', 'r') as f:
    private_keys = [line.strip() for line in f.readlines()]

with open('recipients.txt', 'r') as f:
    exchange_addresses = [line.strip() for line in f.readlines()]

if len(private_keys) != len(exchange_addresses):
    print("❌ Кількість гаманців і адрес не співпадає!")
    exit(1)

for pk, exchange_address in zip(private_keys, exchange_addresses):
    account = Account.from_key(pk)
    sender = account.address
    print(f"\n➡️ Обробка {sender} → {exchange_address}")

    balance = w3.eth.get_balance(sender)
    gas_price = w3.eth.gas_price
    gas_fee_eth = gas_price * GAS_LIMIT / 10**18
    gas_fee_usd = gas_fee_eth * ETH_USD

    if gas_fee_usd > MAX_GAS_FEE_USD:
        print(f"   ❌ Комісія занадто висока: ${gas_fee_usd:.4f}")
        continue

    buffer_eth = random.uniform(0.0001, 0.00024)
    buffer = int(buffer_eth * 10**18)
    estimated_fee = gas_price * GAS_LIMIT
    send_amount = balance - estimated_fee - buffer

    if send_amount <= 0:
        print("   ⚠️ Недостатньо коштів після врахування комісії та буфера")
        continue

    tx = {
        'to': Web3.to_checksum_address(exchange_address),
        'value': send_amount,
        'gas': GAS_LIMIT,
        'gasPrice': gas_price,
        'nonce': w3.eth.get_transaction_count(sender),
        'chainId': 8453  # Base mainnet
    }

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"   ✅ Відправлено {(send_amount / 10**18):.6f} ETH. Tx: {w3.to_hex(tx_hash)}")
    print(f"   🧮 Буфер залишку: {buffer_eth:.8f} ETH")

    sleep_time = random.randint(10, 30)
    print(f"   🕒 Очікування {sleep_time} сек...")
    time.sleep(sleep_time)

print("\n✅ Готово!")
