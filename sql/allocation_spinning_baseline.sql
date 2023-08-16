select o.order_id, o.weight, d.efficiency * s.efficiency as efficiency,
       iif(date(created_time) <= '2020-09-06', 1, 0) as is_training_set
from orders o join
(select batch_id, 100 / (100 + sum(production * scrap_rate) / sum(production)) as efficiency
from spinning
group by batch_id) s join dea d
on o.batch_id = s.batch_id and o.order_id = d.order_id