# debuglog

## Installation

```
$ pip install debuglog
```

## Usage

### Logging for any timing.

```python
import debuglog
debug_logger = debuglog.get_debug_logger()
debug_logger.debug("debug")
```

The message for info-level is output to the standard-out.

```python
debug_logger.info("info")
```
```
INFO   info
```

And, the message for more than warning-level is output to the standard-error-out.

```python
debug_logger.warning("warning")
```
```
WARNING    warning
```

Create "./log/debug.log" when called `get_debug_logger ()`.
and, write the all message for more than debug-level is to the file.

```
.
└log
    └debug.log
```

```
2019-12-26 02:34:09,871	debuglog.py	223	DEBUG	--- Maked RootLogger "debug" -----
2019-12-26 02:34:23,923	<stdin>	1	DEBUG	debug
2019-12-26 02:34:34,251	<stdin>	1	INFO	info
2019-12-26 02:34:49,341	<stdin>	1	WARNING	warning
```

### Logging for calls of function and method.

Decorate the function want to get the log with `debuglog.calledlog`.

```python
import time
import debuglog
@debuglog.calledlog
def sample():
    debuglogger = debuglog.get_debug_logger()
    time.sleep(1)
    debuglogger.debug("sample")
```

Then will logged with debug-level is start timing, terminate timing and processing time, when called the function.

```python
sample()
```
```
2019-12-26 02:50:54,637	debuglog.py	223	DEBUG	--- Maked RootLogger "debug" -----
2019-12-26 02:50:54,638	debuglog.py	228	DEBUG	--- Changed ChildLogger "debug.__main__" -----
2019-12-26 02:50:54,638	debuglog.py	273	DEBUG	================================================================================
2019-12-26 02:50:54,638	debuglog.py	274	DEBUG	Started the __main__.sample
2019-12-26 02:50:54,639	debuglog.py	275	DEBUG	--------------------------------------------------------------------------------
2019-12-26 02:50:55,640	<stdin>	6	DEBUG	sample
2019-12-26 02:50:55,641	debuglog.py	279	DEBUG	--------------------------------------------------------------------------------
2019-12-26 02:50:55,641	debuglog.py	280	DEBUG	Proccessing Time	0:00:01.000734
2019-12-26 02:50:55,641	debuglog.py	281	DEBUG	Terminated the __main__.sample
2019-12-26 02:50:55,641	debuglog.py	282	DEBUG	================================================================================
```

### Logging for time at any timing.

When create a instance by the `get_measurer` as set a measurer start time.

```python
import debuglog
measurer = debuglog.get_measurer()
print(measurer.start)
```
```
2019-12-26 04:04:43.786672
```

Can get the final record time by `end` property but, initially the same the start time. It because record is the only one.

```python
print(measurer.end)
```
```
2019-12-26 04:04:43.786672
```

Add the time records, when called `record_split()`.

```python
measurer.record_split()
print(measurer.end)
```
```
2019-12-26 04:04:44.786745
```

Can executes `record_split()` is any number as long as memory-size allow.
And, can get records by `get_splittime()` or `get_laptime()`.
`get_splittime()` is delta time from start time, `get_laptime()` is delta time from previous record.

```python
for _ in range(10):
    time.sleep(0.1)
    measurer.record_split()
```
```python
for split in measurer.get_splittime():
    print(split)
```
```
Splittime(event='0', time=datetime.timedelta(microseconds=100413))
Splittime(event='1', time=datetime.timedelta(microseconds=200731))
Splittime(event='2', time=datetime.timedelta(microseconds=300978))
Splittime(event='3', time=datetime.timedelta(microseconds=401584))
Splittime(event='4', time=datetime.timedelta(microseconds=502032))
Splittime(event='5', time=datetime.timedelta(microseconds=602433))
Splittime(event='6', time=datetime.timedelta(microseconds=702726))
Splittime(event='7', time=datetime.timedelta(microseconds=803317))
Splittime(event='8', time=datetime.timedelta(microseconds=903703))
Splittime(event='9', time=datetime.timedelta(seconds=1, microseconds=4957))
```
```python
for lap in measurer.get_laptime():
    print(lap)
```
```
Laptime(event='0', time=datetime.timedelta(microseconds=100413))
Laptime(event='1', time=datetime.timedelta(microseconds=100318))
Laptime(event='2', time=datetime.timedelta(microseconds=100247))
Laptime(event='3', time=datetime.timedelta(microseconds=100606))
Laptime(event='4', time=datetime.timedelta(microseconds=100448))
Laptime(event='5', time=datetime.timedelta(microseconds=100401))
Laptime(event='6', time=datetime.timedelta(microseconds=100293))
Laptime(event='7', time=datetime.timedelta(microseconds=100591))
Laptime(event='8', time=datetime.timedelta(microseconds=100386))
Laptime(event='9', time=datetime.timedelta(microseconds=101254))
```

### Logging for times of function and method.

Decorate the function want to record with `debuglog.time_record(measurer_name)`
but, be careful will recorded is becomes another instance when different is the specifies`measurer_name`.

```python
import time
import debuglog

@debuglog.time_record("sample")
def sample():
    time.sleep(1)
```

Then will recorded with debug-level is start timing and terminate timing, when called the function.

```python
sample()
sample()
measurer = debuglog.get_measurer("sample")
print(measurer.start)
print(measurer.end)
for split in measurer.get_splittime():
    print(split)
```
```
2019-12-26 05:00:50.684892
2019-12-26 05:00:52.685775
Splittime(event='sample_start', time=datetime.timedelta(0))
Splittime(event='sample_end', time=datetime.timedelta(seconds=1, microseconds=642))
Splittime(event='sample_start', time=datetime.timedelta(seconds=1, microseconds=642))
Splittime(event='sample_end', time=datetime.timedelta(seconds=2, microseconds=883))
```

Then will logged with debug-level is start timing, terminate timing and processing time, when called the function.

### Create csv file of records.

Create "./log/xxx.csv" when called `to_csv()` method.
"xxx" is replace the measurer name property.

```python
measurer.to_csv()
```
```
.
└log
    └sample.csv
```
```csv
Event,Time,SplitTime,LapTime
Start,2019-12-26 05:21:44.051794,-,-
sample_start,2019-12-26 05:21:44.051794,0:00:00,0:00:00
sample_end,2019-12-26 05:21:45.052078,0:00:01.000284,0:00:01.000284
sample_start,2019-12-26 05:21:45.052078,0:00:01.000284,0:00:00
sample_end,2019-12-26 05:21:46.052876,0:00:02.001082,0:00:01.000798
```
