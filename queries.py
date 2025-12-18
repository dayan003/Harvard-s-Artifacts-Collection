queries = {
    "1  Top 10 most descriptive artifacts": """
        SELECT id, title, LENGTH(description) AS desc_len
        FROM artifact_metadata
        ORDER BY desc_len DESC
        LIMIT 10;
    """,

    "2  Artifacts with most images": """
        SELECT objectid, imagecount
        FROM artifact_media
        ORDER BY imagecount DESC
        LIMIT 10;
    """,

    "3  Artifacts using red color hue": """
        SELECT objectid, color, hue
        FROM artifact_colors
        WHERE hue = 'Red';
    """,

    "4  Cultures with more than 100 artifacts": """
        SELECT culture, COUNT(*) total
        FROM artifact_metadata
        GROUP BY culture
        HAVING total > 100;
    """,

    "5  Total artifacts per classification and century": """
        SELECT classification, century, COUNT(*) total
        FROM artifact_metadata
        GROUP BY classification, century;
    """,

    "6  Artifacts missing titles": """
        SELECT *
        FROM artifact_metadata
        WHERE title IS NULL OR title = '';
    """,

    "7  Artifacts with more than 1 image": """
        SELECT *
        FROM artifact_media
        WHERE imagecount > 1;
    """,

    "8  Average accession year": """
        SELECT AVG(accessionyear) AS avg_accession_year
        FROM artifact_metadata;
    """,

    "9  Artifacts with more colors than media": """
    SELECT 
        m.objectid,
        m.mediacount,
        COUNT(c.color) AS total_colors
        FROM artifact_media m
        JOIN artifact_colors c 
        ON m.objectid = c.objectid
         GROUP BY 
        m.objectid, m.mediacount
        HAVING 
        total_colors > m.mediacount;
    """,


    "10  Artifacts created between 1500 and 1600": """
        SELECT *
        FROM artifact_metadata
        WHERE CAST(SUBSTRING(century, 1, 4) AS UNSIGNED) BETWEEN 1500 AND 1600;
    """,

    "11  Artifacts with no media": """
        SELECT *
        FROM artifact_metadata
        WHERE id NOT IN (SELECT objectid FROM artifact_media);
    """,

    "12  Byzantine 11th century artifacts": """
        SELECT *
        FROM artifact_metadata
        WHERE century = '11th century'
        AND culture = 'Byzantine';
    """,

    "13  Unique cultures": """
        SELECT DISTINCT culture
        FROM artifact_metadata;
    """,

    "14  Archaic period artifacts": """
        SELECT *
        FROM artifact_metadata
        WHERE period = 'Archaic';
    """,

    "15  Titles ordered by accession year": """
        SELECT title, accessionyear
        FROM artifact_metadata
        ORDER BY accessionyear DESC;
    """,

    "16  Artifacts per department": """
        SELECT department, COUNT(*) total
        FROM artifact_metadata
        GROUP BY department;
    """,

    "17  Distinct hues": """
        SELECT DISTINCT hue
        FROM artifact_colors;
    """,

    "18  Top 5 most used colors": """
        SELECT color, COUNT(*) total
        FROM artifact_colors
        GROUP BY color
        ORDER BY total DESC
        LIMIT 5;
    """,

    "19  Average percent per hue": """
        SELECT hue, AVG(percent) avg_percent
        FROM artifact_colors
        GROUP BY hue;
    """,

    "20  Colors by artifact ID": """
        SELECT objectid, color, hue
        FROM artifact_colors;
    """,

    "21  Total color entries": """
        SELECT COUNT(*) total_colors
        FROM artifact_colors;
    """,

    "22  Titles and hues (Byzantine culture)": """
        SELECT m.title, c.hue
        FROM artifact_metadata m
        JOIN artifact_colors c ON m.id = c.objectid
        WHERE m.culture = 'Byzantine';
    """,

    "23  Artifact titles + hues": """
        SELECT m.title, c.hue
        FROM artifact_metadata m
        JOIN artifact_colors c ON m.id = c.objectid;
    """,

    "24  Titles & culture (period not null)": """
        SELECT title, culture, period
        FROM artifact_metadata
        WHERE period IS NOT NULL;
    """,

    "25  Top 10 grey artifacts": """
        SELECT m.title, m.culture, c.hue
        FROM artifact_metadata m
        JOIN artifact_colors c ON m.id = c.objectid
        WHERE c.hue = 'Grey'
        LIMIT 10;
""",

}
