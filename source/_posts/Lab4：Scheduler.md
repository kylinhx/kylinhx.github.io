---
title: Lab4:Scheduler
tags: [Code,C,xv6]
categories: Study
mathjax: true
---



# Lab4：Scheduler

------

## 实验目标：

改变进程调度的方式（由时间轮转法改为优先级调度）

## 实验内容：

为每个进程添加一个优先级值（假设取一个介于 0 到 31 之间的范围）。从就绪列表进行调度时，始终首先调度优先级最高的进程。添加系统调用以更改进程的优先级。进程可以随时更改其优先级。如果优先级低于就绪列表上的任何进程，则必须切换到该进程。为避免进程饥饿，进程优先级可变。如果进程等待，增加其优先级。当它运行时，请将其减小。

## 实验背景以及一些学习笔记：

#### 1. XV6中进程相关的数据结构

在XV6中，与进程有关的数据结构如下

```c
// Per-process state
struct proc {
  uint sz;                     // Size of process memory (bytes)
  pde_t* pgdir;                // Page table
  char *kstack;                // Bottom of kernel stack for this process
  enum procstate state;        // Process state
  int pid;                     // Process ID
  struct proc *parent;         // Parent process
  struct trapframe *tf;        // Trap frame for current syscall
  struct context *context;     // swtch() here to run process
  void *chan;                  // If non-zero, sleeping on chan
  int killed;                  // If non-zero, have been killed
  struct file *ofile[NOFILE];  // Open files
  struct inode *cwd;           // Current directory
  char name[16];               // Process name (debugging)
};
```

与前述的两类信息的对应关系如下

1. 操作系统管理进程有关的信息：内核栈`kstack`，进程的状态`state`，进程的`pid`，进程的父进程`parent`，进程的中断帧`tf`，进程的上下文`context`，与`sleep`和`kill`有关的`chan`和`killed`变量。
2. 进程本身运行所需要的全部环境：虚拟内存信息`sz`和`pgdir`，打开的文件`ofile`和当前目录`cwd`。

额外地，`proc`中还有一条用于调试的进程名字`name`。

在操作系统中，所有的进程信息`struct proc`都存储在`ptable`中，`ptable`的定义如下

下面是`proc`结构体保存的一些重要数据结构

- 首先是保存了用户空间线程寄存器的trapframe字段
- 其次是保存了内核线程寄存器的context字段
- 还有保存了当前进程的内核栈的kstack字段，这是进程在内核中执行时保存函数调用的位置
- state字段保存了当前进程状态，要么是RUNNING，要么是RUNABLE，要么是SLEEPING等等
- lock字段保护了很多数据，目前来说至少保护了对于state字段的更新。举个例子，因为有锁的保护，两个CPU的调度器线程不会同时拉取同一个RUNABLE进程并运行它

```c
struct {
  struct spinlock lock;
  struct proc proc[NPROC];
} ptable;
```

除了互斥锁`lock`之外，一个值得注意的一点是XV6系统中允许同时存在的进程数量是有上限的。在这里`NPROC`为64，所以XV6最多只允许同时存在64个进程。

要注意操作系统的资源分配的单位是进程，处理机调度的单位是线程；

#### 2. 第一个用户进程

##### 1. userinit函数

在 `main` 初始化了一些设备和子系统后，它通过调用 `userinit`建立了第一个进程。

`userinit` 首先调用 `allocproc`。`allocproc`的工作是在页表中分配一个槽（即结构体 `struct proc`），并初始化进程的状态，为其内核线程的运行做准备。注意一点：`userinit` 仅仅在创建第一个进程时被调用，而 `allocproc` 创建每个进程时都会被调用。`allocproc` 会在 `proc` 的表中找到一个标记为 `UNUSED`的槽位。当它找到这样一个未被使用的槽位后，`allocproc` 将其状态设置为 `EMBRYO`，使其被标记为被使用的并给这个进程一个独有的 `pid`（2201-2219）。接下来，它尝试为进程的内核线程分配内核栈。如果分配失败了，`allocproc` 会把这个槽位的状态恢复为 `UNUSED` 并返回0以标记失败。

```c
// Set up first user process.
void
userinit(void)
{
  struct proc *p;
  extern char _binary_initcode_start[], _binary_initcode_size[];

  p = allocproc();
  
  initproc = p;
  if((p->pgdir = setupkvm()) == 0)
    panic("userinit: out of memory?");
  inituvm(p->pgdir, _binary_initcode_start, (int)_binary_initcode_size);
  p->sz = PGSIZE;
  memset(p->tf, 0, sizeof(*p->tf));
  p->tf->cs = (SEG_UCODE << 3) | DPL_USER;
  p->tf->ds = (SEG_UDATA << 3) | DPL_USER;
  p->tf->es = p->tf->ds;
  p->tf->ss = p->tf->ds;
  p->tf->eflags = FL_IF;
  p->tf->esp = PGSIZE;
  p->tf->eip = 0;  // beginning of initcode.S

  safestrcpy(p->name, "initcode", sizeof(p->name));
  p->cwd = namei("/");

  // this assignment to p->state lets other cores
  // run this process. the acquire forces the above
  // writes to be visible, and the lock is also needed
  // because the assignment might not be atomic.
  acquire(&ptable.lock);

  p->state = RUNNABLE;

  release(&ptable.lock);
}
```

##### 2. allocproc函数

1. 在ptable中找到一个没有被占用的槽位
2. 找到之后分配pid然后把他的状态设置为`EMBRYO`

```c
static struct proc*
allocproc(void)
{
  struct proc *p;
  char *sp;

  acquire(&ptable.lock);

  for(p = ptable.proc; p < &ptable.proc[NPROC]; p++)
    if(p->state == UNUSED)
      goto found;

  release(&ptable.lock);
  return 0;

found:
  p->state = EMBRYO;
  p->pid = nextpid++;

  release(&ptable.lock);

  // Allocate kernel stack.
  if((p->kstack = kalloc()) == 0){
    p->state = UNUSED;
    return 0;
  }
  sp = p->kstack + KSTACKSIZE;

  // Leave room for trap frame.
  sp -= sizeof *p->tf;
  p->tf = (struct trapframe*)sp;

  // Set up new context to start executing at forkret,
  // which returns to trapret.
  sp -= 4;
  *(uint*)sp = (uint)trapret;

  sp -= sizeof *p->context;
  p->context = (struct context*)sp;
  memset(p->context, 0, sizeof *p->context);
  p->context->eip = (uint)forkret;

  return p;
}
```

这里进行调用完之后得到的状态如下图所示

[![](https://th0ar.gitbooks.io/xv6-chinese/content/pic/f1-3.png)](https://th0ar.gitbooks.io/xv6-chinese/content/pic/f1-3.png)

##### 3. mpmain函数

```c
// Common CPU setup code.
static void
mpmain(void)
{
  cprintf("cpu%d: starting %d\n", cpuid(), cpuid());
  idtinit();       // load idt register
  xchg(&(mycpu()->started), 1); // tell startothers() we're up
  scheduler();     // start running processes
}
```

##### 1. scheduler()函数

```c
void
scheduler(void)
{
  struct proc *p;
  struct cpu *c = mycpu();
  c->proc = 0;
  
  for(;;){
    // Enable interrupts on this processor.
    sti();

    // Loop over process table looking for process to run.
    acquire(&ptable.lock);
    for(p = ptable.proc; p < &ptable.proc[NPROC]; p++){
      if(p->state != RUNNABLE)
        continue;

      // Switch to chosen process.  It is the process's job
      // to release ptable.lock and then reacquire it
      // before jumping back to us.
      c->proc = p;
      switchuvm(p);
      p->state = RUNNING;

      swtch(&(c->scheduler), p->context);
      switchkvm();

      // Process is done running for now.
      // It should have changed its p->state before coming back.
      c->proc = 0;
    }
    release(&ptable.lock);

  }
}
```

### 2. switchuvm函数

1. 这里要设置当前cpu的taskstate。关于[taskstate的知识补充](https://blog.csdn.net/pirloofmilan/article/details/8857382)

**taskstate的知识补充**

1. 对于cpu而言是没有进程或者线程的概念，对于cpu只有任务的概念
2. 对于ss0是存储的0环的栈段选择子
3. 对于`esp`是存储的0环的栈指针
4. 而对于ring的概念也就是环的概念这里可以简单理解成特权集[参考博客](https://www.cnblogs.com/wangwangfei/p/13942235.html)

![](image-20210822224911938-16782586432763.png)

```c
// Switch TSS and h/w page table to correspond to process p.
void
switchuvm(struct proc *p)
{
  if(p == 0)
    panic("switchuvm: no process");
  if(p->kstack == 0)
    panic("switchuvm: no kstack");
  if(p->pgdir == 0)
    panic("switchuvm: no pgdir");

  pushcli();
  mycpu()->gdt[SEG_TSS] = SEG16(STS_T32A, &mycpu()->ts,
                                sizeof(mycpu()->ts)-1, 0);
  mycpu()->gdt[SEG_TSS].s = 0;
  mycpu()->ts.ss0 = SEG_KDATA << 3;
  mycpu()->ts.esp0 = (uint)p->kstack + KSTACKSIZE;
  // setting IOPL=0 in eflags *and* iomb beyond the tss segment limit
  // forbids I/O instructions (e.g., inb and outb) from user space
  mycpu()->ts.iomb = (ushort) 0xFFFF;
  ltr(SEG_TSS << 3);
  lcr3(V2P(p->pgdir));  // switch to process's address space
  popcli();
}
```

##### 3. 第一个程序Initcode.S

第一个程序会在虚拟地址[0-pagesize]这一段

```asm
# exec(init, argv)
.globl start
start:
  pushl $argv
  pushl $init
  pushl $0  // where caller pc would be
  movl $SYS_exec, %eax
  int $T_SYSCALL

# for(;;) exit();
exit:
  movl $SYS_exit, %eax
  int $T_SYSCALL
  jmp exit

# char init[] = "/init\0";
init:
  .string "/init\0"

# char *argv[] = { init, 0 };
.p2align 2
argv:
  .long init
  .long 0
```

这里是调用了exec执行`init`函数

这个其实更像什么，更像shell终端的启动

```c
int
main(void)
{
  int pid, wpid;

  if(open("console", O_RDWR) < 0){
    mknod("console", 1, 1);
    open("console", O_RDWR);
  }
  dup(0);  // stdout
  dup(0);  // stderr

  for(;;){
    printf(1, "init: starting sh\n");
    pid = fork();
    if(pid < 0){
      printf(1, "init: fork failed\n");
      exit();
    }
    if(pid == 0){
      exec("sh", argv);
      printf(1, "init: exec sh failed\n");
      exit();
    }
    while((wpid=wait()) >= 0 && wpid != pid)
      printf(1, "zombie!\n");
  }
}
```

#### 4. 进程切换

进程切换解决之后，对于xv6的进程调度就会有一个比较清晰的分析了

[![](https://th0ar.gitbooks.io/xv6-chinese/content/pic/f5-1.png)](https://th0ar.gitbooks.io/xv6-chinese/content/pic/f5-1.png)

几个重要的概念就是

- 每一个进程都有一个对应的内核线程(也就是scheduler thread)线程。
- 在xv6中想要从一个进程(当然这里叫线程也是无所谓的)切换到另一个线程中，必须要先从当前进程-->当前进程的内核线程-->目的线程的内核线程-->目的线程的用户进程。这样一个过程才能完成调度

##### 1. 先从yied和sched开始

这个函数就是当前进程要让出cpu。所以把当前proc()的状态设置成`RUNNABLE`

最后调用sched()

```c
// Give up the CPU for one scheduling round.
void
yield(void)
{
  acquire(&ptable.lock);  //DOC: yieldlock
  myproc()->state = RUNNABLE;
  sched();
  release(&ptable.lock);
}
```

这里先进行一些状态判断，如果出问题就会panic。

##### 2. 随后调用swtch函数

这个函数就是`switch`这里为了不与c语言中的库函数同名

```c
void
sched(void)
{
  int intena;
  struct proc *p = myproc();

  if(!holding(&ptable.lock))
    panic("sched ptable.lock");
  if(mycpu()->ncli != 1)
    panic("sched locks");
  if(p->state == RUNNING)
    panic("sched running");
  if(readeflags()&FL_IF)
    panic("sched interruptible");
  intena = mycpu()->intena;
  swtch(&p->context, mycpu()->scheduler);
  mycpu()->intena = intena;
}
```

`swtch`函数就是传说中的上下文切换。只不过和之前说的用户状态的上下文切换不一样

这里是把当前cpu的内核线程的寄存器保存到`p->context`中

这里的`（esp + 4）`存储的就是`edi`寄存器的值。而`(esp + 8)`存储的就是`esi`寄存器的值，也就是第一个参数和第二个参数

```assembly
.globl swtch
swtch:
  movl 4(%esp), %eax
  movl 8(%esp), %edx

  # Save old callee-saved registers
  pushl %ebp
  pushl %ebx
  pushl %esi
  pushl %edi

  # Switch stacks
  movl %esp, (%eax)
  movl %edx, %esp

  # Load new callee-saved registers
  popl %edi
  popl %esi
  popl %ebx
  popl %ebp
  ret
```

![](image-20210823173722313.png)

所以这里最后就会把`mycpu()->scheduler`中保存的context信息弹出到寄存器中。同时把esp寄存器更换成`mycpu()->scheduler`那里。所以这里的ret的返回地址就是`mycpu()->scheduler`保存的eip的值。也就会返回到

[![](https://cdn.jsdelivr.net/gh/JayL-zxl/picture_store@master//xv_4.assets/image-20210823183713981.png)](https://cdn.jsdelivr.net/gh/JayL-zxl/picture_store@master//xv_4.assets/image-20210823183713981.png)

红色箭头所指向的一行。

##### 3. 回到`scheduler`函数

现在我们在scheduler函数的循环中，代码会检查所有的进程并找到一个来运行。随后再来调用swtch函数

又调用了swtch函数来保存调度器线程的寄存器，并恢复目标进程的寄存器（注，实际上恢复的是目标进程的内核线程）

这里有件事情需要注意，调度器线程调用了swtch函数，但是我们从swtch函数返回时，实际上是返回到了对于switch的另一个调用，而不是调度器线程中的调用。我们返回到的是pid为目的进程的进程在很久之前对于switch的调用。这里可能会有点让人困惑，但是这就是线程切换的核心。

##### 4. 回到用户空间

最后的返回是利用了`trapret`

```assembly
# Return falls through to trapret...
.globl trapret
trapret:
  popal
  popl %gs
  popl %fs
  popl %es
  popl %ds
  addl $0x8, %esp  # trapno and errcode
  iret
```

这个函数把保存的trapframe恢复。最后通过iret恢复到用户空间

#### 5. 看一下fork、wait、exit函数

##### 1. fork函数

1. 创建一个进程
2. 把父进程的页表copy过来(这里还不是cow方式的)
3. 这里比较重要的点是先加锁。然后把子进程的状态设置成runnable。如果在解锁之前子进程就被调度的话。那返回值就是利用tf->eax来获取
4. 否则的话解锁return父进程的pid，表示从父进程返回

```c
// Create a new process copying p as the parent.
// Sets up stack to return as if from system call.
// Caller must set state of returned proc to RUNNABLE.
int
fork(void)
{
  int i, pid;
  struct proc *np;
  struct proc *curproc = myproc();

  // Allocate process.
  if((np = allocproc()) == 0){
    return -1;
  }

  // Copy process state from proc.
  if((np->pgdir = copyuvm(curproc->pgdir, curproc->sz)) == 0){
    kfree(np->kstack);
    np->kstack = 0;
    np->state = UNUSED;
    return -1;
  }
  np->sz = curproc->sz;
  np->parent = curproc;
  *np->tf = *curproc->tf;

  // Clear %eax so that fork returns 0 in the child.
  np->tf->eax = 0;

  for(i = 0; i < NOFILE; i++)
    if(curproc->ofile[i])
      np->ofile[i] = filedup(curproc->ofile[i]);
  np->cwd = idup(curproc->cwd);

  safestrcpy(np->name, curproc->name, sizeof(curproc->name));

  pid = np->pid;

  acquire(&ptable.lock);

  np->state = RUNNABLE;

  release(&ptable.lock);

  return pid;
}
```

##### 2. wait函数

1. 如果找到了处于`ZOMBIE`状态子进程会把他释放掉。（分别释放对于的pid、内核栈、页表）
2. 否则如果没有子进程则return -1
3. 否则调用slepp函数等待

```c
// Wait for a child process to exit and return its pid.
// Return -1 if this process has no children.
int
wait(void)
{
  struct proc *p;
  int havekids, pid;
  struct proc *curproc = myproc();
  
  acquire(&ptable.lock);
  for(;;){
    // Scan through table looking for exited children.
    havekids = 0;
    for(p = ptable.proc; p < &ptable.proc[NPROC]; p++){
      if(p->parent != curproc)
        continue;
      havekids = 1;
      if(p->state == ZOMBIE){
        // Found one.
        pid = p->pid;
        kfree(p->kstack);
        p->kstack = 0;
        freevm(p->pgdir);
        p->pid = 0;
        p->parent = 0;
        p->name[0] = 0;
        p->killed = 0;
        p->state = UNUSED;
        release(&ptable.lock);
        return pid;
      }
    }

    // No point waiting if we don't have any children.
    if(!havekids || curproc->killed){
      release(&ptable.lock);
      return -1;
    }

    // Wait for children to exit.  (See wakeup1 call in proc_exit.)
    sleep(curproc, &ptable.lock);  //DOC: wait-sleep
  }
}
```

**sleep函数**会在后面讲锁的时候去看

##### 3. exit函数

1. 首先exit函数关闭了所有已打开的文件。这里可能会很复杂，因为关闭文件系统中的文件涉及到引用计数，虽然我们还没学到但是这里需要大量的工作。不管怎样，一个进程调用exit系统调用时，会关闭所有自己拥有的文件。
2. 进程有一个对于当前目录的记录，这个记录会随着你执行cd指令而改变。在exit过程中也需要将对这个目录的引用释放给文件系统。
3. 如果这个想要退出的进程，它又有自己的子进程，接下来需要设置这些子进程的父进程为init进程。我们接下来会看到，每一个正在exit的进程，都有一个父进程中的对应的wait系统调用。父进程中的wait系统调用会完成进程退出最后的几个步骤。所以如果父进程退出了，那么子进程就不再有父进程，当它们要退出时就没有对应的父进程的wait。所以在exit函数中，会为即将exit进程的子进程重新指定父进程为init进程，也就是PID为1的进程。
4. 最后把要exit的进程状态设置成`ZOMBIE`
5. 执行`sched`函数重新回到内核线程。。。找新的线程去执行

```c
void
exit(void)
{
  struct proc *curproc = myproc();
  struct proc *p;
  int fd;

  if(curproc == initproc)
    panic("init exiting");

  // Close all open files.
  for(fd = 0; fd < NOFILE; fd++){
    if(curproc->ofile[fd]){
      fileclose(curproc->ofile[fd]);
      curproc->ofile[fd] = 0;
    }
  }
  begin_op();
  iput(curproc->cwd);
  end_op();
  curproc->cwd = 0;

  acquire(&ptable.lock);

  // Parent might be sleeping in wait().
  wakeup1(curproc->parent);

  // Pass abandoned children to init.
  for(p = ptable.proc; p < &ptable.proc[NPROC]; p++){
    if(p->parent == curproc){
      p->parent = initproc;
      if(p->state == ZOMBIE)
        wakeup1(initproc);
    }
  }

  // Jump into the scheduler, never to return.
  curproc->state = ZOMBIE;
  sched();
  panic("zombie exit");
}
```

##### 4. kill函数

Unix中的一个进程可以将另一个进程的ID传递给kill系统调用，并让另一个进程停止运行。如果不够小心的话，kill一个还在内核执行代码的进程，会有风险，比如想要杀掉的进程的内核线程还在更新一些数据，比如说更新文件系统，创建一个文件。如果这样的话，我们不能就这样杀掉进程，因为这样会使得一些需要多步完成的操作只执行了一部分。所以kill系统调用不能就直接停止目标进程的运行。实际上，在XV6和其他的Unix系统中，kill系统调用基本上不做任何事情。

```c
// Kill the process with the given pid.
// Process won't exit until it returns
// to user space (see trap in trap.c).
int
kill(int pid)
{
  struct proc *p;

  acquire(&ptable.lock);
  for(p = ptable.proc; p < &ptable.proc[NPROC]; p++){
    if(p->pid == pid){
      p->killed = 1;
      // Wake process from sleep if necessary.
      if(p->state == SLEEPING)
        p->state = RUNNABLE;
      release(&ptable.lock);
      return 0;
    }
  }
  release(&ptable.lock);
  return -1;
}
```

## 实验过程：

#### 1、修改proc.c

```
增加
priority表示优先级

waitTime表示总等待时间

currentWait当前等待时间

runTime表示运行时间

currentRun表示当前运行时间

turnAroundTime表示总周转时间
```

```c
struct proc {
  uint sz;                     // Size of process memory (bytes)
  pde_t* pgdir;                // Page table
  char *kstack;                // Bottom of kernel stack for this process
  enum procstate state;        // Process state
  int pid;                     // Process ID
  struct proc *parent;         // Parent process
  struct trapframe *tf;        // Trap frame for current syscall
  struct context *context;     // swtch() here to run process
  void *chan;                  // If non-zero, sleeping on chan
  int killed;                  // If non-zero, have been killed
  struct file *ofile[NOFILE];  // Open files
  struct inode *cwd;           // Current directory
  char name[16];               // Process name (debugging)
  int priority;
  int waitTime;
  int runTime;
  int turnAroundTime;
  int currentWait;
  int currentRun;
};
```

#### 2、修改proc.c

（1）、修改`allocproc`

```c
found:
  p->state = EMBRYO;
  p->pid = nextpid++;
  p->priority = 15; //设置初始优先级为15
  p->waitTime = 0;
  p->runTime = 0;
  p->turnAroundTime = 0;
  p->currentWait = 0;
  p->currentRun = 0;
```

（2）、修改`scheduler`

```c
void
scheduler(void)
{
  struct proc *p;
  struct cpu *c = mycpu();
  c->proc = 0;
  
  for(;;){
    // Enable interrupts on this processor.
    sti();

    // Loop over process table looking for process to run.
    acquire(&ptable.lock);
  
	struct proc * tempProcess = 0;
    for(p = ptable.proc; p < &ptable.proc[NPROC]; p++){
      	if(p->state != RUNNABLE)
        	continue;
        	
	  	//遍历一次进程数组，找出优先级最高的进程
      	for(tempProcess = ptable.proc; tempProcess < &ptable.proc[NPROC]; tempProcess++)
      	{
      		//遍历等待或者运行状态的进程，如果选中等待状态的，就进行进程切换；如果选中运行状态的，当前运行进程继续执行
        	if(tempProcess->state != RUNNABLE || tempProcess->state != RUNNING)
        		continue;
        	//priority越小，优先级越高
        	if(tempProcess->priority < p->priority)
        	{
          		p = tempProcess;
        	}
      	}
      	
      	//p进程被选中，下一轮将被执行，因此运行次数加一
      	p->runTime++;
		p->currentRun++;
		p->turnAroundTime++;
		//如果p进程运行次数达到了一定程度，则优先级降低
		if(p->currentRun > 100&& p->priority < 31){
			p->priority++;
			p->currentRun =0;
			cprintf("%d priority ++, turn into %d\n", p->pid, p->priority);
		}
		
		//p进程被选中执行，则其他进程将要等待，遍历进程数组找出除p进程之外在运行或等待的进程，等待次数加一
		for(tempProcess = ptable.proc; tempProcess < &ptable.proc[NPROC]; tempProcess++){
			//选出除p进程之外在等待或运行的进程
			if((tempProcess->state != RUNNABLE && tempProcess->state != RUNNING)
				||tempProcess->pid==p->pid)
       			continue;
			tempProcess->waitTime++;
			tempProcess->currentWait++;
			tempProcess->turnAroundTime++;
			//如果等待次数达到一定程度，优先级升高
			if(tempProcess->currentWait>220&& tempProcess->priority > 0)
			{
				tempProcess->priority--;
				tempProcess->currentWait=0;
				cprintf("%d priority --, turn into %d\n", tempProcess->pid, tempProcess->priority);
			}
		}  

		//如果p进程本身就是运行状态且优先级最高，则直接跳过本轮循环，不需要进程上下文切换
		if(p->state == RUNNING)
			continue;
		
		//p进程是等待状态，此时进行进程上下文切换
     	// Switch to chosen process.  It is the process's job
      	// to release ptable.lock and then reacquire it
      	// before jumping back to us.
      	c->proc = p;
      	switchuvm(p);
      	p->state = RUNNING;

      	swtch(&(c->scheduler), p->context);
      	switchkvm();

      	// Process is done running for now.
      	// It should have changed its p->state before coming back.
      	c->proc = 0;
    }
    release(&ptable.lock);

  }
}
```

（3）、添加`changePriority()`，修改选中进程的优先级

```c
int 
changePriority(int tempPid, int tempPriority){
    struct proc * p;
    acquire(&ptable.lock);
    for(p = ptable.proc; p < &ptable.proc[NPROC]; p++){
		if(p->pid == tempPid){
    		p->priority = tempPriority;
			break;
		}
    }
    release(&ptable.lock);
    return tempPid;
}
```

（4）、添加`showProcess()`，展示当前所有进程的运行情况，包括pid、优先级、进程状态、周转时间等。

```c
int
showProcess(void)
{
    struct proc *p;
    sti();
    acquire(&ptable.lock);
    for (p = ptable.proc; p < &ptable.proc[NPROC]; p++)
    {
        if (p->state == SLEEPING)
        {
            cprintf("Proc: %s\tPid:%d\tstate:SLEEPING\tPriority:%d\t", p->name, p->pid, p->priority);
            cprintf("turnTime:%d\trunTime:%d\twaitTime:%d\n",p->turnAroundTime,p->runTime,p->waitTime);
        }
        else if (p->state == RUNNING)
        {
            cprintf("Proc: %s\tPid:%d\tstate:RUNNING\tPriority:%d\t", p->name, p->pid, p->priority);
            cprintf("turnTime:%d\trunTime:%d\twaitTime:%d\n",p->turnAroundTime,p->runTime,p->waitTime);
        }
        else if (p->state == RUNNABLE)
        {
            cprintf("Proc: %s\tPid:%d\tstate:RUNNABLE\tPriority:%d\t", p->name, p->pid, p->priority);
            cprintf("turnTime:%d\trunTime:%d\twaitTime:%d\n",p->turnAroundTime,p->runTime,p->waitTime);
        }
    }
    release(&ptable.lock);
    return 1;
}
```

#### 3、修改syscall.h

```c
#define SYS_changePriority 22
#define SYS_showProcess 23
```

#### 4、修改syscall.c

```c
extern int sys_changePriority(void);
extern int sys_showProcess(void);
...
[SYS_changePriority] sys_changePriority,
[SYS_showProcess] sys_showProcess,
```

#### 5、修改usys.S

```c
SYSCALL(changePriority)
SYSCALL(showProcess)
```

#### 6、修改user.h

```c
int changePriority(int, int);
int showProcess(void);
```

#### 7、修改sysproc.h

```C
int sys_changePriority(void){
    int pid, priority;
    if(argint(0, &pid) < 0) return -1;
    if(argint(1, &priority) < 0) return -1;
    return changePriority(pid, priority);
}

int sys_showProcess(void){
    return showProcess();
}
```

#### 8、修改defs.h

```c
int             changePriority(int, int);
int             showProcess(void);
```

#### 9、编写showproc.c，调用showProcess()

```c
#include "types.h"
#include "stat.h"
#include "user.h"

int
main(int args,char *argv[])
{
    showProcess();
    return 0;
}
```

#### 10、编写changeproc.c，调用changePriority()

```c
#include "types.h"
#include "stat.h"
#include "user.h"

int 
main(int argc, char * argv[])
{
    int tempPriority, tempPid;
    if(argc < 3)
    {
		printf(0, "Invalid command.\n");
    }
    else
    {
        tempPid = atoi(argv[1]);
		tempPriority = atoi(argv[2]);
		if(tempPriority < 0 || tempPriority > 31) 
	        printf(0, "Priority num error.\n");
		else 
			changePriority(tempPid, tempPriority);
	}
   	return 0;
}
```

#### 11、编写makefork.c，用于创建子进程

```C
#include "types.h"
#include "stat.h"
#include "user.h"

int
main(int argc, char* argv[])
{
	pid = fork(); 
    int a,b;
   	if (pid < 0) 
      	printf(0, "fork error\n");
   	else if (pid == 0)//Child
   	{
   		printf(1, "Child %d is created!\n", getpid());
   		for ( a = 0; a < 100; a++)
   		{
        	for ( b = 0; b < 10; b++)
        	{
                   a*=b;
      		}
   		}
      	exit();
  	}
    wait();
    return 0;
}
```

#### 12、修改MakeFile

#### 13、编译运行结果展示

运行myfork创建子进程，随着运行次数的增加，child5进程优先级越来越高

输入ps查看进程状态，只有myfork在running，其他都在sleeping

![](image-20220929085012732.png)

------

过一段时间再次输入ps查看进程状态，发现myfork进程turntime与runtime还有waittime都增加

![](image-20220929084825882.png)

------

输入myfork再次创建新进程，发现两个进程前后优先级不断变化，输入ps查看进程状态

![](image-20220929084745093.png)

------

输入chpr 5 20，将5进程优先级升高到20

![](image-20220929085105486.png)

然后优先级会随着进程运行进一步降低

![](image-20220929085131511.png)