
-- 1. OVERALL LIFETIME SENTIMENT & PLAYTIME

SELECT 
    recommended AS is_positive_review,
    COUNT(review_id) AS total_reviews,
    ROUND(AVG(playtime_at_review) / 60.0, 1) AS avg_hours_played
FROM reviews
GROUP BY recommended
ORDER BY total_reviews DESC;



-- 2. Critics with Negative reviews and 40+ hours of playtime

SELECT 
    review_date,
    ROUND(playtime_at_review / 60.0, 1) AS hours_played,
    helpful_votes,
    review_text
FROM reviews
WHERE recommended = false 
  AND (playtime_at_review / 60.0) > 40
ORDER BY helpful_votes DESC
LIMIT 5;



-- 3. THE GOD QUERY: Cross-Game Patch Sentiment Delta (Redemption Index)

WITH GameBaselines AS (
    -- Step 1: Calculate the overall lifetime sentiment for every game
    SELECT 
        game_id,
        COUNT(review_id) AS total_lifetime_reviews,
        ROUND(AVG(CASE WHEN recommended = true THEN 100.0 ELSE 0.0 END), 1) AS lifetime_approval
    FROM reviews
    GROUP BY game_id
),
PatchImpact AS (
    -- Step 2: Calculate sentiment strictly during active development cycles (30 days post-patch)
    SELECT 
        r.game_id,
        COUNT(r.review_id) AS post_patch_reviews,
        ROUND(AVG(CASE WHEN r.recommended = true THEN 100.0 ELSE 0.0 END), 1) AS post_patch_approval
    FROM reviews r
    JOIN patch_events p ON r.game_id = p.game_id
    WHERE (r.review_date::DATE - p.event_date) BETWEEN 0 AND 30
    GROUP BY r.game_id
)
-- Step 3: Map the names and calculate the "Redemption Delta"
SELECT 
    CASE 
        WHEN g.game_id = 1091500 THEN 'Cyberpunk 2077'
        WHEN g.game_id = 275850 THEN 'No Man''s Sky'
        WHEN g.game_id = 379720 THEN 'DOOM'
        WHEN g.game_id = 397540 THEN 'Borderlands 3'
        WHEN g.game_id = 553850 THEN 'Helldivers 2'
        WHEN g.game_id = 1716740 THEN 'Starfield'
        WHEN g.game_id = 1151340 THEN 'Fallout 76'
        WHEN g.game_id = 1086940 THEN 'Baldur''s Gate 3'
        WHEN g.game_id = 292030 THEN 'The Witcher 3'
        WHEN g.game_id = 271590 THEN 'Grand Theft Auto V'
        ELSE 'Unknown Title'
    END AS game_title,
    g.total_lifetime_reviews,
    g.lifetime_approval AS baseline_rating,
    p.post_patch_approval AS active_dev_rating,
    ROUND(COALESCE(p.post_patch_approval, g.lifetime_approval) - g.lifetime_approval, 1) AS patch_sentiment_bump
FROM GameBaselines g
LEFT JOIN PatchImpact p ON g.game_id = p.game_id
ORDER BY patch_sentiment_bump DESC;