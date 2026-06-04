#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Ladnut Amazon Storefront Visual Layout PDF and Markdown source.

The PDF is generated without external packages so it can run in constrained CI.
It uses the built-in CJK CID font STSong-Light via UniGB-UCS2-H encoding.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

OUT_PDF = Path("Ladnut_Amazon_Storefront_Visual_Layout.pdf")
OUT_MD = Path("Ladnut_Amazon_Storefront_Visual_Layout.md")
PAGE_W, PAGE_H = 842, 595  # A4 landscape in points
MARGIN = 42

BRAND = {
    "name": "Ladnut",
    "tagline": "Cleaner Homes. Healthier Routines. Happier Pets.",
    "positioning": "宠物家庭健康护理品牌",
    "systems": ["OzoIon CleanAir System™", "CareRhythm™ Daily Wellness"],
}

COLORS = {
    "ink": (0.12, 0.16, 0.15),
    "muted": (0.40, 0.47, 0.44),
    "sage": (0.64, 0.75, 0.68),
    "sage_dark": (0.23, 0.38, 0.31),
    "cream": (0.96, 0.94, 0.88),
    "mist": (0.89, 0.94, 0.92),
    "blue": (0.57, 0.75, 0.80),
    "sand": (0.86, 0.76, 0.58),
    "white": (1, 1, 1),
    "line": (0.78, 0.84, 0.80),
}

@dataclass
class Module:
    name: str
    layout: str
    visual: str
    copy: str
    design: str

@dataclass
class PagePlan:
    title: str
    goal: str
    modules: list[Module] = field(default_factory=list)

DIRECTION = [
    ("色彩 Color", "主色采用 Sage Green + Warm Cream，辅助以 Clean Air Blue 与 Natural Sand，建立“洁净空气 + 日常护理 + 宠物亲和”的统一感。"),
    ("字体 Typography", "英文标题建议用现代无衬线加粗，中文使用清晰黑体；标题短、强识别，正文控制在 Amazon 可读长度内。"),
    ("品牌调性 Tone", "专业但不冰冷、健康但不医疗化、家庭感但不杂乱；画面强调明亮、通风、自然生活方式。"),
    ("视觉语言 Visual System", "使用柔和圆角卡片、浅色背景、线性图标、半透明空气流线与规律节奏线，强化两大技术支点。"),
]

ARCHITECTURE = [
    ("Home", "品牌总入口：建立 Ladnut 认知，清晰分流到 Clean Air 与 Daily Wellness。"),
    ("Clean Air", "技术资产页面：集中解释 OzoIon CleanAir System™、产品功能与家庭场景。"),
    ("Daily Wellness", "日常健康页面：解释 CareRhythm™ Daily Wellness，并承接粉剂、咀嚼软粒等护理产品。"),
    ("Our Impact", "品牌信任页面：讲述品牌故事、使命支柱、公益项目与可持续责任。"),
]

PAGES: list[PagePlan] = [
    PagePlan("Home 页面完整 Visual Layout", "用 5–8 秒建立品牌定位、两大系统认知与首个购买入口。页面应像品牌旗舰店首页，而不是单品集合页。", [
        Module("Hero Banner", "全宽 Hero；左侧 45% 文案，右侧 55% 生活方式主视觉", "明亮客厅、宠物与清洁设备/护理产品同框；加入轻微空气流线和晨光。", "Ladnut / Cleaner Homes. Healthier Routines. Happier Pets. / For pet families who care about every breath and every routine.", "首屏必须干净、有呼吸感；CTA 使用 Shop Clean Air / Explore Daily Wellness 双按钮。"),
        Module("Brand Mission", "居中使命区 + 三段短句；下方细线连接", "家庭、宠物、洁净空气、日常护理四个轻量图标。", "我们帮助宠物家庭把清洁、护理与陪伴变成更健康的日常节奏。", "用 Warm Cream 背景提升温度；避免大段叙事，保持品牌宣言感。"),
        Module("Two Product System Navigation", "双卡片导航：Clean Air 与 Daily Wellness 左右并列", "左卡用空气净化/除味视觉；右卡用牙粉、软粒、喂食互动视觉。", "OzoIon CleanAir System™ / CareRhythm™ Daily Wellness；分别说明“环境洁净”与“身体日常护理”。", "两卡使用同一网格但不同色彩点缀；卡片底部设置 Learn More CTA。"),
        Module("OzoIon Technology Highlight", "横向技术带；左侧产品近景，右侧三步原理", "空气流线、离子/臭氧控制图示、宠物安全家居背景。", "Targets odor at the source / Supports fresher shared spaces / Designed for pet-family routines.", "强调“技术感 + 安心感”，不做过度医疗或绝对化承诺；用编号 01/02/03 建立可读性。"),
        Module("Featured Product", "产品主推卡；大图 + 3 个利益点 + CTA", "产品 3/4 角度白底图，旁边配一张使用场景小图。", "Featured for Cleaner Homes：核心功能、适用空间、日常使用方式。", "Amazon 转化模块应更接近商品卡；CTA 用 Shop Now，放置星级/评价占位但不虚构数据。"),
        Module("Brand Promise / Trust Icons", "四图标横排信任带", "Pet-family safe mindset、Routine-friendly、Clean design、Support & care 图标。", "Cleaner air / Simpler routines / Thoughtful formulas / Happier homes.", "作为首页收尾，提升可信度并引导继续浏览。"),
    ]),
    PagePlan("Clean Air 页面完整 Visual Layout", "把 OzoIon CleanAir System™ 打造成独立技术资产，并让消费者理解“为什么宠物家庭需要专门的空气护理”。", [
        Module("Hero", "全宽 Hero；大面积浅蓝绿色空气背景 + 产品/空间合成", "猫狗活动区、猫砂区或客厅角落，空气流线从问题区域过渡到清新空间。", "OzoIon CleanAir System™ / Cleaner shared spaces for homes with pets.", "首屏要比首页更技术化；CTA 指向核心产品。"),
        Module("Problem Definition", "三栏问题卡片：Odor / Dander / Routine Mess", "真实但克制的宠物家庭场景：猫砂盆、宠物床、沙发织物。", "Pet homes don’t just need fragrance. They need a cleaner air routine.", "使用灰绿低饱和图示，不做脏乱夸张；建立问题但保持高级感。"),
        Module("OzoIon Technical Principle", "中心流程图：Detect / Circulate / Refresh / Maintain", "离子空气流线、微粒/异味分子示意、空间循环箭头。", "解释 OzoIon 的净味与空气循环逻辑，强调系统化而非单点香氛。", "用技术图层表达“可理解的科学感”；备注文案需合规，避免治疗、杀灭等高风险表述。"),
        Module("Product Feature Block", "左右分栏；左产品爆炸图，右 4 个功能点", "产品局部细节：出风口、控制面板、滤芯/模块、尺寸场景。", "Quiet daily use / Space-friendly design / Odor-focused refresh / Pet-home routine ready.", "功能点配图标；重点层级：标题 > 功能短句 > 使用说明。"),
        Module("Usage Scenarios", "2×2 场景网格", "猫砂区、宠物睡眠区、客厅共享区、洗衣/杂物间。", "Place it where pet life happens most.", "每格采用同一构图比例；右下角放小标签说明推荐使用场景。"),
        Module("Future Expansion", "横向路线图 / Coming Soon 系统延展", "滤芯、便携设备、空间喷雾或智能配件的抽象剪影。", "A growing clean-air ecosystem for pet families.", "弱化具体未上市承诺，用概念占位；强化系统资产可延展。"),
    ]),
    PagePlan("Daily Wellness 页面完整 Visual Layout", "呈现 CareRhythm™ Daily Wellness 的“日常节奏”理念，并把口腔、免疫/情绪、营养补充等产品纳入同一护理系统。", [
        Module("Hero", "全宽 Hero；晨间喂食台场景 + 产品组合", "狗碗、猫碗、牙粉、蘑菇软粒、日历/节奏线元素。", "CareRhythm™ Daily Wellness / Simple care rituals, every day.", "整体更温暖，使用 Cream + Sand；CTA 为 Build Their Daily Routine。"),
        Module("CareRhythm Philosophy", "三步节奏图：Add / Repeat / Support", "勺粉加入食物、手喂软粒、宠物日常陪伴的连续镜头。", "把护理变成容易坚持的日常，而不是偶尔想起的补救。", "使用时间轴和圆形节点；强调轻松、持续、可组合。"),
        Module("Dental Powder Product Block", "产品卡 + 使用步骤；左大包装图，右三步说明", "牙粉包装、撒粉动作、宠物进食特写。", "Daily dental support made easy / Sprinkle, serve, repeat.", "避免医疗化承诺；突出便利性、日常坚持和口腔清新支持。"),
        Module("Mushroom Chews Product Block", "左右交错分栏，与牙粉区形成节奏变化", "蘑菇软粒质地特写、手喂宠物、天然成分意向图。", "Wellness chews for daily support / A treat-like moment with purpose.", "用 Natural Sand 做区块底色；卖点用短标签而非长说明。"),
        Module("Shared System Logic", "组合逻辑矩阵：Morning / Mealtime / Treat Moment / Bedtime", "四个日常时段图标 + 对应产品放置。", "CareRhythm connects products into one repeatable wellness routine.", "该模块负责交叉销售；视觉上让不同 SKU 看起来属于同一系统。"),
        Module("Future CareRhythm Expansion", "模块化货架/产品家族墙", "未来营养粉、皮毛护理、情绪舒缓、消化支持等包装占位。", "A flexible wellness platform for future pet-care needs.", "保留扩展想象但不虚构具体上市信息；统一包装系统和色带规则。"),
    ]),
    PagePlan("Our Impact 页面完整 Visual Layout", "建立品牌信任与价值观，解释 Ladnut 为什么存在，以及如何以更负责任的方式服务宠物家庭。", [
        Module("Hero", "情绪化全宽 Hero；人、宠物、家居空间同框", "领养家庭或日常陪伴场景，画面自然、真实、有温度。", "Our Impact / Better routines for pets, homes, and the people who love them.", "比技术页更有人情味；少用强销售 CTA，更多使用 Learn Our Story。"),
        Module("Our Story", "左图右文叙事区", "创始灵感：宠物家庭中空气、清洁、健康护理交织的生活瞬间。", "Ladnut was built for the everyday reality of pet families.", "文字控制在 80–120 字中文；配图应真实而非过度摆拍。"),
        Module("Mission Pillars", "三支柱卡片：Cleaner Homes / Healthier Routines / Happier Pets", "每张卡配生活方式图 + 线性图标。", "对应品牌主张三段式，并解释每一支柱如何落地到产品和内容。", "这是全站品牌资产回收点；与封面口号形成闭环。"),
        Module("Fresh Start Program", "公益项目重点横幅 + 数据占位区", "宠物救助、领养包、清洁护理 starter kit 的温暖画面。", "Fresh Start Program：帮助更多宠物家庭以更洁净、更健康的方式开始共同生活。", "可预留未来真实数据：Donations / Kits / Shelter Partners；不得虚构数字。"),
        Module("Responsibility & Sustainability", "四项责任网格", "可回收包装、精简说明书、长期可替换部件、负责任成分选择图标。", "Thoughtful design, responsible routines, less unnecessary waste.", "用可信、克制的表达；如无认证，不展示认证徽章。"),
    ]),
]

RHYTHM = [
    "首屏建立情绪与定位，中段解释系统逻辑，后段承接产品转化与信任背书。",
    "每个页面保持 1 个 Hero、1 个教育模块、2–3 个产品/场景模块、1 个收尾信任或扩展模块。",
    "Amazon Storefront 中尽量使用模块化图片切片：全宽图、双列图、三/四卡片图、产品主图卡。",
    "文案采用短标题 + 一句话解释 + 三个以内要点，避免页面变成说明书。",
    "技术表达必须合规克制，避免绝对化、医疗化或无法证实的性能承诺。",
]

ASSETS = [
    "品牌主视觉：明亮家居 + 宠物 + Ladnut 产品组合，横版与竖版各一套。",
    "OzoIon 技术图示：空气流线、净味流程、设备局部细节、使用空间四场景。",
    "CareRhythm 产品图：Dental Powder、Mushroom Chews 包装图、使用步骤图、产品家族占位图。",
    "信任图标库：Cleaner Air、Daily Routine、Pet-Family Mindset、Thoughtful Formula、Sustainability。",
    "Our Impact 素材：品牌故事生活方式图、Fresh Start Program 公益视觉、责任与可持续图标。",
]

RECOMMENDATIONS = [
    "优先制作 Home、Clean Air、Daily Wellness 三个页面，Our Impact 可作为第二阶段完善品牌信任。",
    "先完成统一视觉母版，再批量制作 Amazon 模块图片，确保字体、色彩、按钮与图标一致。",
    "所有技术与功效文案在上线前进行合规复核，尤其是 OzoIon 与健康护理相关表述。",
    "产品摄影需同时覆盖白底转化图与生活方式图，避免 Storefront 只像商品陈列。",
]

CONCLUSION = [
    "建议实施该 Storefront 视觉方案。",
    "有利于建立品牌统一认知：从首页到子页面持续重复 Cleaner Homes / Healthier Routines / Happier Pets。",
    "有利于沉淀 OzoIon CleanAir System™ 与 CareRhythm™ Daily Wellness 两大品牌资产。",
    "有利于未来产品延展和交叉销售：页面结构已预留技术生态、护理生态与产品家族墙。",
    "有利于提升品牌专业感与美国消费者信任感：视觉克制、信息清晰、重视场景、合规与责任表达。",
]


def text_width_units(s: str) -> float:
    total = 0.0
    for ch in s:
        if ch == " ":
            total += 0.45
        elif ord(ch) < 128:
            total += 0.58
        else:
            total += 1.0
    return total


def wrap_text(s: str, max_units: float) -> list[str]:
    s = re.sub(r"\s+", " ", s.strip())
    lines, current = [], ""
    for part in re.split(r"( )", s):
        if not part:
            continue
        candidate = current + part
        if text_width_units(candidate) <= max_units or not current:
            current = candidate
        else:
            lines.append(current.strip())
            current = part.strip()
    if current:
        lines.append(current.strip())
    out = []
    for line in lines:
        if text_width_units(line) <= max_units:
            out.append(line)
            continue
        buf = ""
        for ch in line:
            if text_width_units(buf + ch) > max_units and buf:
                out.append(buf)
                buf = ch
            else:
                buf += ch
        if buf:
            out.append(buf)
    return out


def pdf_text(s: str) -> str:
    return "<" + s.encode("utf-16-be").hex().upper() + ">"


class PDF:
    def __init__(self):
        self.objects: list[bytes] = []
        self.pages: list[int] = []
        self.stream = ""

    def add_obj(self, data: str | bytes) -> int:
        if isinstance(data, str):
            data = data.encode("latin-1")
        self.objects.append(data)
        return len(self.objects)

    def begin_page(self):
        self.stream = ""
        self.rect(0, 0, PAGE_W, PAGE_H, COLORS["cream"], fill=True, stroke=False)

    def cmd(self, s: str):
        self.stream += s + "\n"

    def color(self, rgb, stroke=False):
        op = "RG" if stroke else "rg"
        self.cmd(f"{rgb[0]:.3f} {rgb[1]:.3f} {rgb[2]:.3f} {op}")

    def rect(self, x, y, w, h, rgb=None, fill=True, stroke=False, stroke_rgb=None):
        if rgb:
            self.color(rgb, False)
        if stroke_rgb:
            self.color(stroke_rgb, True)
        op = "B" if fill and stroke else "f" if fill else "S"
        self.cmd(f"{x:.1f} {y:.1f} {w:.1f} {h:.1f} re {op}")

    def line(self, x1, y1, x2, y2, rgb=None, width=1):
        if rgb:
            self.color(rgb, True)
        self.cmd(f"{width:.1f} w {x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S")

    def circle(self, x, y, r, rgb):
        self.color(rgb, False)
        c = 0.55228475 * r
        self.cmd(f"{x+r:.1f} {y:.1f} m {x+r:.1f} {y+c:.1f} {x+c:.1f} {y+r:.1f} {x:.1f} {y+r:.1f} c {x-c:.1f} {y+r:.1f} {x-r:.1f} {y+c:.1f} {x-r:.1f} {y:.1f} c {x-r:.1f} {y-c:.1f} {x-c:.1f} {y-r:.1f} {x:.1f} {y-r:.1f} c {x+c:.1f} {y-r:.1f} {x+r:.1f} {y-c:.1f} {x+r:.1f} {y:.1f} c f")

    def text(self, x, y, s, size=12, rgb=None, leading=None):
        if rgb:
            self.color(rgb, False)
        self.cmd(f"BT /F1 {size:.1f} Tf {x:.1f} {y:.1f} Td {pdf_text(s)} Tj ET")

    def paragraph(self, x, y, s, width_units, size=11, rgb=None, leading=None, max_lines=None):
        leading = leading or size * 1.45
        lines = wrap_text(s, width_units)
        if max_lines:
            lines = lines[:max_lines]
        for i, line in enumerate(lines):
            self.text(x, y - i * leading, line, size, rgb)
        return y - len(lines) * leading

    def finish_page(self, footer: str):
        self.line(MARGIN, 32, PAGE_W - MARGIN, 32, COLORS["line"], 0.6)
        self.text(MARGIN, 18, "Ladnut Amazon Storefront Visual Layout", 8, COLORS["muted"])
        self.text(PAGE_W - 210, 18, footer, 8, COLORS["muted"])
        stream_bytes = self.stream.encode("latin-1")
        content_id = self.add_obj(f"<< /Length {len(stream_bytes)} >>\nstream\n".encode("latin-1") + stream_bytes + b"endstream")
        page_id = self.add_obj(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>")
        self.pages.append(page_id)

    def save(self, path: Path):
        self.objects[2] = b"<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light /Encoding /UniGB-UCS2-H /DescendantFonts [4 0 R] >>"
        self.objects[3] = b"<< /Type /Font /Subtype /CIDFontType0 /BaseFont /STSong-Light /CIDSystemInfo << /Registry (Adobe) /Ordering (GB1) /Supplement 2 >> >>"
        kids = " ".join(f"{pid} 0 R" for pid in self.pages)
        self.objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(self.pages)} >>".encode("latin-1")
        self.objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
        output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for i, obj in enumerate(self.objects, start=1):
            offsets.append(len(output))
            output.extend(f"{i} 0 obj\n".encode("latin-1"))
            output.extend(obj)
            output.extend(b"\nendobj\n")
        xref = len(output)
        output.extend(f"xref\n0 {len(self.objects)+1}\n0000000000 65535 f \n".encode("latin-1"))
        for off in offsets[1:]:
            output.extend(f"{off:010d} 00000 n \n".encode("latin-1"))
        output.extend(f"trailer << /Size {len(self.objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("latin-1"))
        path.write_bytes(output)


def header(pdf: PDF, title: str, eyebrow="STORE FRONT SYSTEM"):
    pdf.text(MARGIN, PAGE_H - 44, eyebrow, 9, COLORS["sage_dark"])
    pdf.text(MARGIN, PAGE_H - 74, title, 24, COLORS["ink"])
    pdf.line(MARGIN, PAGE_H - 88, PAGE_W - MARGIN, PAGE_H - 88, COLORS["sage"], 1.2)


def draw_card(pdf: PDF, x, y, w, h, title, body, accent="sage"):
    pdf.rect(x, y, w, h, COLORS["white"], True, True, COLORS["line"])
    pdf.rect(x, y + h - 7, w, 7, COLORS[accent], True, False)
    pdf.text(x + 14, y + h - 28, title, 12.5, COLORS["ink"])
    pdf.paragraph(x + 14, y + h - 48, body, (w - 28) / 7.0, 9.2, COLORS["muted"], 13, 8)


def cover(pdf: PDF):
    pdf.begin_page()
    pdf.rect(0, 0, PAGE_W, PAGE_H, COLORS["mist"], True, False)
    pdf.circle(705, 435, 115, COLORS["sage"])
    pdf.circle(760, 370, 74, COLORS["blue"])
    pdf.circle(645, 310, 48, COLORS["sand"])
    pdf.text(70, 405, BRAND["name"], 48, COLORS["sage_dark"])
    pdf.text(72, 365, "Amazon Storefront Visual Layout", 25, COLORS["ink"])
    pdf.paragraph(74, 325, "完整品牌旗舰店视觉排版方案｜用于内部汇报与设计执行", 70, 15, COLORS["muted"], 22)
    pdf.rect(72, 210, 560, 90, COLORS["white"], True, True, COLORS["line"])
    pdf.text(95, 263, BRAND["tagline"], 19, COLORS["ink"])
    pdf.text(95, 235, "品牌定位：宠物家庭健康护理品牌", 13, COLORS["muted"])
    pdf.text(95, 214, "两大技术支点：OzoIon CleanAir System™ / CareRhythm™ Daily Wellness", 12, COLORS["sage_dark"])
    pdf.text(72, 112, "Document purpose: visual hierarchy, storefront modules, image direction, copy focus and execution guidance.", 10, COLORS["muted"])
    pdf.finish_page("Cover")


def overview_page(pdf: PDF):
    pdf.begin_page(); header(pdf, "整体视觉方向")
    x, y, w, h = MARGIN, PAGE_H - 145, 360, 86
    for idx, (t, b) in enumerate(DIRECTION):
        draw_card(pdf, x + (idx % 2) * 390, y - (idx // 2) * 120, w, h, t, b, "sage" if idx % 2 == 0 else "blue")
    pdf.text(MARGIN, 92, "视觉基调关键词：Clean / Warm / Systematic / Trustworthy / Pet-Family Friendly", 15, COLORS["ink"])
    pdf.paragraph(MARGIN, 66, "整体设计避免过度促销感，采用“家居生活方式 + 技术图示 + 产品转化卡”的组合，让美国消费者快速理解 Ladnut 是一个专业且可信赖的宠物家庭健康护理品牌。", 120, 11, COLORS["muted"], 17)
    pdf.finish_page("Section 2")


def architecture_page(pdf: PDF):
    pdf.begin_page(); header(pdf, "信息架构总览：Home / Clean Air / Daily Wellness / Our Impact")
    start_x, y = 64, 375
    card_w, card_h, gap = 166, 145, 24
    for i, (name, desc) in enumerate(ARCHITECTURE):
        x = start_x + i * (card_w + gap)
        pdf.rect(x, y, card_w, card_h, COLORS["white"], True, True, COLORS["line"])
        pdf.circle(x + 32, y + 105, 20, [COLORS["sage"], COLORS["blue"], COLORS["sand"], COLORS["sage_dark"]][i])
        pdf.text(x + 18, y + 99, f"0{i+1}", 12, COLORS["white"])
        pdf.text(x + 18, y + 70, name, 15, COLORS["ink"])
        pdf.paragraph(x + 18, y + 45, desc, 20, 8.8, COLORS["muted"], 13)
        if i < 3:
            pdf.line(x + card_w + 5, y + 72, x + card_w + gap - 5, y + 72, COLORS["sage_dark"], 1.0)
    pdf.text(MARGIN, 235, "页面层级逻辑", 18, COLORS["ink"])
    points = ["Home 是品牌总入口与导航中心。", "Clean Air 与 Daily Wellness 是两条产品系统路径。", "Our Impact 回收品牌使命、责任与长期信任。", "所有页面共享同一视觉母版，降低设计执行成本并提高品牌一致性。"]
    for i, p in enumerate(points):
        pdf.circle(MARGIN + 8, 198 - i * 32, 5, COLORS["sage_dark"])
        pdf.text(MARGIN + 24, 193 - i * 32, p, 12, COLORS["muted"])
    pdf.finish_page("Section 3")


def module_card(pdf: PDF, x, y, w, h, mod: Module, number: int):
    pdf.rect(x, y, w, h, COLORS["white"], True, True, COLORS["line"])
    pdf.rect(x, y + h - 34, w, 34, COLORS["mist"], True, False)
    pdf.circle(x + 22, y + h - 17, 12, COLORS["sage_dark"])
    pdf.text(x + 15.5, y + h - 22, str(number), 10, COLORS["white"])
    pdf.text(x + 42, y + h - 23, mod.name, 13, COLORS["ink"])
    fields = [("布局形式", mod.layout), ("视觉内容", mod.visual), ("文案重点", mod.copy), ("设计重点", mod.design)]
    yy = y + h - 54
    for label, val in fields:
        pdf.text(x + 16, yy, label, 8.5, COLORS["sage_dark"])
        yy = pdf.paragraph(x + 70, yy, val, (w - 88) / 6.7, 8.4, COLORS["muted"], 11, 3) - 4


def page_plan(pdf: PDF, plan: PagePlan, sec_num: int):
    pdf.begin_page(); header(pdf, plan.title, f"SECTION {sec_num}")
    pdf.text(MARGIN, PAGE_H - 118, "页面目标", 13, COLORS["sage_dark"])
    pdf.paragraph(MARGIN + 72, PAGE_H - 118, plan.goal, 96, 10.2, COLORS["muted"], 15, 3)
    per_page = 2
    chunks = [plan.modules[i:i+per_page] for i in range(0, len(plan.modules), per_page)]
    first = True
    page_index = 1
    for chunk_idx, chunk in enumerate(chunks):
        if not first:
            pdf.finish_page(f"Section {sec_num}.{page_index-1}")
            pdf.begin_page(); header(pdf, plan.title + "（续）", f"SECTION {sec_num}")
        first = False
        y_positions = [286, 86]
        for j, mod in enumerate(chunk):
            module_card(pdf, MARGIN, y_positions[j], PAGE_W - 2*MARGIN, 168, mod, chunk_idx*per_page + j + 1)
        page_index += 1
    pdf.finish_page(f"Section {sec_num}.{page_index-1}")


def rhythm_page(pdf: PDF):
    pdf.begin_page(); header(pdf, "页面节奏与设计原则")
    for i, item in enumerate(RHYTHM):
        y = 420 - i * 62
        pdf.circle(MARGIN + 11, y + 4, 11, COLORS["sage_dark"])
        pdf.text(MARGIN + 5, y, str(i+1), 10, COLORS["white"])
        pdf.paragraph(MARGIN + 36, y + 5, item, 116, 12, COLORS["ink"], 17, 2)
    pdf.rect(530, 104, 238, 300, COLORS["white"], True, True, COLORS["line"])
    pdf.text(552, 368, "Storefront Module Rhythm", 14, COLORS["sage_dark"])
    labels = ["Hero", "Education", "Product", "Scenario", "Trust"]
    for i, lab in enumerate(labels):
        pdf.rect(555, 325 - i*44, 185 - i*16, 24, [COLORS["sage"], COLORS["blue"], COLORS["sand"], COLORS["mist"], COLORS["sage_dark"]][i], True, False)
        pdf.text(565, 331 - i*44, lab, 10, COLORS["white"] if i==4 else COLORS["ink"])
    pdf.finish_page("Section 8")


def assets_page(pdf: PDF):
    pdf.begin_page(); header(pdf, "关键素材清单")
    for i, item in enumerate(ASSETS):
        y = 410 - i * 70
        draw_card(pdf, MARGIN, y, PAGE_W - 2*MARGIN, 50, f"Asset {i+1}", item, "blue" if i % 2 else "sage")
    pdf.finish_page("Section 9")


def recommendations_page(pdf: PDF):
    pdf.begin_page(); header(pdf, "最终执行建议")
    for i, item in enumerate(RECOMMENDATIONS):
        y = 420 - i * 72
        pdf.circle(MARGIN + 14, y + 4, 14, COLORS["sage_dark"])
        pdf.text(MARGIN + 6, y - 1, f"{i+1}", 12, COLORS["white"])
        pdf.paragraph(MARGIN + 44, y + 8, item, 110, 12.5, COLORS["ink"], 18, 2)
    pdf.finish_page("Section 10")


def conclusion_page(pdf: PDF):
    pdf.begin_page()
    pdf.rect(0, 0, PAGE_W, PAGE_H, COLORS["sage_dark"], True, False)
    pdf.circle(710, 455, 110, COLORS["sage"])
    pdf.circle(770, 330, 70, COLORS["blue"])
    pdf.text(70, 464, "Final Conclusion", 32, COLORS["white"])
    pdf.text(70, 424, "建议实施该 Storefront 视觉方案", 25, COLORS["cream"])
    y = 355
    for i, item in enumerate(CONCLUSION[1:], 1):
        pdf.circle(92, y - 2, 13, COLORS["cream"])
        pdf.text(86, y - 7, str(i), 12, COLORS["sage_dark"])
        pdf.paragraph(122, y + 5, item, 100, 14, COLORS["white"], 21, 2)
        y -= 68
    pdf.text(70, 58, BRAND["tagline"], 15, COLORS["cream"])
    pdf.finish_page("Conclusion")


def build_pdf():
    pdf = PDF()
    pdf.add_obj("placeholder catalog")
    pdf.add_obj("placeholder pages")
    pdf.add_obj("placeholder font")
    pdf.add_obj("placeholder descendant")
    cover(pdf)
    overview_page(pdf)
    architecture_page(pdf)
    for idx, plan in enumerate(PAGES, start=4):
        page_plan(pdf, plan, idx)
    rhythm_page(pdf)
    assets_page(pdf)
    recommendations_page(pdf)
    conclusion_page(pdf)
    pdf.save(OUT_PDF)


def build_markdown():
    lines = [
        "# Ladnut Amazon Storefront Visual Layout",
        "",
        f"**品牌名：** {BRAND['name']}",
        f"**品牌主张：** {BRAND['tagline']}",
        f"**品牌定位：** {BRAND['positioning']}",
        f"**两大技术支点：** {BRAND['systems'][0]}；{BRAND['systems'][1]}",
        "",
        "## 1. 封面",
        "- 标题：Ladnut Amazon Storefront Visual Layout",
        "- 副标题：完整品牌旗舰店视觉排版方案｜用于内部汇报与设计执行",
        f"- 核心口号：{BRAND['tagline']}",
        "- 封面视觉：浅绿色家居底色、空气流线、宠物与产品组合剪影，突出洁净、温暖与系统化。",
        "",
        "## 2. 整体视觉方向（色彩、字体、品牌调性）",
    ]
    for t, b in DIRECTION:
        lines.append(f"- **{t}：** {b}")
    lines += ["", "## 3. 信息架构总览（Home / Clean Air / Daily Wellness / Our Impact）"]
    for name, desc in ARCHITECTURE:
        lines.append(f"- **{name}：** {desc}")
    for idx, plan in enumerate(PAGES, start=4):
        lines += ["", f"## {idx}. {plan.title}", f"- **页面目标：** {plan.goal}"]
        for n, mod in enumerate(plan.modules, 1):
            lines += [
                f"### 模块 {n}：{mod.name}",
                f"- **模块名称：** {mod.name}",
                f"- **布局形式：** {mod.layout}",
                f"- **视觉内容：** {mod.visual}",
                f"- **文案重点：** {mod.copy}",
                f"- **设计重点：** {mod.design}",
            ]
    lines += ["", "## 8. 页面节奏与设计原则"]
    lines += [f"- {item}" for item in RHYTHM]
    lines += ["", "## 9. 关键素材清单"]
    lines += [f"- {item}" for item in ASSETS]
    lines += ["", "## 10. 最终执行建议"]
    lines += [f"- {item}" for item in RECOMMENDATIONS]
    lines += ["", "## 最后一页：明确结论"]
    lines += [f"- {item}" for item in CONCLUSION]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build_markdown()
    build_pdf()
    print(f"Generated {OUT_PDF} and {OUT_MD}")
