---
title: LEETCODE刷题笔记
tags: [Code,Python]
categories: Leetcode
---



# LEETCODE刷题笔记：6.Z字型变换

将字符串填充，然后寻找规律对字符串从新排列

```
class Solution:
    def convert(self, s: str, numRows: int) -> str:
        new_str = ''
        index = []
        str_len = len(s)
        group_members = numRows * 2 - 2
        if group_members == 0:
            return s
        if str_len == group_members:
            group_number = 1
            number1 = 0
        elif str_len < group_members:
            group_number = 1
            number1 = group_members - str_len
            for i in range(number1):
                s = s + '?'
        else:
            number1 = group_members - (str_len % group_members)
            for i in range(number1):
                s = s + '?'
            group_number =  len(s) // group_members 
        print(s)
        otherLines = numRows - 2
        for i in range(numRows):
            if i == 0:
                for j in range(group_number):
                    index.append(group_members*j)
            elif i == numRows - 1:
                for j in range(group_number):
                    index.append(group_members*j + numRows - 1)
            else:
                for j in range(group_number):
                    index.append(i+j*group_members)
                    index.append(j*group_members + i + otherLines * 2)
                otherLines = otherLines - 1
        for i in index:
            if s[i] == '?':
                continue
            else:
                new_str = new_str + s[i]
        return new_str
```

