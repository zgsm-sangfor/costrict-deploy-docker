## 模型配置自动化脚本

通过配置json文件，和运行python脚本调用接口，快速帮你设置模型。

你需要准备python3环境,并安装 `requests` `pyyaml` 库

```bash
pip install requests pyyaml
```

将[./higress.py](./higress.py) 保存到你的电脑上(任意可以访问higress的主机都可以)，并参考[model.json.example](./model.json.example) 在同级目录创建 `model.json`，其内容含义如下：

```js
{
    "server": "http://192.168.79.136:38001", // higress地址,请替换
    "username": "admin", // 用户名
    "password": "123", // 密码
    "models": [
        {
            "id": "claude",  // id,唯一，且只能包含小写字母或数字和'-'符号，且'-'符号不能再开头和结尾。
            "name": "Claude", // 模型名称，你在插件端看到的名字
            "realName": "claude-opus-4-6", // 目标模型名称，真实调用接口的模型名称，默认和name相同
            "key": "sk-****", // 密钥
            "url": "https://model-server.com/v1", // url,到/v1结束
            "context": 280000, // 最大上下文
            "maxToken": 32000, // 最大输出
            "desc": "这是描述", // 描述，任意字符串
            "suportImg": false // 是否支持图片
        },
        // 第二个模型。
        {
            "id": "claude2",
            "name": "Claude2",
            "realName": "claude-opus-4-6",
            "key": "sk-****",
            "url": "https://model-server.com/v1",
            "context": 280000,
            "maxToken": 32000,
            "desc": "这是描述",
            "suportImg": false
        }
    ]
}

```

> 请注意，你可以复制 [model.json.example](./model.json.example) 的内容并修改，文档中含义解释的json包含了js注释，不是标准的json,直接使用将会出错。

运行，脚本将会自动新增或者更新模型(主要根据id和name区分是否为同一个模型)

```bash
python higress.py
```