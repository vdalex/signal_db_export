# Signal Messenger DB to JSON

Python application to export messages from Signal Messenger DB to JSON. 

Based on signal-export application https://github.com/carderne/signal-export

```bash
python .\signaldb_to_json.py --help
Usage: signaldb_to_json.py [OPTIONS]

  Read the Signal directory and output chats as json.

Options:
  --source PATH     Path to Signal source database
  --chats TEXT      Comma-separated chat names to include
  --ts INTEGER      UNIX timestamp
  -l, --list-chats  List available chats and exit
  --help            Show this message and exit
```

Output example:

```bash
python .\signaldb_to_json.py --ts 1687790388197
Signal database exported as output/json_data_1687790388197.json
```

export_config.json format:

```json
{
    "version": "1.0",
    "groups": "'group_1', 'group_2', 'group_3'"
}
```

Output file format:

```json
{
    "groups_name_id": [
        {"group_name_1": "group_id_1"}, 
        {"group_name_2": "group_id_2"}],
    "messsages": [{message_obj_1}, {message_obj_2}]
}
```

Messge object example:

```json
"messsages": [
    {
        "timestamp": 1688677422493,
        "attachments": [],
        "id": "some_id",
        "conversationId": "some_id",
        "readStatus": 0,
        "received_at": 1688493072558,
        "received_at_ms": 1688677422991,
        "seenStatus": 2,
        "sent_at": 1688677422493,
        "serverGuid": "some_id",
        "serverTimestamp": 1688677422896,
        "sourceDevice": 3,
        "sourceUuid": "some_id",
        "type": "incoming",
        "unidentifiedDeliveryReceived": true,
        "schemaVersion": 10,
        "body": "some_message",
        "bodyRanges": [],
        "contact": [],
        "decrypted_at": 1688677423657,
        "errors": [],
        "flags": 0,
        "hasAttachments": 0,
        "isViewOnce": false,
        "mentionsMe": false,
        "preview": [],
        "requiredProtocolVersion": 6,
        "supportedVersionAtReceive": 7
    }]
```

## pysqlcipher3 library

https://github.com/rigglemania/pysqlcipher3

Follow README to build and install

## Some pysqlcipher3 build and import related issues on Windows

1. Illegal escape sequence (https://stackoverflow.com/questions/65345077/unable-to-build-sqlcipher3-on-windows)

```python
error C2017: illegal escape sequence
```

Simplest solution for VC compiler is to change pysqlcipher3 `setup.py`

From

```python
def quote_argument(arg):
    quote = '"' if sys.platform != 'win32' else '\\"'
    return quote + arg + quote
```
To

```python
def quote_argument(arg):
    quote = '"' if sys.platform != 'win32' else '"'
    return quote + arg + quote
```

2. The library names of OpenSSL have changed in version 1.1.0 (from libeay32.lib to libcrypto.lib) (https://stackoverflow.com/questions/65345077/unable-to-build-sqlcipher3-on-windows)

Simplest solution is to change pysqlcipher3 `setup.py`

From

```python
ext.extra_link_args.append("libeay32.lib")
```

To
```python
ext.extra_link_args.append("libcrypto.lib")
```

3. In some installation with 64 bit OpenSSL and 64 bit Python when you try to import


```python
from pysqlcipher3 import dbapi2 as sqlcipher
```
Error message:
```
  File "C:\Python39-64\lib\site-packages\pysqlcipher3-1.2.0-py3.9-win-amd64.egg\pysqlcipher3\dbapi2.py", line 33, in <module>
    from pysqlcipher3._sqlite3 import *
ImportError: DLL load failed while importing _sqlite3: The specified module could not be found.
```

it looks lile PATH issue or previous 32 bit OpenSSL installation issue (Issue doesn't exists on 32 bit python). 

Quick and "dirty" solution - copy `libcrypto-3-x64.dll` from openssl-win64 to `<your_python_path>\lib\site-packages\pysqlcipher3-1.2.0-py3.9-win-amd64.egg\pysqlcipher3\`
