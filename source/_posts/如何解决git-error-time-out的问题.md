---
title: 如何解决git error: time out的问题
tags: [Git]
categories: Tips
---



# 如何解决git error: time out的问题



大部分情况呢，可以通过以下两个命令解决：

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

