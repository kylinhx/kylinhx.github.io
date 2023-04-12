---
title: LEETCODE刷题笔记
tags: [Code,Python]
categories: Leetcode
---



# LEETCODE刷题笔记：2.两数相加

第一次解题代码：

```
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        List1=[]
        List2=[]
        result=[]
        while(l1):
            List1.append(l1.val)
            l1=l1.next
        while(l2):
            List2.append(l2.val)
            l2=l2.next
        num=max(len(List1),len(List2))
        index=[]
        for i in range(num+1):
            index.append(0)
        for i in range(0,num):
            if i < min(len(List1),len(List2)):
                if List1[i]+List2[i]+index[i]>=10:
                    index[i+1]=1
                result.append((List1[i]+List2[i]+index[i])%10)
            else:
                if i >=len(List1):
                    if List2[i]+index[i]>=10:
                        index[i+1]=1
                    result.append((List2[i]+index[i])%10)
                else:
                    if List1[i]+index[i]>=10:
                        index[i+1]=1
                    result.append((List1[i]+index[i])%10)
        if index[-1]>0:
            result.append(index[-1])
        l3=ListNode()
        node=l3
        node.val=1
        for i in range(len(result)):
            if i < len(result)-1:
                node.val=result[i]
                nodeNext=ListNode()
                node.next=nodeNext
                node=nodeNext
            else:
                node.val=result[i]
        return l3
```



进行改进：

```
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        l3=ListNode()
        node=l3
        index=0
        sum=0
        while(l1 or l2):
            if l1 and l2:
                sum = l1.val+l2.val
            elif l1:
                sum = l1.val
            elif l2:
                sum = l2.val
            if sum+index>=10:
                node.val=(sum+index)%10
                index=1
            else:
                node.val=(sum+index)%10
                index=0   
            if l1:
                l1=l1.next
            if l2:
                l2=l2.next
            if index==1 :
                nodeNext=ListNode()
                node.next=nodeNext
                node = nodeNext
                node.val=index
            else:
                if l2 or l1:
                    nodeNext=ListNode()
                    node.next=nodeNext
                    node = nodeNext
                    node.val=index
        return l3
```

