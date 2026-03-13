from eth_account import Account
priv = "0xc60fae2827e4f0101bf5930fb099036e039afb590c213bb910412a5e26e075e5"
acc = Account.from_key(priv)
print(f"Address: {acc.address}")
