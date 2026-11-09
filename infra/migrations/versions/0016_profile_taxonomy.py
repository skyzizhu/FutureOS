"""Append expanded product-owned industry options, retaining all v1 code/parent pairs."""

import json

import sqlalchemy as sa
from alembic import op

revision = "0016_profile"
down_revision = "0015_consumer"
branch_labels = None
depends_on = None

# Frozen v2 additions; do not import the evolving product taxonomy during migrations.
ADDITIONS = json.loads(
    r"""
[
  {
    "code": "agriculture",
    "parent_code": null,
    "label": "农林牧渔",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "mining",
    "parent_code": null,
    "label": "采矿与矿产资源",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "utilities",
    "parent_code": null,
    "label": "电力热力燃气与水务",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "construction",
    "parent_code": null,
    "label": "建筑与工程",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "commerce",
    "parent_code": null,
    "label": "批发零售与电商",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "transport",
    "parent_code": null,
    "label": "交通运输仓储与物流",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "hospitality_food",
    "parent_code": null,
    "label": "住宿餐饮与旅游",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "real_estate",
    "parent_code": null,
    "label": "房地产与物业",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "business",
    "parent_code": null,
    "label": "租赁与商务服务",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "science",
    "parent_code": null,
    "label": "科研与专业技术服务",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "environment",
    "parent_code": null,
    "label": "生态环保与公共设施",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "personal_services",
    "parent_code": null,
    "label": "居民服务与维修",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "culture",
    "parent_code": null,
    "label": "文化传媒体育与娱乐",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "public_services",
    "parent_code": null,
    "label": "公共管理与社会组织",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "international",
    "parent_code": null,
    "label": "国际组织与国际合作",
    "level": 1,
    "version": "futureos-industry-v2",
    "domain_tags": []
  },
  {
    "code": "technology_detail_1",
    "parent_code": "technology",
    "label": "人工智能算法与模型",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_2",
    "parent_code": "technology",
    "label": "AI 应用与智能体",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_3",
    "parent_code": "technology",
    "label": "企业软件与 SaaS",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_4",
    "parent_code": "technology",
    "label": "移动应用开发",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_5",
    "parent_code": "technology",
    "label": "前端与用户体验",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_6",
    "parent_code": "technology",
    "label": "后端与系统架构",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_7",
    "parent_code": "technology",
    "label": "游戏研发",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_8",
    "parent_code": "technology",
    "label": "网络安全",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_9",
    "parent_code": "technology",
    "label": "云计算与云原生",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_10",
    "parent_code": "technology",
    "label": "运维与 DevOps",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_11",
    "parent_code": "technology",
    "label": "数据工程与数据库",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_12",
    "parent_code": "technology",
    "label": "通信与电信",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_13",
    "parent_code": "technology",
    "label": "物联网与嵌入式",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_14",
    "parent_code": "technology",
    "label": "集成电路设计",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_15",
    "parent_code": "technology",
    "label": "互联网平台",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_16",
    "parent_code": "technology",
    "label": "数字内容与信息服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_17",
    "parent_code": "technology",
    "label": "IT 咨询与系统集成",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_detail_18",
    "parent_code": "technology",
    "label": "数据标注与数据服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "technology_other",
    "parent_code": "technology",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "workforce"
    ]
  },
  {
    "code": "manufacturing_detail_1",
    "parent_code": "manufacturing",
    "label": "半导体与芯片制造",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_2",
    "parent_code": "manufacturing",
    "label": "机器人与自动化设备",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_3",
    "parent_code": "manufacturing",
    "label": "新能源汽车制造",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_4",
    "parent_code": "manufacturing",
    "label": "汽车零部件",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_5",
    "parent_code": "manufacturing",
    "label": "航空航天制造",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_6",
    "parent_code": "manufacturing",
    "label": "船舶与轨道交通装备",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_7",
    "parent_code": "manufacturing",
    "label": "电气机械与电力设备",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_8",
    "parent_code": "manufacturing",
    "label": "仪器仪表",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_9",
    "parent_code": "manufacturing",
    "label": "化学原料与化工",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_10",
    "parent_code": "manufacturing",
    "label": "医药制造",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_11",
    "parent_code": "manufacturing",
    "label": "生物制品制造",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_12",
    "parent_code": "manufacturing",
    "label": "食品加工",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_13",
    "parent_code": "manufacturing",
    "label": "饮料与酒类",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_14",
    "parent_code": "manufacturing",
    "label": "纺织与服装",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_15",
    "parent_code": "manufacturing",
    "label": "家具与家居制造",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_16",
    "parent_code": "manufacturing",
    "label": "造纸与印刷",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_17",
    "parent_code": "manufacturing",
    "label": "金属冶炼与加工",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_18",
    "parent_code": "manufacturing",
    "label": "塑料与橡胶制品",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_19",
    "parent_code": "manufacturing",
    "label": "建材与非金属材料",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_20",
    "parent_code": "manufacturing",
    "label": "精密加工与模具",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_21",
    "parent_code": "manufacturing",
    "label": "医疗设备制造",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_detail_22",
    "parent_code": "manufacturing",
    "label": "再生资源加工",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "manufacturing_other",
    "parent_code": "manufacturing",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "supply_chain"
    ]
  },
  {
    "code": "healthcare_detail_1",
    "parent_code": "healthcare",
    "label": "综合医院与专科医院",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_2",
    "parent_code": "healthcare",
    "label": "基层医疗与社区卫生",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_3",
    "parent_code": "healthcare",
    "label": "口腔医疗",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_4",
    "parent_code": "healthcare",
    "label": "中医与中药服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_5",
    "parent_code": "healthcare",
    "label": "康复与护理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_6",
    "parent_code": "healthcare",
    "label": "医学检验与影像",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_7",
    "parent_code": "healthcare",
    "label": "公共卫生与疾控",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_8",
    "parent_code": "healthcare",
    "label": "心理健康服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_9",
    "parent_code": "healthcare",
    "label": "养老与长期照护",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_10",
    "parent_code": "healthcare",
    "label": "生物技术与药物研发",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_11",
    "parent_code": "healthcare",
    "label": "数字医疗与医疗信息化",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_12",
    "parent_code": "healthcare",
    "label": "医药流通",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_detail_13",
    "parent_code": "healthcare",
    "label": "社会工作与福利服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health",
      "society"
    ]
  },
  {
    "code": "healthcare_other",
    "parent_code": "healthcare",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "health"
    ]
  },
  {
    "code": "education_detail_1",
    "parent_code": "education",
    "label": "学前教育",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_detail_2",
    "parent_code": "education",
    "label": "基础教育",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_detail_3",
    "parent_code": "education",
    "label": "高中与中等教育",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_detail_4",
    "parent_code": "education",
    "label": "高等教育",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_detail_5",
    "parent_code": "education",
    "label": "职业院校",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_detail_6",
    "parent_code": "education",
    "label": "职业技能培训",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_detail_7",
    "parent_code": "education",
    "label": "语言与国际教育",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_detail_8",
    "parent_code": "education",
    "label": "在线教育",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_detail_9",
    "parent_code": "education",
    "label": "教育科技与工具",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_detail_10",
    "parent_code": "education",
    "label": "特殊教育",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_detail_11",
    "parent_code": "education",
    "label": "教育咨询与服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_detail_12",
    "parent_code": "education",
    "label": "艺术与体育培训",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education",
      "workforce"
    ]
  },
  {
    "code": "education_other",
    "parent_code": "education",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "education"
    ]
  },
  {
    "code": "finance_detail_1",
    "parent_code": "finance",
    "label": "证券与经纪服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "macro_finance",
      "policy"
    ]
  },
  {
    "code": "finance_detail_2",
    "parent_code": "finance",
    "label": "基金与资产管理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "macro_finance",
      "policy"
    ]
  },
  {
    "code": "finance_detail_3",
    "parent_code": "finance",
    "label": "支付与清算",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "macro_finance",
      "policy"
    ]
  },
  {
    "code": "finance_detail_4",
    "parent_code": "finance",
    "label": "金融科技",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "macro_finance",
      "policy"
    ]
  },
  {
    "code": "finance_detail_5",
    "parent_code": "finance",
    "label": "消费金融",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "macro_finance",
      "policy"
    ]
  },
  {
    "code": "finance_detail_6",
    "parent_code": "finance",
    "label": "融资租赁",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "macro_finance",
      "policy"
    ]
  },
  {
    "code": "finance_detail_7",
    "parent_code": "finance",
    "label": "信托与财富管理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "macro_finance",
      "policy"
    ]
  },
  {
    "code": "finance_detail_8",
    "parent_code": "finance",
    "label": "金融基础设施",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "macro_finance",
      "policy"
    ]
  },
  {
    "code": "finance_detail_9",
    "parent_code": "finance",
    "label": "风险管理与合规",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "macro_finance",
      "policy"
    ]
  },
  {
    "code": "finance_detail_10",
    "parent_code": "finance",
    "label": "普惠金融",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "macro_finance",
      "policy"
    ]
  },
  {
    "code": "finance_other",
    "parent_code": "finance",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "macro_finance"
    ]
  },
  {
    "code": "services_detail_1",
    "parent_code": "services",
    "label": "综合商业服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "services_detail_2",
    "parent_code": "services",
    "label": "社区生活服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "services_detail_3",
    "parent_code": "services",
    "label": "平台与到家服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "services_detail_4",
    "parent_code": "services",
    "label": "家居生活服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "services_detail_5",
    "parent_code": "services",
    "label": "综合咨询服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "services_other",
    "parent_code": "services",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption"
    ]
  },
  {
    "code": "energy_detail_1",
    "parent_code": "energy",
    "label": "光伏与太阳能",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "industry"
    ]
  },
  {
    "code": "energy_detail_2",
    "parent_code": "energy",
    "label": "风电",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "industry"
    ]
  },
  {
    "code": "energy_detail_3",
    "parent_code": "energy",
    "label": "水电",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "industry"
    ]
  },
  {
    "code": "energy_detail_4",
    "parent_code": "energy",
    "label": "核能",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "industry"
    ]
  },
  {
    "code": "energy_detail_5",
    "parent_code": "energy",
    "label": "氢能与燃料电池",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "industry"
    ]
  },
  {
    "code": "energy_detail_6",
    "parent_code": "energy",
    "label": "电池技术与材料",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "industry"
    ]
  },
  {
    "code": "energy_detail_7",
    "parent_code": "energy",
    "label": "充电与换电服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "industry"
    ]
  },
  {
    "code": "energy_detail_8",
    "parent_code": "energy",
    "label": "智慧能源与能源管理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "industry"
    ]
  },
  {
    "code": "energy_detail_9",
    "parent_code": "energy",
    "label": "油气技术与能源服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "industry"
    ]
  },
  {
    "code": "energy_detail_10",
    "parent_code": "energy",
    "label": "能源贸易与碳管理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "industry"
    ]
  },
  {
    "code": "energy_other",
    "parent_code": "energy",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy"
    ]
  },
  {
    "code": "agriculture_detail_1",
    "parent_code": "agriculture",
    "label": "种植与农业生产",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "consumption"
    ]
  },
  {
    "code": "agriculture_detail_2",
    "parent_code": "agriculture",
    "label": "林业与林产品",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "consumption"
    ]
  },
  {
    "code": "agriculture_detail_3",
    "parent_code": "agriculture",
    "label": "畜牧养殖",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "consumption"
    ]
  },
  {
    "code": "agriculture_detail_4",
    "parent_code": "agriculture",
    "label": "渔业与水产养殖",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "consumption"
    ]
  },
  {
    "code": "agriculture_detail_5",
    "parent_code": "agriculture",
    "label": "种业与育种",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "consumption"
    ]
  },
  {
    "code": "agriculture_detail_6",
    "parent_code": "agriculture",
    "label": "农业机械与农技服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "consumption"
    ]
  },
  {
    "code": "agriculture_detail_7",
    "parent_code": "agriculture",
    "label": "农产品加工与流通",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "consumption"
    ]
  },
  {
    "code": "agriculture_detail_8",
    "parent_code": "agriculture",
    "label": "智慧农业",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "consumption"
    ]
  },
  {
    "code": "agriculture_other",
    "parent_code": "agriculture",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "consumption"
    ]
  },
  {
    "code": "mining_detail_1",
    "parent_code": "mining",
    "label": "煤炭开采",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "energy",
      "supply_chain"
    ]
  },
  {
    "code": "mining_detail_2",
    "parent_code": "mining",
    "label": "石油与天然气开采",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "energy",
      "supply_chain"
    ]
  },
  {
    "code": "mining_detail_3",
    "parent_code": "mining",
    "label": "金属矿采选",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "energy",
      "supply_chain"
    ]
  },
  {
    "code": "mining_detail_4",
    "parent_code": "mining",
    "label": "非金属矿采选",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "energy",
      "supply_chain"
    ]
  },
  {
    "code": "mining_detail_5",
    "parent_code": "mining",
    "label": "矿业勘探与技术服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "energy",
      "supply_chain"
    ]
  },
  {
    "code": "mining_detail_6",
    "parent_code": "mining",
    "label": "矿山装备与安全",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "energy",
      "supply_chain"
    ]
  },
  {
    "code": "mining_detail_7",
    "parent_code": "mining",
    "label": "关键矿产与资源回收",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "energy",
      "supply_chain"
    ]
  },
  {
    "code": "mining_other",
    "parent_code": "mining",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "energy",
      "supply_chain"
    ]
  },
  {
    "code": "utilities_detail_1",
    "parent_code": "utilities",
    "label": "电力生产与供应",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society"
    ]
  },
  {
    "code": "utilities_detail_2",
    "parent_code": "utilities",
    "label": "电网与配电服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society"
    ]
  },
  {
    "code": "utilities_detail_3",
    "parent_code": "utilities",
    "label": "热力供应",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society"
    ]
  },
  {
    "code": "utilities_detail_4",
    "parent_code": "utilities",
    "label": "燃气供应",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society"
    ]
  },
  {
    "code": "utilities_detail_5",
    "parent_code": "utilities",
    "label": "自来水与供水",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society"
    ]
  },
  {
    "code": "utilities_detail_6",
    "parent_code": "utilities",
    "label": "污水处理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society"
    ]
  },
  {
    "code": "utilities_detail_7",
    "parent_code": "utilities",
    "label": "公用事业运营",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society"
    ]
  },
  {
    "code": "utilities_other",
    "parent_code": "utilities",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society"
    ]
  },
  {
    "code": "construction_detail_1",
    "parent_code": "construction",
    "label": "房屋建筑",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "housing"
    ]
  },
  {
    "code": "construction_detail_2",
    "parent_code": "construction",
    "label": "土木与基础设施工程",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "housing"
    ]
  },
  {
    "code": "construction_detail_3",
    "parent_code": "construction",
    "label": "建筑安装",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "housing"
    ]
  },
  {
    "code": "construction_detail_4",
    "parent_code": "construction",
    "label": "建筑装饰与装修",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "housing"
    ]
  },
  {
    "code": "construction_detail_5",
    "parent_code": "construction",
    "label": "工程设计与咨询",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "housing"
    ]
  },
  {
    "code": "construction_detail_6",
    "parent_code": "construction",
    "label": "工程施工与项目管理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "housing"
    ]
  },
  {
    "code": "construction_detail_7",
    "parent_code": "construction",
    "label": "装配式建筑",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "housing"
    ]
  },
  {
    "code": "construction_detail_8",
    "parent_code": "construction",
    "label": "建筑节能与绿色建筑",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "housing"
    ]
  },
  {
    "code": "construction_other",
    "parent_code": "construction",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "housing"
    ]
  },
  {
    "code": "commerce_detail_1",
    "parent_code": "commerce",
    "label": "日用消费品零售",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "supply_chain"
    ]
  },
  {
    "code": "commerce_detail_2",
    "parent_code": "commerce",
    "label": "食品与生鲜零售",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "supply_chain"
    ]
  },
  {
    "code": "commerce_detail_3",
    "parent_code": "commerce",
    "label": "服装与美妆零售",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "supply_chain"
    ]
  },
  {
    "code": "commerce_detail_4",
    "parent_code": "commerce",
    "label": "家电与数码零售",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "supply_chain"
    ]
  },
  {
    "code": "commerce_detail_5",
    "parent_code": "commerce",
    "label": "汽车销售与服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "supply_chain"
    ]
  },
  {
    "code": "commerce_detail_6",
    "parent_code": "commerce",
    "label": "医药与健康零售",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "supply_chain"
    ]
  },
  {
    "code": "commerce_detail_7",
    "parent_code": "commerce",
    "label": "工业品批发",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "supply_chain"
    ]
  },
  {
    "code": "commerce_detail_8",
    "parent_code": "commerce",
    "label": "跨境电商",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "supply_chain"
    ]
  },
  {
    "code": "commerce_detail_9",
    "parent_code": "commerce",
    "label": "内容电商与直播",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "supply_chain"
    ]
  },
  {
    "code": "commerce_detail_10",
    "parent_code": "commerce",
    "label": "零售运营与连锁经营",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "supply_chain"
    ]
  },
  {
    "code": "commerce_other",
    "parent_code": "commerce",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "supply_chain"
    ]
  },
  {
    "code": "transport_detail_1",
    "parent_code": "transport",
    "label": "道路客货运输",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "transport_detail_2",
    "parent_code": "transport",
    "label": "铁路运输",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "transport_detail_3",
    "parent_code": "transport",
    "label": "航空运输",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "transport_detail_4",
    "parent_code": "transport",
    "label": "水上与港口运输",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "transport_detail_5",
    "parent_code": "transport",
    "label": "城市公共交通",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "transport_detail_6",
    "parent_code": "transport",
    "label": "快递与邮政",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "transport_detail_7",
    "parent_code": "transport",
    "label": "仓储与配送",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "transport_detail_8",
    "parent_code": "transport",
    "label": "供应链与货运代理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "transport_detail_9",
    "parent_code": "transport",
    "label": "多式联运",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "transport_detail_10",
    "parent_code": "transport",
    "label": "冷链物流",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "transport_detail_11",
    "parent_code": "transport",
    "label": "智能交通与出行服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "transport_other",
    "parent_code": "transport",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "supply_chain",
      "industry"
    ]
  },
  {
    "code": "hospitality_food_detail_1",
    "parent_code": "hospitality_food",
    "label": "酒店与住宿",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "hospitality_food_detail_2",
    "parent_code": "hospitality_food",
    "label": "餐饮门店经营",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "hospitality_food_detail_3",
    "parent_code": "hospitality_food",
    "label": "连锁餐饮",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "hospitality_food_detail_4",
    "parent_code": "hospitality_food",
    "label": "食品配送与团餐",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "hospitality_food_detail_5",
    "parent_code": "hospitality_food",
    "label": "咖啡茶饮与烘焙",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "hospitality_food_detail_6",
    "parent_code": "hospitality_food",
    "label": "旅游服务与旅行社",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "hospitality_food_detail_7",
    "parent_code": "hospitality_food",
    "label": "景区与文旅运营",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "hospitality_food_detail_8",
    "parent_code": "hospitality_food",
    "label": "会展与旅游活动",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "hospitality_food_other",
    "parent_code": "hospitality_food",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "real_estate_detail_1",
    "parent_code": "real_estate",
    "label": "房地产开发",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "housing",
      "industry"
    ]
  },
  {
    "code": "real_estate_detail_2",
    "parent_code": "real_estate",
    "label": "房地产经纪与交易",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "housing",
      "industry"
    ]
  },
  {
    "code": "real_estate_detail_3",
    "parent_code": "real_estate",
    "label": "住房租赁",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "housing",
      "industry"
    ]
  },
  {
    "code": "real_estate_detail_4",
    "parent_code": "real_estate",
    "label": "商业地产运营",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "housing",
      "industry"
    ]
  },
  {
    "code": "real_estate_detail_5",
    "parent_code": "real_estate",
    "label": "园区与产业地产",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "housing",
      "industry"
    ]
  },
  {
    "code": "real_estate_detail_6",
    "parent_code": "real_estate",
    "label": "物业管理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "housing",
      "industry"
    ]
  },
  {
    "code": "real_estate_detail_7",
    "parent_code": "real_estate",
    "label": "房地产评估与咨询",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "housing",
      "industry"
    ]
  },
  {
    "code": "real_estate_detail_8",
    "parent_code": "real_estate",
    "label": "城市更新",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "housing",
      "industry"
    ]
  },
  {
    "code": "real_estate_other",
    "parent_code": "real_estate",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "housing",
      "industry"
    ]
  },
  {
    "code": "business_detail_1",
    "parent_code": "business",
    "label": "企业管理咨询",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "workforce"
    ]
  },
  {
    "code": "business_detail_2",
    "parent_code": "business",
    "label": "法律服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "workforce"
    ]
  },
  {
    "code": "business_detail_3",
    "parent_code": "business",
    "label": "会计税务与审计",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "workforce"
    ]
  },
  {
    "code": "business_detail_4",
    "parent_code": "business",
    "label": "人力资源与招聘",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "workforce"
    ]
  },
  {
    "code": "business_detail_5",
    "parent_code": "business",
    "label": "广告营销与品牌",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "workforce"
    ]
  },
  {
    "code": "business_detail_6",
    "parent_code": "business",
    "label": "会展与活动服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "workforce"
    ]
  },
  {
    "code": "business_detail_7",
    "parent_code": "business",
    "label": "商务外包",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "workforce"
    ]
  },
  {
    "code": "business_detail_8",
    "parent_code": "business",
    "label": "设备与物品租赁",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "workforce"
    ]
  },
  {
    "code": "business_detail_9",
    "parent_code": "business",
    "label": "知识产权服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "workforce"
    ]
  },
  {
    "code": "business_detail_10",
    "parent_code": "business",
    "label": "市场调研与信息咨询",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "workforce"
    ]
  },
  {
    "code": "business_other",
    "parent_code": "business",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "industry",
      "workforce"
    ]
  },
  {
    "code": "science_detail_1",
    "parent_code": "science",
    "label": "自然科学研究",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "education",
      "industry"
    ]
  },
  {
    "code": "science_detail_2",
    "parent_code": "science",
    "label": "工程技术研发",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "education",
      "industry"
    ]
  },
  {
    "code": "science_detail_3",
    "parent_code": "science",
    "label": "社会科学研究",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "education",
      "industry"
    ]
  },
  {
    "code": "science_detail_4",
    "parent_code": "science",
    "label": "实验与检测认证",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "education",
      "industry"
    ]
  },
  {
    "code": "science_detail_5",
    "parent_code": "science",
    "label": "工程勘察与测绘",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "education",
      "industry"
    ]
  },
  {
    "code": "science_detail_6",
    "parent_code": "science",
    "label": "技术推广与成果转化",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "education",
      "industry"
    ]
  },
  {
    "code": "science_detail_7",
    "parent_code": "science",
    "label": "工业设计与专业设计",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "education",
      "industry"
    ]
  },
  {
    "code": "science_detail_8",
    "parent_code": "science",
    "label": "气象与地质技术服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "education",
      "industry"
    ]
  },
  {
    "code": "science_detail_9",
    "parent_code": "science",
    "label": "科研仪器与技术平台",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "education",
      "industry"
    ]
  },
  {
    "code": "science_other",
    "parent_code": "science",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "technology",
      "education",
      "industry"
    ]
  },
  {
    "code": "environment_detail_1",
    "parent_code": "environment",
    "label": "生态保护与修复",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society",
      "industry"
    ]
  },
  {
    "code": "environment_detail_2",
    "parent_code": "environment",
    "label": "环境治理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society",
      "industry"
    ]
  },
  {
    "code": "environment_detail_3",
    "parent_code": "environment",
    "label": "固废处理与循环利用",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society",
      "industry"
    ]
  },
  {
    "code": "environment_detail_4",
    "parent_code": "environment",
    "label": "水利管理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society",
      "industry"
    ]
  },
  {
    "code": "environment_detail_5",
    "parent_code": "environment",
    "label": "园林绿化",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society",
      "industry"
    ]
  },
  {
    "code": "environment_detail_6",
    "parent_code": "environment",
    "label": "城市公共设施运营",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society",
      "industry"
    ]
  },
  {
    "code": "environment_detail_7",
    "parent_code": "environment",
    "label": "土地整治与管理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society",
      "industry"
    ]
  },
  {
    "code": "environment_detail_8",
    "parent_code": "environment",
    "label": "环境监测与咨询",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society",
      "industry"
    ]
  },
  {
    "code": "environment_other",
    "parent_code": "environment",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "energy",
      "society",
      "industry"
    ]
  },
  {
    "code": "personal_services_detail_1",
    "parent_code": "personal_services",
    "label": "家政与家庭服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "personal_services_detail_2",
    "parent_code": "personal_services",
    "label": "美容美发与生活护理",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "personal_services_detail_3",
    "parent_code": "personal_services",
    "label": "洗染与清洁服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "personal_services_detail_4",
    "parent_code": "personal_services",
    "label": "家电与电子产品维修",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "personal_services_detail_5",
    "parent_code": "personal_services",
    "label": "汽车维修与养护",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "personal_services_detail_6",
    "parent_code": "personal_services",
    "label": "家居与日用品维修",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "personal_services_detail_7",
    "parent_code": "personal_services",
    "label": "摄影与个人服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "personal_services_detail_8",
    "parent_code": "personal_services",
    "label": "宠物服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "personal_services_detail_9",
    "parent_code": "personal_services",
    "label": "殡葬与礼仪服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "personal_services_other",
    "parent_code": "personal_services",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society"
    ]
  },
  {
    "code": "culture_detail_1",
    "parent_code": "culture",
    "label": "新闻与出版",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society",
      "technology"
    ]
  },
  {
    "code": "culture_detail_2",
    "parent_code": "culture",
    "label": "影视与广播",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society",
      "technology"
    ]
  },
  {
    "code": "culture_detail_3",
    "parent_code": "culture",
    "label": "音乐与音频内容",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society",
      "technology"
    ]
  },
  {
    "code": "culture_detail_4",
    "parent_code": "culture",
    "label": "网络内容与创作者",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society",
      "technology"
    ]
  },
  {
    "code": "culture_detail_5",
    "parent_code": "culture",
    "label": "游戏运营与数字娱乐",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society",
      "technology"
    ]
  },
  {
    "code": "culture_detail_6",
    "parent_code": "culture",
    "label": "文化艺术与演出",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society",
      "technology"
    ]
  },
  {
    "code": "culture_detail_7",
    "parent_code": "culture",
    "label": "博物馆与文化场馆",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society",
      "technology"
    ]
  },
  {
    "code": "culture_detail_8",
    "parent_code": "culture",
    "label": "体育赛事与运营",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society",
      "technology"
    ]
  },
  {
    "code": "culture_detail_9",
    "parent_code": "culture",
    "label": "健身与运动服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society",
      "technology"
    ]
  },
  {
    "code": "culture_detail_10",
    "parent_code": "culture",
    "label": "休闲娱乐服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society",
      "technology"
    ]
  },
  {
    "code": "culture_other",
    "parent_code": "culture",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "consumption",
      "society",
      "technology"
    ]
  },
  {
    "code": "public_services_detail_1",
    "parent_code": "public_services",
    "label": "公共行政与政务服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  },
  {
    "code": "public_services_detail_2",
    "parent_code": "public_services",
    "label": "社会保障服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  },
  {
    "code": "public_services_detail_3",
    "parent_code": "public_services",
    "label": "社会团体与行业组织",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  },
  {
    "code": "public_services_detail_4",
    "parent_code": "public_services",
    "label": "基层社区服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  },
  {
    "code": "public_services_detail_5",
    "parent_code": "public_services",
    "label": "公益慈善与志愿服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  },
  {
    "code": "public_services_detail_6",
    "parent_code": "public_services",
    "label": "公共安全与应急服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  },
  {
    "code": "public_services_other",
    "parent_code": "public_services",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  },
  {
    "code": "international_detail_1",
    "parent_code": "international",
    "label": "国际组织事务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  },
  {
    "code": "international_detail_2",
    "parent_code": "international",
    "label": "国际发展与合作",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  },
  {
    "code": "international_detail_3",
    "parent_code": "international",
    "label": "国际交流与项目服务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  },
  {
    "code": "international_detail_4",
    "parent_code": "international",
    "label": "跨国公共事务",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  },
  {
    "code": "international_other",
    "parent_code": "international",
    "label": "其他细分方向（自行填写）",
    "level": 2,
    "version": "futureos-industry-v2",
    "domain_tags": [
      "policy",
      "society"
    ]
  }
]
"""
)


def upgrade() -> None:
    table = sa.table(
        "industry_taxonomy",
        sa.column("code", sa.String),
        sa.column("parent_code", sa.String),
        sa.column("label", sa.String),
        sa.column("level", sa.Integer),
        sa.column("version", sa.String),
        sa.column("domain_tags", sa.JSON),
    )
    present = set(op.get_bind().scalars(sa.select(table.c.code)))
    for row in ADDITIONS:
        if row["code"] not in present:
            op.bulk_insert(table, [row])


def downgrade() -> None:
    if op.get_bind().exec_driver_sql("SELECT count(*) FROM profiles").scalar():
        raise RuntimeError("PROFILE_V2_REQUIRES_FORWARD_REPAIR")
    # Unused lookup rows remain append-only. Earlier full-schema teardown removes the table.
