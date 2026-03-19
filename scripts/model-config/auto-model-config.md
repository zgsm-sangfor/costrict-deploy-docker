## Model Configuration Automation Script

Configure models quickly by editing a JSON file and running a Python script to call the API.

You need a Python 3 environment with the `requests` and `pyyaml` libraries installed:

```bash
pip install requests pyyaml
```

Save [./higress.py](./higress.py) to your computer(Any host that can access higress), then refer to [model.json.example](./model.json.example) to create a `model.json` file in the same directory. The fields are described below:

```js
{
    "server": "http://192.168.79.136:38001", // Higress address, replace with your own
    "username": "admin",                     // Username
    "password": "123",                       // Password
    "models": [
        {
            "id": "claude",          // Unique ID; only lowercase letters, digits, and '-' are allowed; '-' cannot appear at the start or end.
            "name": "Claude",        // Display name shown in the plugin UI
            "realName": "claude-opus-4-6", // Actual model name used when calling the API; defaults to the same as "name"
            "key": "sk-****",        // API key / secret
            "url": "https://model-server.com/v1", // Base URL, ending at /v1
            "context": 280000,       // Maximum context length
            "maxToken": 32000,       // Maximum output tokens
            "desc": "This is a description", // Description, any string
            "suportImg": false       // Whether image input is supported
        },
        // Second model
        {
            "id": "claude2",
            "name": "Claude2",
            "realName": "claude-opus-4-6",
            "key": "sk-****",
            "url": "https://model-server.com/v1",
            "context": 280000,
            "maxToken": 32000,
            "desc": "This is a description",
            "suportImg": false
        }
    ]
}
```

> **Note:** You can copy the content of [model.json.example](./model.json.example) and modify it. The JSON shown above includes JS-style comments for explanation purposes — it is **not** valid JSON. Using it directly will cause errors.

Run the script. It will automatically add or update models (models are identified by their `id` and `name` fields):

```bash
python higress.py
```
