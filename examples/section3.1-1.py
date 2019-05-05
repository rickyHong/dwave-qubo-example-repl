"""
Section 3.1 The Number Partitioning Problem
Partition a set of numbers into two subsets such that the subset sums are as close to each other as possible.

Test list size 50
"""

import copy
import dimod
import random
import sys
import time
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

def generate_numbers(num_numbers):
    random.seed(51229)
    numbers = random.sample(xrange(1, 1000), num_numbers)
    return numbers

def to_bqm(numbers):
    c = sum(numbers)
    c_square = c**c

    linear = {}
    quadratic = {}
    offset = 0.0
    vartype = dimod.BINARY
    for index, value in enumerate(numbers):
        linear[index+1] = value * (value - c)
    for index1, value1 in enumerate(numbers[:-1]):
        for index2 in range(index1+1, len(numbers)):
            value = value1 * numbers[index2]
            idx = (index1+1, index2+1)
            quadratic[idx] = quadratic[tuple(reversed(idx))] = value

    bqm = dimod.BinaryQuadraticModel(
        linear, 
        quadratic, 
        offset, 
        vartype)
    print len(linear)
    print len(quadratic)
    return bqm

def solve(sampler, bqm, num_reads=None):
    params = {}
    if num_reads:
        params['num_reads'] = num_reads
    return sampler.sample(bqm, **params)

def split_numbers_list(numbers, result):
    list1 = []
    list2 = []
    for key, include_in_list in result.items():
        index = key-1
        if include_in_list:
            list1.append(numbers[index])
        else:
            list2.append(numbers[index])
    return list1, list2

def print_result(sample_set):
    for sample in sample_set.samples():
        list1, list2 = split_numbers_list(numbers, sample)
        print "list1: {}, sum: {}, list2: {}, sum: {}".format(list1, sum(list1), list2, sum(list2))

exact_solver = dimod.ExactSolver()
simulated_annealing_sampler = dimod.SimulatedAnnealingSampler()
dwave_sampler = EmbeddingComposite(DWaveSampler())

print "#"*80
numbers = generate_numbers(50)  # generate a list of numbers to be split into equal sums
# numbers = [25,7,13,31,42,17,21,10]
bqm = to_bqm(numbers)

#
# ExactSolver does not work when list has many items eg. len(numbers) == 100
#
# start = time.time()
# sample_set = solve(exact_solver, bqm)
# end = time.time()
# print "Using ExactSolver (elapsed time: {}s)".format(end-start)
# sample_set = sample_set.truncate(5)
# print sample_set
# print_result(sample_set)
# print ""

start = time.time()
sample_set = solve(simulated_annealing_sampler, bqm)
end = time.time()
print "Using SimulatedAnnlearingSampler (elapsed time: {}s)".format(end-start)
sample_set = sample_set.truncate(5)
print sample_set
print_result(sample_set)
print ""

# Using Simulated (elapsed time: 15.2062799931s)
#    1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 ... 50       energy num_oc.
# 0  1  1  1  1  1  1  1  1  1  1  1  0  1  1  1  0 ...  0 -134235392.0       1
# 1  1  0  1  1  0  0  1  1  1  1  0  1  1  1  1  1 ...  0 -134235392.0       1
# 2  0  0  0  0  0  0  0  1  0  1  1  0  1  1  1  1 ...  1 -134235332.0       1
# 3  1  1  1  1  1  1  1  1  1  1  0  0  1  0  0  1 ...  0 -134235315.0       1
# 4  1  1  1  1  0  1  1  0  0  1  1  0  1  1  0  0 ...  1 -134235200.0       1
# ['BINARY', 5 rows, 5 samples, 50 variables]
# list1: [871, 448, 112, 490, 834, 608, 488, 295, 455, 174, 911, 107, 67, 324, 88, 902, 209, 256, 500, 523, 102, 71, 696, 266, 280, 86, 417, 267, 206, 531], sum: 11584, list2: [977, 588, 239, 264, 766, 980, 762, 345, 170, 998, 993, 514, 673, 564, 561, 24, 6, 566, 996, 602], sum: 11588
# list1: [871, 112, 490, 488, 295, 455, 174, 977, 107, 67, 324, 588, 239, 762, 345, 500, 523, 102, 514, 71, 673, 696, 266, 24, 86, 267, 6, 566, 996], sum: 11584, list2: [448, 834, 608, 911, 264, 88, 766, 902, 980, 209, 170, 256, 998, 993, 564, 280, 561, 417, 206, 531, 602], sum: 11588
# list1: [295, 174, 911, 107, 67, 324, 588, 239, 264, 902, 980, 762, 170, 500, 998, 71, 696, 266, 561, 24, 531, 566, 996, 602], sum: 11594, list2: [871, 448, 112, 490, 834, 608, 488, 455, 977, 88, 766, 209, 345, 256, 523, 102, 993, 514, 673, 564, 280, 86, 417, 267, 6, 206], sum: 11578
# list1: [871, 448, 112, 490, 834, 608, 488, 295, 455, 174, 107, 588, 239, 264, 88, 980, 345, 256, 500, 993, 514, 673, 564, 86, 417, 206], sum: 11595, list2: [911, 977, 67, 324, 766, 902, 762, 209, 170, 523, 998, 102, 71, 696, 266, 280, 561, 24, 267, 6, 531, 566, 996, 602], sum: 11577
# list1: [871, 448, 112, 490, 608, 488, 174, 911, 107, 67, 264, 88, 209, 345, 170, 102, 993, 514, 673, 564, 266, 561, 24, 86, 267, 6, 566, 996, 602], sum: 11572, list2: [834, 295, 455, 977, 324, 588, 239, 766, 902, 980, 762, 256, 500, 523, 998, 71, 696, 280, 417, 206, 531], sum: 11600

start = time.time()
sample_set = solve(dwave_sampler, bqm, num_reads=10)
end = time.time()
print "Using DWaveSampler (elapsed time: {}s)".format(end-start)
print sample_set
print_result(sample_set)
print ""

# Using DWaveSampler (elapsed time: 5.94733715057s)
#    1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 ... 50       energy num_oc. ...
# 6  0  0  1  1  1  1  1  1  1  1  1  0  0  0  0 ...  0 -134229771.0       1 ...
# 4  0  0  0  1  0  1  1  0  1  0  0  0  1  1  0 ...  0 -134187872.0       1 ...
# 0  0  1  1  1  1  1  1  0  1  0  1  0  0  1  0 ...  0 -133890827.0       1 ...
# 2  0  1  1  0  0  1  1  0  1  0  1  0  1  0  0 ...  0 -133853472.0       1 ...
# 9  0  0  0  1  1  1  1  0  1  1  0  0  0  0  1 ...  0 -133832171.0       1 ...
# 3  0  0  1  1  1  0  0  0  1  0  1  0  1  1  0 ...  0 -133666880.0       1 ...
# 5  0  1  0  0  0  0  1  1  1  1  0  0  0  0  0 ...  0 -132553187.0       1 ...
# 8  0  0  1  1  1  1  1  1  0  1  1  1  1  1  1 ...  0 -132482420.0       1 ...
# 7  0  0  0  1  1  1  0  1  1  1  1  1  0  1  1 ...  1 -120751812.0       1 ...
# 1  0  1  0  1  1  1  1  1  1  1  1  1  1  1  0 ...  1 -113687307.0       1 ...
# ['BINARY', 10 rows, 10 samples, 50 variables]
# list1: [112, 490, 834, 608, 488, 295, 455, 174, 911, 588, 239, 88, 766, 980, 762, 102, 673, 564, 266, 561, 86, 417, 206, 996], sum: 11661, list2: [871, 448, 977, 107, 67, 324, 264, 902, 209, 345, 170, 256, 500, 523, 998, 993, 514, 71, 696, 280, 24, 267, 6, 531, 566, 602], sum: 11511
# list1: [490, 608, 488, 455, 107, 67, 264, 88, 766, 980, 762, 209, 345, 256, 500, 998, 102, 993, 71, 673, 696, 564, 266, 280, 86, 417, 267, 6], sum: 11804, list2: [871, 448, 112, 834, 295, 174, 911, 977, 324, 588, 239, 902, 170, 523, 514, 561, 24, 206, 531, 566, 996, 602], sum: 11368
# list1: [448, 112, 490, 834, 608, 488, 455, 911, 67, 980, 762, 500, 102, 993, 71, 673, 266, 561, 24, 86, 6, 566, 996], sum: 10999, list2: [871, 295, 174, 977, 107, 324, 588, 239, 264, 88, 766, 902, 209, 345, 170, 256, 523, 998, 514, 696, 564, 280, 417, 267, 206, 531, 602], sum: 12173
# list1: [448, 112, 608, 488, 455, 911, 107, 264, 980, 762, 209, 345, 500, 523, 993, 673, 696, 266, 561, 86, 417, 267, 6, 531, 996], sum: 12204, list2: [871, 490, 834, 295, 174, 977, 67, 324, 588, 239, 88, 766, 902, 170, 256, 998, 102, 514, 71, 564, 280, 24, 206, 566, 602], sum: 10968
# list1: [490, 834, 608, 488, 455, 174, 324, 588, 239, 264, 88, 980, 762, 170, 500, 523, 993, 514, 71, 673, 564, 266, 280, 24, 86, 267, 996], sum: 12221, list2: [871, 448, 112, 295, 911, 977, 107, 67, 766, 902, 209, 345, 256, 998, 102, 696, 561, 417, 6, 206, 531, 566, 602], sum: 10951
# list1: [112, 490, 834, 455, 911, 107, 67, 264, 88, 766, 980, 762, 209, 170, 256, 998, 102, 993, 673, 564, 561, 86, 417, 267, 6, 206, 996], sum: 12340, list2: [871, 448, 608, 488, 295, 174, 977, 324, 588, 239, 902, 345, 500, 523, 514, 71, 696, 266, 280, 24, 531, 566, 602], sum: 10832
# list1: [448, 488, 295, 455, 174, 588, 239, 766, 980, 762, 345, 170, 256, 500, 998, 102, 514, 71, 673, 696, 564, 266, 561, 86, 417, 267, 206, 996], sum: 12883, list2: [871, 112, 490, 834, 608, 911, 977, 107, 67, 324, 264, 88, 902, 209, 523, 993, 280, 24, 6, 531, 566, 602], sum: 10289
# list1: [112, 490, 834, 608, 488, 295, 174, 911, 977, 107, 67, 324, 588, 239, 88, 980, 762, 209, 170, 500, 102, 514, 266, 561, 86, 417, 267, 6, 206, 566, 996], sum: 12910, list2: [871, 448, 455, 264, 766, 902, 345, 256, 523, 998, 993, 71, 673, 696, 564, 280, 24, 531, 602], sum: 10262
# list1: [490, 834, 608, 295, 455, 174, 911, 977, 67, 324, 588, 239, 264, 902, 980, 762, 170, 500, 523, 102, 993, 673, 696, 280, 561, 86, 206, 996, 602], sum: 15258, list2: [871, 448, 112, 488, 107, 88, 766, 209, 345, 256, 998, 514, 71, 564, 266, 24, 417, 267, 6, 531, 566], sum: 7914
# list1: [448, 490, 834, 608, 488, 295, 455, 174, 911, 977, 107, 67, 588, 239, 264, 88, 766, 980, 209, 345, 170, 256, 998, 102, 993, 514, 673, 696, 561, 417, 267, 6, 531, 602], sum: 16119, list2: [871, 112, 324, 902, 762, 500, 523, 71, 564, 266, 280, 24, 86, 206, 566, 996], sum: 7053

#
# The result does not look too good, let's try again with larger num_reads
#
start = time.time()
sample_set = solve(dwave_sampler, bqm, num_reads=1000)
end = time.time()
print "Using DWaveSampler (elapsed time: {}s)".format(end-start)
sample_set = sample_set.truncate(100)
print sample_set
print_result(sample_set)
print ""

# Using DWaveSampler (elapsed time: 11.7918388844s)
#     1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 ... 50       energy num_oc. ...
# 0   1  0  0  0  0  1  0  1  0  1  1  0  0  0  1 ...  1 -134235392.0       1 ...
# 1   0  0  1  1  0  1  1  1  0  0  1  0  1  0  0 ...  1 -134235380.0       1 ...
# 2   1  1  1  0  0  1  0  0  0  1  1  0  1  0  0 ...  1 -134235380.0       1 ...
# 3   0  1  1  0  1  0  0  1  0  0  1  1  1  0  1 ...  1 -134235380.0       1 ...
# 4   0  0  1  0  1  0  0  1  1  1  0  1  0  0  0 ...  1 -134235275.0       1 ...
# 5   0  1  1  0  0  0  0  1  0  1  0  0  0  0  1 ...  1 -134235107.0       1 ...
# 6   1  0  1  1  0  1  0  0  1  0  0  0  1  0  0 ...  1 -134235072.0       1 ...
# 7   1  0  1  0  1  0  0  0  0  1  1  0  0  1  1 ...  1 -134235035.0       1 ...
# 8   1  0  1  1  0  1  1  1  0  1  0  0  1  0  1 ...  0 -134234720.0       1 ...
# 9   0  1  1  0  0  0  0  1  0  1  1  0  0  0  0 ...  1 -134234435.0       1 ...
# 10  0  1  1  1  0  0  1  1  0  1  1  0  0  0  0 ...  1 -134234372.0       1 ...
# ...
# ['BINARY', 100 rows, 100 samples, 50 variables]
# list1: [871, 608, 295, 174, 911, 324, 239, 766, 980, 209, 345, 500, 523, 514, 71, 673, 696, 266, 561, 417, 267, 206, 566, 602], sum: 11584, list2: [448, 112, 490, 834, 488, 455, 977, 107, 67, 588, 264, 88, 902, 762, 170, 256, 998, 102, 993, 564, 280, 24, 86, 6, 531, 996], sum: 11588
# list1: [112, 490, 608, 488, 295, 911, 107, 239, 264, 766, 980, 762, 209, 345, 170, 256, 500, 523, 998, 102, 673, 561, 417, 6, 206, 602], sum: 11590, list2: [871, 448, 834, 455, 174, 977, 67, 324, 588, 88, 902, 993, 514, 71, 696, 564, 266, 280, 24, 86, 267, 531, 566, 996], sum: 11582
# list1: [871, 448, 112, 608, 174, 911, 107, 588, 239, 766, 902, 762, 209, 345, 170, 998, 673, 564, 266, 86, 417, 206, 566, 602], sum: 11590, list2: [490, 834, 488, 295, 455, 977, 67, 324, 264, 88, 980, 256, 500, 523, 102, 993, 514, 71, 696, 280, 561, 24, 267, 6, 531, 996], sum: 11582
# list1: [448, 112, 834, 295, 911, 977, 107, 324, 588, 88, 766, 902, 209, 345, 500, 514, 266, 86, 417, 206, 531, 566, 996, 602], sum: 11590, list2: [871, 490, 608, 488, 455, 174, 67, 239, 264, 980, 762, 170, 256, 523, 998, 102, 993, 71, 673, 696, 564, 280, 561, 24, 267, 6], sum: 11582
# list1: [112, 834, 295, 455, 174, 977, 588, 239, 88, 766, 980, 209, 345, 523, 514, 673, 696, 561, 417, 531, 996, 602], sum: 11575, list2: [871, 448, 490, 608, 488, 911, 107, 67, 324, 264, 902, 762, 170, 256, 500, 998, 102, 993, 71, 564, 266, 280, 24, 86, 267, 6, 206, 566], sum: 11597
# list1: [448, 112, 295, 174, 324, 588, 239, 766, 902, 209, 345, 500, 523, 998, 102, 514, 673, 696, 266, 280, 561, 24, 417, 267, 6, 206, 566, 602], sum: 11603, list2: [871, 490, 834, 608, 488, 455, 911, 977, 107, 67, 264, 88, 980, 762, 170, 256, 993, 71, 564, 86, 531, 996], sum: 11569
# list1: [871, 112, 490, 608, 455, 107, 239, 88, 766, 902, 345, 170, 256, 523, 998, 673, 561, 86, 417, 206, 531, 566, 996, 602], sum: 11568, list2: [448, 834, 488, 295, 174, 911, 977, 67, 324, 588, 264, 980, 762, 209, 500, 102, 993, 514, 71, 696, 564, 266, 280, 24, 267, 6], sum: 11604
# list1: [871, 112, 834, 174, 911, 67, 324, 588, 264, 88, 902, 209, 345, 256, 500, 514, 71, 696, 561, 417, 206, 531, 566, 996, 602], sum: 11605, list2: [448, 490, 608, 488, 295, 455, 977, 107, 239, 766, 980, 762, 170, 523, 998, 102, 993, 673, 564, 266, 280, 24, 86, 267, 6], sum: 11567
# list1: [871, 112, 490, 608, 488, 295, 174, 107, 324, 239, 264, 902, 980, 762, 209, 170, 256, 523, 998, 102, 514, 71, 673, 266, 561, 24, 417, 6, 206], sum: 11612, list2: [448, 834, 455, 911, 977, 67, 588, 88, 766, 345, 500, 993, 696, 564, 280, 86, 267, 531, 566, 996, 602], sum: 11560
# list1: [448, 112, 295, 174, 911, 588, 239, 264, 88, 766, 902, 209, 345, 500, 523, 998, 102, 993, 673, 696, 417, 206, 566, 602], sum: 11617, list2: [871, 490, 834, 608, 488, 455, 977, 107, 67, 324, 980, 762, 170, 256, 514, 71, 564, 266, 280, 561, 24, 86, 267, 6, 531, 996], sum: 11555