from Miner import Miner
import time

miner = Miner(4)
cont = True
while cont:
    time1 = time.perf_counter()
    miner.mine_block("MIIBCgKCAQEAn6w660T90g+Oty4PFTvy20rUuQ0BY8OkyfSjhcRJLcd+0Elm1zaePpK0Swk7z/mcdqEAfFmlVJB1WDMbK4i6W6dwvLXLguXokRWHS+n+zxPPwj15zaszuIi/eKfWf8pVHRu8y0yyKr1JP8qezxbP7hecKOsttPm6G5aWZyJemonYAmfdcvc5AVlgetUko/KAcqPLkYu8wp2w5mrM0zhiwiG8gGqwPUMgyPLfBuxjoa7PX3kbOch4xYemuMOfNKy6B2zZq9r5d0SCanc1kheOTCqmD/4wxzjc2JrrbsEhWu8QXfVW9fVtBr/Ld0xtIEhraB4yKozivpVlCPm5NbFMowIDAQAB")
    time2 = time.perf_counter()
    print("-"*50)
    print(f"Transactions in block: {len(miner.block)}")
    print(f"Time Elapsed: {time2-time1:.2f} Seconds")
    print(f"Nonce: {miner.num}")
    print("-"*50)
    miner.post_block()
    cont = False