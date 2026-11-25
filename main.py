#!/usr/bin/env python3
"""news-image-20261124 rev2 entrypoint.

Renders one PNG that sums up the world news of Tuesday 24 November 2026.
Every story below was read on a source page dated 24 November 2026 and is
printed with its outlet attribution. Pure stdlib + Pillow, no network,
no clock, no randomness: two runs produce a byte-identical entry.png.
The page uses a compact three-column layout and a limited palette so the
file stays small (image bytes are a tie-break) while text stays legible.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- stories
# (section, headline, detail, outlet) -- all reported on 24 Nov 2026.
STORIES = [
    ("TOP STORIES",
     "Huawei guilty of trade-secret theft and bank fraud in US trial, acquitted of racketeering",
     "Jury convicted the company on 10 of 12 counts after a two-month trial; Huawei says it will appeal.",
     "Daily Summary Of"),
    ("TOP STORIES",
     "Iran says four tankers hit mines in the Strait of Hormuz",
     "The IRGC said a fourth tanker struck a mine and caught fire; Tehran threatens to close the strait further.",
     "Daily Summary Of"),
    ("TOP STORIES",
     "Ukraine strikes Russian ships in the Gulf of Finland and off Libya",
     "Kyiv says naval drones sank a Russian corvette off Libya; the cargo ship Sparta II was towed to port.",
     "Daily Summary Of"),
    ("TOP STORIES",
     "Drone attack on Saudi PIF tower in Riyadh wounds at least 11",
     "Second hit in a week on the PIF tower in Riyadh's King Abdullah Financial District.",
     "Daily Summary Of"),
    ("TOP STORIES",
     "Fourteen countries back ICJ ruling that Myanmar committed Rohingya genocide",
     "The UK, Spain, Canada, Australia and ten others recognise the World Court decision.",
     "Horizon"),
    ("TOP STORIES",
     "Nvidia reinstates Jensen Huang as chief executive after Trump intervenes",
     "The board restored Huang ten days after his resignation; lawmakers criticise the president's role.",
     "Principia"),
    ("TOP STORIES",
     "UN climate summit ends without a deal after fossil-fuel dispute",
     "Talks concluded in failure amid splits over fossil fuels and climate finance.",
     "Principia"),
    ("TOP STORIES",
     "Turkish Air Force helicopter crash kills five in western Turkiye",
     "An AS-532 crashed after taking off from Eskisehir for a training flight, the defence ministry said.",
     "Daily Summary Of"),

    ("MIDDLE EAST & CONFLICT",
     "IRGC says it attacked a container ship in the Strait of Hormuz",
     "Tehran said the vessel had switched off its navigation systems inside a restricted area north of Khasab.",
     "Daily Summary Of"),
    ("MIDDLE EAST & CONFLICT",
     "Iran rules out any negotiation until Washington meets seven conditions",
     "Iran's chief negotiator said Tehran will use 'all available means' against the American blockade.",
     "Horizon"),
    ("MIDDLE EAST & CONFLICT",
     "Yemen says Houthis are 60 km from Aden and ready to attack",
     "Government forces have built a defence line north and west of the temporary capital, a spokesman said.",
     "Daily Summary Of"),
    ("MIDDLE EAST & CONFLICT",
     "Saudi strikes on Yemen buses and trucks leave 25 dead or missing",
     "Aircraft hit vehicles in Wadi Maabaq in Lahj governorate, the Saba news agency reported.",
     "Daily Summary Of"),
    ("MIDDLE EAST & CONFLICT",
     "UK sanctions Yemen's Houthis and four senior officials",
     "Asset freezes and travel bans cite attacks on Red Sea shipping and strikes on Saudi infrastructure.",
     "Daily Summary Of"),
    ("MIDDLE EAST & CONFLICT",
     "Israel kills Hamas internal security chief in Gaza strike",
     "Brigadier General Naeem Nahel was killed in a joint operation with Shin Bet, Gaza's Interior Ministry said.",
     "Daily Summary Of"),
    ("MIDDLE EAST & CONFLICT",
     "Gaza issues meningitis epidemic alert after case surge",
     "272 infections were reported in October, more than eight times the normal monthly rate.",
     "Daily Summary Of"),
    ("MIDDLE EAST & CONFLICT",
     "Iraq orders federal control of Kurdish oilfields and crossings",
     "PM al-Zaidi said exports must go through Baghdad only; Kurdish PM Barzani called it unacceptable.",
     "Daily Summary Of"),
    ("MIDDLE EAST & CONFLICT",
     "Libya's Haftar visits Turkey for the first time",
     "The eastern commander met President Erdogan in Ankara as Turkey rebuilds ties with eastern Libya.",
     "Daily Summary Of"),
    ("MIDDLE EAST & CONFLICT",
     "Iran inflicts 74 lashes on singer Parastoo Ahmadi",
     "The 'Woman, Life, Freedom' figure was punished for singing without a veil, her lawyers said.",
     "Horizon"),

    ("EUROPE & THE UKRAINE WAR",
     "Medvedev warns Russia could carry out a 'preventive nuclear attack'",
     "He said Ukraine and NATO had crossed a line, as the alliance moved to support Poland.",
     "Principia"),
    ("EUROPE & THE UKRAINE WAR",
     "Leaked-data analysis puts Russian war dead above 700,000",
     "A new study of leaked Russian government data counts soldiers killed or missing in Ukraine.",
     "France 24"),
    ("EUROPE & THE UKRAINE WAR",
     "NATO deploys advanced detection aircraft to Poland after missiles fell",
     "An AWACS aircraft will reinforce the eastern flank; Rutte meets Trump in Florida on Wednesday.",
     "Horizon"),
    ("EUROPE & THE UKRAINE WAR",
     "UK warns Ukraine's suppliers of heightened Russian sabotage risk",
     "The defence ministry and MI5 issued a rare public alert over arson and threats to staff.",
     "BBC"),
    ("EUROPE & THE UKRAINE WAR",
     "Zaporizhzhia hit by new night attacks: two killed, over 30 wounded",
     "A baby and four minors were among the wounded in the southern Ukrainian city.",
     "Horizon"),
    ("EUROPE & THE UKRAINE WAR",
     "Zelensky urges four-way talks with Russia, the US and Europe soon",
     "Kyiv said it is ready to meet as early as Tuesday and repeated its call for NATO membership.",
     "Daily Summary Of"),
    ("EUROPE & THE UKRAINE WAR",
     "EU proposes ban on Russian symbols at sports events in new Russia sanctions",
     "The package also targets crypto financing and Europeans holding posts in Russian sports bodies.",
     "Horizon"),
    ("EUROPE & THE UKRAINE WAR",
     "NATO vows defence against space threat over Russian satellite reports",
     "The alliance responded to reports Moscow may put a nuclear-armed satellite in orbit within 60 days.",
     "Daily Summary Of"),

    ("AMERICAS",
     "Armed men hold 25 hostages at Cartagena supermarket",
     "Five older women were released; the airport briefly halted landings, the president said.",
     "Daily Summary Of"),
    ("AMERICAS",
     "Car bomb damages buildings in Villavicencio, Colombia",
     "The blast came on the eve of the tenth anniversary of the FARC peace deal.",
     "The Hindu"),
    ("AMERICAS",
     "US drone helps capture 'El Chapo Isidro'; Mexico to try him",
     "The cartel chief was seized in a Guasave firefight; Mexico rejected a US extradition request.",
     "Daily Summary Of"),
    ("AMERICAS",
     "Bukele names three Salvadoran soldiers killed in Haiti mission",
     "The troops died in an accidental explosion during an anti-gang deployment in Haiti.",
     "Daily Summary Of"),
    ("AMERICAS",
     "Pentagon rebukes Canada over defence spending and F-35 review",
     "A fact sheet said only 41.9% of Canada's air force fleet was serviceable in 2025-26.",
     "Daily Summary Of"),
    ("AMERICAS",
     "Trump awards Rudy Giuliani the Presidential Medal of Freedom",
     "The former New York mayor and Trump legal adviser was honoured at the White House.",
     "Washington Post"),
    ("AMERICAS",
     "CIA and ODNI suffer cyber breach of unclassified information",
     "A source said the breach hit both US intelligence agencies; the extent of data taken is unclear.",
     "Reuters"),
    ("AMERICAS",
     "Record Thanksgiving travel forecast: 81.5 million travellers",
     "AAA expects 72.9 million by car and 5.96 million by air; the average round-trip fare booked is $800.",
     "CIVIL / AAA"),

    ("ASIA-PACIFIC",
     "South Korea scrambles jets as Russian aircraft enter its air defence zone",
     "Ulleungdo residents were ordered to shelter; Seoul said no territorial airspace was violated.",
     "Daily Summary Of"),
    ("ASIA-PACIFIC",
     "China sentences official to death for spying for a foreign country",
     "The official, surnamed Ma, passed 35 classified items and took over 1 million yuan, a state publisher said.",
     "Daily Summary Of"),
    ("ASIA-PACIFIC",
     "Indonesia nominates two candidates to replace its vice president",
     "President Prabowo named Andi Amran Sulaiman and Sugiono after Gibran Rakabuming Raka resigned.",
     "Daily Summary Of"),
    ("ASIA-PACIFIC",
     "Malaysia to send thousands of migrants back to Myanmar",
     "1,500 Rohingya by navy ships in December and 5,303 by aircraft, PM Anwar Ibrahim said.",
     "Daily Summary Of"),
    ("ASIA-PACIFIC",
     "Hasina plans to return to Bangladesh from exile on December 16",
     "The former prime minister, sentenced to death in absentia, said she will fly back on Victory Day.",
     "Daily Summary Of"),
    ("ASIA-PACIFIC",
     "Magnitude 5.6 earthquake strikes Nepal near the Chinese border",
     "The tremor hit Koshi province at about 10 km depth; no toll was reported.",
     "Horizon"),
    ("ASIA-PACIFIC",
     "Pakistan's first astronaut to fly on China's Shenzhou-24 mission",
     "Air Force pilot Muhammad Zishan Ali will spend about a week aboard the Tiangong space station.",
     "The Straits Times"),
    ("ASIA-PACIFIC",
     "Solomon Islands drops China security deal, signs treaty with Australia",
     "The new treaty bars foreign military bases in the Pacific island nation.",
     "ABC News (Australia)"),
    ("ASIA-PACIFIC",
     "Bangladesh garment workers clash with police as pay protests shut factories",
     "Gazipur workers demand the wage more than double to 30,000 taka; police fired tear gas.",
     "Reuters"),

    ("AFRICA",
     "DR Congo searches for missing plane as rebels claim shootdown",
     "A Cessna 208 cargo plane was lost near Minembwe in South Kivu with four people aboard.",
     "Daily Summary Of"),
    ("AFRICA",
     "Fighting in eastern Congo traps Ebola response teams, WHO says",
     "Heavy fighting in Ituri province is trapping the health workers responding to the outbreak.",
     "Principia"),
    ("AFRICA",
     "Sudan army accuses RSF of drone strike on UN building from Ethiopia",
     "Khartoum said the paramilitaries launched their air offensive from Ethiopian territory.",
     "Horizon"),

    ("BUSINESS & MARKETS",
     "Nvidia bounce fades: shares slide about 6% as the AI rally stumbles",
     "On Tuesday the Nasdaq fell 1.5% and the S&P 500 0.5%, while the Dow rose 0.9%.",
     "Reuters"),
    ("BUSINESS & MARKETS",
     "US prepares new tariff findings on 16 major trading partners",
     "The USTR probe into alleged excess industrial capacity could pave the way for new duties.",
     "Reuters"),
    ("BUSINESS & MARKETS",
     "Sanofi agrees to buy US biotech Insmed for $41 billion",
     "The French drugmaker's deal is the largest biotech acquisition in nearly three years.",
     "Principia"),
    ("BUSINESS & MARKETS",
     "US consumer confidence jumps to highest level in nearly two years",
     "The index rose to 103.3 in November, up from October, before Wednesday's core PCE data.",
     "Reuters"),
    ("BUSINESS & MARKETS",
     "South Korea to let banks issue stablecoins under new rules",
     "Participation by digital asset platforms will be capped at 20%, Yonhap reported.",
     "Yonhap"),

    ("SCIENCE, HEALTH & TECH",
     "United States loses measles elimination status after more than 25 years",
     "The status, held since 2000, fell as measles cases climbed across the country.",
     "Principia"),
    ("SCIENCE, HEALTH & TECH",
     "Pennsylvania records a ninth measles death",
     "The outbreak now affects 46 counties in the state; state and CDC death tolls differ.",
     "Horizon"),
    ("SCIENCE, HEALTH & TECH",
     "FDA approves first drug for limb-girdle muscular dystrophy",
     "BridgeBio's treatment is the first approved therapy for the genetic muscle disease.",
     "Principia"),
    ("SCIENCE, HEALTH & TECH",
     "Astronomers find most distant glowing black hole from the early universe",
     "The quasar formed within 630 million years of the Big Bang.",
     "Principia"),
    ("SCIENCE, HEALTH & TECH",
     "Guterres urges a global AI safety framework within a year",
     "The UN chief asked member states to build a multilateral framework to manage AI risks.",
     "Horizon"),
    ("SCIENCE, HEALTH & TECH",
     "US states sue Musk's businesses over sexualised images from Grok chatbot",
     "State attorneys general targeted AI-generated sexualised imagery from the chatbot.",
     "Principia"),
    ("SCIENCE, HEALTH & TECH",
     "UN says Gaza war has undone 77 years of human development",
     "A UN report warned the war has erased decades of development progress in Gaza.",
     "Principia"),
    ("SCIENCE, HEALTH & TECH",
     "US adds Megaspeed to trade blacklist at centre of Nvidia scandal",
     "The Singapore firm and six others were placed on the Entity List on Monday.",
     "Daily Summary Of"),

    ("SPORT & SOCIETY",
     "Senegal regains the Africa Cup of Nations title after a sports court appeal",
     "The Court of Arbitration for Sport overturned the decision that stripped Senegal of the 2025 crown.",
     "Daily Summary Of"),
    ("SPORT & SOCIETY",
     "UK panel to examine the health legacy of nuclear test veterans",
     "Prime Minister Burnham promised veterans the full truth about the Cold War atomic programme.",
     "BBC"),
    ("SPORT & SOCIETY",
     "Denmark's Supreme Court upholds the 'ghetto plan' for housing areas",
     "The court validated criteria targeting tenants from 'non-Western' countries.",
     "Le Monde"),
]

# ---------------------------------------------------------------- layout
W = 2048
MARGIN = 40
NCOLS = 3
GAP = 28
COL_W = (W - 2 * MARGIN - (NCOLS - 1) * GAP) // NCOLS
HEADER_H = 206
FOOTER_H = 52

BG = (10, 17, 32)
PANEL = (17, 27, 48)
PANEL_EDGE = (38, 54, 86)
SECTION_BG = (24, 40, 74)
INK = (233, 238, 249)
MUTED = (158, 174, 203)
ACCENT = (245, 179, 1)
SRC = (126, 200, 255)

FONT_DIR = "/usr/share/fonts/truetype/noto"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)


F_TITLE = font("NotoSans-Black.ttf", 64)
F_DATE = font("NotoSans-Bold.ttf", 36)
F_SUB = font("NotoSans-Regular.ttf", 24)
F_SECTION = font("NotoSans-Black.ttf", 25)
F_HEAD = font("NotoSans-Bold.ttf", 25)
F_BODY = font("NotoSans-Regular.ttf", 20)
F_SRC = font("NotoSans-Bold.ttf", 16)
F_FOOT = font("NotoSans-Regular.ttf", 20)

NUM_W = 46
TEXT_W = COL_W - NUM_W - 22


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def build_blocks(draw):
    blocks = []
    current = None
    for i, (sec, head, body, src) in enumerate(STORIES, start=1):
        if sec != current:
            blocks.append(("section", sec))
            current = sec
        hl = wrap(draw, head, F_HEAD, TEXT_W)
        bl = wrap(draw, body, F_BODY, TEXT_W)
        blocks.append(("card", i, hl, bl, src))
    return blocks


def block_height(block):
    if block[0] == "section":
        return 48
    _, _, hl, bl, _ = block
    return 10 + len(hl) * 31 + 2 + len(bl) * 25 + 21 + 8


def split_blocks(blocks, heights, n):
    """Split the block list into n runs of roughly equal total height,
    never splitting immediately after a section header if avoidable."""
    total = sum(heights)
    runs, start, acc = [], 0, 0
    targets = [total * (k + 1) / n for k in range(n - 1)]
    ti = 0
    for i, h in enumerate(heights):
        acc += h
        if ti < len(targets) and acc >= targets[ti] and i + 1 < len(blocks):
            cut = i + 1
            if blocks[cut][0] == "card" and blocks[i][0] == "section":
                cut = i  # keep a section header with its first card
            if cut > start:
                runs.append(blocks[start:cut])
                start = cut
            ti += 1
    runs.append(blocks[start:])
    while len(runs) < n:
        runs.append([])
    return runs


def render(path):
    probe = Image.new("RGB", (W, 100))
    pd = ImageDraw.Draw(probe)
    blocks = build_blocks(pd)
    heights = [block_height(b) for b in blocks]
    runs = split_blocks(blocks, heights, NCOLS)
    run_heights = []
    idx = 0
    for run in runs:
        run_heights.append(sum(heights[idx:idx + len(run)]))
        idx += len(run)
    H = HEADER_H + max(run_heights) + FOOTER_H + 14

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # header
    d.rectangle([0, 0, W, HEADER_H - 12], fill=(13, 22, 42))
    d.rectangle([0, HEADER_H - 12, W, HEADER_H - 6], fill=ACCENT)
    d.text((MARGIN, 26), "THE WORLD IN ONE IMAGE", font=F_TITLE, fill=INK)
    d.text((MARGIN, 106), "Tuesday 24 November 2026", font=F_DATE, fill=ACCENT)
    d.text((MARGIN, 156),
           "%d verified stories from that day's reporting - every item carries its source"
           % len(STORIES), font=F_SUB, fill=MUTED)

    def draw_block(block, x, y):
        if block[0] == "section":
            d.rectangle([x, y + 6, x + COL_W, y + 40], fill=SECTION_BG)
            d.rectangle([x, y + 6, x + 5, y + 40], fill=ACCENT)
            d.text((x + 14, y + 10), block[1], font=F_SECTION, fill=INK)
            return y + 48
        _, num, hl, bl, src = block
        h = block_height(block)
        d.rectangle([x, y, x + COL_W, y + h - 6], fill=PANEL, outline=PANEL_EDGE, width=1)
        d.text((x + 12, y + 9), "%02d" % num, font=F_SRC, fill=ACCENT)
        tx = x + NUM_W
        cy = y + 8
        for line in hl:
            d.text((tx, cy), line, font=F_HEAD, fill=INK)
            cy += 31
        cy += 1
        for line in bl:
            d.text((tx, cy), line, font=F_BODY, fill=MUTED)
            cy += 25
        d.text((tx, cy), "SOURCE: " + src.upper(), font=F_SRC, fill=SRC)
        return y + h

    for c, run in enumerate(runs):
        x = MARGIN + c * (COL_W + GAP)
        y = HEADER_H + 4
        for b in run:
            y = draw_block(b, x, y)

    fy = H - FOOTER_H + 10
    d.text((MARGIN, fy),
           "Compiled only from reports published on 24 November 2026. Stale, duplicated and "
           "unverifiable items were dropped.", font=F_FOOT, fill=MUTED)

    img = img.quantize(colors=128, dither=Image.Dither.NONE)
    img.save(path, optimize=True)
    return path


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(os.getcwd(), "entry.png")
    render(out)
    alt = os.path.join(here, "entry.png")
    if os.path.abspath(alt) != os.path.abspath(out):
        render(alt)
    print("wrote entry.png (%d stories)" % len(STORIES))


if __name__ == "__main__":
    main()
