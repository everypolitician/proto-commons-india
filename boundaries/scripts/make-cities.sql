
    SELECT
        'Ahmedabad' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Ahmedabad a
UNION
    SELECT
        'Bangalore' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Bangalore a
UNION
    SELECT
        'Bhopal' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Bhopal a
UNION
    SELECT
        'Bhubaneswar' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Bhubaneswar a
UNION
    SELECT
        'Bodh_Gaya' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Bodh_Gaya a
UNION
    SELECT
        'Chandigarh' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Chandigarh a
UNION
    SELECT
        'Chennai' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Chennai a
UNION
    SELECT
        'Coimbatore' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Coimbatore a
UNION
    SELECT
        'Delhi' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Delhi a
UNION
    SELECT
        'Faridabad' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Faridabad a
UNION
    SELECT
        'Hyderabad' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Hyderabad a
UNION
    SELECT
        'Jaipur' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Jaipur a
UNION
    SELECT
        'Katihar' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Katihar a
UNION
    SELECT
        'Kishangarh' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Kishangarh a
UNION
    SELECT
        'Pune' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Pune a
UNION
    SELECT
        'Mumbai' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Mumbai a
UNION
    SELECT
        'NMMC' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        NMMC a
UNION
    SELECT
        'PCMC' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        PCMC a
UNION
    SELECT
        'Purnia' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Purnia a
UNION
    SELECT
        'Vijayawada' AS NAME_EN,
        '' AS MS_FB_PARE,
        '' AS MS_FB,
        ST_Buffer(ST_Buffer(ST_Collect(a.geometry),0.0001), -0.0001) AS geometry
    FROM
        Vijayawada a

