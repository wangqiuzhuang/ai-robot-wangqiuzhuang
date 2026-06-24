#!/usr/bin/env python3
"""
Week 9: URDF 模型检查工具
==========================
验证 URDF 文件的语法正确性，检查必需的 <link> 和 <joint> 元素。
支持命令行和 Python 导入两种使用方式。

运行方式:
  python3 check_urdf.py robot.urdf
"""

import sys
import xml.etree.ElementTree as ET


def check_urdf(filepath: str) -> dict:
    """检查 URDF 文件的基本结构"""
    result = {"valid": False, "errors": [], "warnings": [], "info": {}}

    try:
        tree = ET.parse(filepath)
    except ET.ParseError as e:
        result["errors"].append(f"XML 解析错误: {e}")
        return result
    except FileNotFoundError:
        result["errors"].append(f"文件不存在: {filepath}")
        return result

    root = tree.getroot()
    if root.tag != "robot":
        result["errors"].append(f"根元素应为 <robot>，实际为 <{root.tag}>")
        return result

    robot_name = root.get("name", "unnamed")
    result["info"]["robot_name"] = robot_name

    # 统计 link 和 joint
    links = root.findall("link")
    joints = root.findall("joint")
    result["info"]["num_links"] = len(links)
    result["info"]["num_joints"] = len(joints)

    # 检查每个 link 是否有 inertial
    for link in links:
        name = link.get("name", "unnamed")
        if link.find("inertial") is None:
            result["warnings"].append(
                f"<link name='{name}'> 缺少 <inertial>，物理仿真将忽略此连杆"
            )

    # 检查 joint 的 parent/child 引用
    link_names = {l.get("name") for l in links}
    for joint in joints:
        name = joint.get("name", "unnamed")
        parent = joint.find("parent")
        child = joint.find("child")
        if parent is not None:
            parent_link = parent.get("link")
            if parent_link not in link_names:
                result["errors"].append(
                    f"<joint name='{name}'> 的 parent link '{parent_link}' 不存在"
                )
        else:
            result["errors"].append(f"<joint name='{name}'> 缺少 <parent>")
        if child is not None:
            child_link = child.get("link")
            if child_link not in link_names:
                result["errors"].append(
                    f"<joint name='{name}'> 的 child link '{child_link}' 不存在"
                )
        else:
            result["errors"].append(f"<joint name='{name}'> 缺少 <child>")

    result["valid"] = len(result["errors"]) == 0
    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python3 check_urdf.py <urdf文件>")
        print("示例: python3 check_urdf.py ../week8/my_robot.urdf")
        sys.exit(1)

    filepath = sys.argv[1]
    print(f"🔍 检查 URDF: {filepath}")
    result = check_urdf(filepath)

    print(f"\n机器人: {result['info'].get('robot_name', '?')}")
    print(f"Links:  {result['info'].get('num_links', 0)}")
    print(f"Joints: {result['info'].get('num_joints', 0)}")

    if result["warnings"]:
        print(f"\n⚠️  警告 ({len(result['warnings'])}):")
        for w in result["warnings"]:
            print(f"  - {w}")

    if result["errors"]:
        print(f"\n❌ 错误 ({len(result['errors'])}):")
        for e in result["errors"]:
            print(f"  - {e}")
    else:
        print("\n✅ URDF 语法检查通过!")


if __name__ == "__main__":
    main()
