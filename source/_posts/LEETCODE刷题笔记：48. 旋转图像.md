---
title: LEETCODE刷题笔记
tags: [Code,Python]
mathjax: true
categories: Leetcode
---

# LEETCODE刷题笔记：[48. 旋转图像](https://leetcode.cn/problems/rotate-image/)

### 转载声明：

来源：力扣（LeetCode）
链接：https://leetcode.cn/problems/rotate-image
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

### 题目描述：

给定一个 `n × n` 的二维矩阵 `matrix` 表示一个图像。请你将图像顺时针旋转 90 度。

你必须在 原地 旋转图像，这意味着你需要直接修改输入的二维矩阵。请**不要**使用另一个矩阵来旋转图像。

### 示例1：

```
输入：matrix = [[1,2,3],[4,5,6],[7,8,9]]
输出：[[7,4,1],[8,5,2],[9,6,3]]
```

### 示例2：

```
输入：matrix = [[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]
输出：[[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]]
```

### 提示：

`n == matrix.length == matrix[i].length`
`1 <= n <= 20`
`-1000 <= matrix[i][j] <= 1000`

### 题解：

顺时针旋转90°主要经过两个变化，第一个是沿**对角线**对称，第二个是沿**竖直对称轴**对称

```
class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.
        """
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if i == j:
                    continue
                elif j < i:
                    k = matrix[i][j]
                    matrix[i][j] = matrix[j][i]
                    matrix[j][i] = k
        
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                mid = (len(matrix)-1) / 2
                if j < mid :
                    k = matrix[i][len(matrix) - 1 - j]
                    matrix[i][len(matrix) - 1 - j] = matrix[i][j]
                    matrix[i][j] = k
```

