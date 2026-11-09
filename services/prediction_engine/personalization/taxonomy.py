"""Product-owned two-level taxonomy v2; not an official statistical standard."""

from typing import Any

TAXONOMY_VERSION = "futureos-industry-v2.1"
INDUSTRIES: tuple[tuple[str, str, tuple[tuple[str, str, tuple[str, ...]], ...]], ...] = (
    (
        "technology",
        "互联网与信息技术",
        (
            ("software", "软件开发", ("technology", "workforce")),
            ("quality", "测试与质量", ("technology",)),
            ("data", "数据与分析", ("technology", "industry")),
        ),
    ),
    (
        "manufacturing",
        "制造业",
        (
            ("electronics", "电子制造", ("industry", "supply_chain")),
            ("automotive", "汽车制造", ("industry", "energy")),
            ("industrial", "工业设备", ("industry",)),
        ),
    ),
    (
        "healthcare",
        "医疗与健康",
        (
            ("clinical", "临床服务", ("health",)),
            ("medical_devices", "医疗器械", ("health", "industry")),
            ("health_services", "健康服务", ("health", "society")),
        ),
    ),
    (
        "education",
        "教育与研究",
        (
            ("school", "学校教育", ("education",)),
            ("adult_learning", "职业与成人教育", ("education", "workforce")),
            ("research", "科研", ("technology", "education")),
        ),
    ),
    (
        "finance",
        "金融服务",
        (
            ("banking", "银行服务", ("macro_finance",)),
            ("insurance", "保险服务", ("macro_finance", "policy")),
            ("investment", "投资服务", ("macro_finance",)),
        ),
    ),
    (
        "services",
        "生活与商业服务",
        (
            ("retail", "零售", ("consumption",)),
            ("logistics", "物流", ("supply_chain",)),
            ("hospitality", "文旅与住宿", ("consumption", "society")),
        ),
    ),
    (
        "energy",
        "能源",
        (
            ("power", "电力", ("energy",)),
            ("storage", "储能", ("energy", "industry")),
            ("renewables", "可再生能源", ("energy", "policy")),
        ),
    ),
    (
        "not_applicable",
        "暂不按职业分类（学生／退休等）",
        (
            ("student", "在校学习", ("education",)),
            ("retired", "退休", ("society",)),
            ("other", "暂不分类", ("society",)),
        ),
    ),
)

# v2 broad coverage, plus a user-specified fallback under each professional parent.
_EXTRA_CHILDREN = {
    "technology": (
        ("technology_product_management", "产品经理", ("technology", "workforce")),
        ("technology_ui_design", "UI设计师", ("technology", "workforce")),
        ("technology_detail_1", "人工智能算法与模型", ("technology", "workforce")),
        ("technology_detail_2", "AI 应用与智能体", ("technology", "workforce")),
        ("technology_detail_3", "企业软件与 SaaS", ("technology", "workforce")),
        ("technology_detail_4", "移动应用开发", ("technology", "workforce")),
        ("technology_detail_5", "前端与用户体验", ("technology", "workforce")),
        ("technology_detail_6", "后端与系统架构", ("technology", "workforce")),
        ("technology_detail_7", "游戏研发", ("technology", "workforce")),
        ("technology_detail_8", "网络安全", ("technology", "workforce")),
        ("technology_detail_9", "云计算与云原生", ("technology", "workforce")),
        ("technology_detail_10", "运维与 DevOps", ("technology", "workforce")),
        ("technology_detail_11", "数据工程与数据库", ("technology", "workforce")),
        ("technology_detail_12", "通信与电信", ("technology", "workforce")),
        ("technology_detail_13", "物联网与嵌入式", ("technology", "workforce")),
        ("technology_detail_14", "集成电路设计", ("technology", "workforce")),
        ("technology_detail_15", "互联网平台", ("technology", "workforce")),
        ("technology_detail_16", "数字内容与信息服务", ("technology", "workforce")),
        ("technology_detail_17", "IT 咨询与系统集成", ("technology", "workforce")),
        ("technology_detail_18", "数据标注与数据服务", ("technology", "workforce")),
    ),
    "manufacturing": (
        ("manufacturing_detail_1", "半导体与芯片制造", ("industry", "supply_chain")),
        ("manufacturing_detail_2", "机器人与自动化设备", ("industry", "supply_chain")),
        ("manufacturing_detail_3", "新能源汽车制造", ("industry", "supply_chain")),
        ("manufacturing_detail_4", "汽车零部件", ("industry", "supply_chain")),
        ("manufacturing_detail_5", "航空航天制造", ("industry", "supply_chain")),
        ("manufacturing_detail_6", "船舶与轨道交通装备", ("industry", "supply_chain")),
        ("manufacturing_detail_7", "电气机械与电力设备", ("industry", "supply_chain")),
        ("manufacturing_detail_8", "仪器仪表", ("industry", "supply_chain")),
        ("manufacturing_detail_9", "化学原料与化工", ("industry", "supply_chain")),
        ("manufacturing_detail_10", "医药制造", ("industry", "supply_chain")),
        ("manufacturing_detail_11", "生物制品制造", ("industry", "supply_chain")),
        ("manufacturing_detail_12", "食品加工", ("industry", "supply_chain")),
        ("manufacturing_detail_13", "饮料与酒类", ("industry", "supply_chain")),
        ("manufacturing_detail_14", "纺织与服装", ("industry", "supply_chain")),
        ("manufacturing_detail_15", "家具与家居制造", ("industry", "supply_chain")),
        ("manufacturing_detail_16", "造纸与印刷", ("industry", "supply_chain")),
        ("manufacturing_detail_17", "金属冶炼与加工", ("industry", "supply_chain")),
        ("manufacturing_detail_18", "塑料与橡胶制品", ("industry", "supply_chain")),
        ("manufacturing_detail_19", "建材与非金属材料", ("industry", "supply_chain")),
        ("manufacturing_detail_20", "精密加工与模具", ("industry", "supply_chain")),
        ("manufacturing_detail_21", "医疗设备制造", ("industry", "supply_chain")),
        ("manufacturing_detail_22", "再生资源加工", ("industry", "supply_chain")),
    ),
    "healthcare": (
        ("healthcare_detail_1", "综合医院与专科医院", ("health", "society")),
        ("healthcare_detail_2", "基层医疗与社区卫生", ("health", "society")),
        ("healthcare_detail_3", "口腔医疗", ("health", "society")),
        ("healthcare_detail_4", "中医与中药服务", ("health", "society")),
        ("healthcare_detail_5", "康复与护理", ("health", "society")),
        ("healthcare_detail_6", "医学检验与影像", ("health", "society")),
        ("healthcare_detail_7", "公共卫生与疾控", ("health", "society")),
        ("healthcare_detail_8", "心理健康服务", ("health", "society")),
        ("healthcare_detail_9", "养老与长期照护", ("health", "society")),
        ("healthcare_detail_10", "生物技术与药物研发", ("health", "society")),
        ("healthcare_detail_11", "数字医疗与医疗信息化", ("health", "society")),
        ("healthcare_detail_12", "医药流通", ("health", "society")),
        ("healthcare_detail_13", "社会工作与福利服务", ("health", "society")),
    ),
    "education": (
        ("education_detail_1", "学前教育", ("education", "workforce")),
        ("education_detail_2", "基础教育", ("education", "workforce")),
        ("education_detail_3", "高中与中等教育", ("education", "workforce")),
        ("education_detail_4", "高等教育", ("education", "workforce")),
        ("education_detail_5", "职业院校", ("education", "workforce")),
        ("education_detail_6", "职业技能培训", ("education", "workforce")),
        ("education_detail_7", "语言与国际教育", ("education", "workforce")),
        ("education_detail_8", "在线教育", ("education", "workforce")),
        ("education_detail_9", "教育科技与工具", ("education", "workforce")),
        ("education_detail_10", "特殊教育", ("education", "workforce")),
        ("education_detail_11", "教育咨询与服务", ("education", "workforce")),
        ("education_detail_12", "艺术与体育培训", ("education", "workforce")),
    ),
    "finance": (
        ("finance_detail_1", "证券与经纪服务", ("macro_finance", "policy")),
        ("finance_detail_2", "基金与资产管理", ("macro_finance", "policy")),
        ("finance_detail_3", "支付与清算", ("macro_finance", "policy")),
        ("finance_detail_4", "金融科技", ("macro_finance", "policy")),
        ("finance_detail_5", "消费金融", ("macro_finance", "policy")),
        ("finance_detail_6", "融资租赁", ("macro_finance", "policy")),
        ("finance_detail_7", "信托与财富管理", ("macro_finance", "policy")),
        ("finance_detail_8", "金融基础设施", ("macro_finance", "policy")),
        ("finance_detail_9", "风险管理与合规", ("macro_finance", "policy")),
        ("finance_detail_10", "普惠金融", ("macro_finance", "policy")),
    ),
    "services": (
        ("services_detail_1", "综合商业服务", ("consumption", "society")),
        ("services_detail_2", "社区生活服务", ("consumption", "society")),
        ("services_detail_3", "平台与到家服务", ("consumption", "society")),
        ("services_detail_4", "家居生活服务", ("consumption", "society")),
        ("services_detail_5", "综合咨询服务", ("consumption", "society")),
    ),
    "energy": (
        ("energy_detail_1", "光伏与太阳能", ("energy", "industry")),
        ("energy_detail_2", "风电", ("energy", "industry")),
        ("energy_detail_3", "水电", ("energy", "industry")),
        ("energy_detail_4", "核能", ("energy", "industry")),
        ("energy_detail_5", "氢能与燃料电池", ("energy", "industry")),
        ("energy_detail_6", "电池技术与材料", ("energy", "industry")),
        ("energy_detail_7", "充电与换电服务", ("energy", "industry")),
        ("energy_detail_8", "智慧能源与能源管理", ("energy", "industry")),
        ("energy_detail_9", "油气技术与能源服务", ("energy", "industry")),
        ("energy_detail_10", "能源贸易与碳管理", ("energy", "industry")),
    ),
}
_NEW_INDUSTRIES = (
    (
        "agriculture",
        "农林牧渔",
        (
            ("agriculture_detail_1", "种植与农业生产", ("industry", "consumption")),
            ("agriculture_detail_2", "林业与林产品", ("industry", "consumption")),
            ("agriculture_detail_3", "畜牧养殖", ("industry", "consumption")),
            ("agriculture_detail_4", "渔业与水产养殖", ("industry", "consumption")),
            ("agriculture_detail_5", "种业与育种", ("industry", "consumption")),
            ("agriculture_detail_6", "农业机械与农技服务", ("industry", "consumption")),
            ("agriculture_detail_7", "农产品加工与流通", ("industry", "consumption")),
            ("agriculture_detail_8", "智慧农业", ("industry", "consumption")),
        ),
    ),
    (
        "mining",
        "采矿与矿产资源",
        (
            ("mining_detail_1", "煤炭开采", ("industry", "energy", "supply_chain")),
            ("mining_detail_2", "石油与天然气开采", ("industry", "energy", "supply_chain")),
            ("mining_detail_3", "金属矿采选", ("industry", "energy", "supply_chain")),
            ("mining_detail_4", "非金属矿采选", ("industry", "energy", "supply_chain")),
            ("mining_detail_5", "矿业勘探与技术服务", ("industry", "energy", "supply_chain")),
            ("mining_detail_6", "矿山装备与安全", ("industry", "energy", "supply_chain")),
            ("mining_detail_7", "关键矿产与资源回收", ("industry", "energy", "supply_chain")),
        ),
    ),
    (
        "utilities",
        "电力热力燃气与水务",
        (
            ("utilities_detail_1", "电力生产与供应", ("energy", "society")),
            ("utilities_detail_2", "电网与配电服务", ("energy", "society")),
            ("utilities_detail_3", "热力供应", ("energy", "society")),
            ("utilities_detail_4", "燃气供应", ("energy", "society")),
            ("utilities_detail_5", "自来水与供水", ("energy", "society")),
            ("utilities_detail_6", "污水处理", ("energy", "society")),
            ("utilities_detail_7", "公用事业运营", ("energy", "society")),
        ),
    ),
    (
        "construction",
        "建筑与工程",
        (
            ("construction_detail_1", "房屋建筑", ("industry", "housing")),
            ("construction_detail_2", "土木与基础设施工程", ("industry", "housing")),
            ("construction_detail_3", "建筑安装", ("industry", "housing")),
            ("construction_detail_4", "建筑装饰与装修", ("industry", "housing")),
            ("construction_detail_5", "工程设计与咨询", ("industry", "housing")),
            ("construction_detail_6", "工程施工与项目管理", ("industry", "housing")),
            ("construction_detail_7", "装配式建筑", ("industry", "housing")),
            ("construction_detail_8", "建筑节能与绿色建筑", ("industry", "housing")),
        ),
    ),
    (
        "commerce",
        "批发零售与电商",
        (
            ("commerce_detail_1", "日用消费品零售", ("consumption", "supply_chain")),
            ("commerce_detail_2", "食品与生鲜零售", ("consumption", "supply_chain")),
            ("commerce_detail_3", "服装与美妆零售", ("consumption", "supply_chain")),
            ("commerce_detail_4", "家电与数码零售", ("consumption", "supply_chain")),
            ("commerce_detail_5", "汽车销售与服务", ("consumption", "supply_chain")),
            ("commerce_detail_6", "医药与健康零售", ("consumption", "supply_chain")),
            ("commerce_detail_7", "工业品批发", ("consumption", "supply_chain")),
            ("commerce_detail_8", "跨境电商", ("consumption", "supply_chain")),
            ("commerce_detail_9", "内容电商与直播", ("consumption", "supply_chain")),
            ("commerce_detail_10", "零售运营与连锁经营", ("consumption", "supply_chain")),
        ),
    ),
    (
        "transport",
        "交通运输仓储与物流",
        (
            ("transport_detail_1", "道路客货运输", ("supply_chain", "industry")),
            ("transport_detail_2", "铁路运输", ("supply_chain", "industry")),
            ("transport_detail_3", "航空运输", ("supply_chain", "industry")),
            ("transport_detail_4", "水上与港口运输", ("supply_chain", "industry")),
            ("transport_detail_5", "城市公共交通", ("supply_chain", "industry")),
            ("transport_detail_6", "快递与邮政", ("supply_chain", "industry")),
            ("transport_detail_7", "仓储与配送", ("supply_chain", "industry")),
            ("transport_detail_8", "供应链与货运代理", ("supply_chain", "industry")),
            ("transport_detail_9", "多式联运", ("supply_chain", "industry")),
            ("transport_detail_10", "冷链物流", ("supply_chain", "industry")),
            ("transport_detail_11", "智能交通与出行服务", ("supply_chain", "industry")),
        ),
    ),
    (
        "hospitality_food",
        "住宿餐饮与旅游",
        (
            ("hospitality_food_detail_1", "酒店与住宿", ("consumption", "society")),
            ("hospitality_food_detail_2", "餐饮门店经营", ("consumption", "society")),
            ("hospitality_food_detail_3", "连锁餐饮", ("consumption", "society")),
            ("hospitality_food_detail_4", "食品配送与团餐", ("consumption", "society")),
            ("hospitality_food_detail_5", "咖啡茶饮与烘焙", ("consumption", "society")),
            ("hospitality_food_detail_6", "旅游服务与旅行社", ("consumption", "society")),
            ("hospitality_food_detail_7", "景区与文旅运营", ("consumption", "society")),
            ("hospitality_food_detail_8", "会展与旅游活动", ("consumption", "society")),
        ),
    ),
    (
        "real_estate",
        "房地产与物业",
        (
            ("real_estate_detail_1", "房地产开发", ("housing", "industry")),
            ("real_estate_detail_2", "房地产经纪与交易", ("housing", "industry")),
            ("real_estate_detail_3", "住房租赁", ("housing", "industry")),
            ("real_estate_detail_4", "商业地产运营", ("housing", "industry")),
            ("real_estate_detail_5", "园区与产业地产", ("housing", "industry")),
            ("real_estate_detail_6", "物业管理", ("housing", "industry")),
            ("real_estate_detail_7", "房地产评估与咨询", ("housing", "industry")),
            ("real_estate_detail_8", "城市更新", ("housing", "industry")),
        ),
    ),
    (
        "business",
        "租赁与商务服务",
        (
            ("business_detail_1", "企业管理咨询", ("industry", "workforce")),
            ("business_detail_2", "法律服务", ("industry", "workforce")),
            ("business_detail_3", "会计税务与审计", ("industry", "workforce")),
            ("business_detail_4", "人力资源与招聘", ("industry", "workforce")),
            ("business_detail_5", "广告营销与品牌", ("industry", "workforce")),
            ("business_detail_6", "会展与活动服务", ("industry", "workforce")),
            ("business_detail_7", "商务外包", ("industry", "workforce")),
            ("business_detail_8", "设备与物品租赁", ("industry", "workforce")),
            ("business_detail_9", "知识产权服务", ("industry", "workforce")),
            ("business_detail_10", "市场调研与信息咨询", ("industry", "workforce")),
        ),
    ),
    (
        "science",
        "科研与专业技术服务",
        (
            ("science_detail_1", "自然科学研究", ("technology", "education", "industry")),
            ("science_detail_2", "工程技术研发", ("technology", "education", "industry")),
            ("science_detail_3", "社会科学研究", ("technology", "education", "industry")),
            ("science_detail_4", "实验与检测认证", ("technology", "education", "industry")),
            ("science_detail_5", "工程勘察与测绘", ("technology", "education", "industry")),
            ("science_detail_6", "技术推广与成果转化", ("technology", "education", "industry")),
            ("science_detail_7", "工业设计与专业设计", ("technology", "education", "industry")),
            ("science_detail_8", "气象与地质技术服务", ("technology", "education", "industry")),
            ("science_detail_9", "科研仪器与技术平台", ("technology", "education", "industry")),
        ),
    ),
    (
        "environment",
        "生态环保与公共设施",
        (
            ("environment_detail_1", "生态保护与修复", ("energy", "society", "industry")),
            ("environment_detail_2", "环境治理", ("energy", "society", "industry")),
            ("environment_detail_3", "固废处理与循环利用", ("energy", "society", "industry")),
            ("environment_detail_4", "水利管理", ("energy", "society", "industry")),
            ("environment_detail_5", "园林绿化", ("energy", "society", "industry")),
            ("environment_detail_6", "城市公共设施运营", ("energy", "society", "industry")),
            ("environment_detail_7", "土地整治与管理", ("energy", "society", "industry")),
            ("environment_detail_8", "环境监测与咨询", ("energy", "society", "industry")),
        ),
    ),
    (
        "personal_services",
        "居民服务与维修",
        (
            ("personal_services_detail_1", "家政与家庭服务", ("consumption", "society")),
            ("personal_services_detail_2", "美容美发与生活护理", ("consumption", "society")),
            ("personal_services_detail_3", "洗染与清洁服务", ("consumption", "society")),
            ("personal_services_detail_4", "家电与电子产品维修", ("consumption", "society")),
            ("personal_services_detail_5", "汽车维修与养护", ("consumption", "society")),
            ("personal_services_detail_6", "家居与日用品维修", ("consumption", "society")),
            ("personal_services_detail_7", "摄影与个人服务", ("consumption", "society")),
            ("personal_services_detail_8", "宠物服务", ("consumption", "society")),
            ("personal_services_detail_9", "殡葬与礼仪服务", ("consumption", "society")),
        ),
    ),
    (
        "culture",
        "文化传媒体育与娱乐",
        (
            ("culture_detail_1", "新闻与出版", ("consumption", "society", "technology")),
            ("culture_detail_2", "影视与广播", ("consumption", "society", "technology")),
            ("culture_detail_3", "音乐与音频内容", ("consumption", "society", "technology")),
            ("culture_detail_4", "网络内容与创作者", ("consumption", "society", "technology")),
            ("culture_detail_5", "游戏运营与数字娱乐", ("consumption", "society", "technology")),
            ("culture_detail_6", "文化艺术与演出", ("consumption", "society", "technology")),
            ("culture_detail_7", "博物馆与文化场馆", ("consumption", "society", "technology")),
            ("culture_detail_8", "体育赛事与运营", ("consumption", "society", "technology")),
            ("culture_detail_9", "健身与运动服务", ("consumption", "society", "technology")),
            ("culture_detail_10", "休闲娱乐服务", ("consumption", "society", "technology")),
        ),
    ),
    (
        "public_services",
        "公共管理与社会组织",
        (
            ("public_services_detail_1", "公共行政与政务服务", ("policy", "society")),
            ("public_services_detail_2", "社会保障服务", ("policy", "society")),
            ("public_services_detail_3", "社会团体与行业组织", ("policy", "society")),
            ("public_services_detail_4", "基层社区服务", ("policy", "society")),
            ("public_services_detail_5", "公益慈善与志愿服务", ("policy", "society")),
            ("public_services_detail_6", "公共安全与应急服务", ("policy", "society")),
        ),
    ),
    (
        "international",
        "国际组织与国际合作",
        (
            ("international_detail_1", "国际组织事务", ("policy", "society")),
            ("international_detail_2", "国际发展与合作", ("policy", "society")),
            ("international_detail_3", "国际交流与项目服务", ("policy", "society")),
            ("international_detail_4", "跨国公共事务", ("policy", "society")),
        ),
    ),
)

INDUSTRIES = tuple(
    (
        parent,
        label,
        children
        + _EXTRA_CHILDREN.get(parent, ())
        + (
            ((parent + "_other", "其他细分方向（自行填写）", children[0][2]),)
            if parent != "not_applicable"
            else ()
        ),
    )
    for parent, label, children in INDUSTRIES + _NEW_INDUSTRIES
)


def rows() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for parent, label, children in INDUSTRIES:
        result.append(
            {
                "code": parent,
                "parent_code": None,
                "label": label,
                "level": 1,
                "version": TAXONOMY_VERSION,
                "domain_tags": [],
            }
        )
        for code, name, tags in children:
            result.append(
                {
                    "code": code,
                    "parent_code": parent,
                    "label": name,
                    "level": 2,
                    "version": TAXONOMY_VERSION,
                    "domain_tags": list(tags),
                }
            )
    return result


def industry(parent: str, child: str) -> dict[str, Any]:
    match = next((r for r in rows() if r["code"] == child and r["parent_code"] == parent), None)
    if match is None:
        raise ValueError("INDUSTRY_HIERARCHY_INVALID")
    return match
