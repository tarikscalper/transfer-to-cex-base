import time
import random
from web3 import Web3
from eth_account import Account

# ==== НАЛАШТУВАННЯ ====
BASE_RPC = 'https://mainnet.base.org'  # офіційний RPC
TOKEN_ADDRESS = Web3.to_checksum_address('0x1111111111166b7FE7bd91427724B487980aFc69')
MAX_GAS_FEE_USD = 0.10  # максимум $0.10
ETH_USD = 3000  # тут постав реальну ціну ETH вручну, або пізніше можна буде автоматизувати
TOKEN_ABI = [{
    "constant": True,
    "inputs": [{"name": "_owner", "type": "address"}],
    "name": "balanceOf",
    "outputs": [{"name": "balance", "type": "uint256"}],
    "type": "function"
}, {
    "constant": False,
    "inputs": [
        {"name": "_to", "type": "address"},
        {"name": "_value", "type": "uint256"}
    ],
    "name": "transfer",
    "outputs": [{"name": "success", "type": "bool"}],
    "type": "function"
}]

w3 = Web3(Web3.HTTPProvider(BASE_RPC))
token = w3.eth.contract(address=TOKEN_ADDRESS, abi=TOKEN_ABI)

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
    address = account.address
    print(f"\n➡️ Обробка {address} → {exchange_address}")

    balance = token.functions.balanceOf(address).call()
    if balance == 0:
        print("   ⚠️ Немає токенів")
        continue

    nonce = w3.eth.get_transaction_count(address)
    gas_price = w3.eth.gas_price
    gas_limit = 100_000

    gas_fee_eth = gas_price * gas_limit / 10**18
    gas_fee_usd = gas_fee_eth * ETH_USD

    if gas_fee_usd > MAX_GAS_FEE_USD:
        print(f"   ❌ Комісія занадто висока: ${gas_fee_usd:.4f}")
        continue

    tx = token.functions.transfer(Web3.to_checksum_address(exchange_address), balance).build_transaction({
        'from': address,
        'nonce': nonce,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': 8453  # Base mainnet
    })

    signed_tx = w3.eth.account.sign_transaction(tx, pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"   ✅ Відправлено {balance} токенів. Тx: {w3.to_hex(tx_hash)}")

    sleep_time = random.randint(10, 30)
    print(f"   🕒 Очікування {sleep_time} сек...")
    time.sleep(sleep_time)

print("\n✅ Готово!")