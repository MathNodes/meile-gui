#!/bin/env python3

speedRate = []
speed = "-124542424242010.28MB+13.25KB"

speedAdj = speed.lstrip().rstrip().split('+')

if "MB" in speedAdj[0]:
        speedRate.append("MB")
elif "KB" in speedAdj[0]:
        speedRate.append("KB")
else:
        speedRate.append("B")

if "MB" in speedAdj[1]:
        speedRate.append("MB")
elif "KB" in speedAdj[1]:
        speedRate.append("KB")
else:
        speedRate.append("B")


speedAdj[0] = speedAdj[0].replace('MB', '').replace('KB', '').replace('B', '')
speedAdj[1] = speedAdj[1].replace('MB', '').replace('KB', '').replace('B', '')

if float(speedAdj[0]) < 0:
        speedAdj[0] = 0
        
if float(speedAdj[1]) < 0:
        speedAdj[1] = 0
        
speed = str(speedAdj[0]) + speedRate[0] + "↓" + "," + str(speedAdj[1]) + speedRate[1] + "↑"
print(speed)


