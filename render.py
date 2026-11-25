#!/usr/bin/env python3
"""Render the entry image for make.fun competition news-image-20261124,
revision 2: the world news of Tuesday 24 November 2026 on one square page.

The 62 stories below are the revision's verified set: each one was read
on a source page dated 24 November 2026, and each is printed with its
outlet attribution. Candidates that were stale, duplicated or could not
be confirmed on a source of that day were dropped.

This file is the build-time renderer (Pillow). It draws entry.png once,
offline, and the result is committed next to it. The shipped program,
main.py, uses only the standard library and copies that committed image
to the output directory, so the graded runs are byte-identical.

Layout: a broadsheet front page of exactly 1024 by 1024 pixels. The
eight top stories run as a lead band with their detail text; the rest
flow through four ruled columns as headline plus source. A short scale
ladder re-measures the page and steps the type down until everything
fits, so the output size never depends on a hand-tuned guess.
"""

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
PAGE = 1024
MARGIN = 26
GUTTER = 16
NCOLS = 4
COL_W = (PAGE - 2 * MARGIN - (NCOLS - 1) * GUTTER) // NCOLS

PAPER = (248, 246, 240)
INK = (22, 22, 26)
BODY_INK = (56, 53, 48)
GREY = (104, 100, 94)
HAIR = (196, 192, 182)
RED = (150, 26, 26)
BAND = (26, 26, 32)

FONT_DIR = "/usr/share/fonts/truetype/noto/"
F_BLACK = FONT_DIR + "NotoSans-Black.ttf"
F_BOLD = FONT_DIR + "NotoSans-Bold.ttf"
F_REG = FONT_DIR + "NotoSans-Regular.ttf"
F_CBOLD = FONT_DIR + "NotoSans-CondensedBold.ttf"
F_CREG = FONT_DIR + "NotoSans-Condensed.ttf"

FOOTER = ("Compiled only from reports published on Tuesday 24 November 2026 - "
          "stale, duplicated and unverifiable items were dropped.")
FOOTER_H = 38
MASTHEAD_H = 106


def load(path, size):
    return ImageFont.truetype(path, max(7, int(round(size))))


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Type:
    """Type sizes and line heights at one scale step."""

    def __init__(self, s):
        self.lead_head = load(F_CBOLD, 16 * s)
        self.lead_head_lh = 19 * s
        self.lead_body = load(F_CREG, 12 * s)
        self.lead_body_lh = 14.5 * s
        self.lead_src = load(F_BOLD, 9 * s)
        self.lead_src_lh = 11.5 * s
        self.sec = load(F_BOLD, 11 * s)
        self.sec_h = 22 * s
        self.col_head = load(F_CBOLD, 13 * s)
        self.col_head_lh = 15.5 * s
        self.col_src = load(F_CREG, 10 * s)
        self.col_src_lh = 12.5 * s


def split_runs(blocks):
    """Split blocks into NCOLS runs of near-equal height by cutting at
    the cumulative heights nearest to each quarter of the total. A run
    is not left ending on a section header when that can be avoided:
    the header moves to the next run so it stays with its first item."""
    total = sum(b[2] for b in blocks)
    cum, acc = [], 0.0
    for b in blocks:
        acc += b[2]
        cum.append(acc)
    cuts, prev = [], 0
    for k in range(1, NCOLS):
        want = total * k / NCOLS
        best = min(range(prev, len(blocks) - 1),
                   key=lambda i: abs(cum[i] - want))
        if blocks[best][0] == "sec" and best > prev:
            best -= 1
        cuts.append(best)
        prev = best + 1
    runs, start = [], 0
    for c in cuts:
        runs.append(blocks[start:c + 1])
        start = c + 1
    runs.append(blocks[start:])
    return runs


def plan(draw, t):
    """Measure the whole page at this scale. Returns the lead rows and
    the column runs with every block's height, exactly as drawn."""
    leads = [s for s in STORIES if s[0] == "TOP STORIES"]
    rest = [s for s in STORIES if s[0] != "TOP STORIES"]

    lead_rows = []
    for r in range(0, len(leads), NCOLS):
        row = []
        for _sec, head, body, src in leads[r:r + NCOLS]:
            hl = wrap(draw, head, t.lead_head, COL_W)
            bl = wrap(draw, body, t.lead_body, COL_W)
            h = (len(hl) * t.lead_head_lh + 2 + len(bl) * t.lead_body_lh
                 + 3 + t.lead_src_lh)
            row.append(((hl, bl, src), h))
        lead_rows.append((row, max(h for _b, h in row)))
    leads_h = 22 + sum(rh + 6 for _row, rh in lead_rows) + 4

    blocks = []
    seen = None
    for sec, head, _body, src in rest:
        if sec != seen:
            blocks.append(("sec", sec, t.sec_h))
            seen = sec
        hl = wrap(draw, head, t.col_head, COL_W)
        blocks.append(("item", (hl, src),
                       len(hl) * t.col_head_lh + t.col_src_lh + 5))

    runs = split_runs(blocks)
    col_h = max(sum(b[2] for b in r) for r in runs)

    bottom = MASTHEAD_H + leads_h + 10 + col_h + FOOTER_H
    return bottom, lead_rows, runs


def draw_masthead(d):
    d.rectangle([0, 0, PAGE, 7], fill=RED)
    f_title = load(F_BLACK, 42)
    title = "THE WORLD IN ONE IMAGE"
    tw = d.textlength(title, font=f_title)
    d.text(((PAGE - tw) / 2, 14), title, font=f_title, fill=INK)
    d.line([MARGIN, 68, PAGE - MARGIN, 68], fill=INK, width=3)
    d.line([MARGIN, 73, PAGE - MARGIN, 73], fill=INK, width=1)
    f_date = load(F_BOLD, 18)
    d.text((MARGIN, 82), "TUESDAY 24 NOVEMBER 2026", font=f_date, fill=INK)
    f_note = load(F_BOLD, 11)
    note = "%d STORIES - EVERY ITEM WITH ITS SOURCE" % len(STORIES)
    nw = d.textlength(note, font=f_note)
    d.text((PAGE - MARGIN - nw, 86), note, font=f_note, fill=RED)


def draw_leads(d, y, lead_rows, t):
    f_lab = load(F_BOLD, 12)
    d.text((MARGIN, y), "TOP STORIES", font=f_lab, fill=RED)
    lab_w = d.textlength("TOP STORIES", font=f_lab)
    d.line([MARGIN + lab_w + 10, y + 7, PAGE - MARGIN, y + 7], fill=HAIR, width=1)
    y += 22
    for row, row_h in lead_rows:
        for c, ((hl, bl, src), _h) in enumerate(row):
            x = MARGIN + c * (COL_W + GUTTER)
            if c:
                d.line([x - GUTTER // 2, y, x - GUTTER // 2, y + row_h - 2],
                       fill=HAIR, width=1)
            cy = y
            for line in hl:
                d.text((x, cy), line, font=t.lead_head, fill=INK)
                cy += t.lead_head_lh
            cy += 2
            for line in bl:
                d.text((x, cy), line, font=t.lead_body, fill=BODY_INK)
                cy += t.lead_body_lh
            cy += 3
            d.text((x, cy), src.upper(), font=t.lead_src, fill=GREY)
        y += row_h + 6
    return y + 4


def draw_columns(d, y, runs, t):
    bottom = PAGE - FOOTER_H - 2
    for c, run in enumerate(runs):
        x = MARGIN + c * (COL_W + GUTTER)
        if c:
            d.line([x - GUTTER // 2, y, x - GUTTER // 2, bottom], fill=HAIR, width=1)
        cy = y
        for kind, payload, h in run:
            if kind == "sec":
                d.rectangle([x, cy, x + COL_W, cy + 17], fill=BAND)
                d.text((x + 6, cy + 3), payload, font=t.sec, fill=(255, 255, 255))
            else:
                hl, src = payload
                for line in hl:
                    d.text((x, cy), line, font=t.col_head, fill=INK)
                    cy += t.col_head_lh
                d.text((x, cy), src.upper(), font=t.col_src, fill=GREY)
            cy += h - (0 if kind == "sec" else len(hl) * t.col_head_lh)


def draw_footer(d):
    y = PAGE - FOOTER_H + 4
    d.line([MARGIN, y, PAGE - MARGIN, y], fill=INK, width=2)
    f = load(F_REG, 11)
    tw = d.textlength(FOOTER, font=f)
    d.text(((PAGE - tw) / 2, y + 7), FOOTER, font=f, fill=GREY)


def render(path):
    probe = Image.new("RGB", (PAGE, PAGE))
    pd = ImageDraw.Draw(probe)
    chosen = None
    for s in (1.0, 0.97, 0.94, 0.91, 0.88, 0.85, 0.82, 0.79, 0.76):
        t = Type(s)
        bottom, lead_rows, runs = plan(pd, t)
        chosen = (t, lead_rows, runs)
        if bottom <= PAGE:
            break
    t, lead_rows, runs = chosen
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    y = draw_leads(d, MASTHEAD_H, lead_rows, t)
    d.line([MARGIN, y, PAGE - MARGIN, y], fill=INK, width=2)
    draw_columns(d, y + 10, runs, t)
    draw_footer(d)
    img = img.quantize(colors=160, dither=Image.Dither.NONE)
    img.save(path, optimize=True)
    return path


def main():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    render(os.path.join(here, "entry.png"))
    print("wrote entry.png (%d stories)" % len(STORIES))


if __name__ == "__main__":
    main()
