---
title: LEETCODE刷题笔记
tags: [Code,Python]
mathjax: true
categories: Leetcode
---

# LEETCODE刷题笔记：[14. 最长公共前缀](https://leetcode.cn/problems/longest-common-prefix/)

### 转载声明：

来源：力扣（LeetCode）
链接：https://leetcode.cn/problems/longest-common-prefix
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

### 题目描述：

编写一个函数来查找字符串数组中的最长公共前缀。

如果不存在公共前缀，返回空字符串 ""。

 

### 示例 1：

输入：strs = ["flower","flow","flight"]
输出："fl"

### 示例 2：

输入：strs = ["dog","racecar","car"]
输出：""
解释：输入不存在公共前缀。

### 提示：

`1 <= strs.length <= 200`
`0 <= strs[i].length <= 200`
`strs[i] 仅由小写英文字母组成`

### 题解：

首先明白，这个最长的公共前缀只可能跟最短的字串有关系，所以首先获得最短字串的长度以及索引，然后用每一个字符串和这个字符串的字符比较，得出最后结果

```
class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        # 首先获得最短的字符串下标
        length = len(strs[0])
        index = 0
        for i,j in enumerate(strs):
            if len(j) < length:
                length = len(j)
                index = i
        ans = ''
        for i in range(length):
            flag = 0
            for j in strs:
                if j == index:
                    continue
                else:
                    if strs[index][i] != j[i]:
                        flag = 1
            if flag == 1:
                break
            else:
                ans = ans + strs[index][i]
        
        return ans
```

### 提交结果：

![](image-20230125220827232.png)