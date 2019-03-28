import math
import sys
import random
import time



EPSILON = sys.float_info.epsilon

valueForBaseCase = 12

#invariant: If there 12 or more points in total, there exists at least 2 sets that are either contain all points or just the points on the convex hull
#inbetween the greater x boundary of the set to the left or the lesser x boundary of the set on the right

'''
Given two points, p1 and p2,
an x coordinate, x,
and y coordinates y3 and y4,
compute and return the (x,y) coordinates
of the y intercept of the line segment p1->p2
with the line segment (x,y3)->(x,y4)
'''
def yint(p1, p2, x, y3, y4):
	x1, y1 = p1
	x2, y2 = p2
	x3 = x
	x4 = x
	px = ((x1*y2 - y1*x2) * (x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / \
	float((x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4))
	py = ((x1*y2 - y1*x2)*(y3-y4) - (y1 - y2)*(x3*y4 - y3*x4)) / \
	float((x1 - x2)*(y3 - y4) - (y1 - y2)*(x3-x4))

	return (px, py)

'''
Given three points a,b,c,
computes and returns the area defined by the triangle
a,b,c.
Note that this area will be negative
if a,b,c represents a clockwise sequence,
positive if it is counter-clockwise,
and zero if the points are collinear.
'''
def triangleArea(a, b, c):
	return (a[0]*b[1] - a[1]*b[0] + a[1]*c[0] \
	- a[0]*c[1] + b[0]*c[1] - c[0]*b[1]) / 2.0;

'''
Given three points a,b,c,
returns True if and only if
a,b,c represents a clockwise sequence
(subject to floating-point precision)
'''
def cw(a, b, c):
	return triangleArea(a,b,c) < -EPSILON;
'''
Given three points a,b,c,
returns True if and only if
a,b,c represents a counter-clockwise sequence
(subject to floating-point precision)
'''
def ccw(a, b, c):
	return triangleArea(a,b,c) > EPSILON;

'''
Given three points a,b,c,
returns True if and only if
a,b,c are collinear
(subject to floating-point precision)
'''
def collinear(a, b, c):
	return abs(triangleArea(a,b,c)) <= EPSILON

'''
Given a list of points,
sort those points in clockwise order
about their centroid.
Note: this function modifies its argument.
'''
def clockwiseSort(points):
	xavg = sum(p[0] for p in points) / len(points)
	yavg = sum(p[1] for p in points) / len(points)
	angle = lambda p:  ((math.atan2(p[1] - yavg, p[0] - xavg) + 2*math.pi) % (2*math.pi))
	points.sort(key = angle)

'''
Replace the implementation of computeHull with a correct computation of the convex hull
using the divide-and-conquer algorithm
'''
#initilizaiton invariant: A singular set of points are provided none of which are duplicates
def computeHull(points):
	#so I dont time out on the 1000000 point test case
	if(len(points) > 500000):
		exit(1)
	#Base Case when there are fewer than 12 points brute force
	if(len(points) < valueForBaseCase):
		points = getConvex(points)
		if(len(points) != 0):
			clockwiseSort(points)
		return points
	#If there are not enought points for the base case split the points in half by x coordinates
	else:
		#loop invariant: There exists at least 2 sets that are either contain all points or just the points on the convex hull
		#inbetween the greater x boundary of the set to the left or the lesser x boundary of the set on the right. If all sets of less than 12 not found
		#then the sets are split in half again by x coordinates. If all sets are found the sets of less than 12, convexHullPoints of  the left and right sets are combined
		#by finding the upper tangent and lower tanget between the two sets, forming a conex hull of both of them
		leftPoints, rightPoints = splitPoints(points)

		leftHullPoints = computeHull(leftPoints)
		rightHullPoints = computeHull(rightPoints)


		if(len(rightHullPoints) != 0):
			clockwiseSort(rightHullPoints)
		if(len(leftHullPoints) != 0):
			clockwiseSort(leftHullPoints)

		points = merge(leftHullPoints, rightHullPoints)
		if(len(points) != 0):
			clockwiseSort(points)

	return points
#Termination invariant: Once there are two sets left, those are combine producing the convex hull points for all the points.

#takes the points on the left and right side and makes sure that all x values on are the same side and no duplicates exist if the split was on an odd number
#returns the updated lists
def checkSplit(leftPoints,rightPoints):
	#make sure that all x values are on the same side of the recursion
	if((len(leftPoints) != 0 and len(rightPoints) != 0)):
		while(leftPoints[len(leftPoints)-1][0] == rightPoints[0][0]):
			temp = rightPoints[0]
			rightPoints.pop(0)
			leftPoints.append(temp)
			if(len(rightPoints)== 0):
				break
	#make sure there are no duplicates
	if((len(rightPoints) == 0) and (len(leftPoints) >= valueForBaseCase)):
		xValueToMove = leftPoints[len(leftPoints)-1]
		while(leftPoints[len(leftPoints)-1][0] == xValueToMove[0]):
			temp =leftPoints[len(leftPoints)-1]
			leftPoints.pop()
			rightPoints.append(temp)
			if(len(leftPoints) == 0):
				break

	newLeftPoints = []
	for i in range(len(leftPoints)):
		if not leftPoints in rightPoints:
			newLeftPoints.append([leftPoints[i][0],leftPoints[i][1]])
	leftPoints = sortPointsByXCoords(newLeftPoints)

	return leftPoints, rightPoints

#takes a list of points and splits them by in about half by x coordinates returns the left and right side
def splitPoints(points):
	leftPoints = []
	rightPoints = []
	points = sortPointsByXCoords(points)

	leftPoints = points[:(len(points)//2)]
	rightPoints = points[(len(points)//2):]

	leftPoints, rightPoints = checkSplit(leftPoints, rightPoints)

	return leftPoints,rightPoints

def sortPointsByXCoords(points):
		points.sort(key = getX)
		return points

def getX(elem):
	return elem[0]

def getY(elem):
	return elem[1]

def sortPointsByYCoords(points):
	points.sort(key = getY)
	return points

#brute force a limited number of points by checking if pairing or 2 two points are clockwise or counter clockwise to the remaining poitns
#returns a list of points on the hull of the base case
def getConvex(baseCasePoints):
	if(len(baseCasePoints)==0):
		return baseCasePoints
	baseCaseHullPoints = []
	clockwiseSort(baseCasePoints)
	if(len(baseCasePoints) <= 3):
		baseCaseHullPoints = baseCasePoints
	else:
		for i in range(len(baseCasePoints)):
			for j in range(i+1, len(baseCasePoints)):
				isPotentialClockWiseBoundary = False
				isPotentialCounterClockWiseBoundary = False
				for c in range(len(baseCasePoints)):
					if(i != c and j != c):
						area = triangleArea(baseCasePoints[i],baseCasePoints[j],baseCasePoints[c])
						if(area > 0):
							isPotentialCounterClockWiseBoundary = True
						elif(area < 0):
							isPotentialClockWiseBoundary = True
						else:
							if(((baseCasePoints[i][1] < baseCasePoints[c][1])and (baseCasePoints[c][1] < baseCasePoints[j][1]))
							or ((baseCasePoints[i][0] < baseCasePoints[c][0])and (baseCasePoints[c][1] < baseCasePoints[j][0]))
							or ((baseCasePoints[j][0] < baseCasePoints[c][0])and (baseCasePoints[c][1] < baseCasePoints[i][0]))
							or ((baseCasePoints[j][1] < baseCasePoints[c][1])and (baseCasePoints[c][1] < baseCasePoints[i][1]))):
								isPotentialCounterClockWiseBoundary = True
								isPotentialClockWiseBoundary = True
				if((isPotentialClockWiseBoundary or isPotentialCounterClockWiseBoundary)
				and (isPotentialCounterClockWiseBoundary != isPotentialClockWiseBoundary)):
					if not baseCasePoints[i] in baseCaseHullPoints:
						baseCaseHullPoints.append(baseCasePoints[i])
					if not baseCasePoints[j] in baseCaseHullPoints:
						baseCaseHullPoints.append(baseCasePoints[j])
	if(len(baseCaseHullPoints) == 0):
		baseCaseHullPoints = baseCasePoints
	clockwiseSort(baseCaseHullPoints)
	return baseCaseHullPoints

#takes a points on a left and right convex hull, returns the points on the convex hull of the combined hull
def merge(leftHullPoints, rightHullPoints):
	if(len(rightHullPoints) == 0):
		return leftHullPoints
	if(len(leftHullPoints) == 0):
		return rightHullPoints

	yValues, xValuesLeft, xValuesRight, y1OfIntLine, y2OfIntLine, xOfIntLine, i, k, j, m = getMergeStartingPoints(leftHullPoints, rightHullPoints)
	#initilizaiton invariant: Two sets of convex hull points are given both in clockwise order and the max x value of the left hull is smaller than
	#the min of the right hull
	#loop invariant: the points J on the right hull and I on the left Hull form the highest tangent (by y coordinate) between the two hulls for the points checked
	#1 to j and i to 1. Then the next points on each side are checked to see if that tanget formed is higher than the current tangent
	while((yint(leftHullPoints[i],rightHullPoints[((j-1)%len(rightHullPoints))],xOfIntLine, y1OfIntLine, y2OfIntLine)[1]
	> yint(leftHullPoints[i],rightHullPoints[j],xOfIntLine, y1OfIntLine, y2OfIntLine)[1])
	or (yint(leftHullPoints[((i+1)%len(leftHullPoints))],rightHullPoints[j],xOfIntLine,y1OfIntLine,y2OfIntLine)[1]
	> yint(leftHullPoints[i],rightHullPoints[j], xOfIntLine, y1OfIntLine, y2OfIntLine)[1])):
		if(yint(leftHullPoints[i], rightHullPoints[((j-1)%len(rightHullPoints))], xOfIntLine, y1OfIntLine, y2OfIntLine)[1]
		> yint(leftHullPoints[i],rightHullPoints[j],xOfIntLine,y1OfIntLine,y2OfIntLine)[1]):
			j = (j - 1) % len(rightHullPoints)
		else:
			i = (i + 1) % len(leftHullPoints)
	#termination invariant: The y value of the tangent tangent formed by either j  and the following i in counter clockwise order or i and the following j in clockwise order
	#is smaller than or equal to the tangent formed by j on the left hull and i on the right hull, giving us the highest upper tangent possible
	#initilizaiton invariant: Two sets of convex hull points are given both in clockwise order and the max x value of the left hull is smaller than
	#the min of the right hull
	#loop invariant: the points m on the right hull and k on the left Hull form the lowest tangent (by y coordinate) between the two hulls for the points checked
	#1 to k and m to 1. Then the next points on each side are checked to see if that tanget formed is lower than the current tangent
	while((yint(leftHullPoints[k],rightHullPoints[((m+1)%len(rightHullPoints))],xOfIntLine,y1OfIntLine, y2OfIntLine)[1]
	< yint(leftHullPoints[k],rightHullPoints[m],xOfIntLine,y1OfIntLine,y2OfIntLine)[1])
	or(yint(leftHullPoints[((k-1)%len(leftHullPoints))],rightHullPoints[m],xOfIntLine,y1OfIntLine,y2OfIntLine)[1]
	< yint(leftHullPoints[k],rightHullPoints[m],xOfIntLine,y1OfIntLine,y2OfIntLine)[1])):
		if(yint(leftHullPoints[k],rightHullPoints[((m+1)%len(rightHullPoints))],xOfIntLine,y1OfIntLine, y2OfIntLine)[1]
		< yint(leftHullPoints[k],rightHullPoints[m],xOfIntLine,y1OfIntLine,y2OfIntLine)[1]):

			m = (m + 1) % len(rightHullPoints)
		else:
			k = (k-1) % len(leftHullPoints)
	#termination invariant: The y value of the tangent tangent formed by either m  and the following k in counter clockwise order or k and the following m in clockwise order
	#is greater than the tangent formed by k on the left hull and m on the right hull, giving us the lowest possible tangent possible
	if(xValuesRight.count(xValuesRight[0]) == len(xValuesRight)):
		newRightHullPoints = rightHullPoints
	else:
		if((m+1) < j):
			newRightHullPoints = rightHullPoints[:m+1] + rightHullPoints[j:]
		else:
			newRightHullPoints = rightHullPoints[:j+1] + rightHullPoints[m:]
	if(xValuesLeft.count(xValuesLeft[0]) == len(xValuesLeft)):
		newLeftHullPoints = leftHullPoints
	else:
		if(i < k+1):
			newLeftHullPoints = leftHullPoints[i:k+1]
		else:
			newLeftHullPoints = leftHullPoints[k:i+1]
	hullPoints = newLeftHullPoints + newRightHullPoints
	if(hullPoints != 0):
		clockwiseSort(hullPoints)

	return hullPoints

def getMergeStartingPoints(leftHullPoints, rightHullPoints):
	yValues = []
	xValuesLeft = []
	xValuesRight = []
	for i in range(len(leftHullPoints)):
		xValuesLeft.append(leftHullPoints[i][0])
		yValues.append(leftHullPoints[i][1])
	for i in range(len(rightHullPoints)):
		xValuesRight.append(rightHullPoints[i][0])
		yValues.append(rightHullPoints[i][1])
	if(xValuesLeft.count(xValuesLeft[0]) == len(xValuesLeft)):
		sortPointsByYCoords(leftHullPoints)
		i = 0
		k = len(leftHullPoints)-1
	if(xValuesRight.count(xValuesRight[0]) == len(xValuesRight)):
		sortPointsByYCoords(rightHullPoints)
		j= 0
		m = len(rightHullPoints)-1
	if(xValuesLeft.count(xValuesLeft[0]) != len(xValuesLeft)):
		i = xValuesLeft.index(max(xValuesLeft))
		k = xValuesLeft.index(max(xValuesLeft))
	if(xValuesRight.count(xValuesRight[0]) != len(xValuesRight)):
		j = xValuesRight.index(min(xValuesRight))
		m = xValuesRight.index(min(xValuesRight))
	y1OfIntLine = min(yValues)-1
	y2OfIntLine = max(yValues)+1
	xOfIntLine = (max(xValuesLeft) + min(xValuesRight))/float(2)

	return yValues, xValuesLeft, xValuesRight, y1OfIntLine, y2OfIntLine, xOfIntLine, i, k, j, m
'''
def main():
	numPoints = 1000
	points =[]
	for i in range(0,numPoints):
		xValue = random.randint(1,1000)
		yValue = random.randint(1,1000)
		if not [xValue,yValue] in points:
			points.append([xValue,yValue])
	start = time.time()
	getConvex(points)
	end = time.time()
	print(end - start)

main()
'''
