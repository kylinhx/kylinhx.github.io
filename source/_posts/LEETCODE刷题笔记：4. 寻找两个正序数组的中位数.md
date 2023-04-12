---
title: LEETCODE刷题笔记
tags: [Code,Python]
categories: Leetcode
---



# LEETCODE刷题笔记：[4. 寻找两个正序数组的中位数](https://leetcode.cn/problems/median-of-two-sorted-arrays/)

第一版直接冒泡排序找中位数

```
class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        # 返回的中位数
        midnumber = 0
        # len1 与 len2 分别为数组nums1和nums2的长度
        len1 = len(nums1)
        len2 = len(nums2)
        # 将两个数组合并
        nums = nums1 + nums2
        # length为两个数组长度之和
        length = len1 + len2
        # 冒泡排序
        for i in range(length):
            for j in range(i+1,length):
                if nums[i] > nums[j]:
                    k = nums[j]
                    nums[j] = nums[i]
                    nums[i] = k
        # length是偶数
        if length % 2 == 0:
            mid_index1 = int(length / 2)
            mid_index2 = int(length / 2 - 1)
            midnumber = (nums[mid_index1] + nums[mid_index2]) / 2
        # length是奇数
        else:
            mid_index = int((length - 1) / 2)
            midnumber = nums[mid_index]
        return midnumber
```

