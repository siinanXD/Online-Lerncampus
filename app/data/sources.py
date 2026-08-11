"""Trusted source seed data for Maschinen- und Anlagenfuehrer content."""

from app.models.domain import SourceDocument

TRUSTED_SOURCES: list[SourceDocument] = [
    SourceDocument(
        key="ihk-aachen-berufsseite-maf",
        title="Maschinen- und Anlagenfuehrer/-in",
        publisher="IHK Aachen",
        url=(
            "https://www.ihk.de/aachen/bildung/ausbildung/"
            "ausbildungsberufe/maschinen-anlagenfuehrer-6888522"
        ),
        trust_tier=1,
        allowed_usage="Metadata, curriculum alignment, source citation.",
        topics=["berufsbild", "ausbildungsdauer", "pruefung"],
    ),
    SourceDocument(
        key="ihk-aachen-pruefungs-faq",
        title="Alles ueber die Ausbildungspruefungen",
        publisher="IHK Aachen",
        url=(
            "https://www.ihk.de/aachen/bildung/ausbildung/"
            "alles-ueber-ausbildungspruefungen-3999084"
        ),
        trust_tier=1,
        allowed_usage="Exam workflow and review rules.",
        topics=["zwischenpruefung", "abschlusspruefung", "zulassung"],
    ),
    SourceDocument(
        key="bze-uelu-maf-metall-kunststoff",
        title="Ueberbetriebliche Unterweisung Maschinen- und Anlagenfuehrer",
        publisher="BZE Euskirchen",
        url=(
            "https://www.bze-euskirchen.de/leistungen/ausbildung/"
            "ueberbetriebliche-unterweisung-industrie/"
            "maschinen-und-anlagenfuehrer/-in-metall-und-kunststofftechnik"
        ),
        trust_tier=1,
        allowed_usage="Course planning and local learning journey alignment.",
        topics=["uelu", "pneumatik", "drehen", "fraesen", "qualitaet"],
    ),
    SourceDocument(
        key="bibb-berufsprofil-maf",
        title="Maschinen- und Anlagenfuehrer Berufsprofil",
        publisher="BIBB",
        url="https://www.bibb.de/dienst/berufesuche/profile/apprenticeship/87iz96t0",
        trust_tier=1,
        allowed_usage="Occupational profile and competencies.",
        topics=["kompetenzen", "taetigkeitsfelder", "schwerpunkte"],
    ),
    SourceDocument(
        key="maschfueausbv",
        title="Verordnung ueber die Berufsausbildung",
        publisher="Gesetze im Internet",
        url="https://www.gesetze-im-internet.de/maschf_ausbv/BJNR064700004.html",
        trust_tier=1,
        allowed_usage="Legal curriculum and examination requirements.",
        topics=["ausbildungsrahmenplan", "pruefungsanforderungen"],
    ),
]

