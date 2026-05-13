#!/usr/bin/env python3
"""Generate the Ladnut Amazon Storefront strategy PDF without external packages.

The script writes a polished, presentation-style PDF using standard PDF primitives
and built-in CJK fonts so it can run in minimal CI/container environments.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import textwrap

OUT = Path(__file__).with_name("Ladnut_Amazon_Storefront_建设方案.pdf")
PAGE_W, PAGE_H = 595.28, 841.89  # A4 portrait points
MARGIN = 46

BG = (247, 246, 241)
INK = (45, 60, 55)
MUTED = (91, 106, 99)
GREEN = (80, 124, 104)
SAGE = (210, 226, 215)
WARM = (232, 197, 153)
BLUE = (217, 233, 235)
WHITE = (255, 255, 255)
RED = (166, 83, 72)


def rgb(c):
    return "{:.3f} {:.3f} {:.3f}".format(c[0] / 255, c[1] / 255, c[2] / 255)


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def hex_utf16(s: str) -> str:
    return s.encode("utf-16-be").hex().upper()


def text_width(s: str, size: float) -> float:
    width = 0.0
    for ch in s:
        o = ord(ch)
        if ch in " .,:;!-()/&+™#'’–—":
            width += 0.33 * size
        elif o < 128:
            width += 0.55 * size
        else:
            width += 0.95 * size
    return width


def wrap_text(s: str, size: float, max_width: float) -> list[str]:
    lines: list[str] = []
    paragraphs = s.split("\n")
    for para in paragraphs:
        if not para.strip():
            lines.append("")
            continue
        chunks: list[str] = []
        for token in para.split(" "):
            if any(ord(c) > 127 for c in token) and len(token) > 14:
                chunks.extend(list(token))
            else:
                chunks.append(token)
        line = ""
        for chunk in chunks:
            sep = "" if (not line or len(chunk) == 1 and ord(chunk[0]) > 127) else " "
            candidate = line + sep + chunk
            if text_width(candidate, size) <= max_width or not line:
                line = candidate
            else:
                lines.append(line)
                line = chunk
        if line:
            lines.append(line)
    return lines


@dataclass
class Page:
    ops: list[str]

    def rect(self, x, y, w, h, fill=None, stroke=None, lw=1):
        if fill:
            self.ops.append(f"q {rgb(fill)} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f Q")
        if stroke:
            self.ops.append(f"q {rgb(stroke)} RG {lw:.2f} w {x:.2f} {y:.2f} {w:.2f} {h:.2f} re S Q")

    def line(self, x1, y1, x2, y2, color=GREEN, lw=1):
        self.ops.append(f"q {rgb(color)} RG {lw:.2f} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S Q")

    def circle(self, x, y, r, fill=None, stroke=None):
        # Bezier approximation.
        k = 0.55228475 * r
        parts = [f"{x+r:.2f} {y:.2f} m", f"{x+r:.2f} {y+k:.2f} {x+k:.2f} {y+r:.2f} {x:.2f} {y+r:.2f} c",
                 f"{x-k:.2f} {y+r:.2f} {x-r:.2f} {y+k:.2f} {x-r:.2f} {y:.2f} c",
                 f"{x-r:.2f} {y-k:.2f} {x-k:.2f} {y-r:.2f} {x:.2f} {y-r:.2f} c",
                 f"{x+k:.2f} {y-r:.2f} {x+r:.2f} {y-k:.2f} {x+r:.2f} {y:.2f} c"]
        if fill:
            self.ops.append(f"q {rgb(fill)} rg {' '.join(parts)} f Q")
        if stroke:
            self.ops.append(f"q {rgb(stroke)} RG 1 w {' '.join(parts)} S Q")

    def text(self, x, y, s, size=11, color=INK, font="F0"):
        self.ops.append(f"BT {rgb(color)} rg /{font} {size:.2f} Tf 1 0 0 1 {x:.2f} {y:.2f} Tm <{hex_utf16(s)}> Tj ET")

    def para(self, x, y, s, size=10.5, color=INK, width=500, leading=None, bullet=False):
        leading = leading or size * 1.45
        for i, line in enumerate(wrap_text(s, size, width - (12 if bullet else 0))):
            if bullet and i == 0:
                self.text(x, y, "•", size, color)
                self.text(x + 12, y, line, size, color)
            else:
                self.text(x + (12 if bullet else 0), y, line, size, color)
            y -= leading
        return y


class Pdf:
    def __init__(self):
        self.pages: list[Page] = []

    def new_page(self, title=None, section=None) -> Page:
        p = Page([])
        p.rect(0, 0, PAGE_W, PAGE_H, fill=BG)
        p.rect(0, PAGE_H - 10, PAGE_W, 10, fill=GREEN)
        p.circle(PAGE_W - 80, PAGE_H - 70, 72, fill=BLUE)
        p.circle(PAGE_W - 25, PAGE_H - 28, 28, fill=SAGE)
        if section:
            p.text(MARGIN, PAGE_H - 36, section, 8.5, GREEN)
        if title:
            p.text(MARGIN, PAGE_H - 68, title, 21, INK)
            p.line(MARGIN, PAGE_H - 84, PAGE_W - MARGIN, PAGE_H - 84, SAGE, 2)
        self.pages.append(p)
        return p

    def save(self, path: Path):
        objects = []
        # Catalog, Pages, Font F0 (CJK), Font F1/F2, page/content objects later.
        objects.append("<< /Type /Catalog /Pages 2 0 R >>")
        kids = " ".join(f"{6 + i*2} 0 R" for i in range(len(self.pages)))
        objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(self.pages)} >>")
        objects.append("<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light /Encoding /UniGB-UCS2-H /DescendantFonts [4 0 R] >>")
        objects.append("<< /Type /Font /Subtype /CIDFontType0 /BaseFont /STSong-Light /CIDSystemInfo << /Registry (Adobe) /Ordering (GB1) /Supplement 2 >> >>")
        objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        for page in self.pages:
            content = "\n".join(page.ops).encode("utf-8")
            content_obj_num = len(objects) + 2
            page_obj = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W:.2f} {PAGE_H:.2f}] /Resources << /Font << /F0 3 0 R /F2 5 0 R >> >> /Contents {content_obj_num} 0 R >>"
            objects.append(page_obj)
            objects.append(f"<< /Length {len(content)} >>\nstream\n{content.decode('utf-8')}\nendstream")
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for i, obj in enumerate(objects, start=1):
            offsets.append(len(out))
            out.extend(f"{i} 0 obj\n{obj}\nendobj\n".encode("utf-8"))
        xref = len(out)
        out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
        for off in offsets[1:]:
            out.extend(f"{off:010d} 00000 n \n".encode())
        out.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
        path.write_bytes(out)


def card(p, x, y, w, h, title, body, accent=GREEN):
    p.rect(x, y - h, w, h, fill=WHITE, stroke=SAGE, lw=0.8)
    p.rect(x, y - 8, w, 8, fill=accent)
    p.text(x + 14, y - 28, title, 12.5, INK)
    return p.para(x + 14, y - 48, body, 9.2, MUTED, w - 28)


def module(p, y, name, title, body, bullets=None):
    p.text(MARGIN, y, name, 8.8, GREEN)
    y -= 18
    p.text(MARGIN, y, title, 14.5, INK)
    y -= 22
    y = p.para(MARGIN, y, body, 9.8, MUTED, PAGE_W - 2 * MARGIN)
    if bullets:
        y -= 4
        for b in bullets:
            y = p.para(MARGIN + 8, y, b, 9.2, INK, PAGE_W - 2 * MARGIN - 8, bullet=True)
    return y - 18


def footer(p, n):
    p.line(MARGIN, 35, PAGE_W - MARGIN, 35, SAGE, 0.7)
    p.text(MARGIN, 20, "Ladnut Amazon Storefront Strategy Proposal", 7.5, MUTED)
    p.text(PAGE_W - MARGIN - 20, 20, str(n), 7.5, MUTED)


def build():
    pdf = Pdf()

    p = pdf.new_page()
    p.rect(0, 0, PAGE_W, PAGE_H, fill=(244, 244, 237))
    p.rect(0, PAGE_H - 120, PAGE_W, 120, fill=GREEN)
    p.circle(PAGE_W - 120, PAGE_H - 115, 90, fill=SAGE)
    p.circle(82, 165, 55, fill=BLUE)
    p.text(MARGIN, PAGE_H - 88, "LADNUT", 15, WHITE)
    p.text(MARGIN, 620, "《Ladnut 亚马逊品牌旗舰店", 25, INK)
    p.text(MARGIN, 585, "Storefront 建设方案》", 25, INK)
    p.text(MARGIN, 542, "基于 OzoIon CleanAir System™ 与 CareRhythm™ Daily Wellness", 13, GREEN)
    p.text(MARGIN, 520, "的品牌技术架构与页面规划", 13, GREEN)
    p.rect(MARGIN, 430, PAGE_W - 2 * MARGIN, 86, fill=WHITE, stroke=SAGE)
    p.text(MARGIN + 18, 484, "文档用途", 11, GREEN)
    p.para(MARGIN + 18, 462, "用于向公司上级汇报 Ladnut Amazon Storefront 的建设方案，讨论是否实施。", 12, INK, PAGE_W - 2 * MARGIN - 36)
    p.text(MARGIN, 340, "Cleaner Homes. Healthier Routines. Happier Pets.", 17, INK)
    p.text(MARGIN, 310, "温暖 · 干净 · 可信 · 有科技底座", 11, MUTED)
    p.text(MARGIN, 90, "专业汇报版 PDF / 中文为主，保留核心英文品牌文案", 9, MUTED)
    footer(p, 1)

    p = pdf.new_page("项目背景", "01 / Background")
    y = 725
    p.para(MARGIN, y, "Ladnut 目前已有多个宠物相关产品线，包括：", 11.5, INK, 500)
    y -= 45
    card(p, MARGIN, y, 240, 105, "清洁净化系列", "猫咪除臭器，未来计划延展空气净化设备。", GREEN)
    card(p, MARGIN + 265, y, 240, 105, "宠物护理系列", "狗狗洁牙粉，狗狗蘑菇咀嚼片。", WARM)
    y -= 145
    p.text(MARGIN, y, "当前问题", 14.5, INK); y -= 24
    y = p.para(MARGIN, y, "如果这些产品只是以单个 SKU 的形式在 Amazon 上独立销售，消费者很难理解它们之间的关系，也难以形成对品牌的长期记忆。", 11, MUTED, 500)
    y -= 22
    p.rect(MARGIN, y - 130, 500, 130, fill=WHITE, stroke=SAGE)
    p.text(MARGIN + 16, y - 28, "本次 Storefront 建设核心目的", 13, GREEN)
    p.para(MARGIN + 16, y - 54, "不是简单陈列产品，而是通过统一的品牌逻辑，将 Ladnut 打造成一个有技术底座、有情感温度、有社会责任感的美国宠物家庭健康品牌。", 11.5, INK, 468)
    footer(p, 2)

    p = pdf.new_page("品牌核心定位与品牌主张", "02 / Positioning")
    y = 735
    p.text(MARGIN, y, "品牌核心定位", 15, INK); y -= 32
    p.rect(MARGIN, y - 105, 500, 105, fill=WHITE, stroke=SAGE)
    p.para(MARGIN + 18, y - 28, "Ladnut is a pet home wellness brand built around cleaner air, easier care routines, and happier everyday lives for pets and the people who love them.", 13, GREEN, 464)
    y -= 142
    p.para(MARGIN, y, "中文理解：Ladnut 不是单纯销售宠物用品，而是围绕宠物家庭中的空气异味、日常清洁、口腔护理、老龄犬健康支持等真实问题，构建一个“宠物家庭健康护理品牌”。", 10.8, MUTED, 500)
    y -= 95
    p.text(MARGIN, y, "品牌主张", 15, INK); y -= 38
    p.text(MARGIN, y, "Cleaner Homes. Healthier Routines. Happier Pets.", 19, GREEN); y -= 35
    p.text(MARGIN, y, "更洁净的家，更健康的日常，更快乐的宠物。", 13, INK); y -= 44
    card(p, MARGIN, y, 155, 115, "Cleaner Homes", "家庭空间、猫砂盆异味管理、宠物活动区空气清新。", GREEN)
    card(p, MARGIN + 172, y, 155, 115, "Healthier Routines", "更容易坚持的日常护养习惯。", WARM)
    card(p, MARGIN + 344, y, 155, 115, "Happier Pets", "更舒适、更少压力、更自然的宠物生活状态。", BLUE)
    footer(p, 3)

    p = pdf.new_page("两大技术支点", "03 / Technology Architecture")
    y = 730
    p.text(MARGIN, y, "OzoIon CleanAir System™", 16, GREEN); y -= 25
    y = p.para(MARGIN, y, "A dual-action air care system that uses ozone to help break down odor-causing molecules and negative ions to help purify lingering airborne residues.", 11.5, INK, 500)
    y -= 10
    y = p.para(MARGIN, y, "中文解释：OzoIon CleanAir System™ 是 Ladnut 清洁净化系列的核心技术系统。它通过臭氧帮助分解异味分子，再通过负离子帮助吸附空气中的异味残留、灰尘、宠物皮屑等微粒，使空气更清新。", 10, MUTED, 500)
    y -= 20
    x0 = MARGIN
    headers = ["Ozone Odor Breakdown", "Source-Level Odor Control", "Negative Ion Residue Purification", "Low-Residue Freshness"]
    bodies = ["分解猫砂、尿液、潮湿环境和宠物活动产生的异味分子。", "处理残留、潮湿和微生物活动带来的异味来源。", "吸附异味残留、灰尘、宠物皮屑等颗粒并帮助沉降。", "臭氧工作后自然回归氧气，负离子帮助减少空气残留。"]
    for i, (h, b) in enumerate(zip(headers, bodies)):
        card(p, x0 + (i % 2) * 255, y - (i // 2) * 108, 235, 86, h, b, GREEN if i < 2 else BLUE)
    y -= 250
    p.text(MARGIN, y, "CareRhythm™ Daily Wellness", 16, GREEN); y -= 26
    y = p.para(MARGIN, y, "A daily wellness approach designed to help pet families build easier, repeatable care routines for oral hygiene, senior support, and everyday vitality.", 11.5, INK, 500)
    y -= 10
    p.para(MARGIN, y, "中文解释：CareRhythm™ Daily Wellness 是 Ladnut 宠物护理系列的核心理念。它强调通过更容易坚持的小习惯，帮助宠物主人完成日常口腔护理、老龄犬支持和长期健康管理。", 10, MUTED, 500)
    footer(p, 4)

    p = pdf.new_page("Amazon Storefront 页面总架构", "04 / Storefront Structure")
    y = 700
    pages = [("Home", "建立品牌定位、使命和两大产品系统。"), ("Clean Air", "打造 OzoIon CleanAir System™ 技术资产。"), ("Daily Wellness", "打造 CareRhythm™ Daily Wellness 护养体系。"), ("Our Impact", "承载品牌故事、公益理念和环保责任。")]
    for i, (t, b) in enumerate(pages):
        yy = y - i * 125
        p.circle(MARGIN + 20, yy - 20, 20, fill=GREEN if i == 0 else SAGE)
        p.text(MARGIN + 14, yy - 26, str(i + 1), 13, WHITE if i == 0 else INK)
        p.rect(MARGIN + 55, yy - 62, 445, 82, fill=WHITE, stroke=SAGE)
        p.text(MARGIN + 73, yy - 10, t, 15, GREEN)
        p.para(MARGIN + 73, yy - 34, b, 11, MUTED, 400)
        if i < 3:
            p.line(MARGIN + 20, yy - 45, MARGIN + 20, yy - 105, SAGE, 2)
    footer(p, 5)

    p = pdf.new_page("Home 首页规划", "05 / Home Page")
    y = 735
    y = module(p, y, "Module 1 / 顶部 Hero Banner", "Cleaner Homes. Healthier Routines. Happier Pets.", "Smart air care and daily wellness solutions designed to help pet families create cleaner spaces, easier routines, and more comfortable lives.\n视觉建议：干净、温暖、现代的美国宠物家庭场景；重点是“干净的家”和“宠物舒适生活”。")
    y = module(p, y, "Module 2 / 品牌使命模块", "Better care should feel easier for people and kinder for pets.", "Pet life brings love, but it also brings odors, brushing battles, aging worries, and daily care routines that can be hard to keep up with. Ladnut was created to make everyday pet care cleaner, smarter, and easier to repeat — from litter box odor control to oral care and senior dog wellness.")
    y = module(p, y, "Module 3 / 两大产品系统导航", "Clean Air & Odor Control + Daily Wellness Care", "左侧：Powered by the OzoIon CleanAir System™... 右侧：Powered by CareRhythm™ Daily Wellness... 通过两个入口把清洁净化与科学护养连接到统一品牌框架。")
    footer(p, 6)

    p = pdf.new_page("Home 首页规划（续）", "05 / Home Page")
    y = 735
    y = module(p, y, "Module 4 / 主推技术模块", "Meet OzoIon CleanAir System™", "A dual-action approach to cleaner pet air. Pet odors often come from odor-causing molecules, airborne residues, dust, and pet dander released by litter, moisture, urine, and daily pet activity. OzoIon is designed to help care for pet air in two ways: ozone helps break down odor molecules, while negative ions help attract lingering airborne particles and residues.", ["Ozone Odor Breakdown：Helps break down odor-causing molecules commonly associated with litter box use and daily pet activity.", "Source-Level Odor Care：Helps support freshness where pet odors often begin — around litter, moisture, and enclosed pet areas.", "Negative Ion Residue Purification：Helps attract airborne particles such as dust, pet dander, and lingering odor residues.", "Freshness Without Heavy Fragrance：Supports a cleaner-feeling space without relying on overpowering perfume sprays."])
    y = module(p, y, "Module 5 / 首页主推产品", "Ladnut Cat Litter Box Deodorizer", "Dual-action freshness for litter box spaces. Designed for everyday cat homes, this compact deodorizer uses the OzoIon CleanAir System™ to help break down litter box odor molecules and reduce lingering airborne residues. With smart sensing, automatic cycling, and a rechargeable design, it supports a cleaner-feeling pet space with less effort.", ["Helps break down litter box odor molecules", "Negative ion support for airborne residue purification", "Smart sensing for pet-aware operation", "Compact, rechargeable design", "Helps reduce reliance on heavy fragrance sprays"])
    footer(p, 7)

    p = pdf.new_page("Clean Air 清洁净化系列页面规划", "06 / Clean Air")
    y = 735
    y = module(p, y, "Module 1 / 页面 Hero", "Clean air, built for pet homes.", "OzoIon CleanAir System™ uses ozone to help break down odor-causing molecules and negative ions to help purify lingering airborne residues — supporting fresher, cleaner pet spaces.")
    y = module(p, y, "Module 2 / 问题定义", "Pet odor is more than a smell problem. It is an air-quality problem.", "Litter boxes, moisture, urine residue, and enclosed pet spaces can release both odor molecules and fine airborne particles into the air. Sprays may cover the smell temporarily, but Ladnut’s clean air approach is designed to help address the problem more directly — by helping break down odors at the source and reduce lingering residues in the air.")
    y = module(p, y, "Module 3 / OzoIon 技术原理模块", "The OzoIon CleanAir System™", "Ozone odor breakdown + negative ion residue purification. 该模块建议用动态图示或四象限图解释“臭氧分解异味分子 + 负离子净化残留颗粒”的双路径。")
    footer(p, 8)

    p = pdf.new_page("Clean Air 清洁净化系列页面规划（续）", "06 / Clean Air")
    y = 735
    y = module(p, y, "Module 3 / 技术支柱", "OzoIon 四大支柱", "页面中建议以图标卡片呈现以下技术利益点。", ["Breaks Down Odor Molecules：Ozone helps react with odor-causing compounds commonly associated with litter, urine, moisture, and pet waste.", "Helps Control Odor at the Source：Ozone-based odor care helps support cleaner, fresher spaces where odor often begins.", "Purifies Lingering Airborne Residues：Negative ions help attract particles such as odor residues, dust, and pet dander.", "Freshness Without Heavy Fragrance：Supports a fresher-feeling environment without heavy fragrance buildup."])
    y = module(p, y, "Module 4 / 现有产品陈列", "Compact odor control for litter box spaces.", "Ladnut Cat Litter Box Deodorizer uses OzoIon dual-action air care to help break down litter box odor molecules and reduce lingering airborne residues. Smart sensing helps the device work around your cat’s natural routine, while its rechargeable design makes daily use simple.", ["For litter box odor zones", "Ozone support for odor molecule breakdown", "Negative ion support for airborne residue purification", "Smart motion sensing", "Rechargeable and compact", "Helps reduce reliance on heavy fragrance sprays"])
    footer(p, 9)

    p = pdf.new_page("Clean Air 清洁净化系列页面规划（场景与延展）", "06 / Clean Air")
    y = 735
    y = module(p, y, "Module 5 / 使用场景模块", "Freshness for the places pets actually use.", "建议用真实家居分区图展示产品不是“孤立电器”，而是嵌入美国宠物家庭真实生活空间。", ["Apartment Living：Helps make small pet spaces feel more comfortable.", "Laundry Rooms：Supports a cleaner-feeling corner for litter box routines.", "Bathrooms：Compact air care for enclosed litter box areas.", "Multi-Cat Homes：Helps support a more consistent odor-control routine."])
    y = module(p, y, "Module 6 / 未来空气净化设备延展", "From litter box odor care to whole-room freshness.", "OzoIon CleanAir System™ begins with odor molecule breakdown and airborne residue purification for litter box spaces, but its long-term vision is broader: a pet air care platform designed to support cleaner, fresher environments across pet corners, litter rooms, bedrooms, and shared home spaces.", ["Odor molecule breakdown", "Airborne residue purification", "Pet dander management", "Room-level air care support", "Future pet air purifier products"])
    footer(p, 10)

    p = pdf.new_page("Daily Wellness 科学护养系列页面规划", "07 / Daily Wellness")
    y = 735
    y = module(p, y, "Module 1 / 页面 Hero", "Daily care, made easier to keep.", "CareRhythm™ Daily Wellness helps pet families build simple, repeatable routines for oral hygiene, senior support, and everyday vitality.")
    y = module(p, y, "Module 2 / CareRhythm™ 理念模块", "Small routines can protect the bigger life you share.", "The best pet care is not always the most complicated. It is the care your pet will accept and your family can repeat. CareRhythm™ Daily Wellness is Ladnut’s approach to daily care — simple, science-informed products designed to fit into real feeding, aging, and wellness routines.")
    y = module(p, y, "Module 3 / 狗狗洁牙粉产品模块", "No-fight oral care for everyday freshness.", "For dogs who resist toothbrushes, better oral care starts with a routine they can accept. Ladnut Dog Dental Powder is made to mix easily with meals, helping support daily oral hygiene and fresher breath without turning care time into a struggle.", ["Easy mealtime dental routine", "Helps support fresher breath", "Designed for dogs who resist brushing", "Sprinkle over food and serve", "A simpler way to build daily oral care"])
    footer(p, 11)

    p = pdf.new_page("Daily Wellness 科学护养系列页面规划（续）", "07 / Daily Wellness")
    y = 735
    y = module(p, y, "Module 4 / 狗狗蘑菇咀嚼片产品模块", "Inside-out support for aging dogs.", "Aging dogs need care that goes beyond the surface. Ladnut Mushroom Chews are designed as a daily functional wellness treat, with a mushroom-based blend to help support immune balance, normal cellular wellness, skin comfort, and everyday senior vitality.", ["Functional mushroom blend", "Daily senior wellness support", "Helps support immune balance", "Supports normal cellular wellness", "Soft chew format for easy daily use"])
    y = module(p, y, "Module 5 / 共同逻辑模块", "Wellness that fits into real life.", "From oral care to senior wellness, CareRhythm™ products are built around one idea: better care works best when it fits naturally into everyday life.", ["Oral Care Routine：Mealtime powder / Fresher breath support / No brushing battle / Daily repeatability", "Senior Wellness Routine：Daily soft chew / Immune balance support / Easy senior care / Long-term care mindset"])
    footer(p, 12)

    p = pdf.new_page("About Us / Our Impact 页面规划", "08 / Our Impact")
    y = 735
    y = module(p, y, "Module 1 / About Hero", "Born for the real homes pets live in.", "Ladnut was created for pet families who want cleaner spaces, easier routines, and care that feels thoughtful from the inside out.")
    y = module(p, y, "Module 2 / Our Story", "品牌起源故事", "Ladnut began with a simple truth every pet parent understands: pets fill our homes with love, but pet life also brings odors, brushing struggles, aging worries, and daily care routines that can be hard to keep up with. We created Ladnut to make those everyday moments easier. Our clean air products help refresh the spaces where pets live, while our daily wellness products help families build simple routines for oral care and senior support. Because better pet care is about creating a home where pets feel comfortable, people feel confident, and care becomes something families can actually keep doing.")
    y = module(p, y, "Module 3 / Our Mission", "Cleaner homes, healthier routines, happier everyday lives.", "Our mission is to help pet families create cleaner homes, healthier routines, and happier everyday lives through smart air care technology and science-informed daily wellness solutions.", ["Cleaner Shared Spaces", "Easier Daily Routines", "Science with Warmth", "Kindness Beyond the Product"])
    footer(p, 13)

    p = pdf.new_page("About Us / Our Impact 页面规划（续）", "08 / Our Impact")
    y = 735
    y = module(p, y, "Module 4 / Ladnut Fresh Start Program", "Care should reach beyond the homes that buy our products.", "Through the Ladnut Fresh Start Program, our long-term goal is to support cleaner, calmer spaces for shelter pets, foster homes, and rescue families. We believe every pet deserves a healthier place to wait, heal, and be loved.", ["Shelter Air Support：support rescue and foster environments with air care education and product-based support where it can make daily care easier.", "Low-Fragrance Pet Home Education：reduce reliance on heavy fragrance sprays and move toward source-focused, routine-based air care.", "Senior Pet Wellness Awareness：senior pets deserve daily routines that support comfort, dignity, and long-term companionship."])
    y = module(p, y, "Module 5 / 可持续理念", "Designed with responsibility in mind.", "We are working toward pet care systems that reduce unnecessary over-spraying, support rechargeable formats where possible, and encourage longer-lasting routines over single-use habits.", ["Rechargeable product design", "Less heavy fragrance", "Routine-based care"])
    footer(p, 14)

    p = pdf.new_page("素材准备清单", "09 / Asset Checklist")
    y = 715
    p.text(MARGIN, y, "必须提供", 15, GREEN); y -= 30
    for item in ["Ladnut Logo", "猫咪除臭器 3D 图", "猫咪除臭器内部结构图", "狗狗洁牙粉产品图", "狗狗蘑菇咀嚼片产品图"]:
        y = p.para(MARGIN + 10, y, item, 11, INK, 460, bullet=True)
    y -= 25
    p.text(MARGIN, y, "建议补充或让 AI 生成", 15, GREEN); y -= 30
    for item in ["首页宠物家庭生活场景图", "猫砂盆使用场景图", "OzoIon 技术原理图", "负离子颗粒沉降示意图", "狗狗用餐场景图", "老龄犬陪伴场景图", "救助空间 / foster home 场景图"]:
        y = p.para(MARGIN + 10, y, item, 11, INK, 460, bullet=True)
    footer(p, 15)

    p = pdf.new_page("合规表达边界", "10 / Compliance Boundary")
    y = 715
    p.rect(MARGIN, y - 260, 240, 260, fill=WHITE, stroke=SAGE)
    p.text(MARGIN + 16, y - 28, "推荐使用", 15, GREEN)
    yy = y - 55
    for item in ["helps break down odor molecules", "helps address odor at the source", "helps purify lingering airborne residues", "supports a fresher environment", "negative ion support", "designed for litter box odor zones", "pet-aware sensing", "use as directed", "helps support daily oral hygiene", "helps support immune balance", "supports normal cellular wellness", "daily wellness routine"]:
        yy = p.para(MARGIN + 22, yy, item, 8.8, INK, 205, bullet=True)
    p.rect(MARGIN + 265, y - 260, 240, 260, fill=WHITE, stroke=(232, 205, 196))
    p.text(MARGIN + 281, y - 28, "避免使用", 15, RED)
    yy = y - 55
    for item in ["eliminates all odor", "kills 99.9% of bacteria", "completely safe ozone", "100% non-toxic in all use conditions", "sterilizes the air", "medical-grade purification", "prevents disease", "treats dental disease", "cures bad breath", "shrinks lumps", "anti-cancer / tumor support", "best / #1 / most effective"]:
        yy = p.para(MARGIN + 287, yy, item, 8.8, INK, 205, bullet=True)
    y -= 310
    p.rect(MARGIN, y - 125, 500, 125, fill=(255, 250, 245), stroke=WARM)
    p.text(MARGIN + 16, y - 28, "特别提醒：臭氧在美国市场表达需要谨慎", 13.5, RED)
    p.para(MARGIN + 16, y - 55, "可以讲 controlled ozone output、ozone odor breakdown、use as directed、designed for litter box odor zones，但不要写“臭氧完全安全”“100%无毒”“可长时间密闭空间使用”。", 10.5, INK, 468)
    footer(p, 16)

    p = pdf.new_page("实施价值与最终建议", "11 / Recommendation")
    y = 720
    card(p, MARGIN, y, 500, 92, "1. 建立品牌统一认知", "将猫咪除臭器、未来空气净化设备、洁牙粉、蘑菇咀嚼片整合成一个统一的宠物家庭健康护理品牌，而不是零散 SKU 组合。", GREEN)
    y -= 118
    card(p, MARGIN, y, 500, 92, "2. 建立技术资产", "通过 OzoIon CleanAir System™ 和 CareRhythm™ Daily Wellness 两大体系，让品牌拥有可延展、可沉淀、可复用的技术与护理语言。", BLUE)
    y -= 118
    card(p, MARGIN, y, 500, 92, "3. 提升交叉销售机会", "买猫咪除臭器的用户，未来可以被引导到空气净化设备；买洁牙粉的用户，也可以被引导到蘑菇咀嚼片或其他日常护养产品。", WARM)
    y -= 145
    p.text(MARGIN, y, "最终目标", 14, GREEN); y -= 28
    p.text(MARGIN, y, "Cleaner Homes. Healthier Routines. Happier Pets.", 18, INK)
    footer(p, 17)

    p = pdf.new_page("是否建议实施：建议实施", "12 / Final Decision")
    y = 705
    p.rect(MARGIN, y - 185, 500, 185, fill=WHITE, stroke=SAGE)
    p.text(MARGIN + 18, y - 45, "结论", 15, GREEN)
    p.text(MARGIN + 18, y - 82, "建议实施 Ladnut Amazon Storefront 建设。", 19, INK)
    p.para(MARGIN + 18, y - 115, "该项目能够将现有 SKU 整合为一个具备技术底座、情感温度与责任感的品牌系统，并为未来空气净化设备与日常护养产品延展提供统一语言。", 11.2, MUTED, 464)
    y -= 245
    p.text(MARGIN, y, "同步推进事项", 15, GREEN); y -= 32
    for item in ["素材准备：补齐 Logo、产品 3D、内部结构图与关键场景视觉。", "商标检索：对 OzoIon CleanAir System™、CareRhythm™ Daily Wellness、Ladnut Fresh Start Program 等命名进行检索。", "合规审核：重点审核臭氧相关表述、宠物健康支持表述和 Amazon 页面用语边界。"]:
        y = p.para(MARGIN + 8, y, item, 11, INK, 488, bullet=True)
    y -= 35
    p.text(MARGIN, y, "建议下一步：以本方案作为 Storefront 页面信息架构和视觉素材 Brief，进入设计执行与合规预审阶段。", 10.5, MUTED)
    footer(p, 18)

    pdf.save(OUT)


if __name__ == "__main__":
    build()
    print(f"Generated {OUT}")
