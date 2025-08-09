with sales as (
    select * from {{ ref('stg_vitamarkets') }}
)
select
    date,
    sku,
    category,
    channel,
    country,
    customer_segment,
    sum(units_sold) as total_units_sold,
    sum(order_value) as total_order_value,
    count(*) as transaction_count,
    max(event) as main_event,
    max(promo_flag) as promo_flag,
    max(discontinued_flag) as discontinued_flag
from sales
group by
    date, sku, category, channel, country, customer_segment
