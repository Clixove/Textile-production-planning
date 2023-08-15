WITH max_lg_sum_weight AS (
    SELECT max(lg_sum_weight) AS max_lg_sum_weight
    FROM specialization_rarity_training
)
SELECT
    o.order_id,
    o.weight * o.price - o.voucher AS b_payment,  -- benefit: get payment
    c.score AS b_customer,                        -- benefit: maintain customer relationship
    log(10, o.weight) AS b_scale,  -- benefit: large orders save management/communication cost and offer better prospect
    o.weight AS c_material,        -- cost: input raw material
    o.quality AS c_quality,        -- cost: require quality control
    max(m.max_lg_sum_weight - r.lg_sum_weight, 0) AS c_rarity  -- cost: rare specialization adds difficulty
FROM orders o
JOIN specialization_rarity_training r ON o.parts = r.parts AND o.specification = r.specification
JOIN customers c ON c.customer_id = o.customer_id
CROSS JOIN max_lg_sum_weight m
WHERE date(o.created_time) <= '2020-09-06'
