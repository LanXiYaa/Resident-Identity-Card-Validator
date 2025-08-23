import datetime
import json
import os
import sys
import re

def get_resource_path(relative_path):
    """
    获取资源的绝对路径
    """
    try:
        # 打包后的资源路径
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境的资源路径
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

def load_region_codes():
    """
    加载地区代码字典，支持多种文件格式和路径
    """
    # 尝试多种可能的文件路径和格式
    possible_files = [
        'region_codes.json',
        'region_codes.txt',
        'data/region_codes.json',
        'data/region_codes.txt'
    ]
    
    region_dict = {}
    
    for file_name in possible_files:
        file_path = get_resource_path(file_name)
        if os.path.exists(file_path):
            print(f"找到地区代码文件: {file_path}")
            try:
                if file_name.endswith('.json'):
                    # 读取JSON格式文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        region_dict = json.load(f)
                else:
                    # 读取文本格式文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 尝试解析文本格式的地区代码
                    if 'REGION_CODE_DICT' in content:
                        # 使用正则表达式提取字典内容
                        pattern = r"REGION_CODE_DICT\s*=\s*\{([^}]+)\}"
                        match = re.search(pattern, content, re.DOTALL)
                        
                        if match:
                            dict_content = "{" + match.group(1) + "}"
                            # 逐行解析键值对
                            lines = dict_content.split('\n')
                            for line in lines:
                                line = line.strip()
                                if not line or line in ['{', '}', ',']:
                                    continue
                                
                                # 提取键和值
                                if ':' in line:
                                    key, value = line.split(':', 1)
                                    key = key.strip().strip("'\"")
                                    value = value.strip().strip(",'\"")
                                    region_dict[key] = value
                
                print(f"成功加载 {len(region_dict)} 个地区代码")
                return region_dict
                
            except Exception as e:
                print(f"解析文件 {file_path} 时出错: {e}")
                continue
    
    print("警告: 未找到有效的地区代码文件")
    # 返回一个空的示例字典，避免程序崩溃
    return {
        '110000': '北京市',
        '110100': '北京市市辖区',
        '110101': '北京市东城区',
        '120000': '天津市',
        '310000': '上海市',
        '440000': '广东省'
    }

def get_region_name(region_code, region_dict):
    """根据地区代码获取地区名称"""
    # 尝试精确匹配
    if region_code in region_dict:
        return region_dict[region_code]
    
    # 尝试前4位匹配（市级）
    if region_code[:4] + '00' in region_dict:
        return region_dict[region_code[:4] + '00'] + "（具体区县未知）"
    
    # 尝试前2位匹配（省级）
    if region_code[:2] + '0000' in region_dict:
        return region_dict[region_code[:2] + '0000'] + "（具体市县未知）"
    
    return f"未知地区（代码: {region_code}）"

def validate_birthdate(date_str):
    """验证出生日期是否有效"""
    try:
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        
        current_year = datetime.datetime.now().year
        
        # 检查日期是否合理
        if year < 1900 or year > current_year:
            return False, f"年份超出范围 (1900-{current_year})"
        
        if month < 1 or month > 12:
            return False, "月份无效 (1-12)"
        
        # 检查日期是否有效
        if day < 1 or day > 31:
            return False, "日期无效 (1-31)"
        
        # 检查具体月份的天数
        if month in [4, 6, 9, 11] and day > 30:
            return False, f"{month}月最多30天"
        
        # 检查闰年二月
        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                if day > 29:
                    return False, f"{year}年是闰年，2月最多29天"
            else:
                if day > 28:
                    return False, f"{year}年不是闰年，2月最多28天"
        
        # 尝试创建日期对象，如果日期无效会抛出异常
        datetime.datetime(year, month, day)
        return True, f"{year}年{month:02d}月{day:02d}日"
        
    except ValueError as e:
        return False, f"无效的日期: {str(e)}"

def get_gender(gender_code):
    """根据性别代码获取性别"""
    try:
        return "男" if int(gender_code) % 2 == 1 else "女"
    except ValueError:
        return "未知"

def calculate_check_digit(first_17):
    """根据前17位计算校验码"""
    if len(first_17) != 17 or not first_17.isdigit():
        return "输入无效"
    
    # 加权因子
    factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    # 校验码对应表
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    total = sum(int(first_17[i]) * factors[i] for i in range(17))
    return check_codes[total % 11]

def get_zodiac(year):
    """根据年份获取生肖"""
    zodiacs = ["猴", "鸡", "狗", "猪", "鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊"]
    return zodiacs[year % 12]

def get_constellation(month, day):
    """根据月日获取星座"""
    if (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "水瓶座"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "双鱼座"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "白羊座"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "金牛座"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 21):
        return "双子座"
    elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
        return "巨蟹座"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "狮子座"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "处女座"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 23):
        return "天秤座"
    elif (month == 10 and day >= 24) or (month == 11 and day <= 22):
        return "天蝎座"
    elif (month == 11 and day >= 23) or (month == 12 and day <= 21):
        return "射手座"
    else:
        return "摩羯座"

def validate_id_card(id_card, region_dict):
    """验证身份证号码"""
    id_card = id_card.upper().strip()
    
    if len(id_card) != 18:
        return False, "身份证号码长度不正确（必须是18位）"
    
    # 检查前17位是否为数字
    if not id_card[:17].isdigit():
        return False, "前17位必须为数字"
    
    # 检查校验码（第18位可以是数字或X）
    if not (id_card[17].isdigit() or id_card[17] == 'X'):
        return False, "第18位必须是数字或X"
    
    # 检查校验码
    calculated_check = calculate_check_digit(id_card[:17])
    if calculated_check != id_card[17]:
        return False, f"校验码错误，应为'{calculated_check}'"
    
    # 检查地区代码是否有效
    region_code = id_card[:6]
    if region_code not in region_dict:
        return False, f"无效的地区代码: {region_code}"
    
    # 检查出生日期是否有效
    birthdate_valid, birthdate_info = validate_birthdate(id_card[6:14])
    if not birthdate_valid:
        return False, f"无效的出生日期: {birthdate_info}"
    
    return True, "身份证号码有效"

def display_id_info(id_card, region_dict):
    """显示身份证详细信息"""
    print("\n" + "="*50)
    print("身份证详细信息")
    print("="*50)
    
    region_code = id_card[:6]
    region_name = get_region_name(region_code, region_dict)
    print(f"📍 居住地: {region_name}")
    
    birthdate_valid, birthdate_info = validate_birthdate(id_card[6:14])
    if birthdate_valid:
        print(f"🎂 出生日期: {birthdate_info}")
        
        # 提取年月日
        year = int(id_card[6:10])
        month = int(id_card[10:12])
        day = int(id_card[12:14])
        
        # 计算生肖和星座
        zodiac = get_zodiac(year)
        constellation = get_constellation(month, day)
        
        print(f"🐉 生肖: {zodiac}")
        print(f"✨ 星座: {constellation}")
    else:
        print(f"❌ 出生日期: {birthdate_info}")
    
    gender = get_gender(id_card[16])
    print(f"👤 性别: {gender}")
    
    print(f"🔢 顺序号: {id_card[14:17]}")
    print(f"✅ 校验码: {id_card[17]}")
    
    # 计算年龄
    if birthdate_valid:
        birth_year = int(id_card[6:10])
        current_year = datetime.datetime.now().year
        age = current_year - birth_year
        print(f"📅 年龄: 约{age}岁")
    
    print("="*50)

def main():
    """主函数"""
    print("🚀 身份证号码检测器")
    print("📋 功能: 验证身份证号码、提取信息、计算校验码")
    
    # 加载地区代码
    region_dict = load_region_codes()
    
    while True:
        print("\n" + "="*50)
        print("请选择操作:")
        print("1. 📋 验证完整身份证号码")
        print("2. 🧮 根据前17位计算校验码")
        print("3. 📊 批量验证身份证号码")
        print("4. ❌ 退出程序")
        print("="*50)
        
        choice = input("请输入选项 (1/2/3/4): ").strip()
        
        if choice == '1':
            id_card = input("请输入18位身份证号码: ").strip()
            
            if len(id_card) != 18:
                print("❌ 错误: 身份证号码必须是18位")
                continue
            
            is_valid, message = validate_id_card(id_card, region_dict)
            if is_valid:
                print(f"✅ {message}")
                display_id_info(id_card, region_dict)
            else:
                print(f"❌ {message}")
        
        elif choice == '2':
            first_17 = input("请输入身份证前17位: ").strip()
            
            if len(first_17) != 17 or not first_17.isdigit():
                print("❌ 错误: 前17位必须是17位数字")
                continue
            
            check_digit = calculate_check_digit(first_17)
            print(f"✅ 身份证第18位: {check_digit}")
            
            full_id = first_17 + check_digit
            print(f"📝 完整身份证号码: {full_id}")
            
            # 显示地区信息
            region_code = first_17[:6]
            region_name = get_region_name(region_code, region_dict)
            print(f"📍 居住地: {region_name}")
            
            # 显示生肖和星座（如果日期有效）
            try:
                year = int(first_17[6:10])
                month = int(first_17[10:12])
                day = int(first_17[12:14])
                
                # 验证日期是否有效
                is_valid, _ = validate_birthdate(first_17[6:14])
                if is_valid:
                    zodiac = get_zodiac(year)
                    constellation = get_constellation(month, day)
                    print(f"🐉 生肖: {zodiac}")
                    print(f"✨ 星座: {constellation}")
            except:
                pass  # 如果日期无效，跳过生肖和星座显示
        
        elif choice == '3':
            print("📊 批量验证模式")
            print("请输入多个身份证号码（每行一个），输入空行结束:")
            
            ids = []
            while True:
                line = input().strip()
                if not line:
                    break
                ids.append(line)
            
            valid_count = 0
            for i, id_card in enumerate(ids, 1):
                is_valid, message = validate_id_card(id_card, region_dict)
                status = "✅" if is_valid else "❌"
                print(f"{i}. {status} {id_card}: {message}")
                if is_valid:
                    valid_count += 1
            
            print(f"\n📈 验证结果: {valid_count}个有效 / {len(ids)}个总数")
        
        elif choice == '4':
            print("👋 感谢使用，再见！")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序发生错误: {e}")
        input("按回车键退出...")