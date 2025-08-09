with raw as (
    select *
    from public.vitamarkets_raw
)
select
    date,
    sku,
    category,
    round(units_sold)::int as units_sold,        -- Integer sales, clean!
    round(order_value::numeric, 2) as order_value,
    channel,
    country,
    customer_segment,
    round(cost_per_unit::numeric, 2) as cost_per_unit,
    round(margin_pct::numeric, 2) as margin_pct,
    promo_flag,
    event,
    round(ad_spend::numeric, 2) as ad_spend,
    round(web_traffic)::int as web_traffic,
    round(review_score::numeric, 2) as review_score,
    discontinued_flag,
    launch_date,
    discontinue_date,
    archetype
from raw
where units_sold is not null and order_value is not null
