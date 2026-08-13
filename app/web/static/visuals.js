/**
 * Visual catalogue for learning journey chapters and illustrated questions.
 * Covers are original workshop photos; figures are exam-style diagrams.
 */
window.OLC_VISUALS = {
  months: {
    1: { file: "cover_berufsbild.jpg", alt: "Azubi an einer Produktionsmaschine" },
    2: { file: "cover_sicherheit.jpg", alt: "Persönliche Schutzausrüstung am Arbeitsplatz" },
    3: { file: "cover_werkstoffe.jpg", alt: "Metall- und Kunststoff-Werkstoffproben" },
    4: { file: "cover_zeichnung.jpg", alt: "Technische Zeichnung und Prüfmittel" },
    5: { file: "cover_berufsbild.jpg", alt: "Arbeitsplatz in der Fertigung" },
    6: { file: "cover_messen.jpg", alt: "Messschieber an einer Welle" },
    7: { file: "cover_drehen.jpg", alt: "Spanende Fertigung an der Drehmaschine" },
    8: { file: "cover_pneumatik.jpg", alt: "Pneumatik-Schulungsstand mit Zylinder und Ventil" },
    9: { file: "cover_drehen.jpg", alt: "Drehen und Fräsen in der Werkstatt" },
    10: { file: "cover_drehen.jpg", alt: "Metallbearbeitung" },
    11: { file: "cover_berufsbild.jpg", alt: "Materialfluss in der Produktion" },
    12: { file: "cover_messen.jpg", alt: "Prüfungsnahe Messaufgabe" },
    13: { file: "cover_werkstoffe.jpg", alt: "Werkstoffeigenschaften von Metall und Kunststoff" },
    14: { file: "cover_berufsbild.jpg", alt: "Abgestimmte Arbeitsabläufe in der Linie" },
    15: { file: "cover_drehen.jpg", alt: "Fügen, Spanen und Umformen" },
    16: { file: "cover_messen.jpg", alt: "Toleranzen und Oberflächen prüfen" },
    17: { file: "cover_steuerung.jpg", alt: "Steuerungs- und Bedienfeld einer Anlage" },
    18: { file: "cover_steuerung.jpg", alt: "Maschine rüsten am Bedienpanel" },
    19: { file: "cover_steuerung.jpg", alt: "Prozessdaten an der Steuerung" },
    20: { file: "cover_stoerung.jpg", alt: "Störungssuche an der Anlage" },
    21: { file: "cover_wartung.jpg", alt: "Wartung und Inspektion" },
    22: { file: "cover_spritzguss.jpg", alt: "Spritzgießmaschine und Kunststoffqualität" },
    23: { file: "cover_blech.jpg", alt: "Blechbearbeitung an der Abkantpresse" },
    24: { file: "cover_messen.jpg", alt: "Abschlussprüfung Messen und Fertigen" },
  },
  figures: [
    {
      keys: ["messschieber", "nonius", "prüfmittel", "pruefmittel", "messen", "messuhr", "rachenlehre", "lehrung"],
      src: "/static/visuals/fig-messschieber.svg",
      alt: "Messschieber, Ablesung 23,50 mm",
      caption: "Abb. Messschieber: Hauptmaß 23 mm + Nonius 0,50 mm",
    },
    {
      keys: ["5/2", "wegeventil", "ventil", "pneumatik", "druckluft"],
      src: "/static/visuals/fig-ventil-5-2.svg",
      alt: "Schaltzeichen 5/2-Wegeventil",
      caption: "Abb. 5/2-Wegeventil nach ISO 1219",
    },
    {
      keys: ["zylinder", "einfachwirk", "doppeltwirk", "kolbenstange"],
      src: "/static/visuals/fig-zylinder.svg",
      alt: "Einfach- und doppeltwirkender Zylinder",
      caption: "Abb. Einfachwirkend mit Feder, doppeltwirkend mit zwei Anschlüssen",
    },
    {
      keys: ["toleranz", "passung", "h7", "h6", "welle", "bohrung", "iso 286", "oberfläche", "oberflaeche"],
      src: "/static/visuals/fig-toleranzfeld.svg",
      alt: "Toleranzfeld Welle-Bohrung",
      caption: "Abb. Spielpassung: Bohrung H7, Welle h6",
    },
    {
      keys: ["spritzgieß", "spritzgiess", "spritzguss", "einspritzen", "granulat"],
      src: "/static/visuals/fig-spritzzyklus.svg",
      alt: "Spritzgießzyklus in vier Phasen",
      caption: "Abb. Spritzgießzyklus: Schließen, Einspritzen, Nachdruck, Entformen",
    },
    {
      keys: ["zeichnung", "bemaß", "bemass", "schnitt", "ansicht", "nennmaß", "nennmass"],
      src: "/static/visuals/fig-zeichnung.svg",
      alt: "Technische Zeichnung einer Welle",
      caption: "Abb. Welle ø20 h6, Länge 80 mm, Fase 1×45°",
    },
    {
      keys: ["psa", "helm", "schutzbrille", "gehörschutz", "gehoerschutz", "handschuh", "sicherheitsschuh", "arbeitsschutz", "unfallverhütung"],
      src: "/static/visuals/fig-psa.svg",
      alt: "Persönliche Schutzausrüstung",
      caption: "Abb. PSA: Helm, Brille, Gehörschutz, Handschuhe, S3-Schuhe",
    },
    {
      keys: ["cnc", "achse", "achsen", "steuerung", "sps", "hmi", "nc-"],
      src: "/static/visuals/fig-cnc.svg",
      alt: "CNC-Achsen X Y Z",
      caption: "Abb. Rechtssystem: X längs, Y quer, Z Spindel",
    },
  ],
};
