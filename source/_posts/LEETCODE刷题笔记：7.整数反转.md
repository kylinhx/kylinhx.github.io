---
title: LEETCODE刷题笔记
tags: [Code,Python]
categories: Leetcode
---



# LEETCODE刷题笔记：7.整数反转

```
class Solution:
    def reverse(self, x: int) -> int:
        new_str = str(x)
        if new_str[0] == '-':
            str1 = '-'
            new_str = new_str[1:]
        else:
            str1 = ''
        for i in range(len(new_str)):
            str1 = str1 + new_str[len(new_str)-i-1]
        int1 = int(str1)
        if int1 > pow(2,31)-1:
            return 0
        elif int1 < -pow(2,31):
            return 0
        return int1
```

