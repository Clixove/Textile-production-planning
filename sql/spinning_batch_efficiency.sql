select s.batch_id, s.scrap_rate, sum(o.weight) as capacity, s.first_appear
from orders o join (
    select batch_id,
           sum(production * scrap_rate) / sum(production) as scrap_rate,
           min(date) as first_appear
    from spinning
    group by batch_id) s
on o.batch_id = s.batch_id
group by s.batch_id
