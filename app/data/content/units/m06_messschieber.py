"""Detailed Messschieber learning unit (month 6, position 2)."""

from app.data.content.helpers import theory, unit

UNITS = [
    unit(
        slug="messschieber",
        month=6,
        position=2,
        title="Messschieber",
        subtitle="Aufbau, Nonius und normgerechtes Messen nach DIN 862",
        learning_goals=[
            "Die Bauteile eines Messschiebers benennen und ihre Funktion erklaeren.",
            "Einen Nonius mit 0,05 mm und 0,02 mm Ablesung sicher ablesen.",
            "Aussen-, Innen- und Tiefenmass fachgerecht aufnehmen.",
            "Typische Messabweichungen erkennen und vermeiden.",
        ],
        theory_blocks=[
            theory(
                heading="Wozu der Messschieber dient",
                body=(
                    "Der Messschieber ist das Universalmessmittel in der Fertigung. Mit "
                    "einem einzigen Geraet nimmst du Aussenmasse, Innenmasse und "
                    "Tiefenmasse auf. Er arbeitet nach dem Prinzip einer festen "
                    "Hauptskala auf der Schiene und einer beweglichen Hilfsskala, dem "
                    "Nonius, auf dem Schieber. Der Messschieber ist schnell und "
                    "vielseitig, aber weniger genau als eine Buegelmessschraube - "
                    "fuer Toleranzen unter etwa 0,05 mm greifst du zum Mikrometer."
                ),
                key_points=[
                    "Ein Messmittel fuer Aussen-, Innen- und Tiefenmass.",
                    "Hauptskala auf der Schiene, Nonius auf dem Schieber.",
                    "Fuer enge Toleranzen nimmst du die Buegelmessschraube.",
                ],
                norm_references=["DIN 862"],
            ),
            theory(
                heading="Aufbau und Bauteile",
                body=(
                    "Die Schiene traegt die Hauptskala in Millimetern. Der Schieber "
                    "laeuft darauf und traegt den Nonius. Die grossen Messschenkel "
                    "unten greifen das Werkstueck von aussen. Die kleinen Messschnaebel "
                    "oben messen Bohrungen und Nuten von innen. Hinten schiebt sich die "
                    "Tiefenmessstange aus der Schiene heraus. Die Feststellschraube "
                    "klemmt den Schieber, damit sich der Messwert beim Ablesen nicht "
                    "verschiebt."
                ),
                key_points=[
                    "Schiene mit Hauptskala, Schieber mit Nonius.",
                    "Messschenkel = aussen, Messschnaebel = innen, Tiefenmassstange = Tiefe.",
                    "Feststellschraube sichert den Messwert vor dem Ablesen.",
                ],
                norm_references=["DIN 862"],
            ),
            theory(
                heading="Den Nonius ablesen",
                body=(
                    "Der Nonius macht Bruchteile eines Millimeters sichtbar. Bei einem "
                    "Nonius mit 0,05 mm sind 20 Noniusstriche auf einer Laenge von 19 mm "
                    "aufgetragen; jeder Noniusstrich liegt also 0,05 mm vor dem "
                    "zugehoerigen Millimeterstrich. Bei 0,02 mm sind es 50 Striche auf "
                    "49 mm.\n\n"
                    "So liest du ab: Zuerst nimmst du am Nullstrich des Nonius den "
                    "vollen Millimeterwert von der Hauptskala. Dann suchst du den "
                    "einen Noniusstrich, der genau mit einem Strich der Hauptskala "
                    "fluchtet. Seine Nummer mal dem Noniuswert ergibt die "
                    "Nachkommastelle. Beispiel: Nullstrich steht hinter 24 mm, der "
                    "7. Noniusstrich fluchtet, Nonius 0,05 mm - das Mass betraegt "
                    "24 mm + 7 x 0,05 mm = 24,35 mm."
                ),
                key_points=[
                    "0,05 mm: 20 Striche auf 19 mm. 0,02 mm: 50 Striche auf 49 mm.",
                    "Ganze Millimeter am Nullstrich des Nonius ablesen.",
                    "Nachkommastelle am fluchtenden Noniusstrich ablesen.",
                ],
                norm_references=["DIN 862"],
            ),
            theory(
                heading="Richtig messen - und was schiefgeht",
                body=(
                    "Pruefe vor jeder Messung den Nullpunkt: Messschenkel schliessen, "
                    "Nullstriche muessen fluchten. Messflaechen und Werkstueck muessen "
                    "sauber und gratfrei sein - ein Span unter dem Messschenkel "
                    "verfaelscht das Mass sofort.\n\n"
                    "Messe mit gleichmaessiger, geringer Messkraft. Druckst du zu "
                    "stark, federt der Schieber und das Mass faellt zu klein aus. "
                    "Setze den Messschieber rechtwinklig an; ein verkantetes Geraet "
                    "misst zu gross (Kippfehler). Miss moeglichst nah an der Schiene, "
                    "denn der Messschieber verletzt das Abbesche Komparatorprinzip: "
                    "Massstab und Messstrecke liegen nicht auf einer Linie, weshalb "
                    "sich ein Kippen direkt als Abweichung auswirkt.\n\n"
                    "Bezugstemperatur fuer Laengenmessungen ist 20 Grad Celsius. Ein "
                    "frisch bearbeitetes, warmes Werkstueck misst du zu gross."
                ),
                key_points=[
                    "Immer zuerst den Nullpunkt pruefen.",
                    "Sauber, gratfrei, rechtwinklig und gefuehlvoll messen.",
                    "Kippfehler: Der Messschieber haelt das Abbesche Prinzip nicht ein.",
                    "Bezugstemperatur 20 Grad Celsius.",
                ],
                norm_references=["DIN 862", "DIN EN ISO 1"],
            ),
        ],
        practice_task=(
            "Nimm einen Messschieber mit 0,05 mm Nonius. Pruefe den Nullpunkt. Miss an "
            "einem Drehteil den Aussendurchmesser an drei Stellen, den "
            "Bohrungsdurchmesser und die Bohrungstiefe. Notiere alle fuenf Messwerte "
            "auf zwei Nachkommastellen und begruende, warum die drei "
            "Durchmesserwerte voneinander abweichen koennen."
        ),
        glossary={
            "Nonius": (
                "Hilfsskala auf dem Schieber, die Bruchteile eines Millimeters "
                "ablesbar macht."
            ),
            "Messschenkel": "Die grossen Backen fuer die Aussenmessung.",
            "Messschnaebel": "Die kleinen Backen oben fuer die Innenmessung.",
            "Kippfehler": (
                "Messabweichung durch verkantetes Ansetzen; das Mass faellt zu gross aus."
            ),
            "Abbesches Komparatorprinzip": (
                "Massstab und Messstrecke sollen auf einer Linie liegen. Der "
                "Messschieber erfuellt das nicht, die Buegelmessschraube schon."
            ),
            "Bezugstemperatur": (
                "20 Grad Celsius, die Normtemperatur fuer Laengenmessungen."
            ),
        },
        category_slugs=["m06-messschieber"],
        source_keys=["bze-uelu-maf-metall-kunststoff", "din-862"],
        estimated_minutes=14,
    ),
]
