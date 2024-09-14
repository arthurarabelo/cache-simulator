# python simulador.py cachesize blocksize groupsize input
import sys
from collections import deque
import math

def build_cache(number_of_sets, groupsize):

    cache = []
    for i in range(number_of_sets):
        cache.append([])
        for j in range(groupsize):
            cache[i].append({"V": 0, "block_identifier": 0})

    return cache

def build_output(cache):
    output = []
    output.append("================\n")
    output.append("IDX V ** ADDR **\n")
    index = -1
    for set in cache:
        for block in set:
            index += 1
            block_id = block["block_identifier"] if block["V"] == 1 else ""
            valid = block["V"]
            if block_id != "":
                block_id = f"0x{block_id:08X}"
            output.append(f"{index:03} {valid} {block_id}\n")

    return output

def simulate_memory_access_in_cache(cache, input, lsb, fifo, output):
    number_of_sets = len(cache)
    blocks_per_set = len(cache[0])
    hits = 0
    misses = 0
    with open(input, 'r') as input_file:
        for address in input_file:
            block_found_in_cache = False
            address.strip()
            address_int = int(address, 16)

            block_set = address_int % number_of_sets
            block_id = (address_int >> lsb)

            for block in cache[block_set]:
                if block["V"] == 1 and block["block_identifier"] == block_id:
                    hits += 1
                    block_found_in_cache = True
                    output.extend(build_output(cache))
                    break
            
            if not block_found_in_cache:
                misses += 1
                pos_to_replace = None
                if(len(fifo[block_set]) == blocks_per_set):
                    pos_to_replace = fifo[block_set].popleft()
                    fifo[block_set].append(pos_to_replace)
                else:
                    for i in range(len(cache[block_set])):
                        if cache[block_set][i]["V"] == 0:
                            pos_to_replace = i
                            fifo[block_set].append(i)
                            break

                cache[block_set][pos_to_replace]["V"] = 1
                cache[block_set][pos_to_replace]["block_identifier"] = block_id
                output.extend(build_output(cache))
                

    return hits, misses

def main():
    if len(sys.argv) != 5:
        print("Number of arguments is incorrect.")
        sys.exit(1)

    cachesize = int(sys.argv[1])
    blocksize = int(sys.argv[2])
    groupsize = int(sys.argv[3])
    input = sys.argv[4]

    number_of_blocks = cachesize // blocksize
    number_of_sets = number_of_blocks // groupsize
    lsb = int(math.log2(blocksize))
    cache = build_cache(number_of_sets, groupsize)
    fifo = [deque() for i in range(number_of_sets)]
    output = []
    hits, miss = simulate_memory_access_in_cache(cache, input, lsb, fifo, output)
    
    with open('output.txt', 'w') as file:
        file.writelines(output)
        file.write("\n")
        file.write(f"#hits: {hits}\n")
        file.write(f"#miss: {miss}")

if __name__ == "__main__":
    main()