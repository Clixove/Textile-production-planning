-- Some ground truth of allocating orders to spinning batches violate train/test split.
-- The selected orders are in the training set, but they're allocated to batches where records appear only in
--  spinning table's testing set.
select d.*, o.parts
from orders o join DEA d
on o.order_id = d.order_id
where date(created_time) <= '2020-09-06' and
      batch_id in (
          select distinct batch_id
          from spinning
          where date > '2020-09-06'
      ) and
      batch_id not in (
          select distinct batch_id
          from spinning
          where date <= '2020-09-06'
      )
