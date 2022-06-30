select s.factory_id, s.line_id,
       sum(1 - s.abandoned_bobbin / (s.abandoned_bobbin + s.small_bobbin + s.middle_bobbin +
                                     s.large_bobbin + s.full_bobbin)) / count(*) as mean_efficiency
from (select factory_id,
       line_id,
       iif(abandoned_bobbin is null, 0, abandoned_bobbin) as abandoned_bobbin,
       iif(small_bobbin is null, 0, small_bobbin) as small_bobbin,
       iif(middle_bobbin is null, 0, middle_bobbin) as middle_bobbin,
       iif(large_bobbin is null, 0, large_bobbin) as large_bobbin,
       iif(full_bobbin is null, 0, full_bobbin) as full_bobbin
      from spinning_efficiency) s
group by factory_id, line_id;
