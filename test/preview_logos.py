import sys
import os
import webbrowser
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.infrastructure.providers.bumeran.bumeran_job_scraper import BumeranJobScraper
from src.infrastructure.providers.computrabajo.computrabajo_job_scraper import ComputrabajoJobScraper
from src.infrastructure.providers.empleosperu.empleosperu_job_scraper import EmpleosPeruJobScraper
from src.infrastructure.providers.universia.universia_job_scraper import UniversiaJobScraper
from src.infrastructure.providers.laborum.laborum_job_scraper import LaborumJobScraper
from src.application.mappers.job_mapper import JobMapper

def get_initials(name: str) -> str:
    if not name:
        return "??"
    words = name.strip().split()
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    return name[:2].upper()

def run_preview(max_per_platform: int = 4, target_platform: str = None):
    print("=" * 60)
    print("Iniciando extracción local para previsualizar logos...")
    print("=" * 60)

    providers = [
        ("Bumeran", BumeranJobScraper(), "#0052cc"),
        ("Computrabajo", ComputrabajoJobScraper(), "#ff6600"),
        ("EmpleosPeru", EmpleosPeruJobScraper(), "#d32f2f"),
        ("Universia", UniversiaJobScraper(), "#00838f"),
        ("Laborum", LaborumJobScraper(), "#673ab7"),
    ]

    if target_platform:
        providers = [p for p in providers if p[0].lower() == target_platform.lower()]
        if not providers:
            print(f"Plataforma '{target_platform}' no encontrada. Opciones: Bumeran, Computrabajo, EmpleosPeru, Universia, Laborum")
            return

    all_cards_html = []
    total_found = 0
    total_with_logo = 0

    for name, scraper, badge_color in providers:
        print(f"\n[+] Obteniendo ofertas de {name}...")
        try:
            # Para Laborum pedimos 30 para asegurar empresas que hayan subido su logo propio
            amount = 30 if name == "Laborum" else max_per_platform
            jobs = scraper.get_jobs_test(amount)

            # Priorizamos mostrar las que tienen logo si existen
            with_logos = [j for j in jobs if j.external_company_image]
            without_logos = [j for j in jobs if not j.external_company_image]
            selected = (with_logos + without_logos)[:max_per_platform]

            for job in selected:
                resp = JobMapper.ToResponse(job)
                total_found += 1
                has_logo = bool(resp.external_company_image)
                if has_logo:
                    total_with_logo += 1

                company_name = resp.external_company_name or "Empresa Confidencial"
                initials = get_initials(company_name)

                logo_markup = f"""
                    <img src="{resp.external_company_image}" 
                         alt="Logo {company_name}" 
                         class="company-logo" 
                         loading="lazy"
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                    <div class="company-initials" style="display: none;">{initials}</div>
                """ if has_logo else f"""
                    <div class="company-initials">{initials}</div>
                """

                status_badge = '<span class="badge badge--success">Con Logo</span>' if has_logo else '<span class="badge badge--neutral">Sin Logo (Iniciales)</span>'

                card = f"""
                <div class="card">
                    <div class="card-header">
                        <div class="avatar-container">
                            {logo_markup}
                        </div>
                        <div class="card-meta">
                            <span class="platform-tag" style="background: {badge_color};">{name}</span>
                            {status_badge}
                            <h3 class="job-title" title="{resp.title}">{resp.title}</h3>
                            <p class="company-name">{company_name}</p>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="details-row">
                            <span>Modalidad: <strong>{resp.job_type or 'No esp.'}</strong></span>
                            <span>Ubicación: <strong>{resp.ubigeo or resp.address or 'Perú'}</strong></span>
                        </div>
                        <div class="url-preview">
                            <span class="url-label">Logo URL:</span>
                            <code class="url-code">{resp.external_company_image or 'null'}</code>
                        </div>
                    </div>
                    <div class="card-footer">
                        <a href="{resp.source_url}" target="_blank" class="btn-link">Ver vacante original &rarr;</a>
                    </div>
                </div>
                """
                all_cards_html.append(card)
                print(f"   -> {company_name[:25]} | Logo: {'SI' if has_logo else 'NO'}")

        except Exception as e:
            print(f"   [!] Error en {name}: {e}")

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Previsualización Local de Logos - Llanqui Scraper</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --border: #334155;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --accent: #10b981;
            --font: system-ui, -apple-system, sans-serif;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text-main);
            font-family: var(--font);
            padding: 2rem;
            line-height: 1.5;
        }}
        .header {{
            max-width: 1200px;
            margin: 0 auto 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1.5rem;
        }}
        .header h1 {{ font-size: 1.8rem; font-weight: 700; color: #fff; }}
        .stats {{
            display: flex;
            gap: 1rem;
        }}
        .stat-badge {{
            background: var(--surface);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            border: 1px solid var(--border);
            font-size: 0.9rem;
        }}
        .stat-badge strong {{ color: var(--accent); }}
        .grid {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 1.5rem;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .card:hover {{
            transform: translateY(-2px);
            border-color: #475569;
        }}
        .card-header {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        .avatar-container {{
            width: 56px;
            height: 56px;
            min-width: 56px;
            border-radius: 12px;
            overflow: hidden;
            background: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid var(--border);
        }}
        .company-logo {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            padding: 4px;
            background: #ffffff;
        }}
        .company-initials {{
            width: 100%;
            height: 100%;
            background: #334155;
            color: #f8fafc;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.1rem;
        }}
        .card-meta {{
            flex: 1;
            min-width: 0;
        }}
        .platform-tag {{
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            color: #fff;
            margin-right: 0.5rem;
        }}
        .badge {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .badge--success {{ background: rgba(16, 185, 129, 0.2); color: #34d399; }}
        .badge--neutral {{ background: rgba(148, 163, 184, 0.2); color: #94a3b8; }}
        .job-title {{
            font-size: 1rem;
            font-weight: 600;
            margin: 0.4rem 0 0.2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: #fff;
        }}
        .company-name {{
            font-size: 0.85rem;
            color: var(--text-sub);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .card-body {{
            font-size: 0.85rem;
            color: var(--text-sub);
            border-top: 1px solid #33415555;
            padding-top: 0.75rem;
            margin-bottom: 0.75rem;
        }}
        .details-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }}
        .details-row strong {{ color: var(--text-main); }}
        .url-preview {{
            background: #0f172a80;
            padding: 6px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            margin-top: 0.5rem;
            word-break: break-all;
        }}
        .url-label {{ color: #64748b; font-weight: 600; }}
        .url-code {{ color: #38bdf8; }}
        .card-footer {{
            border-top: 1px solid #33415555;
            padding-top: 0.75rem;
            display: flex;
            justify-content: flex-end;
        }}
        .btn-link {{
            color: #38bdf8;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        .btn-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Previsualización de Vacantes y Logos Scrapeados</h1>
            <p style="color: var(--text-sub); margin-top: 4px;">Datos en vivo extraídos por los scrapers de Llanqui</p>
        </div>
        <div class="stats">
            <div class="stat-badge">Total mostradas: <strong>{total_found}</strong></div>
            <div class="stat-badge">Con logo propio: <strong>{total_with_logo}</strong></div>
        </div>
    </div>
    <div class="grid">
        {"".join(all_cards_html)}
    </div>
</body>
</html>
"""

    output_path = ROOT_DIR / "test" / "preview_logos.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("\n" + "=" * 60)
    print(f"Archivo HTML generado exitosamente en:\n{output_path}")
    print("Abriendo en el navegador...")
    print("=" * 60)
    webbrowser.open(output_path.as_uri())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Previsualizar logos scrapeados en el navegador")
    parser.add_argument("--platform", "-p", type=str, default=None, help="Nombre de la plataforma (Bumeran, Computrabajo, EmpleosPeru, Universia, Laborum)")
    parser.add_argument("--amount", "-n", type=int, default=3, help="Cantidad de ofertas por plataforma")
    args = parser.parse_args()

    run_preview(max_per_platform=args.amount, target_platform=args.platform)
