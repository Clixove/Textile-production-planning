select d.*, round(o.weight, 0) as weight, o.batch_id
from orders o join DEA d
on o.order_id = d.order_id
where date(created_time) > '2020-09-06' and
      batch_id in (
          select distinct batch_id
          from spinning
      )
