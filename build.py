#!/usr/bin/env python3
"""Build the lab website from content files.
Edit content/*.json or drop PDFs into pdfs/, then run:  python3 build.py
This regenerates index.html. Then git add + git push to publish.
"""
import json, os, shutil
from pathlib import Path

BASE = Path(__file__).parent
CONTENT = BASE / "content"
PDFS = BASE / "pdfs"
OUT = BASE / "index.html"

def load_json(name):
    with open(CONTENT / name, encoding="utf-8") as f:
        return json.load(f)

def esc(s):
    """Escape for HTML attribute context."""
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")

def render():
    profile = load_json("profile.json")
    news = load_json("news.json")
    research = load_json("research.json")
    team = load_json("team.json")
    pubs = load_json("publications.json")
    projects = load_json("projects.json")

    # Copy PDFs to images/ for reference (optional)
    pdfs_dir = PDFS
    out_pdfs = BASE / "pdfs"
    pdfs_dir.mkdir(exist_ok=True)
    out_pdfs.mkdir(exist_ok=True)

    # Build HTML parts
    news_items = ""
    for n in news:
        # Parse date
        parts = n["date"].split("-")
        month_map = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        day = str(int(parts[2]))
        month = month_map[int(parts[1])]
        news_items += f"""<div class="hero-news-item">
                    <div class="hero-news-date"><div class="d">{day}</div><div class="m">{month}</div></div>
                    <div class="hero-news-body"><h4>{esc(n['title'])}</h4><p>{esc(n['text'])}</p></div>
                </div>
"""

    research_items = ""
    for r in research:
        research_items += f"""<div class="research-item"><strong>{esc(r['title'])}</strong><p>{esc(r['desc'])}</p></div>
"""

    team_cards = ""
    for m in team:
        colors = m.get("color", "#5a8c4f,#7aac6f")
        team_cards += f"""<div class="card team-card">
                <div class="team-avatar" style="background:linear-gradient(135deg,{colors});">
                    <img src="{esc(m['photo'])}" alt="{esc(m['name'])}" onerror="this.style.display='none'">
                </div>
                <h4>{esc(m['name'])}</h4>
                <div class="team-role">{esc(m['role'])}</div>
                <p class="team-focus">{esc(m.get('focus',''))}</p>
            </div>
"""

    pub_items = ""
    for p in pubs:
        pdf_link = ""
        if p.get("pdf"):
            pdf_link = f' <a href="{esc(p["pdf"])}" style="font-size:.82rem;color:var(--accent);">[PDF]</a>'
        pub_items += f"""<div class="pub-item">
                <div class="pub-title">{esc(p['title'])}{pdf_link}</div>
                <div class="pub-authors">{esc(p['authors'])}</div>
                <div class="pub-venue">{esc(p['venue'])}</div>
                <div class="pub-year">{esc(p['year'])}</div>
            </div>
"""

    pi_projects = ""
    for pr in projects["pi"]:
        pi_projects += f"""<div class="project-item">
            <div class="project-title">{esc(pr['title'])}</div>
            <div class="project-details"><strong>Title:</strong> {esc(pr['detail'])} | <strong>Period:</strong> {esc(pr['period'])}</div>
        </div>
"""

    coi_projects = ""
    for pr in projects["coi"]:
        coi_projects += f"""<div class="project-item">
            <div class="project-title">{esc(pr['title'])}</div>
            <div class="project-details"><strong>Title:</strong> {esc(pr['detail'])} | <strong>Period:</strong> {esc(pr['period'])}</div>
        </div>
"""

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Soil Microbiome Ecology Lab | Institute of Soil Science, CAS</title>
    <style>
        :root {{
            --primary: #1a3c34;
            --primary-light: #2d6a4f;
            --primary-lighter: #95b46a;
            --accent: #c4a35a;
            --text: #1e2930;
            --text-muted: #5c6c6b;
            --bg: #f6f7f5;
            --white: #ffffff;
            --border: #e2e8e0;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.06);
            --shadow-lg: 0 12px 28px rgba(0,0,0,0.08);
            --radius: 6px;
        }}
        *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            color: var(--text);
            background: var(--bg);
            line-height: 1.65;
            -webkit-font-smoothing: antialiased;
        }}
        a {{ color: var(--primary-light); text-decoration: none; transition: color .25s; }}
        a:hover {{ color: var(--accent); }}

        .nav {{
            position: fixed; top: 0; width: 100%; z-index: 1000;
            background: rgba(255,255,255,.92);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
        }}
        .nav-inner {{
            max-width: 1200px; margin: 0 auto; padding: 0 24px;
            display: flex; justify-content: space-between; align-items: center;
            height: 72px;
        }}
        .nav-logo {{
            display: flex; align-items: center; gap: 12px;
            font-weight: 700; font-size: 1.05rem; color: var(--primary);
        }}
        .nav-logo img {{ height: 44px; width: 44px; object-fit: contain; flex-shrink: 0; }}
        .nav-logo-sub {{ font-size: .7rem; color: var(--text-muted); font-weight: 500; margin-top: 1px; }}
        .nav-links {{ display: flex; gap: 28px; }}
        .nav-links a {{
            font-size: .9rem; color: var(--text-muted); font-weight: 500;
            position: relative; padding: 4px 0;
        }}
        .nav-links a::after {{
            content: ''; position: absolute; bottom: 0; left: 0;
            width: 0; height: 2px; background: var(--primary-light);
            transition: width .3s; border-radius: 2px;
        }}
        .nav-links a:hover::after {{ width: 100%; }}
        .nav-links a:hover {{ color: var(--primary); }}
        .nav-toggle {{
            display: none; flex-direction: column; gap: 5px; cursor: pointer;
            background: none; border: none; padding: 4px;
        }}
        .nav-toggle span {{
            display: block; width: 24px; height: 2px;
            background: var(--primary); border-radius: 2px;
            transition: all .3s;
        }}

        .hero {{
            position: relative; margin-top: 72px;
            background: linear-gradient(160deg, var(--primary) 0%, #1b5e4a 40%, #2d6a4f 100%);
            color: var(--white); padding: 80px 24px 60px; overflow: hidden;
        }}
        .hero::before {{
            content: ''; position: absolute; inset: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: .5;
        }}
        .hero-content {{ max-width: 1200px; margin: 0 auto; position: relative; z-index: 1; text-align: center; }}
        .hero h1 {{ font-size: 2.8rem; font-weight: 800; letter-spacing: -.02em; margin-bottom: 12px; }}
        .hero .sub {{ font-size: 1.15rem; opacity: .85; margin-bottom: 32px; font-weight: 400; }}
        .hero-actions {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-bottom: 48px; }}
        .btn {{
            display: inline-flex; align-items: center; gap: 8px;
            padding: 12px 28px; border-radius: var(--radius);
            font-weight: 600; font-size: .92rem; cursor: pointer;
            transition: all .25s; border: none;
        }}
        .btn-outline {{ background: transparent; color: var(--white); border: 2px solid rgba(255,255,255,.6); }}
        .btn-outline:hover {{ background: rgba(255,255,255,.1); border-color: var(--white); }}
        .hero-news {{
            max-width: 860px; margin: 0 auto;
            background: rgba(255,255,255,.08); border-radius: var(--radius);
            backdrop-filter: blur(4px); overflow: hidden;
        }}
        .hero-news-inner {{
            display: flex; overflow-x: auto; scroll-snap-type: x mandatory;
            -ms-overflow-style: none; scrollbar-width: none;
        }}
        .hero-news-inner::-webkit-scrollbar {{ display: none; }}
        .hero-news-item {{
            flex: 0 0 100%; scroll-snap-align: start;
            padding: 24px 32px; display: flex; gap: 20px; align-items: flex-start;
            background: rgba(255,255,255,.92); color: var(--text);
            text-align: left;
        }}
        .hero-news-date {{
            flex-shrink: 0; background: var(--primary-light); color: var(--white);
            border-radius: var(--radius); padding: 12px 16px; text-align: center; min-width: 80px;
        }}
        .hero-news-date .d {{ font-size: 1.6rem; font-weight: 700; line-height: 1.2; }}
        .hero-news-date .m {{ font-size: .7rem; text-transform: uppercase; opacity: .85; }}
        .hero-news-body h4 {{ color: var(--primary); margin-bottom: 6px; font-size: 1.05rem; }}
        .hero-news-body p {{ color: var(--text-muted); font-size: .92rem; }}
        .hero-news-ctrl {{ display: flex; gap: 8px; justify-content: flex-end; padding: 12px 16px; }}
        .hero-news-ctrl button {{
            width: 36px; height: 36px; border-radius: 50%;
            background: var(--primary-light); color: var(--white);
            border: none; cursor: pointer; transition: all .2s;
            display: flex; align-items: center; justify-content: center;
            font-size: .85rem;
        }}
        .hero-news-ctrl button:hover {{ background: var(--accent); transform: scale(1.05); }}

        .section {{ padding: 80px 24px; }}
        .section-alt {{ background: var(--white); }}
        .section-inner {{ max-width: 1200px; margin: 0 auto; }}
        .section-label {{
            display: inline-block; font-size: .75rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: .06em; color: var(--primary-lighter); margin-bottom: 8px;
        }}
        .section-title {{
            font-size: 1.8rem; font-weight: 700; color: var(--primary);
            margin-bottom: 12px;
        }}
        .section-title::after {{
            content: ''; display: block; width: 44px; height: 3px;
            background: var(--accent); border-radius: 2px; margin-top: 12px;
        }}
        .section-desc {{ color: var(--text-muted); margin-top: 16px; margin-bottom: 40px; max-width: 720px; }}
        .fade-in {{ opacity: 0; transform: translateY(20px); transition: opacity .6s ease, transform .6s ease; }}
        .fade-in.visible {{ opacity: 1; transform: translateY(0); }}

        .grid {{ display: grid; gap: 24px; }}
        .grid-2 {{ grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }}
        .grid-3 {{ grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); }}
        .grid-1 {{ grid-template-columns: 1fr; }}
        .card {{
            background: var(--white); border-radius: var(--radius);
            border: 1px solid var(--border);
            padding: 28px; transition: all .3s;
        }}
        .section-alt .card {{ background: var(--bg); }}
        .card:hover {{ box-shadow: var(--shadow-lg); transform: translateY(-2px); }}
        .card h3 {{ color: var(--primary); margin-bottom: 10px; font-size: 1.05rem; }}
        .card p {{ color: var(--text-muted); font-size: .92rem; }}

        .profile {{
            display: grid; grid-template-columns: 260px 1fr; gap: 40px; align-items: start;
        }}
        .profile-img {{
            width: 100%; aspect-ratio: 1; border-radius: var(--radius);
            overflow: hidden; background: var(--primary-light);
            box-shadow: var(--shadow-lg);
        }}
        .profile-img img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
        .profile h3 {{ font-size: 1.4rem; color: var(--primary); margin-bottom: 4px; }}
        .profile-role {{ color: var(--accent); font-weight: 600; font-size: 1rem; margin-bottom: 16px; }}
        .profile-bio {{ color: var(--text-muted); margin-bottom: 20px; }}
        .profile-meta {{ display: grid; gap: 8px; }}
        .profile-meta-row {{ display: flex; gap: 12px; }}
        .profile-meta-label {{ color: var(--text-muted); min-width: 100px; font-size: .9rem; }}
        .profile-meta-val {{ color: var(--text); font-weight: 500; font-size: .9rem; }}

        .research-list {{ display: grid; gap: 16px; margin-top: 8px; }}
        .research-item {{
            padding: 20px 24px; background: var(--white); border-radius: var(--radius);
            border: 1px solid var(--border); border-left: 4px solid var(--primary-light);
        }}
        .section-alt .research-item {{ background: var(--bg); }}
        .research-item strong {{ color: var(--primary); }}
        .research-item p {{ color: var(--text-muted); margin-top: 4px; font-size: .92rem; }}

        .team-card {{ text-align: center; padding: 24px 20px; }}
        .team-avatar {{
            width: 96px; height: 96px; border-radius: 50%; margin: 0 auto 16px;
            overflow: hidden; object-fit: cover; display: block;
        }}
        .team-avatar img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
        .team-card h4 {{ color: var(--primary); margin-bottom: 4px; }}
        .team-role {{ color: var(--text-muted); font-size: .85rem; margin-bottom: 8px; }}
        .team-focus {{ color: var(--text-muted); font-size: .82rem; }}

        .pub-item {{
            padding: 20px 24px; border-left: 4px solid transparent;
            background: var(--white); border-radius: var(--radius);
            border: 1px solid var(--border); transition: all .3s;
        }}
        .section-alt .pub-item {{ background: var(--bg); }}
        .pub-item:hover {{ border-left-color: var(--accent); box-shadow: var(--shadow-md); }}
        .pub-title {{ font-weight: 700; font-size: 1rem; margin-bottom: 6px; color: var(--text); }}
        .pub-authors {{ color: var(--text-muted); font-size: .85rem; }}
        .pub-venue {{ color: var(--primary-light); font-weight: 600; margin: 6px 0 2px; font-size: .88rem; }}
        .pub-year {{ color: var(--text-muted); font-size: .82rem; }}

        .project-sub {{ font-size: 1.15rem; color: var(--primary); margin: 32px 0 16px; font-weight: 700; }}
        .project-item {{
            padding: 18px 24px; border-radius: var(--radius);
            border: 1px solid var(--border); border-left-width: 4px; margin-bottom: 12px;
            background: var(--white);
        }}
        .section-alt .project-item {{ background: var(--bg); }}
        .project-title {{ font-weight: 700; color: var(--primary); margin-bottom: 4px; font-size: .95rem; }}
        .project-details {{ color: var(--text-muted); font-size: .85rem; }}

        .contact-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; }}
        .contact-card {{ padding: 24px; }}
        .contact-card h3 {{ margin-bottom: 16px; }}
        .contact-row {{ display: flex; gap: 12px; align-items: flex-start; }}
        .contact-icon {{
            width: 40px; height: 40px; border-radius: 50%;
            background: var(--bg); display: flex; align-items: center;
            justify-content: center; flex-shrink: 0; font-size: 1rem;
        }}
        .contact-label {{ font-size: .72rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 2px; }}
        .contact-row p {{ font-size: .9rem; }}

        .footer {{
            background: var(--primary); color: rgba(255,255,255,.65);
            text-align: center; padding: 40px 24px 32px;
        }}
        .footer a {{ color: rgba(255,255,255,.85); }}
        .footer-inner {{ max-width: 1200px; margin: 0 auto; }}
        .footer p {{ font-size: .85rem; }}
        .footer-links {{ margin-top: 12px; }}
        .footer-links a {{ margin: 0 8px; font-size: .85rem; }}
        .footer-visitor {{
            display: flex; align-items: center; justify-content: center;
            gap: 8px; margin-top: 20px; padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,.12);
            font-size: .8rem; color: rgba(255,255,255,.5);
        }}

        .back-top {{
            position: fixed; bottom: 28px; right: 28px;
            width: 44px; height: 44px; border-radius: 50%;
            background: var(--primary-light); color: var(--white);
            border: none; cursor: pointer; box-shadow: var(--shadow-md);
            transition: all .3s; display: none; align-items: center;
            justify-content: center; z-index: 999; font-size: 1.1rem;
        }}
        .back-top.show {{ display: flex; }}
        .back-top:hover {{ background: var(--accent); transform: translateY(-2px); }}

        @media (max-width: 768px) {{
            .nav-links {{
                position: fixed; top: 72px; left: 0; width: 100%;
                background: rgba(255,255,255,.98); flex-direction: column;
                padding: 16px 24px; gap: 4px;
                transform: translateY(-100%); opacity: 0;
                transition: all .35s; pointer-events: none;
                border-bottom: 1px solid var(--border);
            }}
            .nav-links.open {{ transform: translateY(0); opacity: 1; pointer-events: auto; }}
            .nav-links a {{ padding: 12px 0; font-size: 1rem; }}
            .nav-toggle {{ display: flex; }}
            .hero h1 {{ font-size: 1.9rem; }}
            .hero {{ padding: 60px 20px 40px; }}
            .hero-news-item {{ flex-direction: column; padding: 20px; }}
            .hero-news-date {{ min-width: 100%; display: flex; gap: 8px; align-items: center; padding: 10px 16px; }}
            .hero-news-date .d {{ font-size: 1.2rem; }}
            .section {{ padding: 56px 20px; }}
            .section-title {{ font-size: 1.5rem; }}
            .profile {{ grid-template-columns: 1fr; }}
            .profile-img {{ max-width: 260px; }}
        }}
    </style>
</head>
<body>

<nav class="nav">
    <div class="nav-inner">
        <a href="#" class="nav-logo">
            <img src="images/isscas-logo.png" alt="ISSCAS" onerror="this.style.display='none'">
            <div>
                <div>Soil Microbiome <span style="color:var(--accent);">Ecology Lab</span></div>
                <div class="nav-logo-sub">Institute of Soil Science, CAS</div>
            </div>
        </a>
        <div class="nav-links" id="navLinks">
            <a href="#about">About</a>
            <a href="#research">Research</a>
            <a href="#team">People</a>
            <a href="#publications">Publications</a>
            <a href="#projects">Projects</a>
            <a href="#contact">Contact</a>
        </div>
        <button class="nav-toggle" id="navToggle" aria-label="Menu">
            <span></span><span></span><span></span>
        </button>
    </div>
</nav>

<section class="hero">
    <div class="hero-content">
        <h1>Soil Microbiome Ecology Research Group</h1>
        <p class="sub">Exploring the Secrets of Soil Life</p>
        <div class="hero-actions">
            <button class="btn btn-outline" onclick="document.querySelector('#contact').scrollIntoView({{behavior:'smooth'}})">Join Us</button>
        </div>
        <div class="hero-news">
            <div class="hero-news-inner" id="newsCarousel">
                {news_items}
            </div>
            <div class="hero-news-ctrl">
                <button onclick="scrollNews(-1)">←</button>
                <button onclick="scrollNews(1)">→</button>
            </div>
        </div>
    </div>
</section>

<section class="section section-alt" id="about">
    <div class="section-inner fade-in">
        <div class="section-label">About</div>
        <h2 class="section-title">Principal Investigator</h2>
        <div class="profile">
            <div class="profile-img">
                <img src="{esc(profile['photo'])}" alt="{esc(profile['name'])}" onerror="this.style.display='none'">
            </div>
            <div>
                <h3>{esc(profile['name'])} <span style="color:var(--text-muted);font-weight:400;font-size:.9rem;">({esc(profile.get('nameCn',''))})</span></h3>
                <div class="profile-role">{esc(profile['title'])}</div>
                <div class="profile-bio">{esc(profile['bio'])}</div>
                <div class="profile-meta">
                    {''.join(f'<div class="profile-meta-row"><span class="profile-meta-label">{esc(m["label"])}</span><span class="profile-meta-val">{esc(m["value"])}</span></div>' for m in profile['meta'])}
                </div>
            </div>
        </div>
    </div>
</section>

<section class="section" id="research">
    <div class="section-inner fade-in">
        <div class="section-label">Research</div>
        <h2 class="section-title">Research Directions</h2>
        <div class="research-list">
            {research_items}
        </div>
    </div>
</section>

<section class="section section-alt" id="team">
    <div class="section-inner fade-in">
        <div class="section-label">People</div>
        <h2 class="section-title">Research Team</h2>
        <div class="grid grid-3">
            {team_cards}
        </div>
    </div>
</section>

<section class="section" id="publications">
    <div class="section-inner fade-in">
        <div class="section-label">Publications</div>
        <h2 class="section-title">Representative Publications</h2>
        <p class="section-desc">Selected research accomplishments in peer-reviewed journals</p>
        <div class="grid grid-1">
            {pub_items}
        </div>
    </div>
</section>

<section class="section section-alt" id="projects">
    <div class="section-inner fade-in">
        <div class="section-label">Projects</div>
        <h2 class="section-title">Research Projects</h2>
        <p class="section-desc">Current and completed funded research projects</p>
        <div class="project-sub">Principal Investigator</div>
        {pi_projects}
        <div class="project-sub">Co-Investigator</div>
        {coi_projects}
    </div>
</section>

<section class="section" id="contact">
    <div class="section-inner fade-in">
        <div class="section-label">Contact</div>
        <h2 class="section-title">Contact Us</h2>
        <p class="section-desc">We welcome inquiries and collaboration opportunities</p>
        <div class="contact-grid">
            <div class="card contact-card">
                <h3>Email</h3>
                <div class="contact-row">
                    <div class="contact-icon">✉</div>
                    <div>
                        <div class="contact-label">Primary Email</div>
                        <p><a href="mailto:gfgao@issas.ac.cn">gfgao@issas.ac.cn</a></p>
                    </div>
                </div>
            </div>
            <div class="card contact-card">
                <h3>Phone</h3>
                <div class="contact-row">
                    <div class="contact-icon">📞</div>
                    <div>
                        <div class="contact-label">Office Phone</div>
                        <p><a href="tel:025-86881345">025-86881345</a></p>
                    </div>
                </div>
            </div>
            <div class="card contact-card">
                <h3>Location</h3>
                <div class="contact-row">
                    <div class="contact-icon">📍</div>
                    <div>
                        <div class="contact-label">Address</div>
                        <p><a href="https://uri.amap.com/search?keyword=南京市江宁区创优路298号" target="_blank" rel="noopener noreferrer" style="border-bottom:1px dashed var(--accent);">No.298 Chuangyou Road, Jiangning District, Nanjing, China</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<footer class="footer">
    <div class="footer-inner">
        <p>&copy; 2026 Soil Microbiome Ecology Research Group | Nanjing Institute of Soil Science, Chinese Academy of Sciences</p>
        <div class="footer-links"><a href="#">Privacy Policy</a> | <a href="#">Contact Information</a></div>
        <div class="footer-visitor">
            <span>👥</span><span>Total Visitors:</span>
            <span><img src="https://api.visitorbadge.io/api/visitors?path=soil-microbiome-ecology-lab&label=&labelColor=%231a3c34&countColor=%23c4a35a&style=flat&labelStyle=none" alt="visitor count" style="height:20px;vertical-align:middle;border-radius:3px;" id="visitorBadge"></span>
        </div>
    </div>
</footer>

<button class="back-top" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" id="backTop">↑</button>

<script>
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    if (navToggle) {{
        navToggle.addEventListener('click', () => navLinks.classList.toggle('open'));
        navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => navLinks.classList.remove('open')));
    }}
    window.addEventListener('scroll', () => {{
        const bt = document.getElementById('backTop');
        if (bt) bt.classList.toggle('show', window.scrollY > 300);
    }});
    function scrollNews(dir) {{
        const c = document.getElementById('newsCarousel');
        if (!c) return;
        const w = c.querySelector('.hero-news-item').offsetWidth || 860;
        c.scrollBy({{ left: dir * w, behavior: 'smooth' }});
    }}
    setInterval(() => {{
        const c = document.getElementById('newsCarousel');
        if (!c) return;
        const m = c.scrollWidth - c.clientWidth;
        if (c.scrollLeft >= m - 10) {{ c.scrollTo({{ left: 0, behavior: 'smooth' }}); }}
        else {{ scrollNews(1); }}
    }}, 5000);
    document.getElementById('visitorBadge')?.addEventListener('error', function() {{
        const K = 'site_visitor_count', V = 'has_visited';
        let c = parseInt(localStorage.getItem(K)) || 0;
        if (!sessionStorage.getItem(V)) {{ c++; localStorage.setItem(K, c); sessionStorage.setItem(V, 'true'); }}
        this.parentElement.innerHTML = '<span style="background:rgba(255,255,255,0.12);padding:2px 10px;border-radius:50px;font-weight:600;color:rgba(255,255,255,0.85);letter-spacing:1px;">' + c.toLocaleString() + '</span>';
    }});
    const observer = new IntersectionObserver(entries => {{
        entries.forEach(e => {{ if (e.isIntersecting) {{ e.target.classList.add('visible'); observer.unobserve(e.target); }} }});
    }}, {{ threshold: 0.1 }});
    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
</script>
</body>
</html>'''

    OUT.write_text(html, encoding="utf-8")
    print(f"✔ Site built: {OUT}")

if __name__ == "__main__":
    render()
