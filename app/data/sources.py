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
        key="ihk-aachen-pruefungsordnung",
        title=(
            "Pruefungsordnung fuer die Durchfuehrung von Abschluss- und "
            "Umschulungspruefungen"
        ),
        publisher="IHK Aachen",
        url=(
            "https://www.ihk.de/aachen/ueber-uns/rechtsgrundlagen/"
            "pruefungsordnung-abschluss-u-umschulung-5007006"
        ),
        trust_tier=1,
        allowed_usage="Exam governance, validation rules, source citation.",
        topics=["pruefungsordnung", "bewertung", "wiederholung"],
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
        key="bze-uelu-maf-metall-kunststoff-2026",
        title=(
            "Angebot fuer ein durchgaengiges Ausbildungssystem fuer Maschinen "
            "und Anlagenfuehrer Metall und Kunststoff 2026"
        ),
        publisher="BZE Euskirchen",
        url=(
            "https://www.bze-euskirchen.de/fileadmin/user_upload/pdfs/"
            "UELU_Industrie_2026/01_MA_Metall_und_Kunststoff_2026_202509.pdf"
        ),
        trust_tier=1,
        allowed_usage="Course dates and local practical module alignment.",
        topics=[
            "pneumatik",
            "drehen",
            "fraesen",
            "werkstoffkunde",
            "technische-kommunikation",
            "grundbildung-metall",
            "pruefungsvorbereitung",
        ],
    ),
    SourceDocument(
        key="bze-uelu-maf-metall-kunststoff-2027",
        title=(
            "Jahresplanung Ueberbetriebliche Lehrlingsunterweisung Maschinen- "
            "und Anlagenfuehrer Metall- und Kunststofftechnik 2027"
        ),
        publisher="BZE Euskirchen",
        url=(
            "https://www.bze-euskirchen.de/fileadmin/user_upload/pdfs/"
            "UELU_Industrie_2027/06_Maschinen-_und_Anlagenfuehrer_M_K.pdf"
        ),
        trust_tier=1,
        allowed_usage="Course dates and local practical module alignment.",
        topics=[
            "blechkurs",
            "qualitaetsmanagement",
            "kunststofftechnik",
            "pneumatik",
            "zwischenpruefung",
            "abschlusspruefung",
        ],
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
        key="bibb-ausbildungsordnung-maf-pdf",
        title="Bundesgesetzblatt-Auszug Maschinen- und Anlagenfuehrer",
        publisher="BIBB",
        url=(
            "https://www.bibb.de/dienst/berufesuche/de/"
            "index_berufesuche.php/regulation/maschinen_und_anlagenfuehrer.pdf"
        ),
        trust_tier=1,
        allowed_usage="Historical regulation PDF and source citation.",
        topics=["ausbildungsordnung", "ausbildungsrahmenplan", "pruefung"],
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
    SourceDocument(
        key="kmk-rahmenlehrplan-maf-2023",
        title=(
            "Rahmenlehrplan fuer Maschinen- und Anlagenfuehrer und "
            "Maschinen- und Anlagenfuehrerin"
        ),
        publisher="Kultusministerkonferenz",
        url=(
            "https://www.kmk.org/service/servicebereich-berufliche-schulen/"
            "downloadbereich-rahmenlehrplaene?"
            "tx_fedownloads_single%5Baction%5D=forceDownload&"
            "tx_fedownloads_single%5Bcontroller%5D=Downloads&"
            "tx_fedownloads_single%5Bdownload%5D=48833&type=150"
        ),
        trust_tier=1,
        allowed_usage="School curriculum alignment by specialization.",
        topics=["rahmenlehrplan", "berufsschule", "metall-kunststofftechnik"],
    ),
    SourceDocument(
        key="bk-eschweiler-maf",
        title="Maschinen- und Anlagenfuehrer/in",
        publisher="Berufskolleg Eschweiler",
        url=(
            "https://www.bk-eschweiler.de/cms/bildungsangebot/"
            "berufsschule/technik/maschinen-und-anlagenfuehrer"
        ),
        trust_tier=2,
        allowed_usage="Regional school context and subject alignment.",
        topics=[
            "berufsschule",
            "blockunterricht",
            "fertigungs-und-prueftechnik",
            "steuerungs-und-regelungstechnik",
        ],
    ),
    SourceDocument(
        key="din-862",
        title="DIN 862 - Messschieber, Anforderungen und Pruefung",
        publisher="DIN Deutsches Institut fuer Normung",
        url="https://www.beuth.de/de/norm/din-862/271946766",
        trust_tier=1,
        allowed_usage=(
            "Normative reference only. The standard is copyrighted and must not be "
            "reproduced; cite requirements in own words and link to the publisher."
        ),
        topics=["messschieber", "laengenpruefung", "messmittel"],
    ),
]
