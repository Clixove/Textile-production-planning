select o.order_id, o.weight, d.efficiency * s.efficiency as efficiency,
       iif(date(created_time) <= '2020-09-06', 1, 0) as is_training_set
from orders o join
(select batch_id, sum((julianday(end_time) - julianday(start_time)) * efficieny) /
                  sum(julianday(end_time) - julianday(start_time)) as efficiency
 from texturing
 group by batch_id) s join dea d
on o.batch_id = s.batch_id and o.order_id = d.order_id