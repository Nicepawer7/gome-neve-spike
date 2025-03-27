def map_range(x,in_min,in_max,out_min,out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
i = 0
while i <= 100:
    print(str(i) + " " + str(map_range(i,0,90,100,1)))
    i += 1