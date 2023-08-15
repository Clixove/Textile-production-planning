select
    order_id,
    weight * price - voucher as b_payment, -- benefit: get payment
    score as b_customer,  -- benefit: maintain customer relationship
    log(10, weight) as b_scale,  -- benefit: large orders save management/communication cost and offer better prospect
    weight as c_material,  -- cost: input raw material
    quality as c_quality, -- cost: require quality control
    max((select max(lg_sum_weight) from specialization_rarity_training) - lg_sum_weight, 0) as c_rarity
    -- cost: rare specialization adds difficulty
from orders o join specialization_rarity_training r join customers c
on o.parts = r.parts and o.specification = r.specification and c.customer_id = o.customer_id
where date(created_time) > '2020-09-06'
