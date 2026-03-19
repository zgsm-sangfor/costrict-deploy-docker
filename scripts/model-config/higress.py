import os
import re
import requests
import time
import json
import yaml



SERVER_ADDR = None
USERNAME = None
PASSWORD = None


def login() -> str:
    """
    登录接口，POST 请求 /session/login，
    从响应头 Set-Cookie 中提取 _hi_sess cookie 值。
    返回 cookie 字符串，供后续请求使用。
    """
    url = f"{SERVER_ADDR}/session/login"
    payload = {"username": USERNAME, "password": PASSWORD}
    resp = requests.post(url, json=payload)
    resp.raise_for_status()

    # 从响应的 cookies 中获取 _hi_sess
    hi_sess = resp.cookies.get("_hi_sess")
    if not hi_sess:
        raise RuntimeError(
            f"登录成功但未在响应中找到 _hi_sess cookie，"
            f"响应头: {dict(resp.headers)}"
        )

    print(f"[登录成功] _hi_sess={hi_sess}")
    return hi_sess


def get_ai_routes(cookie: str) -> dict:
    """
    获取 AI 路由列表，GET 请求 /v1/ai/routes，
    需要携带登录后获取的 cookie。
    返回并打印 JSON 响应体。
    """
    ts = int(time.time() * 1000)
    url = f"{SERVER_ADDR}/v1/ai/routes?ts={ts}"
    headers = {"Cookie": f"_hi_sess={cookie}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    data = resp.json()
    print("[AI Routes 响应]")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def get_ai_providers(cookie: str) -> dict:
    """
    获取 AI Provider 列表，GET 请求 /v1/ai/providers。
    需要携带登录后获取的 cookie。
    返回并打印 JSON 响应体。
    """
    ts = int(time.time() * 1000)
    url = f"{SERVER_ADDR}/v1/ai/providers?ts={ts}"
    headers = {"Cookie": f"_hi_sess={cookie}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    data = resp.json()
    print("[AI Providers 响应]")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def update_ai_provider(
    cookie: str,
    name: str,
    token: str,
    openai_custom_url: str,
) -> dict:
    """
    更新已有的 AI Provider，PUT 请求 /v1/ai/providers/{name}。
    需要携带登录后获取的 cookie。

    参数:
        cookie: 登录后获取的 _hi_sess cookie 值
        name: provider 名称（即 id）
        token: API token 字符串
        openai_custom_url: 自定义的 OpenAI 兼容接口地址
    返回并打印 JSON 响应体。
    """
    _validate_name(name)

    url = f"{SERVER_ADDR}/v1/ai/providers/{name}"
    headers = {"Cookie": f"_hi_sess={cookie}"}
    payload = {
        "type": "openai",
        "name": name,
        "tokens": [token],
        "version": 0,
        "protocol": "openai/v1",
        "tokenFailoverConfig": {
            "enabled": False
        },
        "rawConfigs": {
            "openaiExtraCustomUrls": [],
            "openaiCustomUrl": openai_custom_url
        }
    }

    resp = requests.put(url, json=payload, headers=headers)
    resp.raise_for_status()

    data = resp.json()
    print("[更新 AI Provider 响应]")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def create_ai_provider(
    cookie: str,
    name: str,
    token: str,
    openai_custom_url: str,
) -> dict:
    """
    创建 AI Provider，POST 请求 /v1/ai/providers。
    需要携带登录后获取的 cookie。

    参数:
        cookie: 登录后获取的 _hi_sess cookie 值
        name: provider 名称，只能包含小写字母、数字和 -，且 - 不能在开头或结尾
        token: API token 字符串
        openai_custom_url: 自定义的 OpenAI 兼容接口地址
    返回并打印 JSON 响应体。
    """
    _validate_name(name)

    url = f"{SERVER_ADDR}/v1/ai/providers"
    headers = {"Cookie": f"_hi_sess={cookie}"}
    payload = {
        "type": "openai",
        "name": name,
        "tokens": [token],
        "version": 0,
        "protocol": "openai/v1",
        "tokenFailoverConfig": {
            "enabled": False
        },
        "rawConfigs": {
            "openaiExtraCustomUrls": [],
            "openaiCustomUrl": openai_custom_url
        }
    }

    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()

    data = resp.json()
    print("[创建 AI Provider 响应]")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def _validate_name(name: str) -> None:
    """校验 name：只能包含小写字母、数字和 -，且 - 不能在开头或结尾。"""
    if not re.match(r'^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$', name):
        raise ValueError(
            f"name 不合法: '{name}'，"
            f"只能包含小写字母、数字和 -，且 - 不能在开头或结尾"
        )


def create_ai_route(
    cookie: str,
    name: str,
    provider: str,
    model_mapping_target: str,
    model_match_value: str,
) -> dict:
    """
    创建 AI 路由，POST 请求 /v1/ai/routes。
    需要携带登录后获取的 cookie。

    参数:
        cookie: 登录后获取的 _hi_sess cookie 值
        name: 路由名称，只能包含小写字母、数字和 -，且 - 不能在开头或结尾
        provider: 上游 provider 名称
        model_mapping_target: 模型映射的目标值（对应 modelMapping 中 "*" 映射的值）
        model_match_value: 模型匹配谓词的值（对应 modelPredicates[0].matchValue）
    返回并打印 JSON 响应体。
    """
    _validate_name(name)

    url = f"{SERVER_ADDR}/v1/ai/routes"
    headers = {"Cookie": f"_hi_sess={cookie}"}
    payload = {
        "name": name,
        "domains": [],
        "pathPredicate": {
            "matchType": "PRE",
            "matchValue": "/",
            "ignoreCase": ["ignore"],
            "caseSensitive": False
        },
        "headerPredicates": [],
        "urlParamPredicates": [],
        "fallbackConfig": {
            "enabled": False
        },
        "authConfig": {
            "enabled": False
        },
        "upstreams": [
            {
                "provider": provider,
                "weight": 100,
                "modelMapping": {
                    "*": model_mapping_target
                }
            }
        ],
        "modelPredicates": [
            {
                "matchType": "EQUAL",
                "matchValue": model_match_value
            }
        ]
    }

    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()

    data = resp.json()
    print("[创建 AI Route 响应]")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def update_ai_route(
    cookie: str,
    name: str,
    provider: str,
    model_mapping_target: str,
    model_match_value: str,
) -> dict:
    """
    更新已有的 AI 路由，PUT 请求 /v1/ai/routes/{name}。
    需要携带登录后获取的 cookie。

    参数:
        cookie: 登录后获取的 _hi_sess cookie 值
        name: 路由名称（即 id）
        provider: 上游 provider 名称
        model_mapping_target: 模型映射的目标值（对应 modelMapping 中 "*" 映射的值）
        model_match_value: 模型匹配谓词的值（对应 modelPredicates[0].matchValue）
    返回并打印 JSON 响应体。
    """
    _validate_name(name)

    url = f"{SERVER_ADDR}/v1/ai/routes/{name}"
    headers = {"Cookie": f"_hi_sess={cookie}"}
    payload = {
        "name": name,
        "domains": [],
        "pathPredicate": {
            "matchType": "PRE",
            "matchValue": "/",
            "ignoreCase": ["ignore"],
            "caseSensitive": False
        },
        "headerPredicates": [],
        "urlParamPredicates": [],
        "fallbackConfig": {
            "enabled": False
        },
        "authConfig": {
            "enabled": False
        },
        "upstreams": [
            {
                "provider": provider,
                "weight": 100,
                "modelMapping": {
                    "*": model_mapping_target
                }
            }
        ],
        "modelPredicates": [
            {
                "matchType": "EQUAL",
                "matchValue": model_match_value
            }
        ]
    }

    resp = requests.put(url, json=payload, headers=headers)
    resp.raise_for_status()

    data = resp.json()
    print("[更新 AI Route 响应]")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def get_ai_quota_plugin(cookie: str) -> dict:
    """
    获取 ai-quota 插件实例配置，GET 请求 /v1/global/plugin-instances/ai-quota。
    需要携带登录后获取的 cookie。
    返回并打印 JSON 响应体。
    """
    ts = int(time.time() * 1000)
    url = f"{SERVER_ADDR}/v1/global/plugin-instances/ai-quota?ts={ts}"
    headers = {"Cookie": f"_hi_sess={cookie}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    data = resp.json()
    print("[AI Quota Plugin 响应]")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def add_ai_quota_model(
    cookie: str,
    name: str,
    context_window: int,
    max_tokens: int,
    description: str = "",
    supports_images: bool = False,
) -> dict:
    """
    向 ai-quota 插件的 providers[0].models 中追加或更新一个模型，
    然后 PUT 请求 /v1/global/plugin-instances/ai-quota 提交更新。

    流程:
        1. GET 获取当前 ai-quota 插件配置
        2. 解析 rawConfigurations (YAML 格式)
        3. 在 providers[0].models 中追加新模型（name 已存在则更新）
        4. 重新序列化 rawConfigurations 并 PUT 提交

    参数:
        cookie: 登录后获取的 _hi_sess cookie 值
        name: 模型名称
        context_window: 上下文窗口大小
        max_tokens: 最大 token 数
        description: 模型描述，默认为空字符串
        supports_images: 是否支持图片，默认 False
    返回并打印 JSON 响应体。
    """
    # 1. 获取当前配置
    current = get_ai_quota_plugin(cookie)
    plugin_data = current["data"]
    raw_config_str = plugin_data["rawConfigurations"]

    # 2. 解析 rawConfigurations YAML
    raw_config = yaml.safe_load(raw_config_str)
    providers = raw_config.get("providers", [])
    if not providers:
        raise RuntimeError("当前配置中没有 providers，无法追加模型")

    models = providers[0].get("models", [])

    # 3. 构造新模型对象
    new_model = {
        "contextWindow": context_window,
        "description": description,
        "maxTokens": max_tokens,
        "name": name,
        "supportsComputerUse": True,
        "supportsImages": supports_images,
        "supportsPromptCache": False,
        "supportsReasoningBudget": False,
    }

    # 4. 检查 name 是否已存在，存在则更新，不存在则追加
    existing_index = None
    for i, m in enumerate(models):
        if m["name"] == name:
            existing_index = i
            break

    if existing_index is not None:
        print(f"[AI Quota] 模型 '{name}' 已存在，执行更新")
        models[existing_index] = new_model
    else:
        print(f"[AI Quota] 模型 '{name}' 不存在，执行追加")
        models.append(new_model)

    providers[0]["models"] = models

    # 4. 重新序列化 rawConfigurations
    raw_config["providers"] = providers
    new_raw_config_str = yaml.dump(
        raw_config, default_flow_style=False, allow_unicode=True
    )

    # 构造 PUT 请求体（仅包含需要的顶层字段）
    put_payload = {
        "version": plugin_data["version"],
        "scope": plugin_data["scope"],
        "target": plugin_data["target"],
        "targets": plugin_data["targets"],
        "pluginName": plugin_data["pluginName"],
        "pluginVersion": plugin_data["pluginVersion"],
        "internal": plugin_data["internal"],
        "enabled": plugin_data["enabled"],
        "rawConfigurations": new_raw_config_str,
    }

    url = f"{SERVER_ADDR}/v1/global/plugin-instances/ai-quota"
    headers = {"Cookie": f"_hi_sess={cookie}"}
    resp = requests.put(url, json=put_payload, headers=headers)
    resp.raise_for_status()

    data = resp.json()
    print("[更新 AI Quota Plugin 响应]")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


MODEL_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.json")


def _load_config(model_json_path: str = MODEL_JSON_PATH) -> dict:
    """
    从 model.json 读取配置文件。
    配置文件为 JSON 对象，包含以下顶层属性:
        server   -> 服务器地址
        username -> 登录用户名
        password -> 登录密码
        models   -> 模型信息数组

    兼容旧格式：如果传入的是数组，则包装为 {"models": [...]}，
    此时 server/username/password 必须通过其他方式提供（会抛出异常）。

    返回配置字典。
    """
    with open(model_json_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 兼容旧格式：如果是数组，包装为对象
    if isinstance(config, list):
        config = {"models": config}

    # 兼容：如果 models 是单个对象而非数组，则包装为数组
    if isinstance(config.get("models"), dict):
        config["models"] = [config["models"]]

    return config


def setup_from_model_json(model_json_path: str = MODEL_JSON_PATH) -> None:
    """
    从 model.json 读取配置，遍历每个模型依次完成:
        1. 登录
        2. 获取已有 providers 和 routes 列表
        3. 对每个模型:
           a. 创建或更新 AI Provider（id 作为 name）
           b. 创建或更新 AI 路由（id 作为 name，name 作为 model_match_value，
              realName 作为 model_mapping_target，realName 为空则等于 name）
           c. 向 ai-quota 插件追加或更新模型配置

    model.json 为对象格式，顶层属性:
        server   -> 服务器地址（SERVER_ADDR）
        username -> 登录用户名
        password -> 登录密码
        models   -> 模型信息数组，每个元素字段映射:
            id       -> provider name / route name（需校验合法性）
            name     -> route model_match_value / quota model name
            realName -> route model_mapping_target（为空则取 name）
            key      -> provider token
            url      -> provider openaiCustomUrl
            context  -> quota model contextWindow
            maxToken -> quota model maxTokens
            desc     -> quota model description（默认空字符串）
            suportImg-> quota model supportsImages（默认 False）
    """
    # 读取配置
    config = _load_config(model_json_path)

    # 提取服务器配置
    global SERVER_ADDR, USERNAME, PASSWORD
    SERVER_ADDR = config["server"]
    USERNAME = config["username"]
    PASSWORD = config["password"]

    models_list = config.get("models", [])

    if not models_list:
        print("[警告] model.json 中 models 为空数组，无需处理")
        return

    # 1. 登录
    cookie = login()

    # 2. 获取已有 providers 列表，提取已有 provider id 集合
    print(f"\n{'='*50}")
    print("[预检] 获取已有 AI Providers 列表")
    print(f"{'='*50}")
    providers_resp = get_ai_providers(cookie)
    existing_provider_ids = set()
    if providers_resp.get("data"):
        for p in providers_resp["data"]:
            pid = p.get("rawConfigs", {}).get("id") or p.get("name")
            if pid:
                existing_provider_ids.add(pid)
    print(f"[预检] 已有 Provider IDs: {existing_provider_ids}")

    # 3. 获取已有路由列表，提取已有 route name 集合
    print(f"\n{'='*50}")
    print("[预检] 获取已有 AI Routes 列表")
    print(f"{'='*50}")
    routes_resp = get_ai_routes(cookie)
    existing_route_names = set()
    if routes_resp.get("data"):
        for r in routes_resp["data"]:
            rname = r.get("name")
            if rname:
                existing_route_names.add(rname)
    print(f"[预检] 已有 Route Names: {existing_route_names}")

    # 4. 遍历每个模型进行处理
    for idx, model in enumerate(models_list):
        model_id = model["id"]
        model_name = model["name"]
        real_name = model.get("realName") or model_name  # 为空则等于 name
        key = model["key"]
        model_url = model["url"]
        context_window = model.get("context", 200000)
        max_tokens = model.get("maxToken", 32000)
        description = model.get("desc", "")
        supports_images = model.get("suportImg", False)

        # 校验 id 合法性
        _validate_name(model_id)

        print(f"\n{'#'*50}")
        print(f"# 处理模型 [{idx + 1}/{len(models_list)}]: {model_id} ({model_name})")
        print(f"{'#'*50}")

        # 步骤 a: 创建或更新 AI Provider
        print(f"\n{'='*50}")
        if model_id in existing_provider_ids:
            print(f"[步骤 1] 更新 AI Provider: {model_id}（已存在）")
            print(f"{'='*50}")
            update_ai_provider(
                cookie=cookie,
                name=model_id,
                token=key,
                openai_custom_url=model_url,
            )
        else:
            print(f"[步骤 1] 创建 AI Provider: {model_id}（新增）")
            print(f"{'='*50}")
            create_ai_provider(
                cookie=cookie,
                name=model_id,
                token=key,
                openai_custom_url=model_url,
            )
            existing_provider_ids.add(model_id)

        # 步骤 b: 创建或更新 AI 路由
        print(f"\n{'='*50}")
        if model_id in existing_route_names:
            print(f"[步骤 2] 更新 AI 路由: {model_id}（已存在）")
            print(f"{'='*50}")
            update_ai_route(
                cookie=cookie,
                name=model_id,
                provider=model_id,
                model_mapping_target=real_name,
                model_match_value=model_name,
            )
        else:
            print(f"[步骤 2] 创建 AI 路由: {model_id}（新增）")
            print(f"{'='*50}")
            create_ai_route(
                cookie=cookie,
                name=model_id,
                provider=model_id,
                model_mapping_target=real_name,
                model_match_value=model_name,
            )
            existing_route_names.add(model_id)

        # 步骤 c: 向 ai-quota 插件追加或更新模型
        print(f"\n{'='*50}")
        print(f"[步骤 3] 追加/更新 AI Quota 模型: {model_name}")
        print(f"{'='*50}")
        add_ai_quota_model(
            cookie=cookie,
            name=model_name,
            context_window=context_window,
            max_tokens=max_tokens,
            description=description,
            supports_images=supports_images,
        )

    print(f"\n{'='*50}")
    print(f"[完成] 所有 {len(models_list)} 个模型配置已成功应用!")
    print(f"{'='*50}")


if __name__ == "__main__":
    setup_from_model_json()
