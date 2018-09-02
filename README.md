# python-sql-performance
测试异步与同步下Python对于PostgreSQL数据库操作的性能

通过测试同步以及异步下对于数据库的增加和查找操作，以进行性能评估。更直观的以及量化地感受同步以及异步下的性能差距。

# 环境初始化
需要安装`pipenv`，详细内容可[参考](https://blog.instcode.top/Python/Ubuntu16.04%E5%AE%89%E8%A3%85Python3.6.html#%E5%AE%89%E8%A3%85pipenv)

```bash
pip3.6 install pipenv
git clone https://github.com/GuangTianLi/python-sql-performance.git
cd python-sql-performance
pipenv sync
pipenv shell
```
# SQL操作性能评估
```bash
python postgresql_speed_test.py
```
> DBAPI:  psycopg2
         11004 function calls in 2.235 seconds
  DBAPI:  asyncpg
         471973 function calls in 2.436 seconds
  DBAPI:  uvloop
         206945 function calls in 0.794 seconds
  DBAPI:  psycopg2, total seconds 2.558364
  DBAPI:  asyncpg, total seconds 2.309759
  DBAPI:  uvloop, total seconds 2.032303       

## 结论
从结果上看，对于数据库操作本身，异步对于其性能本身只能算是锦上添花。而异步操作本身则也需要添加对事件循环的处理，
等于是变相的增加了运行时间，而如果每个数据库操作本身所需要的时间小于事件循环处理的时间，则其总时间就是增加的。

所以异步架构在用于单纯的数据库操作时，并不能取得非常良好的性能优化，
数据库操作本身的优化还是依赖于操作本身以及数据库结构的优化。
      
# WebServer性能评估

## flask
```bash
python flask_server_speed_test.py
```

>✗ wrk -d 60 -c 100 -t 12 --timeout 8 http://127.0.0.1:8080/db
Running 1m test @ http://127.0.0.1:8080/db
  12 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   331.47ms  221.85ms   2.01s    89.71%
    Req/Sec    30.95     17.90    80.00     63.85%
  18597 requests in 1.00m, 3.10MB read
Requests/sec:    309.41
Transfer/sec:     52.88KB

## sanic
```bash
python sanic_server_speed_test.py
```

>✗ wrk -d 60 -c 100 -t 12 --timeout 8 http://127.0.0.1:8080/db
Running 1m test @ http://127.0.0.1:8080/db
  12 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   162.95ms   99.56ms   1.89s    87.88%
    Req/Sec    52.26     23.73   148.00     61.57%
  36702 requests in 1.00m, 4.83MB read
Requests/sec:    610.64
Transfer/sec:     82.29KB

## 结论
从中等量级的压测的结果上看，对于异步架构的网络服务器，在性能上有了很大的提升。