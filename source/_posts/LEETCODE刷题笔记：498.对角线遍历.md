---
title: LEETCODE刷题笔记
tags: [Code,Python]
mathjax: true
categories: Leetcode
---



# LEETCODE刷题笔记：498.对角线遍历

### 转载声明：

来源：力扣（LeetCode）
链接：https://leetcode.cn/problems/diagonal-traverse
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

### 题目描述：

给你一个大小为 `m x n` 的矩阵 `mat` ，请以对角线遍历的顺序，用一个数组返回这个矩阵中的所有元素。

### 示例1：

![](image-20230125190843856.png)

```
输入：mat = [[1,2,3],[4,5,6],[7,8,9]]
输出：[1,2,4,7,5,3,6,8,9]
```

### 示例2：

```
输入：mat = [[1,2],[3,4]]
输出：[1,2,3,4]
```



### 提示：

`m == mat.length`
`n == mat[i].length`
`1 <= m, n <= 104`
`1 <= m * n <= 104`
`-105 <= mat[i][j] <= 105`



### 题解：

主要是寻找规律，可以发现下面三个规律：

1、`对角线个数为 m + n - 1`

2、`第n个对角线为偶数时，向右上走；第n个对角线为奇数时，向左下走`

3、`数到矩阵边缘停止，偶数时边缘为上面和右面，奇数时边缘为左面和下面`

```
class Solution:
    def findDiagonalOrder(self, mat):
        m = len(mat[0])
        n = len(mat)
        #  第偶数个对角线向右上走
        #  第奇数个对角线向左下走
        #  一直到矩阵边缘：横坐标或者纵坐标有一个为0
        count = m + n -1
        line = 0
        row = 0
        ans = []
        for i in range(count):
            # 第i个对角线为偶数
            if i % 2 == 0:
                # 判断是否是矩阵边缘：由于是偶数个对角线，只需要判断line是否为0
                while(1):
                    if line == 0 : 
                        # 矩阵边缘
                        ans.append(mat[line][row])
                        # 判断row是否到最右端
                        if row == m - 1:
                            line = line + 1
                        if row < m-1:
                            row = row + 1
                        break
                    elif row == m - 1:
                        ans.append(mat[line][row])
                        if line < n - 1:
                            line = line + 1
                        break
                    else:
                        # 向右上走
                        ans.append(mat[line][row])
                        line = line - 1
                        row = row + 1
            # 第i个对角线为奇数
            else:
                # 判断是否是矩阵边缘：由于是奇数个对角线，只需要判断row 是否为0
                while(1):
                    if row == 0 : 
                        # 矩阵边缘
                        ans.append(mat[line][row])
                        # 判断line是否到最下端
                        if line == n - 1:
                            row = row + 1
                        if line < n - 1:
                            line = line + 1
                        break
                    elif line == n - 1:
                        ans.append(mat[line][row])
                        if row < m - 1:
                            row = row + 1
                        break
                    else:
                        # 向左下走
                        ans.append(mat[line][row])
                        line = line + 1
                        row = row - 1
        return ans

```



### 提交结果：

![](image-20230125203503702.png)