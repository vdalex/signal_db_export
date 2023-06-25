# Signal Messenger DB to JSON

Python application to export messages from Signal Messenger DB to JSON. 

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
    "messsages": [{}, {}]
}
```