select 'Min-cost flow (' || iif(date(created_time) <= '2020-09-06', 'training', 'testing') || ')'  as method,
       sum(allocate * efficiency) / sum(allocate) as avg_efficiency
from min_cost_flow_texturing m join orders o
on m.order_id = o.order_id
group by iif(date(created_time) <= '2020-09-06', 'training', 'testing')
union
select 'Baseline (' || iif(date(created_time) <= '2020-09-06', 'training', 'testing') || ')',
       sum(weight * d.efficiency * s.efficiency) / sum(weight) as avg_efficiency
from orders o join
(select batch_id, sum((julianday(end_time) - julianday(start_time)) * efficieny) /
                 sum(julianday(end_time) - julianday(start_time)) as efficiency
from texturing
group by batch_id) s join dea d
on o.batch_id = s.batch_id and o.order_id = d.order_id
group by iif(date(created_time) <= '2020-09-06', 'training', 'testing')
