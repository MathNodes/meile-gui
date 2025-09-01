price = 0.00052
MAX_SPEND = 25

qty = int(MAX_SPEND/price)

x = 1 / price
if x < 10:
    factor = 1
elif 10 < x < 100:
    factor = 10
elif 100 < x < 1000:
    factor = 100
elif 1000 < x < 10000:
    factor = 1000
else:
    factor = 10000

mod_qty = qty % factor

qty = qty - mod_qty

print(qty/8)
