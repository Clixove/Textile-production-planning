select 'Min-cost flow (training)' as method, sum(allocate * efficiency) / sum(allocate) as avg_efficiency
from min_cost_flow_spinning m join orders o
on m.order_id = o.order_id
where date(created_time) <= '2020-09-06'
union
select 'Min-cost flow (testing)', sum(allocate * efficiency) / sum(allocate) as avg_efficiency
from min_cost_flow_spinning m join orders o
on m.order_id = o.order_id
where date(created_time) > '2020-09-06'
union
select 'Baseline (training)', sum(weight * d.efficiency / (100 + s.scrap_rate) * 100) / sum(weight) as avg_efficiency
from orders o join
(select batch_id, sum(production * scrap_rate) / sum(production) as scrap_rate, min(date) as first_appear
from spinning
group by batch_id) s join dea d
on o.batch_id = s.batch_id and o.order_id = d.order_id
where date(created_time) <= '2020-09-06'
union
select 'Baseline (testing)', sum(weight * d.efficiency / (100 + s.scrap_rate) * 100) / sum(weight) as avg_efficiency
from orders o join
(select batch_id, sum(production * scrap_rate) / sum(production) as scrap_rate, min(date) as first_appear
from spinning
group by batch_id) s join dea d
on o.batch_id = s.batch_id and o.order_id = d.order_id
where date(created_time) > '2020-09-06'
