"""
取证分析策略 - 针对不同类型检材的快速分析策略
支持: 安卓/iOS手机、Windows电脑、服务器
目标: 短时间内准确分析，建立跨检材关联能力
"""
import os
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class EvidenceType(Enum):
    """检材类型"""
    ANDROID_PHONE = "android_phone"
    IOS_PHONE = "ios_phone"
    WINDOWS_PC = "windows_pc"
    LINUX_SERVER = "linux_server"
    WINDOWS_SERVER = "windows_server"
    UNKNOWN = "unknown"

@dataclass
class AnalysisStrategy:
    """分析策略"""
    evidence_type: EvidenceType
    name: str
    description: str
    priority_steps: List[Dict[str, Any]]
    tools: List[str]
    time_estimate: int  # 分钟
    key_artifacts: List[str]
    cross_check_points: List[str]

class ForensicAnalysisEngine:
    """取证分析引擎"""
    
    def __init__(self):
        self.strategies = self._init_strategies()
    
    def _init_strategies(self) -> Dict[EvidenceType, AnalysisStrategy]:
        """初始化分析策略"""
        return {
            EvidenceType.ANDROID_PHONE: self._android_strategy(),
            EvidenceType.IOS_PHONE: self._ios_strategy(),
            EvidenceType.WINDOWS_PC: self._windows_pc_strategy(),
            EvidenceType.LINUX_SERVER: self._linux_server_strategy(),
            EvidenceType.WINDOWS_SERVER: self._windows_server_strategy(),
        }
    
    def _android_strategy(self) -> AnalysisStrategy:
        """安卓手机取证策略"""
        return AnalysisStrategy(
            evidence_type=EvidenceType.ANDROID_PHONE,
            name="安卓手机取证分析",
            description="针对安卓手机E01镜像的快速取证分析",
            priority_steps=[
                {
                    "step": 1,
                    "name": "镜像挂载与识别",
                    "commands": [
                        "file evidence.E01",
                        "ewfinfo evidence.E01",
                        "mount -t ewf evidence.E01 /mnt/ewf"
                    ],
                    "time": 2,
                    "目标": "确认镜像类型、大小、设备信息"
                },
                {
                    "step": 2,
                    "name": "系统信息提取",
                    "commands": [
                        "cat /mnt/ewf/system/build.prop",
                        "cat /mnt/ewf/default.prop",
                        "getprop"
                    ],
                    "time": 3,
                    "目标": "Android版本、设备型号、IMEI、手机号"
                },
                {
                    "step": 3,
                    "name": "用户数据提取",
                    "commands": [
                        "ls -la /mnt/ewf/data/data/",
                        "ls -la /mnt/ewf/data/user/0/",
                        "find /mnt/ewf -name '*.db' -type f"
                    ],
                    "time": 5,
                    "目标": "应用列表、用户数据目录"
                },
                {
                    "step": 4,
                    "name": "通讯录与短信",
                    "commands": [
                        "sqlite3 /mnt/ewf/data/data/com.android.providers.contacts/databases/contacts2.db",
                        "sqlite3 /mnt/ewf/data/data/com.android.providers.telephony/databases/mmssms.db"
                    ],
                    "time": 5,
                    "目标": "联系人、通话记录、短信"
                },
                {
                    "step": 5,
                    "name": "微信/QQ数据",
                    "commands": [
                        "find /mnt/ewf -path '*/com.tencent.mm*' -type f",
                        "find /mnt/ewf -path '*/com.tencent.mobileqq*' -type f",
                        "ls -la /mnt/ewf/data/data/com.tencent.mm/MicroMsg/"
                    ],
                    "time": 10,
                    "目标": "聊天记录、联系人、文件传输"
                },
                {
                    "step": 6,
                    "name": "浏览器历史",
                    "commands": [
                        "sqlite3 /mnt/ewf/data/data/com.android.browser/databases/browser2.db",
                        "find /mnt/ewf -name 'History' -path '*chrome*'"
                    ],
                    "time": 5,
                    "目标": "浏览记录、书签、下载记录"
                },
                {
                    "step": 7,
                    "name": "WiFi与位置信息",
                    "commands": [
                        "cat /mnt/ewf/data/misc/wifi/WifiConfigStore.xml",
                        "find /mnt/ewf -name '*.kml' -o -name '*.gpx'"
                    ],
                    "time": 3,
                    "目标": "WiFi连接历史、GPS轨迹"
                },
                {
                    "step": 8,
                    "name": "删除数据恢复",
                    "commands": [
                        "strings /mnt/ewf/data/data/*/databases/*.db | grep -i 'delete'",
                        "photorec /mnt/ewf evidence_recovery"
                    ],
                    "time": 15,
                    "目标": "恢复已删除的短信、聊天记录、文件"
                }
            ],
            tools=["sqlite3", "strings", "file", "ewfinfo", "photorec", "autopsy"],
            time_estimate=50,
            key_artifacts=[
                "IMEI/IMSI", "手机号", "通讯录", "短信", "通话记录",
                "微信聊天记录", "QQ聊天记录", "浏览器历史", "WiFi密码",
                "GPS位置", "APP数据", "照片EXIF"
            ],
            cross_check_points=[
                "IMEI与运营商记录关联",
                "WiFi MAC地址与位置关联",
                "微信/QQ账号与服务器日志关联",
                "手机号与支付记录关联"
            ]
        )
    
    def _ios_strategy(self) -> AnalysisStrategy:
        """iOS手机取证策略"""
        return AnalysisStrategy(
            evidence_type=EvidenceType.IOS_PHONE,
            name="iOS手机取证分析",
            description="针对iPhone/iPad E01镜像的快速取证分析",
            priority_steps=[
                {
                    "step": 1,
                    "name": "镜像挂载与识别",
                    "commands": [
                        "file evidence.E01",
                        "ewfinfo evidence.E01",
                        "mount -t ewf evidence.E01 /mnt/ewf"
                    ],
                    "time": 2,
                    "目标": "确认镜像类型、iOS设备信息"
                },
                {
                    "step": 2,
                    "name": "系统信息提取",
                    "commands": [
                        "cat /mnt/ewf/System/Library/CoreServices/SystemVersion.plist",
                        "plutil -p /mnt/ewf/var/mobile/Library/Preferences/com.apple.springboard.plist"
                    ],
                    "time": 3,
                    "目标": "iOS版本、设备型号、序列号、UDID"
                },
                {
                    "step": 3,
                    "name": "备份数据分析",
                    "commands": [
                        "ls -la /mnt/ewf/var/mobile/Library/Preferences/",
                        "find /mnt/ewf -name 'Manifest.db' -o -name 'Manifest.plist'",
                        "sqlite3 /mnt/ewf/Manifest.db"
                    ],
                    "time": 5,
                    "目标": "备份文件列表、应用数据"
                },
                {
                    "step": 4,
                    "name": "通讯录与短信",
                    "commands": [
                        "sqlite3 /mnt/ewf/var/mobile/Library/AddressBook/AddressBook.sqlitedb",
                        "sqlite3 /mnt/ewf/var/mobile/Library/SMS/sms.db"
                    ],
                    "time": 5,
                    "目标": "联系人、短信、iMessage"
                },
                {
                    "step": 5,
                    "name": "微信/QQ数据",
                    "commands": [
                        "find /mnt/ewf -path '*WeChat*' -type f",
                        "find /mnt/ewf -path '*QQ*' -type f",
                        "ls -la /mnt/ewf/var/mobile/Containers/Data/Application/"
                    ],
                    "time": 10,
                    "目标": "微信/QQ聊天记录、文件"
                },
                {
                    "step": 6,
                    "name": "Safari历史",
                    "commands": [
                        "sqlite3 /mnt/ewf/var/mobile/Library/Safari/History.db",
                        "plutil -p /mnt/ewf/var/mobile/Library/Safari/Bookmarks.plist"
                    ],
                    "time": 5,
                    "目标": "浏览记录、书签"
                },
                {
                    "step": 7,
                    "name": "照片与位置",
                    "commands": [
                        "find /mnt/ewf -name '*.jpg' -o -name '*.heic'",
                        "exiftool /mnt/ewf/var/mobile/Media/DCIM/*",
                        "sqlite3 /mnt/ewf/var/mobile/Library/Photos/Photos.sqlite"
                    ],
                    "time": 10,
                    "目标": "照片、EXIF信息、位置数据"
                },
                {
                    "step": 8,
                    "name": "Keychain提取",
                    "commands": [
                        "find /mnt/ewf -name 'keychain*' -type f",
                        "python3 ios_keychain_decrypt.py /mnt/ewf"
                    ],
                    "time": 10,
                    "目标": "WiFi密码、应用密码、证书"
                }
            ],
            tools=["sqlite3", "plutil", "exiftool", "strings", "ewfinfo"],
            time_estimate=50,
            key_artifacts=[
                "UDID", "序列号", "Apple ID", "通讯录", "短信",
                "iMessage", "微信聊天", "QQ聊天", "Safari历史",
                "照片EXIF", "Keychain密码", "WiFi密码"
            ],
            cross_check_points=[
                "Apple ID与iCloud记录关联",
                "UDID与iTunes备份关联",
                "手机号与运营商记录关联",
                "WiFi密码与位置关联"
            ]
        )
    
    def _windows_pc_strategy(self) -> AnalysisStrategy:
        """Windows电脑取证策略"""
        return AnalysisStrategy(
            evidence_type=EvidenceType.WINDOWS_PC,
            name="Windows电脑取证分析",
            description="针对Windows电脑E01镜像的快速取证分析",
            priority_steps=[
                {
                    "step": 1,
                    "name": "镜像挂载与识别",
                    "commands": [
                        "file evidence.E01",
                        "ewfinfo evidence.E01",
                        "mmls evidence.E01",
                        "mount -t ewf evidence.E01 /mnt/ewf"
                    ],
                    "time": 2,
                    "目标": "确认镜像类型、分区结构"
                },
                {
                    "step": 2,
                    "name": "系统信息提取",
                    "commands": [
                        "regdump /mnt/ewf/Windows/System32/config/SYSTEM",
                        "regdump /mnt/ewf/Windows/System32/config/SOFTWARE",
                        "cat /mnt/ewf/Windows/System32/config/SAM"
                    ],
                    "time": 5,
                    "目标": "计算机名、Windows版本、安装时间、用户列表"
                },
                {
                    "step": 3,
                    "name": "用户账户分析",
                    "commands": [
                        "samdump2 /mnt/ewf/Windows/System32/config/SAM",
                        "reglookup /mnt/ewf/Windows/System32/config/SAM",
                        "ls -la /mnt/ewf/Users/"
                    ],
                    "time": 5,
                    "目标": "用户名、SID、密码哈希、登录时间"
                },
                {
                    "step": 4,
                    "name": "最近活动分析",
                    "commands": [
                        "fls -r -m / /mnt/ewf > filelist.txt",
                        "mactime -b filelist.txt > timeline.csv",
                        "find /mnt/ewf -name '*.lnk' -type f"
                    ],
                    "time": 10,
                    "目标": "文件时间线、最近打开文件、快捷方式"
                },
                {
                    "step": 5,
                    "name": "浏览器历史",
                    "commands": [
                        "sqlite3 /mnt/ewf/Users/*/AppData/Local/Google/Chrome/User Data/Default/History",
                        "sqlite3 /mnt/ewf/Users/*/AppData/Local/Microsoft/Edge/User Data/Default/History",
                        "find /mnt/ewf -name 'places.sqlite' -path '*Firefox*'"
                    ],
                    "time": 10,
                    "目标": "浏览历史、下载记录、Cookie、书签"
                },
                {
                    "step": 6,
                    "name": "注册表分析",
                    "commands": [
                        "reglookup /mnt/ewf/Windows/System32/config/SYSTEM",
                        "reglookup /mnt/ewf/Windows/System32/config/SOFTWARE",
                        "python3 reg_parser.py /mnt/ewf/Windows/System32/config/"
                    ],
                    "time": 10,
                    "目标": "USB设备历史、网络配置、自启动项、MRU"
                },
                {
                    "step": 7,
                    "name": "日志分析",
                    "commands": [
                        "find /mnt/ewf -name '*.evtx' -type f",
                        "python3 evtx_parser.py /mnt/ewf/Windows/System32/winevt/Logs/",
                        "cat /mnt/ewf/Windows/Prefetch/*.pf"
                    ],
                    "time": 10,
                    "目标": "事件日志、Prefetch、程序执行记录"
                },
                {
                    "step": 8,
                    "name": "邮件与文档",
                    "commands": [
                        "find /mnt/ewf -name '*.pst' -o -name '*.ost'",
                        "find /mnt/ewf -name '*.docx' -o -name '*.xlsx' -o -name '*.pdf'",
                        "exiftool /mnt/ewf/Users/*/Documents/*"
                    ],
                    "time": 10,
                    "目标": "Outlook邮件、Office文档、PDF元数据"
                },
                {
                    "step": 9,
                    "name": "删除数据恢复",
                    "commands": [
                        "tsk_recover /mnt/ewf recovery/",
                        "photorec /mnt/ewf evidence_recovery"
                    ],
                    "time": 15,
                    "目标": "恢复已删除文件"
                }
            ],
            tools=["regdump", "reglookup", "samdump2", "sqlite3", "fls", "icat", 
                   "mactime", "exiftool", "strings", "tsk_recover", "photorec"],
            time_estimate=80,
            key_artifacts=[
                "计算机名", "用户账户", "密码哈希", "登录时间",
                "浏览历史", "下载记录", "USB设备", "WiFi连接",
                "最近文件", "邮件", "文档", "注册表",
                "事件日志", "Prefetch", "删除文件"
            ],
            cross_check_points=[
                "用户账户与域控日志关联",
                "USB设备序列号与设备台账关联",
                "WiFi MAC与位置关联",
                "浏览器Cookie与网站登录关联",
                "邮件与网络流量关联"
            ]
        )
    
    def _linux_server_strategy(self) -> AnalysisStrategy:
        """Linux服务器取证策略"""
        return AnalysisStrategy(
            evidence_type=EvidenceType.LINUX_SERVER,
            name="Linux服务器取证分析",
            description="针对Linux服务器E01镜像的快速取证分析",
            priority_steps=[
                {
                    "step": 1,
                    "name": "镜像挂载与识别",
                    "commands": [
                        "file evidence.E01",
                        "ewfinfo evidence.E01",
                        "mmls evidence.E01",
                        "mount -t ewf evidence.E01 /mnt/ewf"
                    ],
                    "time": 2,
                    "目标": "确认镜像类型、分区结构、文件系统"
                },
                {
                    "step": 2,
                    "name": "系统信息提取",
                    "commands": [
                        "cat /mnt/ewf/etc/os-release",
                        "cat /mnt/ewf/etc/hostname",
                        "cat /mnt/ewf/etc/passwd",
                        "cat /mnt/ewf/etc/shadow"
                    ],
                    "time": 3,
                    "目标": "发行版、主机名、用户列表、密码哈希"
                },
                {
                    "step": 3,
                    "name": "登录与认证分析",
                    "commands": [
                        "cat /mnt/ewf/var/log/auth.log",
                        "cat /mnt/ewf/var/log/secure",
                        "lastlog -f /mnt/ewf/var/log/lastlog",
                        "cat /mnt/ewf/var/log/wtmp"
                    ],
                    "time": 5,
                    "目标": "登录历史、SSH登录、sudo使用、失败尝试"
                },
                {
                    "step": 4,
                    "name": "Web服务分析",
                    "commands": [
                        "ls -la /mnt/ewf/var/log/nginx/",
                        "ls -la /mnt/ewf/var/log/apache2/",
                        "cat /mnt/ewf/var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn",
                        "find /mnt/ewf/var/www -name '*.php' -mtime -7"
                    ],
                    "time": 10,
                    "目标": "Web访问日志、可疑IP、最近修改的Web文件"
                },
                {
                    "step": 5,
                    "name": "数据库分析",
                    "commands": [
                        "find /mnt/ewf -name '*.sql' -o -name '*.db' -o -name '*.sqlite'",
                        "cat /mnt/ewf/var/log/mysql/error.log",
                        "ls -la /mnt/ewf/var/lib/mysql/"
                    ],
                    "time": 10,
                    "目标": "数据库文件、数据库日志、数据导出"
                },
                {
                    "step": 6,
                    "name": "进程与服务",
                    "commands": [
                        "cat /mnt/ewf/var/log/syslog",
                        "cat /mnt/ewf/var/log/messages",
                        "find /mnt/ewf/etc/init.d/ -type f",
                        "find /mnt/ewf/etc/systemd/system/ -type f"
                    ],
                    "time": 5,
                    "目标": "系统日志、自启动服务、异常进程"
                },
                {
                    "step": 7,
                    "name": "网络配置分析",
                    "commands": [
                        "cat /mnt/ewf/etc/network/interfaces",
                        "cat /mnt/ewf/etc/resolv.conf",
                        "cat /mnt/ewf/etc/hosts",
                        "find /mnt/ewf -name '*.pcap' -o -name '*.cap'"
                    ],
                    "time": 5,
                    "目标": "网络配置、DNS设置、抓包文件"
                },
                {
                    "step": 8,
                    "name": "计划任务与后门",
                    "commands": [
                        "cat /mnt/ewf/var/spool/cron/crontabs/*",
                        "find /mnt/ewf -name '.bash_history' -type f",
                        "find /mnt/ewf -perm -4000 -type f",
                        "find /mnt/ewf -name '.*' -path '*/bin/*'"
                    ],
                    "time": 10,
                    "目标": "定时任务、命令历史、SUID文件、隐藏后门"
                },
                {
                    "step": 9,
                    "name": "Webshell检测",
                    "commands": [
                        "find /mnt/ewf/var/www -name '*.php' -exec grep -l 'eval\\|system\\|exec\\|passthru' {} \\;",
                        "find /mnt/ewf/var/www -name '*.jsp' -exec grep -l 'Runtime\\|ProcessBuilder' {} \\;",
                        "find /mnt/ewf -name '*.asp' -o -name '*.aspx'"
                    ],
                    "time": 10,
                    "目标": "Webshell文件、可疑脚本"
                }
            ],
            tools=["file", "strings", "grep", "find", "awk", "lastlog", 
                   "cat", "ls", "mmls", "ewfinfo"],
            time_estimate=60,
            key_artifacts=[
                "主机名", "用户账户", "密码哈希", "SSH登录",
                "Web访问日志", "数据库", "系统日志", "网络配置",
                "定时任务", "命令历史", "Webshell", "后门"
            ],
            cross_check_points=[
                "SSH登录IP与Web访问IP关联",
                "Webshell与Web日志时间关联",
                "数据库操作与Web请求关联",
                "命令历史与入侵时间关联"
            ]
        )
    
    def _windows_server_strategy(self) -> AnalysisStrategy:
        """Windows服务器取证策略"""
        return AnalysisStrategy(
            evidence_type=EvidenceType.WINDOWS_SERVER,
            name="Windows服务器取证分析",
            description="针对Windows服务器E01镜像的快速取证分析",
            priority_steps=[
                {
                    "step": 1,
                    "name": "镜像挂载与识别",
                    "commands": [
                        "file evidence.E01",
                        "ewfinfo evidence.E01",
                        "mmls evidence.E01",
                        "mount -t ewf evidence.E01 /mnt/ewf"
                    ],
                    "time": 2,
                    "目标": "确认镜像类型、分区结构"
                },
                {
                    "step": 2,
                    "name": "系统信息提取",
                    "commands": [
                        "regdump /mnt/ewf/Windows/System32/config/SYSTEM",
                        "regdump /mnt/ewf/Windows/System32/config/SOFTWARE",
                        "systeminfo /mnt/ewf"
                    ],
                    "time": 5,
                    "目标": "服务器角色、Windows版本、补丁状态"
                },
                {
                    "step": 3,
                    "name": "用户与权限分析",
                    "commands": [
                        "samdump2 /mnt/ewf/Windows/System32/config/SAM",
                        "cat /mnt/ewf/Windows/System32/config/SECURITY",
                        "net user /domain"
                    ],
                    "time": 5,
                    "目标": "本地用户、域用户、管理员组、权限提升"
                },
                {
                    "step": 4,
                    "name": "事件日志分析",
                    "commands": [
                        "find /mnt/ewf -name '*.evtx' -type f",
                        "python3 evtx_parser.py /mnt/ewf/Windows/System32/winevt/Logs/Security.evtx",
                        "python3 evtx_parser.py /mnt/ewf/Windows/System32/winevt/Logs/System.evtx"
                    ],
                    "time": 15,
                    "目标": "登录事件、权限变更、服务安装、计划任务"
                },
                {
                    "step": 5,
                    "name": "IIS日志分析",
                    "commands": [
                        "find /mnt/ewf -path '*LogFiles*W3SVC*' -name '*.log'",
                        "cat /mnt/ewf/inetpub/logs/LogFiles/W3SVC1/*.log | awk '{print $1}' | sort | uniq -c | sort -rn",
                        "find /mnt/ewf/inetpub -name '*.asp' -o -name '*.aspx'"
                    ],
                    "time": 10,
                    "目标": "Web访问日志、可疑请求、Webshell"
                },
                {
                    "step": 6,
                    "name": "服务与进程",
                    "commands": [
                        "reglookup /mnt/ewf/Windows/System32/config/SYSTEM",
                        "find /mnt/ewf -name '*.exe' -path '*Temp*' -mtime -7",
                        "find /mnt/ewf -name '*.dll' -path '*Temp*' -mtime -7"
                    ],
                    "time": 10,
                    "目标": "服务列表、可疑进程、恶意程序"
                },
                {
                    "step": 7,
                    "name": "网络连接分析",
                    "commands": [
                        "reglookup /mnt/ewf/Windows/System32/config/SYSTEM",
                        "find /mnt/ewf -name '*.pcap' -o -name '*.cap'",
                        "cat /mnt/ewf/Windows/System32/drivers/etc/hosts"
                    ],
                    "time": 5,
                    "目标": "网络配置、防火墙规则、抓包文件"
                },
                {
                    "step": 8,
                    "name": "计划任务与持久化",
                    "commands": [
                        "find /mnt/ewf/Windows/Tasks -type f",
                        "reglookup /mnt/ewf/Windows/System32/config/SOFTWARE",
                        "find /mnt/ewf -name 'RunOnce' -o -name 'Run'"
                    ],
                    "time": 10,
                    "目标": "计划任务、注册表自启动、持久化后门"
                },
                {
                    "step": 9,
                    "name": "数据库与文件",
                    "commands": [
                        "find /mnt/ewf -name '*.mdf' -o -name '*.ldf'",
                        "find /mnt/ewf -name '*.bak' -mtime -30",
                        "find /mnt/ewf -name '*.config' -path '*web*'"
                    ],
                    "time": 10,
                    "目标": "数据库文件、备份文件、配置文件"
                }
            ],
            tools=["regdump", "reglookup", "samdump2", "sqlite3", "fls", 
                   "icat", "mactime", "exiftool", "strings", "find"],
            time_estimate=75,
            key_artifacts=[
                "服务器角色", "用户账户", "密码哈希", "域信息",
                "事件日志", "IIS日志", "服务列表", "网络配置",
                "计划任务", "Webshell", "数据库", "备份文件"
            ],
            cross_check_points=[
                "事件日志与IIS日志时间关联",
                "用户登录与Web访问关联",
                "服务安装与恶意进程关联",
                "数据库操作与Web请求关联"
            ]
        )
    
    def detect_evidence_type(self, evidence_path: str) -> EvidenceType:
        """自动检测检材类型"""
        # 使用file命令检测
        import subprocess
        
        try:
            result = subprocess.run(
                ["file", evidence_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout.lower()
            
            # 检测Android
            if "android" in output or "ext4" in output:
                return EvidenceType.ANDROID_PHONE
            
            # 检测iOS
            if "hfs" in output or "iphone" in output or "ipad" in output:
                return EvidenceType.IOS_PHONE
            
            # 检测Windows
            if "ntfs" in output or "fat32" in output:
                # 进一步区分服务器和PC
                if "server" in output:
                    return EvidenceType.WINDOWS_SERVER
                return EvidenceType.WINDOWS_PC
            
            # 检测Linux
            if "ext4" in output or "ext3" in output or "xfs" in output:
                return EvidenceType.LINUX_SERVER
            
        except Exception as e:
            print(f"检测失败: {e}")
        
        return EvidenceType.UNKNOWN
    
    def get_strategy(self, evidence_type: EvidenceType) -> AnalysisStrategy:
        """获取分析策略"""
        return self.strategies.get(evidence_type)
    
    def generate_analysis_plan(self, evidence_path: str, 
                               question: str = None) -> Dict[str, Any]:
        """生成分析计划"""
        # 检测检材类型
        evidence_type = self.detect_evidence_type(evidence_path)
        
        # 获取策略
        strategy = self.get_strategy(evidence_type)
        
        if not strategy:
            return {
                "error": f"不支持的检材类型: {evidence_type}",
                "evidence_path": evidence_path
            }
        
        # 生成计划
        plan = {
            "evidence_path": evidence_path,
            "evidence_type": evidence_type.value,
            "strategy_name": strategy.name,
            "description": strategy.description,
            "total_time_estimate": strategy.time_estimate,
            "question": question,
            "steps": [],
            "tools": strategy.tools,
            "key_artifacts": strategy.key_artifacts,
            "cross_check_points": strategy.cross_check_points
        }
        
        for step in strategy.priority_steps:
            plan["steps"].append({
                "step": step["step"],
                "name": step["name"],
                "commands": step["commands"],
                "time_estimate": step["time"],
                "target": step["目标"]
            })
        
        return plan
    
    def generate_cross_analysis_plan(self, evidences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成跨检材分析计划"""
        plan = {
            "evidences": evidences,
            "cross_analysis_steps": [],
            "correlation_points": [],
            "timeline_merge_strategy": ""
        }
        
        # 提取所有检材的时间线
        plan["timeline_merge_strategy"] = """
        1. 从每个检材提取时间线
        2. 统一时间格式为UTC
        3. 按时间排序合并
        4. 标记每个事件的来源检材
        5. 识别跨检材的关联事件
        """
        
        # 关联分析点
        plan["correlation_points"] = [
            {
                "type": "IP关联",
                "description": "相同IP在不同检材中的活动",
                "method": "提取所有IP地址，找出重复出现的IP"
            },
            {
                "type": "账号关联",
                "description": "相同账号在不同系统中的使用",
                "method": "提取所有账号，找出跨系统使用的账号"
            },
            {
                "type": "时间关联",
                "description": "同一时间段内的异常活动",
                "method": "识别攻击时间窗口，分析各检材在该时间段的活动"
            },
            {
                "type": "文件关联",
                "description": "相同文件在不同检材中的存在",
                "method": "计算文件哈希，找出在多个检材中出现的文件"
            },
            {
                "type": "行为关联",
                "description": "攻击者行为模式",
                "method": "分析攻击者在不同系统中的操作手法"
            }
        ]
        
        return plan

def main():
    """主函数 - 演示策略生成"""
    engine = ForensicAnalysisEngine()
    
    print("=" * 60)
    print("取证分析策略引擎")
    print("=" * 60)
    
    # 示例：生成Windows PC分析计划
    plan = engine.generate_analysis_plan(
        evidence_path="evidence.E01",
        question="找出恶意软件和入侵痕迹"
    )
    
    print(f"\n检材类型: {plan['evidence_type']}")
    print(f"策略名称: {plan['strategy_name']}")
    print(f"预计时间: {plan['total_time_estimate']} 分钟")
    
    print("\n分析步骤:")
    for step in plan['steps']:
        print(f"  {step['step']}. {step['name']} ({step['time_estimate']}分钟)")
        print(f"     目标: {step['target']}")
    
    print("\n关键证据:")
    for artifact in plan['key_artifacts']:
        print(f"  - {artifact}")
    
    print("\n跨检材关联点:")
    for point in plan['cross_check_points']:
        print(f"  - {point}")

if __name__ == "__main__":
    main()
