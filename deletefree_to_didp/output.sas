begin_version
3
end_version
begin_metric
0
end_metric
21
begin_variable
var0
-1
2
Atom on(c, a)
NegatedAtom on(c, a)
end_variable
begin_variable
var1
-1
2
Atom on(c, c)
NegatedAtom on(c, c)
end_variable
begin_variable
var2
-1
2
Atom ontable(c)
NegatedAtom ontable(c)
end_variable
begin_variable
var3
-1
2
Atom holding(c)
NegatedAtom holding(c)
end_variable
begin_variable
var4
-1
2
Atom on(c, d)
NegatedAtom on(c, d)
end_variable
begin_variable
var5
-1
2
Atom on(b, a)
NegatedAtom on(b, a)
end_variable
begin_variable
var6
-1
2
Atom on(b, d)
NegatedAtom on(b, d)
end_variable
begin_variable
var7
-1
2
Atom on(a, a)
NegatedAtom on(a, a)
end_variable
begin_variable
var8
-1
2
Atom on(a, c)
NegatedAtom on(a, c)
end_variable
begin_variable
var9
-1
2
Atom on(a, d)
NegatedAtom on(a, d)
end_variable
begin_variable
var10
-1
2
Atom on(d, a)
NegatedAtom on(d, a)
end_variable
begin_variable
var11
-1
2
Atom on(d, c)
NegatedAtom on(d, c)
end_variable
begin_variable
var12
-1
2
Atom on(d, d)
NegatedAtom on(d, d)
end_variable
begin_variable
var13
-1
2
Atom holding(a)
NegatedAtom holding(a)
end_variable
begin_variable
var14
-1
2
Atom holding(d)
NegatedAtom holding(d)
end_variable
begin_variable
var15
-1
2
Atom on(d, b)
NegatedAtom on(d, b)
end_variable
begin_variable
var16
-1
2
Atom on(b, b)
NegatedAtom on(b, b)
end_variable
begin_variable
var17
-1
2
Atom clear(b)
NegatedAtom clear(b)
end_variable
begin_variable
var18
-1
2
Atom holding(b)
NegatedAtom holding(b)
end_variable
begin_variable
var19
-1
2
Atom on(b, c)
NegatedAtom on(b, c)
end_variable
begin_variable
var20
-1
2
Atom on(a, b)
NegatedAtom on(a, b)
end_variable
0
begin_state
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
end_state
begin_goal
3
4 0
19 0
20 0
end_goal
37
begin_operator
pick-up a
0
1
0 13 -1 0
1
end_operator
begin_operator
pick-up b
1
17 0
1
0 18 -1 0
1
end_operator
begin_operator
pick-up c
1
2 0
1
0 3 -1 0
1
end_operator
begin_operator
pick-up d
0
1
0 14 -1 0
1
end_operator
begin_operator
put-down b
1
18 0
1
0 17 -1 0
1
end_operator
begin_operator
put-down c
1
3 0
1
0 2 -1 0
1
end_operator
begin_operator
stack a a
1
13 0
1
0 7 -1 0
1
end_operator
begin_operator
stack a b
2
17 0
13 0
1
0 20 -1 0
1
end_operator
begin_operator
stack a c
1
13 0
1
0 8 -1 0
1
end_operator
begin_operator
stack a d
1
13 0
1
0 9 -1 0
1
end_operator
begin_operator
stack b a
1
18 0
2
0 17 -1 0
0 5 -1 0
1
end_operator
begin_operator
stack b b
2
17 0
18 0
1
0 16 -1 0
1
end_operator
begin_operator
stack b c
1
18 0
2
0 17 -1 0
0 19 -1 0
1
end_operator
begin_operator
stack b d
1
18 0
2
0 17 -1 0
0 6 -1 0
1
end_operator
begin_operator
stack c a
1
3 0
1
0 0 -1 0
1
end_operator
begin_operator
stack c c
1
3 0
1
0 1 -1 0
1
end_operator
begin_operator
stack c d
1
3 0
1
0 4 -1 0
1
end_operator
begin_operator
stack d a
1
14 0
1
0 10 -1 0
1
end_operator
begin_operator
stack d b
2
17 0
14 0
1
0 15 -1 0
1
end_operator
begin_operator
stack d c
1
14 0
1
0 11 -1 0
1
end_operator
begin_operator
stack d d
1
14 0
1
0 12 -1 0
1
end_operator
begin_operator
unstack a a
1
7 0
1
0 13 -1 0
1
end_operator
begin_operator
unstack a b
1
20 0
2
0 17 -1 0
0 13 -1 0
1
end_operator
begin_operator
unstack a c
1
8 0
1
0 13 -1 0
1
end_operator
begin_operator
unstack a d
1
9 0
1
0 13 -1 0
1
end_operator
begin_operator
unstack b a
2
17 0
5 0
1
0 18 -1 0
1
end_operator
begin_operator
unstack b b
2
17 0
16 0
1
0 18 -1 0
1
end_operator
begin_operator
unstack b c
2
17 0
19 0
1
0 18 -1 0
1
end_operator
begin_operator
unstack b d
2
17 0
6 0
1
0 18 -1 0
1
end_operator
begin_operator
unstack c a
1
0 0
1
0 3 -1 0
1
end_operator
begin_operator
unstack c b
0
2
0 17 -1 0
0 3 -1 0
1
end_operator
begin_operator
unstack c c
1
1 0
1
0 3 -1 0
1
end_operator
begin_operator
unstack c d
1
4 0
1
0 3 -1 0
1
end_operator
begin_operator
unstack d a
1
10 0
1
0 14 -1 0
1
end_operator
begin_operator
unstack d b
1
15 0
2
0 17 -1 0
0 14 -1 0
1
end_operator
begin_operator
unstack d c
1
11 0
1
0 14 -1 0
1
end_operator
begin_operator
unstack d d
1
12 0
1
0 14 -1 0
1
end_operator
0
