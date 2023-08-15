select o.batch_id, s.efficiency, sum(o.weight) as capacity
from orders o join
(select batch_id, sum((julianday(end_time) - julianday(start_time)) * efficieny) /
                 sum(julianday(end_time) - julianday(start_time)) as efficiency,
    start_time, end_time
from texturing
group by batch_id) s
on o.batch_id = s.batch_id
group by s.batch_id
