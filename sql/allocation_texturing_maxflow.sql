-- length different because order_id = 13489 is split into 2 batches
-- caution: when resampling, draw order_id instead of row_id to keep flow-out from orders complete
select o.order_id, allocate as weight, efficiency,
       iif(date(created_time) <= '2020-09-06', 1, 0) as is_training_set
from min_cost_flow_texturing m join orders o
on m.order_id = o.order_id
