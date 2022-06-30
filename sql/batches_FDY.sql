-- combine orders into groups
-- retrieve current batches of FDY
select batch_id,
       sum(weight) as total_weight,  -- input
       sum(weight * o.price - o.voucher) as total_price, -- output
       iif(total_weight_inhist is null, 0, total_weight_inhist) as total_weight_inhist,
           -- input: whether the specification is common
       sum(iif(quality like 'AAA%', 4,
               iif(quality like 'AA%', 3,
                   iif(quality == 'A', 2, iif(quality == 'B', 1, null))
                   )
               ) * o.weight
           ) / sum(weight) as quality, -- input
       cl.level as customer_level -- output
from orders o join customers c on c.name = o.customer_name and c.production = o.production
    join customers_level cl on cl.name = c.level
    left join (
        select specification, sum(weight) as total_weight_inhist
        from orders_historical
        where production == 'FDY'
        group by specification
    ) s on s.specification = o.specification
where o.production == 'FDY'
group by batch_id;
