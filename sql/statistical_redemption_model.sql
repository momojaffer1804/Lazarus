WITH GameBaselines AS (
    SELECT 
        game_id,
        COUNT(review_id) AS n_baseline,
        SUM(CASE WHEN recommended = true THEN 1 ELSE 0 END) AS x_baseline,
        ROUND(AVG(CASE WHEN recommended = true THEN 100.0 ELSE 0.0 END), 2) AS baseline_approval_pct
    FROM reviews
    GROUP BY game_id
),
PatchImpact AS (
    SELECT 
        r.game_id,
        COUNT(r.review_id) AS n_post,
        SUM(CASE WHEN r.recommended = true THEN 1 ELSE 0 END) AS x_post,
        ROUND(AVG(CASE WHEN r.recommended = true THEN 100.0 ELSE 0.0 END), 2) AS post_patch_approval_pct
    FROM reviews r
    JOIN patch_events p ON r.game_id = p.game_id
    WHERE (r.review_date::DATE - p.event_date::DATE) BETWEEN 0 AND 30
    GROUP BY r.game_id
),
CombinedStats AS (
    SELECT 
        g.game_id,
        g.n_baseline,
        g.x_baseline,
        g.baseline_approval_pct,
        COALESCE(p.n_post, 0) AS n_post,
        COALESCE(p.x_post, 0) AS x_post,
        COALESCE(p.post_patch_approval_pct, g.baseline_approval_pct) AS post_patch_approval_pct,
        (g.x_baseline + COALESCE(p.x_post, 0))::NUMERIC / NULLIF(g.n_baseline + COALESCE(p.n_post, 0), 0) AS p_pool
    FROM GameBaselines g
    LEFT JOIN PatchImpact p ON g.game_id = p.game_id
)
SELECT 
    CASE 
        WHEN c.game_id = 1091500 THEN 'Cyberpunk 2077'
        WHEN c.game_id = 275850 THEN 'No Man''s Sky'
        WHEN c.game_id = 379720 THEN 'DOOM'
        WHEN c.game_id = 397540 THEN 'Borderlands 3'
        WHEN c.game_id = 553850 THEN 'Helldivers 2'
        WHEN c.game_id = 1716740 THEN 'Starfield'
        WHEN c.game_id = 1151340 THEN 'Fallout 76'
        WHEN c.game_id = 1086940 THEN 'Baldur''s Gate 3'
        WHEN c.game_id = 292030 THEN 'The Witcher 3'
        WHEN c.game_id = 271590 THEN 'Grand Theft Auto V'
        ELSE 'Unknown Title'
    END AS game_title,
    c.n_baseline AS total_reviews,
    c.n_post AS post_patch_reviews,
    c.baseline_approval_pct,
    c.post_patch_approval_pct,
    ROUND(c.post_patch_approval_pct - c.baseline_approval_pct, 2) AS raw_delta,
    CASE 
        WHEN c.n_post < 30 THEN 0.00
        WHEN c.p_pool = 0 OR c.p_pool = 1 THEN 0.00
        ELSE ROUND(
            ((c.post_patch_approval_pct - c.baseline_approval_pct) / 100.0) / 
            NULLIF(SQRT(c.p_pool * (1.0 - c.p_pool) * ((1.0 / c.n_post) + (1.0 / c.n_baseline))), 0),
            2
        )
    END AS z_score,
    CASE 
        WHEN c.n_post < 30 THEN 'Insufficient Sample (<30)'
        WHEN ABS(
            ((c.post_patch_approval_pct - c.baseline_approval_pct) / 100.0) / 
            NULLIF(SQRT(c.p_pool * (1.0 - c.p_pool) * ((1.0 / c.n_post) + (1.0 / c.n_baseline))), 0)
        ) >= 1.96 THEN 'Significant (p < 0.05)'
        ELSE 'Not Significant'
    END AS significance_status
FROM CombinedStats c
ORDER BY raw_delta DESC;