"""
韩国文化适应训练游戏
Korea Culture Adaptation Training Game
基于 Pygame 开发 · 面向在韩中国留学生
"""

import pygame
import sys
import math
import time

# ─────────────────────────────────────────
#  初始化
# ─────────────────────────────────────────
pygame.init()

W, H = 900, 620
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("🇰🇷 韩国文化适应训练 · Korea Culture Game")
clock = pygame.time.Clock()

# ─────────────────────────────────────────
#  字体：跨平台自动检测 CJK 字体
# ─────────────────────────────────────────
import os, platform

def _find_cjk_font():
    """
    按优先级自动寻找支持中文+韩文的字体文件路径。
    覆盖 Windows / macOS / Linux 三平台。
    返回 (regular_path_or_None, bold_path_or_None)
    """
    system = platform.system()

    # ── Windows ──────────────────────────
    win_candidates = [
        # 微软雅黑（Win 内置，中文极佳）
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        # 思源黑体（用户自装）
        r"C:\Windows\Fonts\NotoSansCJK-Regular.ttc",
        r"C:\Windows\Fonts\NotoSansCJK-Bold.ttc",
        # 苹方（部分 Win11）
        r"C:\Windows\Fonts\PingFang.ttc",
    ]

    # ── macOS ─────────────────────────────
    mac_candidates = [
        "/System/Library/Fonts/PingFang.ttc",           # 苹方（macOS 内置）
        "/Library/Fonts/NotoSansCJK-Regular.ttc",
        "/Library/Fonts/NotoSansCJK-Bold.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf",
    ]

    # ── Linux ─────────────────────────────
    linux_candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    ]

    if system == "Windows":
        candidates = win_candidates
    elif system == "Darwin":
        candidates = mac_candidates
    else:
        candidates = linux_candidates

    found = [p for p in candidates if os.path.isfile(p)]

    reg  = found[0] if len(found) >= 1 else None
    bold = found[1] if len(found) >= 2 else reg   # bold 找不到就复用 regular
    return reg, bold


def _find_cjk_sysfont():
    """
    通过 pygame.font.SysFont 名称列表寻找 CJK 字体（备用方案）。
    """
    priority = [
        # Windows
        "microsoftyahei", "microsoftyaheibold", "simhei", "simsun",
        "dengxian", "fangsong",
        # macOS
        "pingfang", "pingfangsc", "stheitisc", "hiragino",
        # Linux / 通用
        "notosanscjksc", "notosanscjkkr", "notosanscjk",
        "wqymicrohei", "wqyzenhei", "unifont",
    ]
    available = set(pygame.font.get_fonts())
    for name in priority:
        if name in available:
            return name
    return None


# 尝试文件路径 → 失败则用 SysFont 名称
_reg_path, _bold_path = _find_cjk_font()
_sys_name = None if _reg_path else _find_cjk_sysfont()


def font(size, bold=False):
    # 1. 优先用文件路径
    path = _bold_path if (bold and _bold_path) else _reg_path
    if path:
        try:
            return pygame.font.Font(path, size)
        except Exception:
            pass
    # 2. 尝试 SysFont CJK
    if _sys_name:
        try:
            return pygame.font.SysFont(_sys_name, size, bold=bold)
        except Exception:
            pass
    # 3. 最终回退（会乱码，但不崩溃）
    return pygame.font.SysFont("arial", size, bold=bold)

F_TITLE  = font(26, bold=True)
F_HEAD   = font(18, bold=True)
F_BODY   = font(14)
F_SMALL  = font(12)
F_KO     = font(15, bold=True)
F_HUGE   = font(52, bold=True)

# ─────────────────────────────────────────
#  颜色
# ─────────────────────────────────────────
C = {
    "bg":        (15,  17,  23),
    "panel":     (24,  27,  34),
    "card":      (30,  33,  42),
    "card_h":    (38,  42,  54),
    "border":    (50,  55,  72),
    "border_a":  (80,  90, 120),
    "white":     (240, 240, 240),
    "muted":     (140, 145, 160),
    "green":     ( 3, 199,  90),
    "green_d":   ( 2, 140,  62),
    "green_bg":  (10,  40,  22),
    "blue":      ( 58, 143, 255),
    "blue_bg":   (15,  30,  60),
    "red":       (226,  75,  74),
    "red_bg":    (50,  15,  15),
    "orange":    (255, 140,  66),
    "yellow":    (245, 200,  66),
    "purple":    (167, 139, 250),
    "pink":      (244, 114, 182),
    "text_ok":   (160, 230, 180),
    "text_err":  (230, 160, 160),
}

# ─────────────────────────────────────────
#  游戏数据
# ─────────────────────────────────────────
SCENES = [
    {
        "id": 0,
        "icon": "🏪",
        "scene_name": "편의점 (便利店)",
        "location": "GS25 신촌점 · 신촌역 2번 출구",
        "bg_color": (18, 28, 22),
        "accent": C["green"],
        "npc_emoji": "👩‍💼",
        "npc_name": "收银员 박씨",
        "npc_say": "您好！请问需要袋子吗？",
        "npc_ko": "봉투 드릴까요?",
        "tip": "💡 在韩国，双手接物是尊重的表现。\n拒绝时微笑摆手比沉默更礼貌。",
        "emotion_n": "😊",
        "emotion_g": "😄",
        "emotion_b": "😐",
        "choices": [
            {
                "text": "① 微笑摆手：'괜찮아요，谢谢！'",
                "correct": True,
                "score": 20,
                "fb": "✅ 完美！'괜찮아요'配合微笑摆手是标准的韩式礼貌拒绝。\n收银员会感到被尊重，好感度+1！",
            },
            {
                "text": "② 单手接过找零，低头看手机。",
                "correct": False,
                "score": 5,
                "fb": "💡 单手接零钱在韩国稍显随意。建议双手接\n或右手接、左手轻扶右臂，更显尊重。",
            },
            {
                "text": "③ 不回应，直接盯着商品。",
                "correct": False,
                "score": 0,
                "fb": "❌ 忽视服务员的问话在韩国很不礼貌，\n会让对方觉得被无视，影响印象分。",
            },
        ],
    },
    {
        "id": 1,
        "icon": "🍽️",
        "scene_name": "학생식당 (食堂)",
        "location": "연세대학교 학생식당",
        "bg_color": (22, 20, 15),
        "accent": C["orange"],
        "npc_emoji": "👴",
        "npc_name": "金教授 김교수",
        "npc_say": "来，一起吃吧！",
        "npc_ko": "같이 먹읍시다!",
        "tip": "💡 与长辈或教授同桌，须等对方先动筷。\n用餐前说'잘 먹겠습니다'是基本礼仪。",
        "emotion_n": "🙂",
        "emotion_g": "😊",
        "emotion_b": "😑",
        "choices": [
            {
                "text": "① 说'잘 먹겠습니다'，等教授先动筷。",
                "correct": True,
                "score": 25,
                "fb": "✅ 完美！'잘 먹겠습니다'是用餐前必说的礼貌语，\n等长辈先吃体现了儒家尊老礼仪！",
            },
            {
                "text": "② 感谢教授，立刻开始吃饭。",
                "correct": False,
                "score": 8,
                "fb": "💡 感谢很好，但抢在教授前动筷不符合韩国\n长幼有序的饮食礼仪，稍微等一下哦。",
            },
            {
                "text": "③ 道谢后，低头看手机开始吃。",
                "correct": False,
                "score": 0,
                "fb": "❌ 与长辈同桌看手机非常失礼！\n这会严重影响你与教授的关系。",
            },
        ],
    },
    {
        "id": 2,
        "icon": "🏛️",
        "scene_name": "출입국관리소 (出入境局)",
        "location": "서울출입국·외국인청 · 공덕역",
        "bg_color": (18, 22, 30),
        "accent": C["blue"],
        "npc_emoji": "👨‍💼",
        "npc_name": "工作人员 이씨",
        "npc_say": "您好，是来办外国人登录证的吗？",
        "npc_ko": "외국인등록증 발급 신청이신가요?",
        "tip": "💡 外国人登录证（외국인등록증）须入境90天内办理。\n提前在 Hi Korea 网站预约可节省等待时间。",
        "emotion_n": "😐",
        "emotion_g": "😊",
        "emotion_b": "😤",
        "choices": [
            {
                "text": "① 已网上预约，双手递上全部材料。",
                "correct": True,
                "score": 25,
                "fb": "✅ 非常棒！提前预约+材料齐全体现了对\n工作人员的尊重，流程会更顺畅！",
            },
            {
                "text": "② 是的，但只带了护照，其他不清楚。",
                "correct": False,
                "score": 5,
                "fb": "💡 还需要：证件照×2、住所证明、手续费。\n建议去前在 hikorea.go.kr 确认材料清单。",
            },
            {
                "text": "③ 不确定要不要来，以为网上能搞定。",
                "correct": False,
                "score": 0,
                "fb": "❌ 外国人登录证必须本人到场！\n90天内未办理将面临罚款，请尽快处理。",
            },
        ],
    },
    {
        "id": 3,
        "icon": "🚇",
        "scene_name": "지하철 (地铁)",
        "location": "서울 2호선 · 아침 출근 시간",
        "bg_color": (20, 18, 28),
        "accent": C["purple"],
        "npc_emoji": "👵",
        "npc_name": "老奶奶 할머니",
        "npc_say": "（老奶奶上车，站在你旁边…）",
        "npc_ko": "",
        "tip": "💡 노약자석（老幼专座）为粉/橙色，任何时候\n都不应占用。普通座位也可主动让座。",
        "emotion_n": "😐",
        "emotion_g": "🥰",
        "emotion_b": "😠",
        "choices": [
            {
                "text": "① 立刻起身，微笑示意：'앉으세요'",
                "correct": True,
                "score": 30,
                "fb": "✅ 满分！主动让座并说'앉으세요（请坐）'\n是韩国社会高度认可的温暖行为！",
            },
            {
                "text": "② 假装没看见，继续刷手机。",
                "correct": False,
                "score": 0,
                "fb": "❌ 视而不见在韩国文化中非常失礼，\n周围人会对此侧目，不利于融入社区。",
            },
            {
                "text": "③ 犹豫了，最终没起身。",
                "correct": False,
                "score": 5,
                "fb": "💡 只要老人站在旁边，主动让座是社会期待。\n即便被拒绝，这个姿态本身也很重要！",
            },
        ],
    },
    {
        "id": 4,
        "icon": "☕",
        "scene_name": "카페 (咖啡馆)",
        "location": "연남동 독립 카페 · 홍대입구역",
        "bg_color": (25, 18, 18),
        "accent": C["pink"],
        "npc_emoji": "🧑‍🍳",
        "npc_name": "咖啡师 최씨",
        "npc_say": "您的美式咖啡好了！\n（取餐铃响起 🔔）",
        "npc_ko": "아메리카노 나왔습니다!",
        "tip": "💡 韩国咖啡馆普遍셀프서비스（自取）。\n离开时须将杯子放到반납대（回收台）。",
        "emotion_n": "😊",
        "emotion_g": "😄",
        "emotion_b": "😕",
        "choices": [
            {
                "text": "① 取餐，说'감사합니다'，离开前还杯子。",
                "correct": True,
                "score": 20,
                "fb": "✅ 完美！自取+还杯是韩国咖啡馆基本规范，\n收拾整洁体现了良好的公民意识！",
            },
            {
                "text": "② 继续等，以为咖啡师会送过来。",
                "correct": False,
                "score": 3,
                "fb": "💡 韩国咖啡馆基本是自取制，铃声=可取餐。\n等送餐会让其他订单积压，也很尴尬。",
            },
            {
                "text": "③ 取餐后直接离开，不收拾桌子。",
                "correct": False,
                "score": 8,
                "fb": "💡 堂食须将杯子放到반납대。\n不收拾被视为不礼貌，请养成好习惯。",
            },
        ],
    },
]

# ─────────────────────────────────────────
#  工具函数
# ─────────────────────────────────────────

def draw_rect(surf, color, rect, radius=10, alpha=255, border=0, border_color=None):
    """绘制圆角矩形，支持透明度"""
    x, y, w, h = rect
    if alpha < 255:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0, 0, w, h), border_radius=radius)
        surf.blit(s, (x, y))
    else:
        pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, width=border, border_radius=radius)


def draw_text(surf, text, font_obj, color, x, y, max_w=None, center=False, right=False):
    """单行文字渲染"""
    surf2 = font_obj.render(text, True, color)
    rx = x - surf2.get_width()//2 if center else (x - surf2.get_width() if right else x)
    if max_w and surf2.get_width() > max_w:
        # 截断
        while surf2.get_width() > max_w and len(text) > 1:
            text = text[:-1]
            surf2 = font_obj.render(text+"…", True, color)
    surf.blit(surf2, (rx, y))
    return surf2.get_width()


def draw_multiline(surf, text, font_obj, color, x, y, max_w, line_h=22):
    """自动换行文字"""
    for line in text.split("\n"):
        words = line
        # 按字符逐步渲染
        cur = ""
        cy = y
        for ch in words:
            test = cur + ch
            w = font_obj.size(test)[0]
            if w > max_w and cur:
                surf2 = font_obj.render(cur, True, color)
                surf.blit(surf2, (x, cy))
                cy += line_h
                cur = ch
            else:
                cur = test
        if cur:
            surf2 = font_obj.render(cur, True, color)
            surf.blit(surf2, (x, cy))
            cy += line_h
        y = cy
    return y


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))


def ease_out(t):
    return 1 - (1 - t) ** 3

# ─────────────────────────────────────────
#  状态机
# ─────────────────────────────────────────
STATE_TITLE    = "title"
STATE_SCENE    = "scene"
STATE_FEEDBACK = "feedback"
STATE_SCORE    = "score"

# ─────────────────────────────────────────
#  游戏主类
# ─────────────────────────────────────────
class Game:
    def __init__(self):
        self.state        = STATE_TITLE
        self.scene_idx    = 0
        self.score        = 0
        self.confidence   = 50
        self.culture      = 0
        self.results      = []          # True/False per scene
        self.chosen       = -1          # which choice was picked
        self.answered     = False

        # 动画
        self.anim_t       = 0.0         # 0→1 进场动画
        self.shake_t      = 0.0         # NPC 震动
        self.bounce_t     = 0.0         # NPC 弹跳
        self.stat_anim    = {}          # stat bar targets
        self.particles    = []          # 粒子特效
        self.title_t      = 0.0

        # 按钮 rects（动态生成）
        self.btn_start    = pygame.Rect(0, 0, 0, 0)
        self.btn_choices  = []
        self.btn_next     = pygame.Rect(0, 0, 0, 0)
        self.btn_restart  = pygame.Rect(0, 0, 0, 0)
        self.hover_idx    = -1

    def scene(self):
        return SCENES[self.scene_idx]

    # ── 状态转换 ──────────────────────────

    def start_game(self):
        self.state      = STATE_SCENE
        self.scene_idx  = 0
        self.score      = 0
        self.confidence = 50
        self.culture    = 0
        self.results    = []
        self.answered   = False
        self.chosen     = -1
        self.anim_t     = 0.0

    def choose(self, idx):
        if self.answered:
            return
        self.answered = True
        self.chosen   = idx
        c = self.scene()["choices"][idx]
        self.score      += c["score"]
        self.results.append(c["correct"])
        if c["correct"]:
            self.confidence  = min(100, self.confidence + 15)
            self.culture     = min(100, self.culture + 20)
            self.bounce_t    = 1.0
            self._spawn_particles(True)
        else:
            self.confidence  = max(5,  self.confidence - 10)
            self.shake_t     = 1.0
            self._spawn_particles(False)
        self.state = STATE_FEEDBACK

    def next_scene(self):
        self.scene_idx += 1
        if self.scene_idx >= len(SCENES):
            self.state = STATE_SCORE
        else:
            self.state    = STATE_SCENE
            self.answered = False
            self.chosen   = -1
            self.anim_t   = 0.0

    def _spawn_particles(self, good):
        cx = W // 2
        cy = 220
        color = C["green"] if good else C["red"]
        for _ in range(18):
            import random
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(2, 6)
            self.particles.append({
                "x": cx, "y": cy,
                "vx": math.cos(angle)*speed,
                "vy": math.sin(angle)*speed - 2,
                "life": 1.0,
                "color": color,
                "r": random.randint(3, 7),
            })

    # ── 更新 ──────────────────────────────

    def update(self, dt):
        self.anim_t   = min(1.0, self.anim_t + dt * 2.0)
        self.title_t += dt

        if self.bounce_t > 0:
            self.bounce_t = max(0, self.bounce_t - dt * 3)
        if self.shake_t > 0:
            self.shake_t  = max(0, self.shake_t - dt * 4)

        for p in self.particles[:]:
            p["x"]   += p["vx"]
            p["y"]   += p["vy"]
            p["vy"]  += 0.15
            p["life"] -= dt * 1.5
            if p["life"] <= 0:
                self.particles.remove(p)

    # ── 绘制 ──────────────────────────────

    def draw(self):
        screen.fill(C["bg"])

        if self.state == STATE_TITLE:
            self._draw_title()
        elif self.state in (STATE_SCENE, STATE_FEEDBACK):
            self._draw_scene()
        elif self.state == STATE_SCORE:
            self._draw_score()

        # 粒子
        for p in self.particles:
            alpha = int(p["life"] * 220)
            r = max(1, int(p["r"] * p["life"]))
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["color"], alpha), (r, r), r)
            screen.blit(s, (int(p["x"])-r, int(p["y"])-r))

        pygame.display.flip()

    # ── 标题界面 ──────────────────────────

    def _draw_title(self):
        # 背景渐变装饰
        t = self.title_t
        for i in range(5):
            cx = 150 + i*160
            cy = 300 + math.sin(t*0.8 + i*1.2)*30
            r  = 80 + math.sin(t*0.5 + i)*20
            s  = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (3, 199, 90, 12), (r, r), r)
            screen.blit(s, (cx-r, cy-r))

        # 标题卡片
        cx = W//2
        draw_rect(screen, C["panel"], (cx-300, 140, 600, 340), radius=20,
                  border=1, border_color=C["border"])

        # 旗帜与标题
        draw_text(screen, "🇰🇷", F_HUGE, C["white"], cx, 160, center=True)
        draw_text(screen, "韩国文化适应训练", F_TITLE, C["white"], cx, 230, center=True)
        draw_text(screen, "Korea Culture Adaptation Game", F_BODY, C["muted"], cx, 264, center=True)

        # 分割线
        pygame.draw.line(screen, C["border"], (cx-220, 295), (cx+220, 295), 1)

        # 特性列表
        features = [
            ("🏪", "5个真实韩国生活场景"),
            ("🎯", "对话选择 + 文化反馈"),
            ("📊", "文化融入度实时追踪"),
            ("✨", "非语言反馈动画系统"),
        ]
        for i, (icon, text) in enumerate(features):
            col = i % 2
            row = i // 2
            fx = cx - 200 + col * 210
            fy = 310 + row * 32
            draw_text(screen, icon + "  " + text, F_SMALL, C["muted"], fx, fy)

        # 开始按钮
        bw, bh = 200, 44
        bx, by = cx - bw//2, 420
        self.btn_start = pygame.Rect(bx, by, bw, bh)
        mx, my = pygame.mouse.get_pos()
        hover = self.btn_start.collidepoint(mx, my)
        bc = C["green_d"] if hover else C["green"]
        draw_rect(screen, bc, (bx, by, bw, bh), radius=22)
        draw_text(screen, "开始训练  →", F_HEAD, C["bg"], cx, by+12, center=True)

        # 底部提示
        draw_text(screen, "共 5 个场景 · 满分 120 分", F_SMALL, C["muted"], cx, 480, center=True)

    # ── 场景界面 ──────────────────────────

    def _draw_scene(self):
        sc  = self.scene()
        t   = ease_out(self.anim_t)
        off = int((1-t)*40)          # 进场偏移

        # ── 左栏（场景信息 + 统计）──
        lx = 20

        # 场景卡头
        draw_rect(screen, C["panel"], (lx, 16+off, 240, 70), radius=12,
                  border=1, border_color=C["border"])
        draw_text(screen, sc["icon"]+"  "+sc["scene_name"], F_HEAD,
                  sc["accent"], lx+12, 26+off)
        draw_text(screen, sc["location"], F_SMALL, C["muted"], lx+12, 54+off, max_w=220)

        # 进度点
        for i in range(len(SCENES)):
            cx2 = lx + 10 + i * 28
            cy2 = 102+off
            done  = i < self.scene_idx
            cur   = i == self.scene_idx
            color = C["green"] if done else (sc["accent"] if cur else C["border"])
            pygame.draw.circle(screen, color, (cx2, cy2), 7 if cur else 5)
            if cur:
                pygame.draw.circle(screen, sc["accent"], (cx2, cy2), 9, 2)

        # 统计栏
        stats = [
            ("文化融入", self.culture,    C["green"]),
            ("自信心",   self.confidence, C["blue"]),
            ("得分",     min(100, int(self.score/120*100)), C["yellow"]),
        ]
        for i, (label, val, color) in enumerate(stats):
            sy = 126 + i*54 + off
            draw_rect(screen, C["panel"], (lx, sy, 240, 46), radius=10,
                      border=1, border_color=C["border"])
            draw_text(screen, label, F_SMALL, C["muted"], lx+10, sy+6)
            vstr = f"{val}%" if label != "得分" else f"{self.score}分"
            draw_text(screen, vstr, F_BODY, color, 248, sy+6, right=True)
            # 进度条
            bw = 220
            draw_rect(screen, C["border"], (lx+10, sy+28, bw, 8), radius=4)
            fw = int(bw * val / 100)
            if fw > 0:
                draw_rect(screen, color, (lx+10, sy+28, fw, 8), radius=4)

        # 文化小贴士
        draw_rect(screen, C["blue_bg"], (lx, 294+off, 240, 90), radius=10,
                  border=1, border_color=(40, 80, 140))
        draw_text(screen, "📌 文化小贴士", F_SMALL, C["blue"], lx+10, 302+off)
        draw_multiline(screen, sc["tip"], F_SMALL, (160, 190, 230),
                       lx+10, 322+off, max_w=218, line_h=18)

        # 场景编号
        draw_text(screen, f"场景 {self.scene_idx+1} / {len(SCENES)}",
                  F_SMALL, C["muted"], lx, 400+off)

        # ── 右栏（NPC + 对话 + 选项）──
        rx = 280

        # NPC 头像区
        npc_cx = rx + 55
        npc_cy = 100 + off

        # 震动/弹跳偏移
        sx = int(math.sin(self.shake_t * 30) * 6 * self.shake_t) if self.shake_t>0 else 0
        sy2 = int(-math.sin(self.bounce_t * math.pi) * 14) if self.bounce_t>0 else 0

        # NPC 背景圆
        draw_rect(screen, sc["bg_color"],
                  (npc_cx-50+sx, npc_cy-50+sy2, 100, 100), radius=50,
                  border=2, border_color=sc["accent"])

        # NPC emoji（大字）
        npc_surf = F_HUGE.render(sc["npc_emoji"], True, C["white"])
        screen.blit(npc_surf, (npc_cx - npc_surf.get_width()//2 + sx,
                                npc_cy - npc_surf.get_height()//2 + sy2 + 8))

        # 情绪徽章
        em = sc["emotion_g"] if (self.state==STATE_FEEDBACK and self.results and self.results[-1]) \
             else (sc["emotion_b"] if (self.state==STATE_FEEDBACK and self.results and not self.results[-1]) \
             else sc["emotion_n"])
        em_surf = F_SMALL.render(em, True, C["white"])
        ex = npc_cx + 28 + sx
        ey = npc_cy + 28 + sy2
        draw_rect(screen, C["card"], (ex-2, ey-2, 22, 22), radius=11,
                  border=1, border_color=C["border"])
        screen.blit(em_surf, (ex, ey))

        # NPC 名字
        draw_text(screen, sc["npc_name"], F_SMALL, C["muted"], npc_cx, npc_cy+58+sy2, center=True)

        # 对话气泡
        bub_x, bub_y = rx+120, 60+off
        bub_w, bub_h = W - bub_x - 20, 90
        draw_rect(screen, C["card"], (bub_x, bub_y, bub_w, bub_h), radius=14,
                  border=1, border_color=C["border"])
        # 气泡尖
        pts = [(bub_x, bub_y+20), (bub_x-12, bub_y+30), (bub_x, bub_y+40)]
        pygame.draw.polygon(screen, C["card"], pts)
        pygame.draw.polygon(screen, C["border"], pts, 1)

        draw_multiline(screen, sc["npc_say"], F_BODY, C["white"],
                       bub_x+14, bub_y+12, bub_w-24, line_h=22)
        if sc["npc_ko"]:
            draw_text(screen, sc["npc_ko"], F_KO, sc["accent"],
                      bub_x+14, bub_y+bub_h-26)

        # ── 选择按钮 ──
        self.btn_choices = []
        choices = sc["choices"]
        mx2, my2 = pygame.mouse.get_pos()

        for i, ch in enumerate(choices):
            cy3 = 175 + i*78 + off
            bw2 = W - rx - 20
            rect = pygame.Rect(rx, cy3, bw2, 66)
            self.btn_choices.append(rect)

            # 颜色逻辑
            if self.state == STATE_FEEDBACK:
                if i == self.chosen:
                    bg = C["green_bg"] if ch["correct"] else C["red_bg"]
                    bc2 = C["green"] if ch["correct"] else C["red"]
                else:
                    bg = C["card"]
                    bc2 = C["border"]
            else:
                hover = rect.collidepoint(mx2, my2)
                bg  = C["card_h"] if hover else C["card"]
                bc2 = sc["accent"] if hover else C["border"]

            draw_rect(screen, bg, (rx, cy3, bw2, 66), radius=12,
                      border=2 if (self.state==STATE_FEEDBACK and i==self.chosen) else 1,
                      border_color=bc2)

            # 序号圆
            num_color = (C["green"] if ch["correct"] else C["red"]) \
                        if (self.state==STATE_FEEDBACK and i==self.chosen) \
                        else bc2
            pygame.draw.circle(screen, num_color, (rx+22, cy3+33), 12)
            draw_text(screen, str(i+1), F_SMALL, C["bg"] if self.state==STATE_FEEDBACK else C["bg"],
                      rx+22, cy3+26, center=True)

            # 选项文字
            tc = (C["text_ok"] if ch["correct"] else C["text_err"]) \
                 if (self.state==STATE_FEEDBACK and i==self.chosen) \
                 else C["white"]
            draw_multiline(screen, ch["text"][2:].strip(), F_BODY, tc,
                           rx+42, cy3+12, bw2-56, line_h=21)

            # 分数标签
            if self.state == STATE_FEEDBACK and i == self.chosen:
                sc_str = f"+{ch['score']}分"
                sc_col = C["green"] if ch["correct"] else C["muted"]
                draw_text(screen, sc_str, F_SMALL, sc_col, rx+bw2-10, cy3+8, right=True)

        # ── 反馈区 ──
        if self.state == STATE_FEEDBACK:
            fb_y = 415 + off
            ch = sc["choices"][self.chosen]
            good = ch["correct"]
            bg   = C["green_bg"] if good else C["red_bg"]
            bc3  = C["green"]    if good else C["red"]
            draw_rect(screen, bg, (rx, fb_y, W-rx-20, 80), radius=12,
                      border=1, border_color=bc3)
            draw_multiline(screen, ch["fb"], F_BODY,
                           C["text_ok"] if good else C["text_err"],
                           rx+14, fb_y+10, W-rx-50, line_h=22)

            # 下一步按钮
            nb_label = "查看结果 →" if self.scene_idx == len(SCENES)-1 else "下一场景 →"
            nw, nh = 170, 38
            nx2 = W - nw - 20
            ny2 = fb_y + 88
            self.btn_next = pygame.Rect(nx2, ny2, nw, nh)
            hover_n = self.btn_next.collidepoint(mx2, my2)
            draw_rect(screen, C["green_d"] if hover_n else C["green"],
                      (nx2, ny2, nw, nh), radius=19)
            draw_text(screen, nb_label, F_BODY, C["bg"], nx2+nw//2, ny2+10, center=True)

    # ── 得分界面 ──────────────────────────

    def _draw_score(self):
        cx = W//2
        t  = self.title_t

        # 背景光晕
        for i in range(3):
            r = 160 + i*60
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            alpha = int(8 + math.sin(t+i)*4)
            pygame.draw.circle(s, (3, 199, 90, alpha), (r, r), r)
            screen.blit(s, (cx-r, 200-r))

        # 主卡片
        draw_rect(screen, C["panel"], (cx-310, 60, 620, 490), radius=20,
                  border=1, border_color=C["border"])

        # 得分
        draw_text(screen, "训练完成！", F_TITLE, C["white"], cx, 80, center=True)
        max_s = sum(max(c["score"] for c in sc["choices"]) for sc in SCENES)
        pct   = int(self.score / max_s * 100)
        score_color = C["green"] if pct>=75 else (C["orange"] if pct>=50 else C["red"])
        draw_text(screen, f"{self.score}分", F_HUGE, score_color, cx, 115, center=True)
        draw_text(screen, f"满分 {max_s} · 正确率 {pct}%", F_BODY, C["muted"], cx, 180, center=True)

        # 分割线
        pygame.draw.line(screen, C["border"], (cx-260, 210), (cx+260, 210), 1)

        # 每场景结果
        for i, (sc2, correct) in enumerate(zip(SCENES, self.results)):
            rx2 = cx - 250 + (i % 5)*102
            ry  = 225 + (i//5)*60
            color = C["green"] if correct else C["red"]
            bg2   = C["green_bg"] if correct else C["red_bg"]
            draw_rect(screen, bg2, (rx2, ry, 95, 46), radius=10,
                      border=1, border_color=color)
            draw_text(screen, sc2["icon"], F_HEAD, C["white"], rx2+47, ry+6, center=True)
            mark = "✓" if correct else "✗"
            draw_text(screen, mark, F_SMALL, color, rx2+80, ry+6)
            draw_text(screen, sc2["scene_name"].split("(")[0].strip(),
                      F_SMALL, C["muted"], rx2+47, ry+28, center=True)

        # 统计栏
        stats2 = [
            ("文化融入度", f"{self.culture}%", C["green"]),
            ("自信心指数", f"{self.confidence}", C["blue"]),
            ("总积分",     f"{self.score}分",   C["yellow"]),
        ]
        for i, (lbl, val, col) in enumerate(stats2):
            sx2 = cx - 250 + i*175
            draw_rect(screen, C["card"], (sx2, 310, 165, 60), radius=10,
                      border=1, border_color=C["border"])
            draw_text(screen, lbl, F_SMALL, C["muted"], sx2+82, 320, center=True)
            draw_text(screen, val, F_HEAD, col, sx2+82, 340, center=True)

        # 评语
        if pct >= 80:
            msg = "🌟 优秀！你已掌握韩国日常礼仪，可以自信融入韩国社区！"
        elif pct >= 55:
            msg = "👏 不错！继续注意长幼礼仪与公共场合规范，加油！"
        else:
            msg = "💪 继续练习！多观察身边的韩国同学，逐步积累文化经验。"
        draw_multiline(screen, msg, F_BODY, C["white"], cx-240, 385, 480, line_h=24)

        # 徽章
        badges = [
            ("편의점달인", self.results[0] if len(self.results)>0 else False),
            ("식사예절왕", self.results[1] if len(self.results)>1 else False),
            ("행정마스터", self.results[2] if len(self.results)>2 else False),
            ("따뜻한시민", self.results[3] if len(self.results)>3 else False),
            ("카페문화통", self.results[4] if len(self.results)>4 else False),
        ]
        draw_text(screen, "획득 배지", F_SMALL, C["muted"], cx, 425, center=True)
        for i, (name, earned) in enumerate(badges):
            bx2 = cx - 270 + i*112
            col2 = C["green"] if earned else C["border"]
            bg3  = C["green_bg"] if earned else C["card"]
            draw_rect(screen, bg3, (bx2, 445, 105, 32), radius=16,
                      border=1, border_color=col2)
            icon3 = "🏆" if earned else "🔒"
            draw_text(screen, icon3+" "+name, F_SMALL, col2, bx2+52, 454, center=True)

        # 重新开始按钮
        rw, rh = 190, 44
        rx3 = cx - rw//2
        ry3 = 498
        self.btn_restart = pygame.Rect(rx3, ry3, rw, rh)
        mx2, my2 = pygame.mouse.get_pos()
        hover_r = self.btn_restart.collidepoint(mx2, my2)
        draw_rect(screen, C["green_d"] if hover_r else C["green"],
                  (rx3, ry3, rw, rh), radius=22)
        draw_text(screen, "↺  重新训练", F_HEAD, C["bg"], cx, ry3+11, center=True)

    # ── 事件处理 ──────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.state == STATE_TITLE:
                if self.btn_start.collidepoint(mx, my):
                    self.start_game()

            elif self.state == STATE_SCENE:
                for i, rect in enumerate(self.btn_choices):
                    if rect.collidepoint(mx, my):
                        self.choose(i)
                        break

            elif self.state == STATE_FEEDBACK:
                if self.btn_next.collidepoint(mx, my):
                    self.next_scene()

            elif self.state == STATE_SCORE:
                if self.btn_restart.collidepoint(mx, my):
                    self.state  = STATE_TITLE
                    self.title_t = 0.0

        if event.type == pygame.KEYDOWN:
            if self.state == STATE_SCENE and not self.answered:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self.choose(0)
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.choose(1)
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.choose(2)
            elif self.state == STATE_FEEDBACK:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT):
                    self.next_scene()
            elif self.state == STATE_TITLE:
                if event.key == pygame.K_RETURN:
                    self.start_game()
            elif self.state == STATE_SCORE:
                if event.key == pygame.K_RETURN:
                    self.state = STATE_TITLE


# ─────────────────────────────────────────
#  主循环
# ─────────────────────────────────────────
def main():
    game = Game()

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)

        game.update(dt)
        game.draw()


if __name__ == "__main__":
    main()