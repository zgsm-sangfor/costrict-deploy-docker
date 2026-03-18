#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理旧版本脚本
扫描 costrict/ 下每个包的每个平台目录，
只保留最新版本，删除旧版本目录，并更新 platform.json。

策略：
- 以文件系统实际存在的版本目录为准（目录名格式为 X.Y.Z），
  找出版本号最大的目录作为最新版本，删除其余旧版本目录。
- 同步更新 platform.json，使其只保留最新版本信息。
- 清理最新版本目录中的 .backup 文件。
- 同时处理 codebase-indexer/config 目录下的 vX.Y.Z 版本子目录。
"""

import os
import sys
import json
import shutil
import argparse


def parse_version(version_str: str):
    """
    解析版本字符串（如 '0.6.4' 或 'v0.6.4'），返回 (major, minor, micro) 元组。
    支持两位或三位版本号，如 '1.0.250802' -> (1, 0, 250802)。
    失败则返回 None。
    """
    s = version_str.strip().lstrip('v')
    parts = s.split('.')
    try:
        nums = [int(p) for p in parts]
        # 统一填充到三位
        while len(nums) < 3:
            nums.append(0)
        return tuple(nums[:3])
    except ValueError:
        return None


def find_latest_version(versions: list) -> str:
    """
    从版本字符串列表中找出最新版本（按语义版本比较）。
    """
    if not versions:
        return None
    best = versions[0]
    best_tuple = parse_version(best)
    for v in versions[1:]:
        t = parse_version(v)
        if t is not None and (best_tuple is None or t > best_tuple):
            best = v
            best_tuple = t
    return best


def scan_version_dirs(parent_dir: str, with_v_prefix: bool = False) -> list:
    """
    扫描 parent_dir 下所有版本格式子目录，返回版本字符串列表。
    
    with_v_prefix=False: 匹配 X.Y.Z 格式（如 '1.1.31'）
    with_v_prefix=True:  匹配 vX.Y.Z 格式（如 'v0.6.4'）
    """
    result = []
    if not os.path.isdir(parent_dir):
        return result
    for entry in os.listdir(parent_dir):
        full_path = os.path.join(parent_dir, entry)
        if not os.path.isdir(full_path):
            continue
        if with_v_prefix:
            if entry.startswith('v') and parse_version(entry) is not None:
                result.append(entry)
        else:
            if not entry.startswith('v') and parse_version(entry) is not None:
                result.append(entry)
    return result


def cleanup_platform_dir(platform_dir: str, dry_run: bool = False) -> dict:
    """
    清理单个平台目录（如 darwin/amd64），只保留最新版本。
    
    策略：
    1. 扫描文件系统中所有 X.Y.Z 格式版本目录
    2. 找出最新版本（版本号最大的）
    3. 删除其余旧版本目录
    4. 清理最新版本目录中的 .backup 文件
    5. 更新 platform.json，只保留最新版本
    
    返回：{'kept': version_str, 'deleted': [version_str, ...]} 或 None
    """
    platform_json_path = os.path.join(platform_dir, 'platform.json')

    # 扫描文件系统中存在的版本目录
    fs_versions = scan_version_dirs(platform_dir, with_v_prefix=False)

    if not fs_versions:
        print(f"  [SKIP] 未发现版本目录: {platform_dir}")
        return None

    # 以文件系统版本为基准，找出最新版本
    latest_str = find_latest_version(fs_versions)
    old_versions = [v for v in fs_versions if v != latest_str]

    print(f"  [INFO] 最新版本: {latest_str}，旧版本: {old_versions}")

    # 删除旧版本目录
    deleted = []
    for old_ver in old_versions:
        old_dir = os.path.join(platform_dir, old_ver)
        if os.path.isdir(old_dir):
            if dry_run:
                print(f"  [DRY-RUN] 将删除目录: {old_dir}")
            else:
                print(f"  [DELETE] 删除目录: {old_dir}")
                shutil.rmtree(old_dir)
            deleted.append(old_ver)

    # 清理最新版本目录中的 .backup 文件
    latest_dir = os.path.join(platform_dir, latest_str)
    if os.path.isdir(latest_dir):
        for fname in os.listdir(latest_dir):
            if fname.endswith('.backup'):
                backup_file = os.path.join(latest_dir, fname)
                if dry_run:
                    print(f"  [DRY-RUN] 将删除 .backup 文件: {backup_file}")
                else:
                    print(f"  [DELETE] 删除 .backup 文件: {backup_file}")
                    os.remove(backup_file)

    # 更新 platform.json
    if os.path.isfile(platform_json_path):
        with open(platform_json_path, 'r', encoding='utf-8') as f:
            platform_data = json.load(f)

        # 找出最新版本在 platform.json 中对应的数据（用于重建 versions 字段）
        latest_tuple = parse_version(latest_str)
        latest_version_data = None

        # 先从现有 versions 列表中查找
        for v in platform_data.get('versions', []):
            vid = v.get('versionId', {})
            t = (vid.get('major', 0), vid.get('minor', 0), vid.get('micro', 0))
            if t == latest_tuple:
                latest_version_data = v
                break

        # 如果 versions 中找不到（说明 platform.json 已经是最新的），尝试从 newest 取
        if latest_version_data is None:
            newest = platform_data.get('newest')
            if newest:
                vid = newest.get('versionId', {})
                t = (vid.get('major', 0), vid.get('minor', 0), vid.get('micro', 0))
                if t == latest_tuple:
                    latest_version_data = newest

        if latest_version_data is not None:
            new_platform_data = dict(platform_data)
            new_platform_data['newest'] = latest_version_data
            new_platform_data['versions'] = [latest_version_data]

            if dry_run:
                print(f"  [DRY-RUN] 将更新 platform.json: {platform_json_path}")
            else:
                print(f"  [UPDATE] 更新 platform.json: {platform_json_path}")
                with open(platform_json_path, 'w', encoding='utf-8') as f:
                    json.dump(new_platform_data, f, indent=2, ensure_ascii=False)
                    f.write('\n')
        else:
            print(f"  [WARN] 无法在 platform.json 中找到最新版本 {latest_str} 的数据，跳过更新")
    else:
        print(f"  [WARN] platform.json 不存在: {platform_json_path}")

    return {'kept': latest_str, 'deleted': deleted}


def cleanup_config_versions(config_dir: str, dry_run: bool = False) -> dict:
    """
    清理 config 目录下的版本文件夹（格式为 vX.Y.Z），只保留最新版本。
    同时保留直接在 config 目录下（非版本子目录）的文件。
    
    返回：{'kept': version_str, 'deleted': [version_str, ...]}
    """
    if not os.path.isdir(config_dir):
        return None

    # 找出所有版本子目录（名称匹配 vX.Y.Z 格式）
    version_dirs = scan_version_dirs(config_dir, with_v_prefix=True)

    if not version_dirs:
        print(f"  [SKIP] config 目录中没有版本子目录: {config_dir}")
        return None

    latest_str = find_latest_version(version_dirs)
    old_versions = [v for v in version_dirs if v != latest_str]

    print(f"  [CONFIG] 最新版本: {latest_str}，旧版本: {old_versions}")

    deleted = []
    for old_ver in old_versions:
        old_dir = os.path.join(config_dir, old_ver)
        if os.path.isdir(old_dir):
            if dry_run:
                print(f"  [DRY-RUN] 将删除 config 版本目录: {old_dir}")
            else:
                print(f"  [DELETE] 删除 config 版本目录: {old_dir}")
                shutil.rmtree(old_dir)
            deleted.append(old_ver)

    return {'kept': latest_str, 'deleted': deleted}


def cleanup_package(package_dir: str, dry_run: bool = False):
    """
    清理单个包目录下的所有平台版本。
    """
    package_name = os.path.basename(package_dir)
    print(f"\n{'='*60}")
    print(f"处理包: {package_name}")
    print(f"{'='*60}")

    if not os.path.isdir(package_dir):
        print(f"  [ERROR] 包目录不存在: {package_dir}")
        return

    # 处理 config 目录（如果存在），如 codebase-indexer/config
    config_dir = os.path.join(package_dir, 'config')
    if os.path.isdir(config_dir):
        print(f"\n  处理 config 目录: {config_dir}")
        cleanup_config_versions(config_dir, dry_run=dry_run)

    # 遍历 OS 目录（darwin, linux, windows 等）
    for entry in sorted(os.listdir(package_dir)):
        if entry == 'config':
            continue
        os_dir = os.path.join(package_dir, entry)
        if not os.path.isdir(os_dir):
            continue

        # 遍历 arch 目录（amd64, arm64 等）
        for arch_name in sorted(os.listdir(os_dir)):
            arch_dir = os.path.join(os_dir, arch_name)
            if not os.path.isdir(arch_dir):
                continue

            print(f"\n  平台: {entry}/{arch_name}")
            cleanup_platform_dir(arch_dir, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(
        description='清理旧版本文件，只保留每个包每个平台的最新版本。'
    )
    parser.add_argument(
        'base_dir',
        nargs='?',
        default='./costrict',
        help='顶级目录路径，默认为 ./costrict'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='模拟运行，只显示将要执行的操作，不实际删除文件'
    )
    parser.add_argument(
        '--package',
        type=str,
        default=None,
        help='只处理指定的包（包名），不指定则处理所有包'
    )
    args = parser.parse_args()

    base_dir = args.base_dir
    dry_run = args.dry_run

    if not os.path.isdir(base_dir):
        print(f"[ERROR] 目录不存在: {base_dir}")
        sys.exit(1)

    if dry_run:
        print("[DRY-RUN 模式] 仅模拟，不实际删除文件\n")

    # 读取 packages.json 获取包列表
    packages_json = os.path.join(base_dir, 'packages.json')
    if os.path.isfile(packages_json):
        with open(packages_json, 'r', encoding='utf-8') as f:
            packages_data = json.load(f)
        packages = packages_data.get('packages', [])
    else:
        # 自动扫描目录
        packages = [
            entry for entry in os.listdir(base_dir)
            if os.path.isdir(os.path.join(base_dir, entry))
        ]

    if args.package:
        if args.package not in packages:
            print(f"[ERROR] 包 '{args.package}' 不在包列表中: {packages}")
            sys.exit(1)
        packages = [args.package]

    print(f"将处理的包: {packages}")

    for pkg in packages:
        pkg_dir = os.path.join(base_dir, pkg)
        if os.path.isdir(pkg_dir):
            cleanup_package(pkg_dir, dry_run=dry_run)
        else:
            print(f"\n[WARN] 包目录不存在，跳过: {pkg_dir}")

    print(f"\n{'='*60}")
    print("清理完成！")
    if dry_run:
        print("（DRY-RUN 模式，未实际删除任何文件）")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
