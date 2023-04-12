---
title: LEETCODE刷题笔记
tags: [Code,Python]
categories: Leetcode
---



# LEETCODE刷题笔记：9.回文串

```
class Solution:
    def isPalindrome(self, x: int) -> bool:
        str1 = str(x)
        str2 = ''
        for i in range(len(str1)):
            str2 = str2 + str1[len(str1)-1-i]
        if str1 == str2:
            return True
        else:
            return False
```

